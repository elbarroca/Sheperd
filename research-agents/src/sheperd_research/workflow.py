from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from time import monotonic
from typing import NamedTuple, Protocol, TypedDict, runtime_checkable
from urllib.parse import urlsplit

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    LaneDiscoveryResult,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    RunResult,
    RunStatus,
    SignalEvent,
    SourceCandidate,
    TopicConfig,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from .db import RepositoryProtocol
from .providers.errors import ProviderError
from .topics import default_topic_configs
from .validation import build_validation_report, source_quality_sources
from .validators import (
    content_hash,
    deduplicate_sources,
    normalize_url,
    url_policy_error,
    validate_claim_citations,
    validate_source_dates,
    with_draft_prefix,
)

MAX_PARALLEL_LANES = 3
MAX_PARALLEL_DISTILLATIONS = 2
DEFAULT_MAX_LLM_CALLS = 48
DEFAULT_MAX_LLM_INPUT_CHARS = 350_000
DEFAULT_MAX_RUN_SECONDS = 900
# Keep workflow accounting aligned with the provider's bounded source window.
MAX_LLM_SOURCE_CHARS = 8_000
PROMPT_VERSION = "workflow-v3"
CHECKPOINT_ALLOWED_MODULES = tuple(
    ("sheperd_research.contracts", name)
    for name in (
        "EvidenceStatus",
        "ReviewState",
        "RunStatus",
        "ValidationStatus",
        "ContractModel",
        "SourceCandidate",
        "ClaimDraft",
        "ReportBullet",
        "ArticleDistillation",
        "SignalEvent",
        "WeeklyBrief",
        "TopicConfig",
        "ResearchRunRequest",
        "RunResult",
        "ValidationCheck",
        "ValidationReport",
    )
)


def checkpoint_serializer() -> JsonPlusSerializer:
    return JsonPlusSerializer(allowed_msgpack_modules=CHECKPOINT_ALLOWED_MODULES)


class LaneSpec(NamedTuple):
    name: str
    query_indexes: tuple[int, ...]
    geographies: tuple[str, ...]


LANES = (
    LaneSpec("regulatory", (0, 4), ("Regulatory", "United States")),
    LaneSpec("us-ports", (1, 2, 4), ("West Coast", "East Coast", "Gulf")),
    LaneSpec("mexico", (3, 4), ("Mexico",)),
)


class TavilyLike(Protocol):
    async def search(
        self,
        query: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        max_results: int = 5,
    ) -> list[SourceCandidate]: ...

    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]: ...


class LlmLike(Protocol):
    async def distill(
        self,
        source: SourceCandidate,
        content: str,
        *,
        prompt_version: str = "distill-v4",
    ) -> ArticleDistillation: ...

    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        *,
        covered_from: datetime,
        covered_until: datetime,
        prompt_version: str = "weekly-brief-v4",
    ) -> WeeklyBrief: ...


@runtime_checkable
class LaneResearchLike(Protocol):
    async def discover_lane(
        self,
        lane: str,
        queries: list[str],
        geographies: tuple[str, ...],
        *,
        since: datetime,
        until: datetime,
        include_domains: list[str],
        exclude_domains: list[str],
        max_results: int,
        tavily: TavilyLike,
    ) -> LaneDiscoveryResult: ...


@runtime_checkable
class CriticLike(Protocol):
    async def critic(
        self,
        claims: list[ClaimDraft],
        source_urls: set[str],
        *,
        prompt_version: str = "critic-v4",
    ) -> list[ClaimDraft]: ...


class GraphState(TypedDict, total=False):
    run_id: str
    request: ResearchRunRequest
    topic: TopicConfig
    sources: list[SourceCandidate]
    content: dict[str, str]
    source_hashes: list[str]
    distillations: list[ArticleDistillation]
    claims: list[ClaimDraft]
    brief: WeeklyBrief
    validation: ValidationReport
    lane_statuses: dict[str, str]
    partial_reasons: list[str]


class ResearchWorkflow:
    def __init__(
        self,
        repository: RepositoryProtocol,
        tavily: TavilyLike,
        llm: LlmLike,
        topic_configs: dict[str, TopicConfig] | None = None,
        checkpointer: BaseCheckpointSaver[str] | None = None,
        max_llm_calls: int = DEFAULT_MAX_LLM_CALLS,
        max_llm_input_chars: int = DEFAULT_MAX_LLM_INPUT_CHARS,
        max_run_seconds: int = DEFAULT_MAX_RUN_SECONDS,
    ) -> None:
        self.repository = repository
        self.tavily = tavily
        self.llm = llm
        self.topic_configs = topic_configs or default_topic_configs()
        self.checkpointer = checkpointer
        self.max_llm_calls = max_llm_calls
        self.max_llm_input_chars = max_llm_input_chars
        self.max_run_seconds = max_run_seconds
        self._llm_calls = 0
        self._llm_input_chars = 0

    def _reserve_llm_call(self, input_chars: int) -> bool:
        if self._llm_calls >= self.max_llm_calls:
            return False
        if self._llm_input_chars + input_chars > self.max_llm_input_chars:
            return False
        self._llm_calls += 1
        self._llm_input_chars += input_chars
        return True

    def _llm_metadata(self, history_start: int | None = None) -> dict[str, object]:
        current_call_metadata = getattr(self.llm, "current_call_metadata", None)
        if callable(current_call_metadata):
            value = current_call_metadata()
            return dict(value) if isinstance(value, dict) else {}
        value = getattr(self.llm, "last_call_metadata", {})
        metadata = dict(value) if isinstance(value, dict) else {}
        history = getattr(self.llm, "call_history", [])
        if history_start is not None and isinstance(history, list):
            metadata["attempts"] = [
                dict(item) for item in history[history_start:] if isinstance(item, dict)
            ]
        return metadata

    def _safe_update_run_status(
        self, run_id: str, status: RunStatus, error: str | None = None
    ) -> str | None:
        try:
            self.repository.update_run_status(run_id, status, error)
        except Exception as status_error:
            return f"status update failed: {status_error.__class__.__name__}"
        return None

    def _record_step(
        self,
        run_id: str,
        agent_name: str,
        status: str,
        metadata: dict[str, object],
        *,
        input_payload: object | None = None,
        output_payload: object | None = None,
        lane: str = "system",
        attempt: int = 1,
        duration_ms: int | None = None,
        started_at: float | None = None,
        error_code: str | None = None,
    ) -> None:
        if duration_ms is None and started_at is not None:
            duration_ms = max(0, int((monotonic() - started_at) * 1000))

        def payload_hash(value: object | None) -> str | None:
            if value is None:
                return None
            serialized = json.dumps(value, default=str, sort_keys=True)
            return content_hash(serialized)

        attempts = metadata.get("attempts")
        if (
            not isinstance(attempts, list)
            or not attempts
            or not all(isinstance(item, dict) for item in attempts)
        ):
            attempts = [metadata.get("call", metadata)]
        for index, call in enumerate(attempts):
            call_metadata = dict(call) if isinstance(call, dict) else {}
            record_metadata = dict(metadata)
            record_metadata["call"] = call_metadata
            provider_attempt = call_metadata.get("attempt")
            if isinstance(provider_attempt, int):
                record_metadata["provider_attempt"] = provider_attempt
            call_duration = call_metadata.get("latency_ms")
            record_attempt = call_metadata.get("record_attempt")
            repository_attempt = (
                record_attempt if isinstance(record_attempt, int) else attempt + index
            )
            call_input_hash = call_metadata.get("input_hash")
            call_output_hash = call_metadata.get("output_hash")
            self.repository.record_step(
                run_id,
                agent_name,
                status if call_metadata.get("error_code") is None else "failed",
                record_metadata,
                lane=lane,
                attempt=repository_attempt,
                duration_ms=call_duration if isinstance(call_duration, int) else duration_ms,
                input_hash=(
                    call_input_hash
                    if isinstance(call_input_hash, str)
                    else payload_hash(input_payload)
                ),
                output_hash=(
                    call_output_hash
                    if isinstance(call_output_hash, str)
                    else payload_hash(output_payload)
                ),
                error_code=(
                    call_metadata.get("error_code")
                    if isinstance(call_metadata.get("error_code"), str)
                    else error_code
                ),
            )
            receipts = call_metadata.get("tool_call_receipts")
            if isinstance(receipts, list):
                self.repository.record_tool_calls(
                    run_id,
                    agent_name,
                    repository_attempt,
                    lane,
                    [item for item in receipts if isinstance(item, dict)],
                )

    @staticmethod
    def _protect_seed_claims(
        claims: list[ClaimDraft], sources: list[SourceCandidate]
    ) -> list[ClaimDraft]:
        seed_urls = {
            normalize_url(source.url) for source in sources if source.is_seed
        }
        protected: list[ClaimDraft] = []
        for claim in claims:
            cited_urls = {normalize_url(url) for url in claim.source_urls}
            if (
                claim.evidence_status.value == "verified"
                and cited_urls
                and cited_urls.issubset(seed_urls)
            ):
                protected.append(
                    claim.model_copy(
                        update={"evidence_status": EvidenceStatus.UNVERIFIED}
                    )
                )
            else:
                protected.append(claim)
        return protected

    async def run(self, request: ResearchRunRequest, run_id: str | None = None) -> RunResult:
        run_id = run_id or str(uuid.uuid4())
        self._llm_calls = 0
        self._llm_input_chars = 0
        self.repository.create_run(run_id, request)
        try:
            topic = self.topic_configs.get(request.topic_set)
            if topic is None:
                raise ValueError(f"unknown topic set: {request.topic_set}")
            graph = self._build_graph(self.checkpointer)
            final_state = await asyncio.wait_for(
                graph.ainvoke(
                    {
                        "run_id": run_id,
                        "request": request,
                        "topic": topic,
                        "partial_reasons": [],
                    },
                    config={"configurable": {"thread_id": run_id}},
                ),
                timeout=self.max_run_seconds,
            )
            brief = final_state.get("brief")
            validation = final_state.get("validation")
            partial_reasons = final_state.get("partial_reasons", [])
            validation_failed = validation is None or validation.status is not ValidationStatus.PASS
            status = (
                RunStatus.FAILED
                if partial_reasons or brief is None or validation_failed
                else RunStatus.SUCCEEDED
            )
            error = "; ".join(partial_reasons) if partial_reasons else None
            if error is None and validation_failed:
                error = (
                    "validation missing"
                    if validation is None
                    else f"validation: {validation.status.value}"
                )
            self.repository.update_run_status(run_id, status, error)
            return RunResult(
                run_id=run_id,
                status=status,
                source_count=len(source_quality_sources(final_state.get("sources", []))),
                distillation_count=len(final_state.get("distillations", [])),
                claim_count=len(final_state.get("claims", [])),
                brief_id=brief.run_id if brief else None,
                error=error,
                citation_coverage=validation.citation_coverage if validation else 0.0,
                validation_status=(
                    validation.status if validation else ValidationStatus.BLOCKED
                ),
                lane_statuses=final_state.get("lane_statuses", {}),
            )
        except TimeoutError:
            message = f"workflow exceeded {self.max_run_seconds}s wall-clock budget"
            status_error = self._safe_update_run_status(run_id, RunStatus.FAILED, message)
            if status_error:
                message = f"{message}; {status_error}"
            return RunResult(run_id=run_id, status=RunStatus.FAILED, error=message)
        except ProviderError as error:
            message = str(error)
            status_error = self._safe_update_run_status(run_id, RunStatus.FAILED, message)
            if status_error:
                message = f"{message}; {status_error}"
            return RunResult(run_id=run_id, status=RunStatus.FAILED, error=message)
        except Exception as error:
            message = str(error) or error.__class__.__name__
            status_error = self._safe_update_run_status(run_id, RunStatus.FAILED, message)
            if status_error:
                message = f"{message}; {status_error}"
            return RunResult(run_id=run_id, status=RunStatus.FAILED, error=message)

    def _build_graph(
        self, checkpointer: BaseCheckpointSaver[str] | None = None
    ) -> CompiledStateGraph[GraphState, None, GraphState, GraphState]:
        builder = StateGraph(GraphState)
        builder.add_node("discover_lanes", self._discover_lanes)
        builder.add_node("extract", self._extract)
        builder.add_node("distill", self._distill)
        builder.add_node("critic", self._critic)
        builder.add_node("synthesize", self._synthesize)
        builder.add_node("validate", self._validate)
        builder.add_edge(START, "discover_lanes")
        builder.add_edge("discover_lanes", "extract")
        builder.add_edge("extract", "distill")
        builder.add_edge("distill", "critic")
        builder.add_edge("critic", "synthesize")
        builder.add_edge("synthesize", "validate")
        builder.add_edge("validate", END)
        return builder.compile(checkpointer=checkpointer)

    @staticmethod
    def _domain_matches(host: str, domains: list[str]) -> bool:
        return any(
            host == domain.removeprefix("www.").lower()
            or host.endswith(f".{domain.removeprefix('www.').lower()}")
            for domain in domains
        )

    @classmethod
    def _validate_lane_source(
        cls,
        source: SourceCandidate,
        lane: LaneSpec,
        since: datetime,
        until: datetime,
        include_domains: list[str],
        exclude_domains: list[str],
    ) -> SourceCandidate:
        normalized_url = normalize_url(source.url)
        if url_policy_error(normalized_url, excluded_domains=exclude_domains) is not None:
            raise ProviderError("discovery returned a source rejected by URL policy")
        host = (urlsplit(normalized_url).hostname or "").lower()
        if not host:
            raise ProviderError("discovery returned a source without a host")
        if cls._domain_matches(host, exclude_domains):
            raise ProviderError("discovery returned an excluded source host")
        if include_domains and not cls._domain_matches(host, include_domains):
            raise ProviderError("discovery returned a source outside allowed hosts")
        if source.published_at is None or not since <= source.published_at <= until:
            raise ProviderError("discovery returned a source outside the date window")
        allowed_geographies = {geography.casefold() for geography in lane.geographies}
        observed_geographies = {geography.casefold() for geography in source.geographies}
        if not observed_geographies.intersection(allowed_geographies):
            raise ProviderError("discovery returned a source outside lane geography")
        return source.model_copy(update={"url": normalized_url})

    async def _discover_lane(
        self,
        lane: LaneSpec,
        request: ResearchRunRequest,
        topic: TopicConfig,
    ) -> tuple[
        str,
        list[SourceCandidate],
        dict[str, str],
        str | None,
        int,
        dict[str, object],
    ]:
        started_at = monotonic()
        since = request.since or request.as_of - timedelta(days=topic.lookback_days)
        sources: list[SourceCandidate] = []
        content: dict[str, str] = {}
        metadata: dict[str, object] = {}
        try:
            if not isinstance(self.llm, LaneResearchLike):
                raise ProviderError("workflow requires model-issued lane discovery")
            configured_queries = [
                topic.queries[index]
                for index in lane.query_indexes
                if index < len(topic.queries)
            ]
            if not self._reserve_llm_call(sum(len(query) for query in configured_queries)):
                raise ProviderError("discovery: llm budget exceeded")
            result = await self.llm.discover_lane(
                lane.name,
                configured_queries,
                lane.geographies,
                since=since,
                until=request.as_of,
                include_domains=topic.include_domains,
                exclude_domains=topic.exclude_domains,
                max_results=max(1, request.max_sources // 5),
                tavily=self.tavily,
            )
            validated_sources = [
                self._validate_lane_source(
                    source,
                    lane,
                    since,
                    request.as_of,
                    topic.include_domains,
                    topic.exclude_domains,
                )
                for source in result.sources
            ]
            sources = [
                source.model_copy(
                    update={
                        "topics": sorted(set(source.topics + [request.topic_set, lane.name])),
                        "geographies": sorted(set(source.geographies)),
                        "lane": lane.name,
                    }
                )
                for source in validated_sources
            ]
            content = dict(result.content)
            metadata = {
                **dict(result.metadata),
                "packet": result.packet.model_dump(mode="json"),
            }
            if not sources:
                return (
                    lane.name,
                    sources,
                    content,
                    "discovery worker returned no sources",
                    max(0, int((monotonic() - started_at) * 1000)),
                    metadata,
                )
            return (
                lane.name,
                sources,
                content,
                None,
                max(0, int((monotonic() - started_at) * 1000)),
                metadata,
            )
        except ProviderError as error:
            raw_attempts = getattr(error, "attempts", [])
            if isinstance(raw_attempts, list):
                metadata["attempts"] = [
                    dict(item) for item in raw_attempts if isinstance(item, dict)
                ]
            return (
                lane.name,
                sources,
                content,
                str(error),
                max(0, int((monotonic() - started_at) * 1000)),
                metadata,
            )
        except Exception as error:
            return (
                lane.name,
                sources,
                content,
                error.__class__.__name__,
                max(0, int((monotonic() - started_at) * 1000)),
                metadata,
            )

    async def _discover_lanes(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        request = state["request"]
        topic = state["topic"]
        lane_results = await asyncio.gather(
            *(self._discover_lane(lane, request, topic) for lane in LANES)
        )
        lane_sources: dict[str, list[SourceCandidate]] = {}
        lane_statuses: dict[str, str] = {}
        lane_content: dict[str, str] = {}
        lane_errors: list[str] = []
        for lane_name, sources, content, error, duration_ms, metadata in lane_results:
            lane_sources[lane_name] = sources
            lane_content.update(content)
            lane_statuses[lane_name] = "failed" if error else "succeeded"
            if error:
                lane_errors.append(f"{lane_name}: {error}")
            step_metadata = {"source_count": len(sources), "error": error, **metadata}
            if "agent_call" in metadata:
                step_metadata["call"] = metadata["agent_call"]
            self._record_step(
                state["run_id"],
                f"discovery:{lane_name}",
                lane_statuses[lane_name],
                step_metadata,
                lane=lane_name,
                duration_ms=duration_ms,
                input_payload={"topic_set": request.topic_set, "lane": lane_name},
                output_payload=[source.url for source in sources],
                error_code="provider" if error else None,
            )

        seed_urls = [*request.seed_urls]
        if request.include_topic_seeds:
            seed_urls = [*topic.seed_urls, *seed_urls]
        seeds, seed_metadata = self._safe_seed_sources(
            seed_urls,
            topic,
            request.topic_set,
        )
        ordered: list[SourceCandidate] = [*seeds]
        max_lane_sources = max((len(items) for items in lane_sources.values()), default=0)
        for index in range(max_lane_sources):
            for lane in LANES:
                if index < len(lane_sources[lane.name]):
                    ordered.append(lane_sources[lane.name][index])
        unique = deduplicate_sources(ordered)[: request.max_sources]
        validate_source_dates(unique, request.as_of)
        for source in unique:
            self.repository.record_source(source)
        self._record_step(
            state["run_id"],
            "discovery",
            "failed" if lane_errors else "succeeded",
            {
                "source_count": len(unique),
                "lane_count": len(LANES),
                **seed_metadata,
                "errors": lane_errors,
            },
            started_at=started_at,
            input_payload={"topic_set": request.topic_set, "as_of": request.as_of},
            output_payload={
                "source_urls": [source.url for source in unique],
                "lane_statuses": lane_statuses,
            },
            error_code="provider" if lane_errors else None,
        )
        if lane_errors:
            raise ProviderError("; ".join(lane_errors))
        return {
            "sources": unique,
            "content": {
                normalize_url(source.url): lane_content[normalize_url(source.url)]
                for source in unique
                if normalize_url(source.url) in lane_content
            },
            "lane_statuses": lane_statuses,
            "partial_reasons": lane_errors,
        }

    @staticmethod
    def _seed_lane(url: str) -> str:
        lowered = url.lower()
        if "linkedin.com" in lowered or "fmc.gov" in lowered or "court" in lowered:
            return "regulatory"
        if any(token in lowered for token in ("mexico", "manzanillo", "veracruz", "altamira")):
            return "mexico"
        if "gcaptain.com" in lowered or "port" in lowered:
            return "us-ports"
        return "unassigned"

    @classmethod
    def _safe_seed_sources(
        cls,
        seed_urls: list[str],
        topic: TopicConfig,
        topic_set: str,
    ) -> tuple[list[SourceCandidate], dict[str, object]]:
        seed_sources: list[SourceCandidate] = []
        accepted_seed_count = 0
        quarantined_reasons: dict[str, int] = {}
        quarantined_domains: set[str] = set()
        for seed_url in seed_urls:
            normalized = normalize_url(seed_url)
            reason = url_policy_error(normalized, excluded_domains=topic.exclude_domains)
            host = (urlsplit(normalized).hostname or "").lower().removeprefix("www.")
            if reason is not None:
                quarantined_reasons[reason] = quarantined_reasons.get(reason, 0) + 1
                if host:
                    quarantined_domains.add(host)
            else:
                accepted_seed_count += 1
            seed_sources.append(
                SourceCandidate(
                    url=normalized,
                    source_kind="seed-only",
                    is_seed=True,
                    evidence_status=EvidenceStatus.UNVERIFIED,
                    topics=[topic_set],
                    lane=cls._seed_lane(normalized),
                )
            )
        return seed_sources, {
            "accepted_seed_count": accepted_seed_count,
            "quarantined_seed_count": len(seed_urls) - accepted_seed_count,
            "quarantined_seed_domains": sorted(quarantined_domains),
            "quarantined_seed_reasons": quarantined_reasons,
        }

    async def _extract(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        sources = state.get("sources", [])
        extractable_sources = [source for source in sources if not source.is_seed]
        content = dict(state.get("content", {}))
        missing = [
            source
            for source in extractable_sources
            if normalize_url(source.url) not in content
        ]
        try:
            missing_content = [
                normalize_url(source.url)
                for source in extractable_sources
                if not content.get(normalize_url(source.url), "").strip()
            ]
            if missing_content:
                raise ProviderError(
                    "extraction missing content for: " + ", ".join(missing_content)
                )
            source_hashes: list[str] = []
            for source in extractable_sources:
                normalized_url = normalize_url(source.url)
                body = content[normalized_url]
                if body.strip():
                    self.repository.record_snapshot(state["run_id"], source, body)
                    source_hashes.append(content_hash(body))
            self._record_step(
                state["run_id"],
                "extraction",
                "succeeded",
                {
                    "extracted_count": len(content),
                    "missing_agent_extractions": len(missing),
                    "seed_only_count": len(sources) - len(extractable_sources),
                },
                started_at=started_at,
                input_payload=[source.url for source in extractable_sources],
                output_payload=source_hashes,
            )
            return {
                "content": content,
                "source_hashes": source_hashes,
                "partial_reasons": list(state.get("partial_reasons", [])),
            }
        except ProviderError as provider_error:
            self._record_step(
                state["run_id"],
                "extraction",
                "failed",
                {
                    "extracted_count": len(content),
                    "missing_agent_extractions": len(missing),
                    "seed_only_count": len(sources) - len(extractable_sources),
                    "error": str(provider_error),
                },
                started_at=started_at,
                input_payload=[source.url for source in extractable_sources],
                output_payload=None,
                error_code="provider",
            )
            raise

    async def _distill_one(
        self,
        source: SourceCandidate,
        body: str,
        as_of: datetime,
        semaphore: asyncio.Semaphore,
    ) -> tuple[ArticleDistillation | None, str | None, dict[str, object]]:
        async with semaphore:
            if not self._reserve_llm_call(min(len(body), MAX_LLM_SOURCE_CHARS)):
                return None, "llm budget exceeded", {"error_code": "budget_exceeded"}
            normalized_source_url = normalize_url(source.url)
            input_hash = content_hash(body)

            def annotate(metadata: dict[str, object]) -> dict[str, object]:
                annotated = dict(metadata)
                annotated["source_url"] = normalized_source_url
                annotated["input_hash"] = input_hash
                nested_attempts = annotated.get("attempts")
                if isinstance(nested_attempts, list):
                    annotated["attempts"] = [
                        {
                            **dict(item),
                            "source_url": normalized_source_url,
                            "input_hash": input_hash,
                        }
                        for item in nested_attempts
                        if isinstance(item, dict)
                    ]
                return annotated

            try:
                distillation = await self.llm.distill(
                    source,
                    body,
                    prompt_version="distill-v4",
                )
                validate_claim_citations(distillation.claims, {source.url}, as_of)
                return distillation, None, annotate(self._llm_metadata())
            except (ProviderError, ValueError) as error:
                return (
                    None,
                    str(error) or error.__class__.__name__,
                    annotate(self._llm_metadata()),
                )

    async def _distill(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        all_sources = state.get("sources", [])
        sources = [source for source in all_sources if not source.is_seed]
        content = dict(state.get("content", {}))
        missing_bodies = [
            normalize_url(source.url)
            for source in sources
            if not content.get(normalize_url(source.url), "").strip()
        ]
        if missing_bodies:
            raise ProviderError(
                "distillation missing source body for: " + ", ".join(missing_bodies)
            )
        bodies: dict[str, str] = {}
        for source in sources:
            normalized_url = normalize_url(source.url)
            body = content.get(normalized_url, "")
            bodies[normalized_url] = body
        semaphore = asyncio.Semaphore(MAX_PARALLEL_DISTILLATIONS)
        tasks = [
            self._distill_one(
                source,
                bodies[normalize_url(source.url)],
                state["request"].as_of,
                semaphore,
            )
            for source in sources
        ]
        results = await asyncio.gather(*tasks)
        distillations: list[ArticleDistillation] = []
        call_metadata: list[dict[str, object]] = []
        errors: list[str] = []
        for distillation, error, metadata in results:
            if metadata:
                call_metadata.append(metadata)
            if distillation is not None:
                distillations.append(distillation)
            elif error:
                errors.append(f"distillation: {error}")
        claims = [claim for item in distillations for claim in item.claims]
        attempts: list[dict[str, object]] = []
        record_attempt = 1
        for call_record in call_metadata:
            nested = call_record.get("attempts")
            if isinstance(nested, list):
                for call in nested:
                    if not isinstance(call, dict):
                        continue
                    attempts.append({**dict(call), "record_attempt": record_attempt})
                    record_attempt += 1
            else:
                attempts.append({**call_record, "record_attempt": record_attempt})
                record_attempt += 1
        source_by_url = {normalize_url(source.url): source for source in sources}
        protected_distillations: list[ArticleDistillation] = []
        for item in distillations:
            matched_source = source_by_url.get(normalize_url(item.source_url))
            protected_claims = self._protect_seed_claims(
                item.claims,
                [matched_source] if matched_source is not None else [],
            )
            protected_distillations.append(item.model_copy(update={"claims": protected_claims}))
        distillations = protected_distillations
        claims = [claim for item in distillations for claim in item.claims]
        for distillation in distillations:
            self.repository.record_distillation(state["run_id"], distillation)
            self.repository.record_claims(state["run_id"], distillation.claims)
        step_status = "failed" if errors else "succeeded"
        self._record_step(
            state["run_id"],
            "distillation",
            step_status,
            {
                "distillation_count": len(distillations),
                "claim_count": len(claims),
                "llm_calls": self._llm_calls,
                "llm_input_chars": self._llm_input_chars,
                "calls": call_metadata,
                "call": call_metadata[-1] if call_metadata else {},
                "attempts": attempts,
                "errors": errors,
            },
            started_at=started_at,
            input_payload=list(bodies.keys()),
            output_payload={
                "source_urls": [item.source_url for item in distillations],
                "claim_count": len(claims),
            },
            error_code="provider-or-schema" if errors else None,
        )
        if errors:
            raise ProviderError("; ".join(errors))
        return {
            "distillations": distillations,
            "claims": claims,
            "partial_reasons": list(state.get("partial_reasons", [])),
        }

    async def _critic(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        claims = list(state.get("claims", []))
        source_urls = {url for claim in claims for url in claim.source_urls}
        revised = claims
        mode = "deterministic"
        critic_call: dict[str, object] = {}
        critic_error: str | None = None
        if isinstance(self.llm, CriticLike) and claims:
            if not self._reserve_llm_call(sum(len(claim.claim) for claim in claims)):
                critic_error = "critic: llm budget exceeded"
            else:
                try:
                    revised = await self.llm.critic(
                        claims,
                        source_urls,
                        prompt_version="critic-v4",
                    )
                    validate_claim_citations(revised, source_urls, state["request"].as_of)
                    mode = "openrouter-structured"
                    critic_call = self._llm_metadata()
                except (ProviderError, ValueError) as error:
                    critic_call = self._llm_metadata()
                    critic_error = f"critic: {error}"
        revised = self._protect_seed_claims(revised, state.get("sources", []))
        revised_by_source: dict[str, list[ClaimDraft]] = defaultdict(list)
        for claim in revised:
            for url in claim.source_urls:
                revised_by_source[normalize_url(url)].append(claim)
        distillations = [
            item.model_copy(
                update={
                    "claims": revised_by_source.get(
                        normalize_url(item.source_url), item.claims
                    )
                }
            )
            for item in state.get("distillations", [])
        ]
        self.repository.record_claims(state["run_id"], revised)
        self._record_step(
            state["run_id"],
            "critic",
            "failed" if critic_error else "succeeded",
            {
                "claim_count": len(revised),
                "mode": mode,
                "llm_calls": self._llm_calls,
                "llm_input_chars": self._llm_input_chars,
                "call": {key: value for key, value in critic_call.items() if key != "attempts"},
                "attempts": critic_call.get("attempts", []),
                "error": critic_error,
            },
            started_at=started_at,
            input_payload=[claim.model_dump(mode="json") for claim in claims],
            output_payload=[claim.model_dump(mode="json") for claim in revised],
            error_code="provider-or-schema" if critic_error else None,
        )
        if critic_error:
            raise ProviderError(critic_error)
        return {
            "claims": revised,
            "distillations": distillations,
            "partial_reasons": list(state.get("partial_reasons", [])),
        }

    @staticmethod
    def _validate_report_bullets(
        brief: WeeklyBrief,
        claims: list[ClaimDraft],
        known_urls: set[str],
    ) -> WeeklyBrief:
        fallback = [
            ReportBullet(
                text=claim.claim,
                source_urls=[normalize_url(url) for url in claim.source_urls],
                evidence_status=claim.evidence_status,
            )
            for claim in claims[:3]
        ]
        updates: dict[str, object] = {}
        for section in (
            "executive_bullets",
            "developments",
            "risks",
            "opportunities",
            "uncertainties",
        ):
            bullets = list(getattr(brief, section))
            if not bullets and section in {"executive_bullets", "developments"}:
                bullets = fallback
            normalized: list[ReportBullet] = []
            for bullet in bullets:
                urls = [normalize_url(url) for url in bullet.source_urls]
                if not urls or not set(urls).issubset(known_urls):
                    raise ValueError(f"{section} contains an uncited or unknown URL")
                normalized.append(bullet.model_copy(update={"source_urls": urls}))
            updates[section] = normalized
        return brief.model_copy(update=updates)

    async def _synthesize(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        request = state["request"]
        distillations = state.get("distillations", [])
        claims = state.get("claims", [])
        source_urls = {source.url for source in state.get("sources", [])}
        validate_claim_citations(claims, source_urls, request.as_of)
        known_urls = {url for claim in claims for url in claim.source_urls}
        source_by_url = {normalize_url(source.url): source for source in state.get("sources", [])}
        events = [
            SignalEvent(
                event_id=content_hash(
                    f"{state['run_id']}:{claim.claim}:"
                    f"{','.join(sorted(normalize_url(url) for url in claim.source_urls))}"
                )[:32],
                run_id=state["run_id"],
                event_type="source-linked-claim",
                summary=claim.claim,
                geographies=sorted(
                    {
                        geography
                        for url in claim.source_urls
                        for geography in source_by_url.get(
                            normalize_url(url), SourceCandidate(url=url)
                        ).geographies
                    }
                ),
                source_urls=claim.source_urls,
                evidence_status=claim.evidence_status,
            )
            for claim in claims
        ]
        self.repository.record_signal_events(events)
        brief: WeeklyBrief | None = None
        synthesis_call: dict[str, object] = {}
        synthesis_error: str | None = None
        if not self._reserve_llm_call(sum(len(item.summary) for item in distillations)):
            synthesis_error = "synthesis: llm budget exceeded"
        else:
            try:
                since = request.since or request.as_of - timedelta(
                    days=state["topic"].lookback_days
                )
                brief = await self.llm.synthesize(
                    state["run_id"],
                    distillations,
                    covered_from=since,
                    covered_until=request.as_of,
                    prompt_version="weekly-brief-v4",
                )
                synthesis_call = self._llm_metadata()
                brief = self._validate_report_bullets(brief, claims, {
                    normalize_url(url) for url in known_urls
                })
                brief = brief.model_copy(
                    update={
                        "summary": with_draft_prefix(brief.summary),
                        "review_state": ReviewState.DRAFT,
                        "source_urls": sorted(known_urls),
                        "signal_event_ids": [event.event_id for event in events],
                    }
                )
                self.repository.record_brief(brief)
            except (ProviderError, ValueError) as error:
                synthesis_call = self._llm_metadata()
                synthesis_error = f"synthesis: {error}"
                brief = None
        self._record_step(
            state["run_id"],
            "synthesis",
            "failed" if synthesis_error else "succeeded",
            {
                "brief_id": brief.run_id if brief else None,
                "source_count": len(known_urls),
                "llm_calls": self._llm_calls,
                "llm_input_chars": self._llm_input_chars,
                "call": {
                    key: value for key, value in synthesis_call.items() if key != "attempts"
                },
                "attempts": synthesis_call.get("attempts", []),
                "error": synthesis_error,
            },
            started_at=started_at,
            input_payload={
                "distillation_count": len(distillations),
                "claim_count": len(claims),
            },
            output_payload=brief.model_dump(mode="json") if brief else None,
            error_code="provider" if synthesis_error else None,
        )
        if synthesis_error:
            raise ProviderError(synthesis_error)
        return {"brief": brief, "partial_reasons": list(state.get("partial_reasons", []))}

    async def _validate(self, state: GraphState) -> dict[str, ValidationReport]:
        started_at = monotonic()
        request = state["request"]
        brief = state.get("brief")
        model_id = (
            brief.model_id
            if brief is not None
            else next(
                (
                    item.model_id
                    for item in state.get("distillations", [])
                    if item.model_id
                ),
                request.model,
            )
        )
        report = build_validation_report(
            run_id=state["run_id"],
            sources=state.get("sources", []),
            claims=state.get("claims", []),
            as_of=request.as_of,
            model_id=model_id,
            lane_statuses=state.get("lane_statuses", {}),
            source_hashes=state.get("source_hashes", []),
            prompt_version=PROMPT_VERSION,
            minimum_sources=1 if request.validation_profile == "canary" else 10,
            minimum_claims=1 if request.validation_profile == "canary" else 5,
            tool_call_count=(
                sum(
                    1
                    for call in self.repository.get_run_tool_calls(state["run_id"])
                    if call.get("status") == "succeeded"
                )
                if isinstance(self.llm, LaneResearchLike)
                else None
            ),
            required_tool_lanes=(
                {
                    lane: {
                        "tavily_search",
                        "tavily_extract",
                    }.issubset(
                        {
                            str(call.get("tool_name"))
                            for call in self.repository.get_run_tool_calls(state["run_id"])
                            if call.get("lane") == lane and call.get("status") == "succeeded"
                        }
                    )
                    for lane in ("regulatory", "us-ports", "mexico")
                }
                if isinstance(self.llm, LaneResearchLike)
                else None
            ),
        )
        self.repository.record_validation(report)
        validation_error = (
            None
            if report.status is ValidationStatus.PASS
            else f"validation: {report.status.value}"
        )
        self._record_step(
            state["run_id"],
            "validation",
            "failed" if validation_error else report.status.value,
            {
                "source_count": report.unique_source_count,
                "claim_count": report.claim_count,
                "citation_coverage": report.citation_coverage,
                "content_hash": report.content_hash,
            },
            started_at=started_at,
            input_payload={
                "source_count": len(state.get("sources", [])),
                "claim_count": len(state.get("claims", [])),
            },
            output_payload=report.model_dump(mode="json"),
            error_code="validation" if validation_error else None,
        )
        if validation_error:
            raise ProviderError(validation_error)
        return {"validation": report}
