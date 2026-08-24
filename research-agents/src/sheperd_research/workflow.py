from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from time import monotonic
from typing import NamedTuple, Protocol, TypedDict, cast, runtime_checkable
from urllib.parse import urlsplit

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    ExtractionStatus,
    LaneDiscoveryResult,
    ReportBullet,
    ResearchCadence,
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
from .progress import ProgressSink
from .providers.errors import ProviderError
from .source_catalog import load_source_catalog
from .topics import default_topic_configs
from .validation import (
    build_validation_report,
    provider_error_codes_from_run,
    source_quality_sources,
)
from .validators import (
    claim_verification_allowed,
    classify_freshness,
    content_hash,
    deduplicate_sources,
    normalize_url,
    url_policy_error,
    validate_article_distillation_quality,
    validate_claim_citations,
    validate_report_sections,
    validate_source_dates,
    with_draft_prefix,
)

MAX_PARALLEL_LANES = 3
MAX_PARALLEL_DISTILLATIONS = 2
CRITIC_CLAIM_BATCH_SIZE = 12
CRITIC_MAX_CONCURRENCY = 2
# Keep weekly reconciliation bounded while retaining one review target per old source.
MAX_RETAINED_CRITIC_CLAIMS_PER_SOURCE = 1
MAX_WEEKLY_SYNTHESIS_DISTILLATIONS = 30
DEFAULT_MAX_LLM_CALLS = 48
DEFAULT_MAX_LLM_INPUT_CHARS = 350_000
DEFAULT_MAX_RUN_SECONDS = 2_400
# Keep workflow accounting aligned with the provider's bounded source window.
MAX_LLM_SOURCE_CHARS = 8_000
PIPELINE_OVERHEAD_RESERVE = 1_024
DISCOVERY_INPUT_BUDGET_RESERVE = MAX_LLM_SOURCE_CHARS + PIPELINE_OVERHEAD_RESERVE
PROMPT_VERSION = "workflow-v3"
DAILY_BRIEF_PROMPT_VERSION = "daily-brief-v6-decision"
WEEKLY_BRIEF_PROMPT_VERSION = "weekly-brief-v6-decision"
DISCOVERY_PROMPT_VERSION = "discovery-v3-multilingual"
DISTILL_PROMPT_VERSION = "distill-v6-insight"
CRITIC_PROMPT_VERSION = "critic-v5-evidence"
GLOBAL_WEEKLY_BRIEF_PROMPT_VERSION = "weekly-brief-v6-decision"
CHECKPOINT_ALLOWED_MODULES = tuple(
    ("sheperd_research.contracts", name)
    for name in (
        "EvidenceStatus",
        "FreshnessStatus",
        "ExtractionStatus",
        "TranslationStatus",
        "InsightStatus",
        "DistillationQualityStatus",
        "ReviewState",
        "RunStatus",
        "ValidationStatus",
        "ContractModel",
        "SourceCandidate",
        "ClaimDraft",
        "ReportBullet",
        "ArticleDistillation",
        "ArticleInsight",
        "SignalEvent",
        "WeeklyBrief",
        "TopicConfig",
        "ResearchRunRequest",
        "ResearchCadence",
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
    LaneSpec("regulatory", (0,), ("Regulatory", "United States")),
    LaneSpec("us-ports", (1, 2), ("West Coast", "East Coast", "Gulf")),
    LaneSpec("mexico", (3, 4), ("Mexico", "Europe")),
)

LANE_REGION_PACKS: dict[str, tuple[str, ...]] = {
    "regulatory": ("us", "canada", "europe", "global"),
    "us-ports": ("us", "canada", "mexico"),
    "mexico": ("mexico", "south-america", "middle-east", "global"),
}

STRICT_GLOBAL_GEOGRAPHIES = {
    "Regulatory",
    "United States",
    "West Coast",
    "East Coast",
    "Gulf",
    "Canada",
    "Mexico",
    "Europe",
    "South America",
    "Middle East",
}

LANE_REQUIRED_COVERAGE: dict[str, tuple[str, ...]] = {
    "regulatory": ("Canada", "Europe"),
    "us-ports": ("West Coast", "East Coast", "Gulf"),
    "mexico": ("Mexico", "South America", "Middle East"),
}

COVERAGE_FOLLOW_UP_QUERIES = {
    "Canada": "Canada Vancouver Prince Rupert Montreal Halifax maritime port shipping update",
    "Europe": "Europe Rotterdam Antwerp Hamburg Valencia Felixstowe maritime port shipping update",
    "West Coast": (
        "West Coast Los Angeles Long Beach Oakland Seattle Tacoma port congestion "
        "dwell TEU update"
    ),
    "East Coast": (
        "East Coast Savannah Charleston New York New Jersey port congestion "
        "terminal carrier update"
    ),
    "Gulf": "Gulf Houston port congestion terminal carrier dwell time update",
    "Mexico": "Mexico Manzanillo Lazaro Cardenas Veracruz Altamira maritime port shipping update",
    "South America": (
        "South America Santos Brazil Chile Argentina Peru Colombia port shipping update"
    ),
    "Middle East": "Middle East Abu Dhabi Saudi Arabia Oman Qatar Egypt port shipping update",
}


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
    retained_sources: list[SourceCandidate]
    retained_distillations: list[ArticleDistillation]
    repair_mode: bool


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
        discovery_query_limit: int | None = None,
        progress: ProgressSink | None = None,
    ) -> None:
        self.repository = repository
        self.tavily = tavily
        self.llm = llm
        self.topic_configs = topic_configs or default_topic_configs()
        self.checkpointer = checkpointer
        self.max_llm_calls = max_llm_calls
        self.max_llm_input_chars = max_llm_input_chars
        self.max_run_seconds = max_run_seconds
        if discovery_query_limit is not None and discovery_query_limit < 1:
            raise ValueError("discovery query limit must be positive")
        self.discovery_query_limit = discovery_query_limit
        self.progress = progress
        self._llm_calls = 0
        self._llm_input_chars = 0

    def _emit(self, event: str, message: str, **details: object) -> None:
        if self.progress is not None:
            self.progress.emit(event, message, **details)

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
            self.repository.update_run_status(
                run_id, status, self._error_code(error)
            )
        except Exception as status_error:
            return f"status update failed: {status_error.__class__.__name__}"
        return None

    @staticmethod
    def _error_code(error: BaseException | str | None) -> str | None:
        if error is None:
            return None
        explicit = getattr(error, "error_code", None)
        if isinstance(explicit, str) and explicit:
            return explicit
        if isinstance(error, TimeoutError):
            return "timeout"
        if isinstance(error, ValueError):
            return "invalid_output"
        if isinstance(error, ProviderError):
            return "provider_error"
        if isinstance(error, str):
            normalized = error.lower()
            known_codes = {
                "budget_exceeded",
                "extraction_failed",
                "incomplete_article_insights",
                "invalid_output",
                "missing_evidence",
                "partial_run",
                "persistence_error",
                "provider",
                "provider_error",
                "rate_limit",
                "synthesis_failed",
                "timeout",
                "validation_failed",
                "workflow_error",
            }
            if normalized in known_codes:
                return normalized
            for marker, code in (
                ("budget", "budget_exceeded"),
                ("validation", "validation_failed"),
                ("extraction", "extraction_failed"),
                ("synthesis", "synthesis_failed"),
                ("status update", "persistence_error"),
                ("timeout", "timeout"),
            ):
                if marker in normalized:
                    return code
            return "workflow_error"
        return "workflow_error"

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
                self._emit(
                    "persist",
                    "Tool receipts saved",
                    agent=agent_name,
                    tool_calls=len(receipts),
                    attempt=repository_attempt,
                )
            self._emit(
                "persist",
                "Agent step saved",
                agent=agent_name,
                status=status,
                attempt=repository_attempt,
                duration_ms=(
                    call_duration if isinstance(call_duration, int) else duration_ms
                ),
            )
            self._emit(
                "checkpoint",
                "Checkpoint boundary reached",
                agent=agent_name,
                enabled=self.checkpointer is not None,
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

    @classmethod
    def _protect_claim_verification(
        cls, claims: list[ClaimDraft], sources: list[SourceCandidate]
    ) -> list[ClaimDraft]:
        protected = cls._protect_seed_claims(claims, sources)
        return [
            claim.model_copy(
                update={
                    "evidence_status": EvidenceStatus.PARTIALLY_SUPPORTED,
                    "verification_basis": (
                        claim.verification_basis
                        or "single-source claim; independent verification not established"
                    ),
                }
            )
            if claim.evidence_status is EvidenceStatus.VERIFIED
            and not claim_verification_allowed(claim, sources)
            else claim
            for claim in protected
        ]

    @staticmethod
    def _merge_claims(claims: list[ClaimDraft]) -> list[ClaimDraft]:
        unique: dict[tuple[str, tuple[str, ...]], ClaimDraft] = {}
        for claim in claims:
            key = (
                claim.claim,
                tuple(sorted(normalize_url(url) for url in claim.source_urls)),
            )
            unique.setdefault(key, claim)
        return list(unique.values())

    @staticmethod
    def _merge_distillations(
        fresh: list[ArticleDistillation], retained: list[ArticleDistillation]
    ) -> list[ArticleDistillation]:
        unique: dict[str, ArticleDistillation] = {}
        for item in [*fresh, *retained]:
            unique.setdefault(normalize_url(item.source_url), item)
        return list(unique.values())

    @staticmethod
    def _merge_sources(
        fresh: list[SourceCandidate], retained: list[SourceCandidate]
    ) -> list[SourceCandidate]:
        return deduplicate_sources([*fresh, *retained])

    @staticmethod
    def _run_since(request: ResearchRunRequest, topic: TopicConfig) -> datetime:
        if request.since is not None:
            return request.since
        days = topic.lookback_days if request.cadence is ResearchCadence.DAILY else 7
        return request.as_of - timedelta(days=days)

    def _retained_evidence(
        self,
        request: ResearchRunRequest,
    ) -> tuple[list[SourceCandidate], list[ArticleDistillation]]:
        if request.cadence is not ResearchCadence.WEEKLY:
            return [], []
        method = getattr(self.repository, "get_trailing_evidence", None)
        if not callable(method):
            return [], []
        sources, distillations = method(
            topic_set=request.topic_set,
            since=request.as_of - timedelta(days=7),
            until=request.as_of,
            limit=request.max_sources * 10,
        )
        complete_distillations = [
            item
            for item in distillations
            if not validate_article_distillation_quality(item)
        ]
        complete_urls = {
            normalize_url(item.source_url) for item in complete_distillations
        }
        return (
            [
                source.model_copy(
                    update={
                        # A persisted complete distillation proves that this
                        # source was extracted in its originating run.  Carry
                        # that fact into the new run's run_sources row.
                        "extraction_status": ExtractionStatus.SUCCEEDED,
                        "extraction_error_code": None,
                    }
                )
                for source in sources
                if not source.is_seed and normalize_url(source.url) in complete_urls
            ],
            complete_distillations,
        )

    async def run(self, request: ResearchRunRequest, run_id: str | None = None) -> RunResult:
        run_id = run_id or str(uuid.uuid4())
        self._llm_calls = 0
        self._llm_input_chars = 0
        self.repository.create_run(run_id, request)
        self._emit(
            "run",
            "Research run started",
            run_id=run_id,
            topic_set=request.topic_set,
            cadence=request.cadence.value,
            as_of=request.as_of.isoformat(),
            max_sources=request.max_sources,
            checkpoint_enabled=self.checkpointer is not None,
        )
        try:
            topic = self.topic_configs.get(request.topic_set)
            if topic is None:
                raise ValueError(f"unknown topic set: {request.topic_set}")
            retained_sources, retained_distillations = self._retained_evidence(request)
            retained_distillations = [
                item.model_copy(
                    update={
                        "claims": self._protect_claim_verification(
                            item.claims, retained_sources
                        )
                    }
                )
                for item in retained_distillations
            ]
            for source in retained_sources:
                self.repository.record_source(source, run_id=run_id)
            for distillation in retained_distillations:
                self.repository.record_distillation(run_id, distillation)
                self.repository.record_claims(run_id, distillation.claims)
            self._emit(
                "checkpoint",
                "Loaded trailing evidence for resumable research",
                source_count=len(retained_sources),
                distillation_count=len(retained_distillations),
            )
            graph = self._build_graph(self.checkpointer)
            final_state = await asyncio.wait_for(
                graph.ainvoke(
                    {
                        "run_id": run_id,
                        "request": request,
                        "topic": topic,
                        "partial_reasons": [],
                        "retained_sources": retained_sources,
                        "retained_distillations": retained_distillations,
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
            error = "partial_run" if partial_reasons else None
            if error is None and validation_failed:
                error = (
                    "validation_missing"
                    if validation is None
                    else "validation_failed"
                )
            self.repository.update_run_status(
                run_id, status, self._error_code(error)
            )
            self._emit(
                "finish" if status is RunStatus.SUCCEEDED else "error",
                "Research run finished",
                run_id=run_id,
                status=status.value,
                source_count=len(final_state.get("sources", [])),
                validation=validation.status.value if validation else "missing",
                error=error or "none",
            )
            return RunResult(
                run_id=run_id,
                status=status,
                cadence=request.cadence,
                source_count=len(
                    source_quality_sources(
                        self._merge_sources(
                            final_state.get("sources", []),
                            final_state.get("retained_sources", []),
                        )
                    )
                ),
                distillation_count=len(
                    self._merge_distillations(
                        final_state.get("distillations", []),
                        final_state.get("retained_distillations", []),
                    )
                ),
                claim_count=len(
                    self._merge_claims(
                        [
                            *final_state.get("claims", []),
                            *[
                                claim
                                for item in final_state.get("retained_distillations", [])
                                for claim in item.claims
                            ],
                        ]
                    )
                ),
                brief_id=brief.run_id if brief else None,
                error=error,
                citation_coverage=validation.citation_coverage if validation else 0.0,
                validation_status=(
                    validation.status if validation else ValidationStatus.BLOCKED
                ),
                lane_statuses=final_state.get("lane_statuses", {}),
            )
        except TimeoutError:
            message = "workflow exceeded wall-clock budget"
            status_error = self._safe_update_run_status(
                run_id, RunStatus.FAILED, self._error_code(message)
            )
            if status_error:
                message = f"{message}; {status_error}"
            self._emit(
                "error", "Research run stopped", run_id=run_id, error="timeout"
            )
            return RunResult(
                run_id=run_id,
                status=RunStatus.FAILED,
                cadence=request.cadence,
                error=message,
            )

        except ProviderError as error:
            message = str(error) or "provider error"
            status_error = self._safe_update_run_status(
                run_id, RunStatus.FAILED, self._error_code(error)
            )
            if status_error:
                message = f"{message}; {status_error}"
            self._emit(
                "error",
                "Research run stopped",
                run_id=run_id,
                error=self._error_code(error) or "provider_error",
            )
            return RunResult(
                run_id=run_id,
                status=RunStatus.FAILED,
                cadence=request.cadence,
                error=message,
            )
        except Exception as error:
            message = str(error) or error.__class__.__name__
            status_error = self._safe_update_run_status(
                run_id, RunStatus.FAILED, self._error_code(error)
            )
            if status_error:
                message = f"{message}; {status_error}"
            self._emit(
                "error",
                "Research run stopped",
                run_id=run_id,
                error=self._error_code(error) or "workflow_error",
            )
            return RunResult(
                run_id=run_id,
                status=RunStatus.FAILED,
                cadence=request.cadence,
                error=message,
            )

    async def repair(
        self,
        request: ResearchRunRequest,
        sources: list[SourceCandidate],
        run_id: str,
    ) -> RunResult:
        """Re-extract and redistill incomplete sources in a new run scope."""
        self._llm_calls = 0
        self._llm_input_chars = 0
        self.repository.create_run(run_id, request)
        try:
            topic = self.topic_configs.get(request.topic_set)
            if topic is None:
                raise ValueError(f"unknown topic set: {request.topic_set}")
            repair_sources = [
                self.repository.record_source(
                    source.model_copy(
                        update={
                            "is_seed": False,
                            "source_kind": "repair",
                            "extraction_status": ExtractionStatus.NOT_ATTEMPTED,
                            "extraction_error_code": None,
                        }
                    ),
                    run_id=run_id,
                )
                for source in deduplicate_sources(sources)[: request.max_sources]
            ]
            if not repair_sources:
                raise ValueError("no incomplete sources were selected for repair")
            self._emit(
                "repair",
                "Re-extracting incomplete sources",
                source_count=len(repair_sources),
            )
            try:
                raw_content = await self.tavily.extract(repair_sources)
                content = {
                    normalize_url(url): body
                    for url, body in raw_content.items()
                    if isinstance(body, str) and body.strip()
                }
            except Exception as extraction_error:
                error_code = "extraction_failed"
                if isinstance(extraction_error, ProviderError):
                    error_code = extraction_error.error_code or "provider_error"
                for source in repair_sources:
                    self.repository.record_source(
                        source.model_copy(
                            update={
                                "extraction_status": ExtractionStatus.FAILED,
                                "extraction_error_code": error_code,
                            }
                        ),
                        run_id=run_id,
                    )
                raise
            state: GraphState = {
                "run_id": run_id,
                "request": request,
                "topic": topic,
                "sources": repair_sources,
                "content": content,
                "source_hashes": [],
                "lane_statuses": {},
                "partial_reasons": [],
                "repair_mode": True,
                "retained_sources": [],
                "retained_distillations": [],
            }
            state.update(cast(GraphState, await self._extract(state)))
            state.update(cast(GraphState, await self._distill(state)))
            state.update(cast(GraphState, await self._critic(state)))
            state.update(cast(GraphState, await self._synthesize(state)))
            state.update(cast(GraphState, await self._validate(state)))
            validation = state.get("validation")
            brief = state.get("brief")
            status = (
                RunStatus.SUCCEEDED
                if brief is not None
                and validation is not None
                and validation.status is ValidationStatus.PASS
                else RunStatus.FAILED
            )
            error = None if status is RunStatus.SUCCEEDED else "validation_failed"
            self.repository.update_run_status(run_id, status, error)
            return RunResult(
                run_id=run_id,
                status=status,
                cadence=request.cadence,
                source_count=len(state.get("sources", [])),
                distillation_count=len(state.get("distillations", [])),
                claim_count=len(state.get("claims", [])),
                brief_id=brief.run_id if brief else None,
                error=error,
                citation_coverage=validation.citation_coverage if validation else 0.0,
                validation_status=validation.status if validation else ValidationStatus.BLOCKED,
                lane_statuses=state.get("lane_statuses", {}),
            )
        except Exception as error:
            message = str(error) or error.__class__.__name__
            self._safe_update_run_status(
                run_id, RunStatus.FAILED, self._error_code(error)
            )
            return RunResult(
                run_id=run_id,
                status=RunStatus.FAILED,
                cadence=request.cadence,
                error=message,
            )

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
        allowed_geographies: tuple[str, ...] | None = None,
    ) -> SourceCandidate:
        if url_policy_error(source.url, excluded_domains=exclude_domains) is not None:
            raise ProviderError("discovery returned a source rejected by URL policy")
        try:
            normalized_url = normalize_url(source.url)
        except ValueError as error:
            raise ProviderError("discovery returned a malformed source URL") from error
        host = (urlsplit(normalized_url).hostname or "").lower()
        if not host:
            raise ProviderError("discovery returned a source without a host")
        if cls._domain_matches(host, exclude_domains):
            raise ProviderError("discovery returned an excluded source host")
        if include_domains and not cls._domain_matches(host, include_domains):
            raise ProviderError("discovery returned a source outside allowed hosts")
        if source.published_at is not None and not since <= source.published_at <= until:
            raise ProviderError("discovery returned a source outside the date window")
        observed_allowed_geographies = {
            geography.casefold()
            for geography in (allowed_geographies or lane.geographies)
        }
        observed_geographies = {geography.casefold() for geography in source.geographies}
        if not observed_geographies.intersection(observed_allowed_geographies):
            raise ProviderError("discovery returned a source outside lane geography")
        return source.model_copy(update={"url": normalized_url})

    @staticmethod
    def _source_region(source: SourceCandidate, lane: str) -> str:
        observed = {value.casefold() for value in source.geographies}
        if "canada" in observed:
            return "canada"
        if "mexico" in observed:
            return "mexico"
        if "europe" in observed:
            return "europe"
        if "south america" in observed:
            return "south-america"
        if "middle east" in observed:
            return "middle-east"
        if "global" in observed:
            return "global"
        if observed.intersection(
            {"regulatory", "united states", "west coast", "east coast", "gulf"}
        ):
            return "us"
        return {"regulatory": "us", "us-ports": "us"}.get(lane, "global")

    @staticmethod
    def _catalog_metadata(source: SourceCandidate) -> dict[str, object]:
        host = (urlsplit(normalize_url(source.url)).hostname or "").lower()
        try:
            catalog = load_source_catalog()
        except (FileNotFoundError, ValueError, OSError):
            return {}
        for catalog_source in catalog.enabled_sources():
            if host == catalog_source.domain or host.endswith(f".{catalog_source.domain}"):
                return {
                    "catalog_source_id": catalog_source.source_id,
                    "authority_tier": catalog_source.authority_tier,
                    "source_type": catalog_source.source_type,
                }
        return {}

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
        since = self._run_since(request, topic)
        sources: list[SourceCandidate] = []
        content: dict[str, str] = {}
        metadata: dict[str, object] = {}
        try:
            if not isinstance(self.llm, LaneResearchLike):
                raise ProviderError("workflow requires model-issued lane discovery")
            legacy_queries = [
                topic.queries[index]
                for index in lane.query_indexes
                if index < len(topic.queries)
            ]
            regional_queries = [
                query
                for pack_name in LANE_REGION_PACKS.get(lane.name, ())
                if (pack := topic.region_packs.get(pack_name)) is not None
                for query in pack.query_families
            ]
            configured_queries = list(dict.fromkeys([*regional_queries, *legacy_queries]))
            if not configured_queries:
                raise ProviderError(f"{lane.name}: no configured query families")
            if self.discovery_query_limit is not None:
                if self.discovery_query_limit == 1:
                    # Canary runs exercise the lane's own legacy query family;
                    # otherwise valid port results can be rejected as out of scope.
                    preferred_queries = legacy_queries or configured_queries
                else:
                    # Full runs keep one query per regional pack plus legacy lane
                    # queries.  This preserves coverage without overflowing the
                    # model context with repeated search and extract messages.
                    pack_queries = [
                        pack.query_families[0]
                        for pack_name in LANE_REGION_PACKS.get(lane.name, ())
                        if (pack := topic.region_packs.get(pack_name)) is not None
                        and pack.query_families
                    ]
                    preferred_queries = [*pack_queries, *legacy_queries]
                configured_queries = preferred_queries[: self.discovery_query_limit]
            lane_geographies = list(lane.geographies)
            if self.discovery_query_limit != 1:
                for pack_name in LANE_REGION_PACKS.get(lane.name, ()):
                    pack = topic.region_packs.get(pack_name)
                    if pack is not None:
                        lane_geographies.extend([*pack.countries, *pack.ports])
            lane_geographies_tuple = tuple(dict.fromkeys(lane_geographies))
            lane_include_domains = list(
                dict.fromkeys(
                    [
                        *topic.include_domains,
                        *[
                            domain
                            for pack_name in LANE_REGION_PACKS.get(lane.name, ())
                            if (pack := topic.region_packs.get(pack_name)) is not None
                            for domain in pack.authority_domains
                        ],
                    ]
                )
            )
            discovery_budget = max(
                0,
                self.max_llm_input_chars - DISCOVERY_INPUT_BUDGET_RESERVE,
            )
            discovery_input = min(
                sum(len(query) for query in configured_queries),
                discovery_budget // MAX_PARALLEL_LANES,
            )
            if not self._reserve_llm_call(discovery_input):
                raise ProviderError("discovery: llm budget exceeded")
            self._emit(
                "discovery",
                "Discovery agent querying configured lane",
                lane=lane.name,
                query_count=len(configured_queries),
                geography_count=len(lane_geographies_tuple),
            )
            result = await self.llm.discover_lane(
                lane.name,
                configured_queries,
                lane_geographies_tuple,
                since=since,
                until=request.as_of,
                include_domains=lane_include_domains,
                exclude_domains=topic.exclude_domains,
                max_results=max(3, request.max_sources // 5),
                tavily=self.tavily,
            )

            def merge_discovery_result(
                additional: LaneDiscoveryResult,
            ) -> None:
                nonlocal result
                result_attempts = result.metadata.get("attempts")
                additional_attempts = additional.metadata.get("attempts")
                result_tool_errors = result.metadata.get("tool_errors")
                additional_tool_errors = additional.metadata.get("tool_errors")

                def metadata_count(metadata: dict[str, object], key: str) -> int:
                    value = metadata.get(key)
                    return value if isinstance(value, int) else 0

                result = result.model_copy(
                    update={
                        "packet": result.packet.model_copy(
                            update={
                                "source_urls": list(
                                    dict.fromkeys(
                                        [
                                            *result.packet.source_urls,
                                            *additional.packet.source_urls,
                                        ]
                                    )
                                ),
                                "selected_queries": list(
                                    dict.fromkeys(
                                        [
                                            *result.packet.selected_queries,
                                            *additional.packet.selected_queries,
                                        ]
                                    )
                                ),
                                "evidence_notes": [
                                    *result.packet.evidence_notes,
                                    *additional.packet.evidence_notes,
                                ][:8],
                            }
                        ),
                        "sources": [*result.sources, *additional.sources],
                        "content": {**result.content, **additional.content},
                        "metadata": {
                            **result.metadata,
                            "attempts": [
                                *(
                                    result_attempts
                                    if isinstance(result_attempts, list)
                                    else []
                                ),
                                *(
                                    additional_attempts
                                    if isinstance(additional_attempts, list)
                                    else []
                                ),
                            ],
                            "tool_calls": metadata_count(result.metadata, "tool_calls")
                            + metadata_count(additional.metadata, "tool_calls"),
                            "search_calls": metadata_count(
                                result.metadata, "search_calls"
                            )
                            + metadata_count(additional.metadata, "search_calls"),
                            "tool_input_chars": metadata_count(
                                result.metadata, "tool_input_chars"
                            )
                            + metadata_count(
                                additional.metadata, "tool_input_chars"
                            ),
                            "tool_errors": [
                                *(
                                    result_tool_errors
                                    if isinstance(result_tool_errors, list)
                                    else []
                                ),
                                *(
                                    additional_tool_errors
                                    if isinstance(additional_tool_errors, list)
                                    else []
                                ),
                            ],
                            "agent_call": additional.metadata.get(
                                "agent_call", result.metadata.get("agent_call", {})
                            ),
                            "extracted_count": len(
                                {**result.content, **additional.content}
                            ),
                            "coverage_follow_up": True,
                        },
                    }
                )

            if self.discovery_query_limit is not None and self.discovery_query_limit > 1:
                observed_coverage = {
                    coverage.casefold()
                    for source in result.sources
                    for coverage in source.geographies
                }
                missing_coverage = [
                    coverage
                    for coverage in LANE_REQUIRED_COVERAGE.get(lane.name, ())
                    if coverage.casefold() not in observed_coverage
                ]
                if missing_coverage:
                    follow_up_queries = [
                        COVERAGE_FOLLOW_UP_QUERIES[coverage]
                        for coverage in missing_coverage
                        if coverage in COVERAGE_FOLLOW_UP_QUERIES
                    ]
                    if follow_up_queries:
                        self._emit(
                            "discovery",
                            "Coverage follow-up searching missing targets",
                            lane=lane.name,
                            targets=missing_coverage,
                            query_count=len(follow_up_queries),
                        )
                        follow_up = await self.llm.discover_lane(
                            lane.name,
                            follow_up_queries,
                            lane_geographies_tuple,
                            since=since,
                            until=request.as_of,
                            include_domains=lane_include_domains,
                            exclude_domains=topic.exclude_domains,
                            max_results=max(
                                len(follow_up_queries),
                                max(3, request.max_sources // 5),
                            ),
                            tavily=self.tavily,
                        )
                        merge_discovery_result(follow_up)
            validated_sources = [
                self._validate_lane_source(
                    source,
                    lane,
                    since,
                    request.as_of,
                    lane_include_domains,
                    topic.exclude_domains,
                    lane_geographies_tuple,
                )
                for source in result.sources
            ]
            sources = [
                source.model_copy(
                    update={
                        "topics": sorted(set(source.topics + [request.topic_set, lane.name])),
                        "geographies": sorted(set(source.geographies)),
                        "lane": lane.name,
                        "region": self._source_region(source, lane.name),
                        **self._catalog_metadata(source),
                        "freshness_status": classify_freshness(
                            source, request.as_of
                        ).freshness_status,
                        "freshness_days": classify_freshness(
                            source, request.as_of
                        ).freshness_days,
                    }
                )
                for source in validated_sources
            ]
            content = dict(result.content)
            metadata = {
                **dict(result.metadata),
                "packet": result.packet.model_dump(mode="json"),
            }
            self._emit(
                "discovery",
                "Discovery agent returned evidence",
                lane=lane.name,
                source_count=len(sources),
                extracted_count=len(content),
                tool_calls=metadata.get("tool_calls", 0),
            )
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
            error_code = self._error_code(error) or "provider_error"
            self._emit(
                "error",
                "Discovery agent failed",
                lane=lane.name,
                error=error_code,
            )
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
        self._emit(
            "discovery",
            "Three bounded discovery agents started",
            lanes=len(LANES),
            max_sources=request.max_sources,
        )
        lane_results = await asyncio.gather(
            *(self._discover_lane(lane, request, topic) for lane in LANES)
        )
        lane_sources: dict[str, list[SourceCandidate]] = {}
        lane_statuses: dict[str, str] = {}
        lane_content: dict[str, str] = {}
        lane_errors: list[str] = []
        lane_failures: list[str] = []
        for lane_name, sources, content, error, duration_ms, metadata in lane_results:
            lane_sources[lane_name] = sources
            lane_content.update(content)
            lane_statuses[lane_name] = "failed" if error else "succeeded"
            if error:
                lane_failures.append(f"{lane_name}: {error}")
                lane_errors.append(f"{lane_name}: {self._error_code(error)}")
            raw_attempts = metadata.get("attempts")
            attempts = raw_attempts if isinstance(raw_attempts, list) else []
            attempt_error_code = next(
                (
                    str(attempt.get("error_code"))
                    for attempt in reversed(attempts)
                    if isinstance(attempt, dict) and attempt.get("error_code")
                ),
                None,
            )
            step_metadata = {
                "source_count": len(sources),
                "error": self._error_code(error),
                **metadata,
            }
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
                error_code=attempt_error_code or ("provider" if error else None),
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
        unique = deduplicate_sources(
            [
                self.repository.record_source(source, run_id=state["run_id"])
                for source in unique
            ]
        )[: request.max_sources]
        self._emit(
            "persist",
            "Sources inserted into Neon",
            source_count=len(unique),
            lane_count=len(LANES),
        )
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
            raise ProviderError(
                "; ".join(lane_failures),
                error_code="provider",
            )
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
            raw_url = seed_url.strip()
            reason = url_policy_error(raw_url, excluded_domains=topic.exclude_domains)
            try:
                normalized = normalize_url(raw_url)
            except ValueError:
                normalized = ""
                reason = reason or "malformed_url"
            host = ""
            if normalized:
                try:
                    host = (urlsplit(normalized).hostname or "").lower().removeprefix("www.")
                except ValueError:
                    reason = reason or "malformed_url"
            if reason is not None:
                quarantined_reasons[reason] = quarantined_reasons.get(reason, 0) + 1
                if host:
                    quarantined_domains.add(host)
            else:
                accepted_seed_count += 1
            if not normalized or reason in {
                "malformed_url",
                "missing_host",
                "unsupported_scheme",
            }:
                continue
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
        self._emit(
            "extract",
            "Received extracted source content",
            source_count=len(extractable_sources),
        )
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
            updated_sources: list[SourceCandidate] = []
            for source in extractable_sources:
                normalized_url = normalize_url(source.url)
                body = content[normalized_url]
                if body.strip():
                    self.repository.record_snapshot(state["run_id"], source, body)
                    source_hashes.append(content_hash(body))
                    updated_sources.append(
                        self.repository.record_source(
                            source.model_copy(
                                update={
                                    "extraction_status": ExtractionStatus.SUCCEEDED,
                                    "extraction_error_code": None,
                                }
                            ),
                            run_id=state["run_id"],
                        )
                    )
            self._emit(
                "persist",
                "Source snapshots and hashes saved to Neon",
                source_count=len(updated_sources),
                hash_count=len(source_hashes),
            )
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
                "sources": [
                    *[source for source in sources if source.is_seed],
                    *updated_sources,
                ],
                "partial_reasons": list(state.get("partial_reasons", [])),
            }
        except ProviderError as provider_error:
            for source in extractable_sources:
                if content.get(normalize_url(source.url), "").strip():
                    continue
                self.repository.record_source(
                    source.model_copy(
                        update={
                            "extraction_status": ExtractionStatus.FAILED,
                            "extraction_error_code": "missing_content",
                        }
                    ),
                    run_id=state["run_id"],
                )
            self._record_step(
                state["run_id"],
                "extraction",
                "failed",
                {
                    "extracted_count": len(content),
                    "missing_agent_extractions": len(missing),
                    "seed_only_count": len(sources) - len(extractable_sources),
                    "error": self._error_code(provider_error) or "provider_error",
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
                    prompt_version=DISTILL_PROMPT_VERSION,
                )
                quality_issues = validate_article_distillation_quality(distillation)
                if quality_issues:
                    raise ValueError(
                        "article insight packet incomplete: "
                        + ", ".join(quality_issues)
                    )
                validate_claim_citations(distillation.claims, {source.url}, as_of)
                return distillation, None, annotate(self._llm_metadata())
            except (ProviderError, ValueError) as error:
                return (
                    None,
                    self._error_code(error) or "distillation_failed",
                    annotate(self._llm_metadata()),
                )

    async def _distill(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        all_sources = state.get("sources", [])
        sources = [source for source in all_sources if not source.is_seed]
        self._emit(
            "distill",
            "Distilling extracted sources",
            source_count=len(sources),
            concurrency=MAX_PARALLEL_DISTILLATIONS,
        )
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
                errors.append(self._error_code(error) or "distillation_failed")
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
            protected_claims = self._protect_claim_verification(
                item.claims,
                [matched_source] if matched_source is not None else [],
            )
            protected_distillations.append(item.model_copy(update={"claims": protected_claims}))
        distillations = protected_distillations
        claims = [claim for item in distillations for claim in item.claims]
        source_by_url = {normalize_url(source.url): source for source in sources}
        for distillation in distillations:
            matched_source = source_by_url.get(normalize_url(distillation.source_url))
            if matched_source is not None:
                translation_failed = distillation.translation_status.value == "failed"
                self.repository.record_source(
                    matched_source.model_copy(
                        update={
                            "language_code": distillation.source_language,
                            "language_confidence": 1.0
                            if distillation.source_language != "und"
                            else 0.0,
                            "extraction_status": ExtractionStatus.SUCCEEDED,
                            "extraction_error_code": None,
                            "evidence_status": (
                                EvidenceStatus.PARTIALLY_SUPPORTED
                                if translation_failed
                                else matched_source.evidence_status
                            ),
                        }
                    ),
                    run_id=state["run_id"],
                )
            self.repository.record_distillation(state["run_id"], distillation)
            self.repository.record_claims(state["run_id"], distillation.claims)
        self._emit(
            "persist",
            "Distillations and claims saved to Neon",
            distillation_count=len(distillations),
            claim_count=len(claims),
        )
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
            raise ProviderError("distillation_failed", error_code="distillation_failed")
        return {
            "distillations": distillations,
            "claims": claims,
            "partial_reasons": list(state.get("partial_reasons", [])),
        }

    async def _critic(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        retained_distillations = list(state.get("retained_distillations", []))
        retained_claims = [
            claim
            for item in retained_distillations
            for claim in item.claims
        ]
        fresh_claims = self._merge_claims(list(state.get("claims", [])))
        claims = self._merge_claims([*fresh_claims, *retained_claims])
        retained_review_claims = [
            item.claims[index]
            for item in retained_distillations
            for index in range(
                min(MAX_RETAINED_CRITIC_CLAIMS_PER_SOURCE, len(item.claims))
            )
        ]
        review_claims = self._merge_claims(
            [*fresh_claims, *retained_review_claims]
        )
        review_keys = {
            (claim.claim, tuple(sorted(normalize_url(url) for url in claim.source_urls)))
            for claim in review_claims
        }
        retained_not_reviewed = [
            claim
            for claim in retained_claims
            if (
                claim.claim,
                tuple(sorted(normalize_url(url) for url in claim.source_urls)),
            )
            not in review_keys
        ]
        self._emit(
            "critic",
            "Critic reconciler reviewing claims",
            claim_count=len(claims),
            reviewed_claim_count=len(review_claims),
            retained_claim_count=len(retained_claims),
        )
        source_urls = {
            normalize_url(url)
            for source in self._merge_sources(
                state.get("sources", []), state.get("retained_sources", [])
            )
            for url in [source.url]
        }
        revised = claims
        mode = "deterministic"
        critic_call: dict[str, object] = {}
        critic_calls: list[dict[str, object]] = []
        critic_attempts: list[dict[str, object]] = []
        critic_error: str | None = None
        if isinstance(self.llm, CriticLike) and review_claims:
            critic_llm = cast(CriticLike, self.llm)
            batches = [
                review_claims[index : index + CRITIC_CLAIM_BATCH_SIZE]
                for index in range(0, len(review_claims), CRITIC_CLAIM_BATCH_SIZE)
            ]
            if len(batches) > self.max_llm_calls - self._llm_calls:
                critic_error = "budget_exceeded"
            else:
                revised = []
                reserved_batches: list[list[ClaimDraft]] = []
                for batch in batches:
                    if not self._reserve_llm_call(sum(len(claim.claim) for claim in batch)):
                        critic_error = "budget_exceeded"
                        break
                    reserved_batches.append(batch)

                async def review_batch(
                    index: int, batch: list[ClaimDraft]
                ) -> tuple[int, list[ClaimDraft] | None, dict[str, object], str | None]:
                    try:
                        revised_batch = await critic_llm.critic(
                            batch,
                            source_urls,
                            prompt_version=CRITIC_PROMPT_VERSION,
                        )
                        validate_claim_citations(
                            revised_batch, source_urls, state["request"].as_of
                        )
                        if len(revised_batch) != len(batch):
                            raise ValueError("critic returned an incomplete claim batch")
                        return index, revised_batch, self._llm_metadata(), None
                    except (ProviderError, ValueError) as error:
                        return (
                            index,
                            None,
                            self._llm_metadata(),
                            self._error_code(error) or "critic_failed",
                        )

                if critic_error is None and reserved_batches:
                    semaphore = asyncio.Semaphore(CRITIC_MAX_CONCURRENCY)

                    async def bounded_review(
                        index: int, batch: list[ClaimDraft]
                    ) -> tuple[int, list[ClaimDraft] | None, dict[str, object], str | None]:
                        async with semaphore:
                            return await review_batch(index, batch)

                    results = await asyncio.gather(
                        *(
                            bounded_review(index, batch)
                            for index, batch in enumerate(reserved_batches)
                        )
                    )
                    for _, revised_batch, call, error in sorted(results):
                        critic_calls.append(call)
                        nested_attempts = call.get("attempts")
                        if isinstance(nested_attempts, list):
                            critic_attempts.extend(
                                item for item in nested_attempts if isinstance(item, dict)
                            )
                        if revised_batch is not None:
                            revised.extend(revised_batch)
                            mode = (
                                f"{getattr(self.llm, 'provider_name', 'openrouter')}-structured"
                            )
                        if error and critic_error is None:
                            critic_error = error
                    if critic_error is None:
                        revised = self._merge_claims(
                            [*revised, *retained_not_reviewed]
                        )
                if critic_calls:
                    critic_call = {
                        **{
                            key: value
                            for key, value in critic_calls[-1].items()
                            if key != "attempts"
                        },
                        "batch_count": len(critic_calls),
                    }
        all_sources = self._merge_sources(
            state.get("sources", []), state.get("retained_sources", [])
        )
        revised = self._protect_claim_verification(revised, all_sources)
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
            for item in self._merge_distillations(
                state.get("distillations", []), state.get("retained_distillations", [])
            )
        ]
        self.repository.record_claims(state["run_id"], revised)
        self._emit(
            "persist",
            "Critic findings saved to Neon",
            claim_count=len(revised),
            mode=mode,
        )
        self._record_step(
            state["run_id"],
            "critic",
            "failed" if critic_error else "succeeded",
            {
                "claim_count": len(revised),
                "reviewed_claim_count": len(review_claims),
                "retained_claim_count": len(retained_claims),
                "retained_claims_not_reviewed": len(retained_not_reviewed),
                "mode": mode,
                "llm_calls": self._llm_calls,
                "llm_input_chars": self._llm_input_chars,
                "call": {key: value for key, value in critic_call.items() if key != "attempts"},
                "attempts": critic_attempts,
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
        del claims
        updates: dict[str, object] = {}
        for section in (
            "executive_bullets",
            "developments",
            "risks",
            "opportunities",
            "uncertainties",
        ):
            bullets = list(getattr(brief, section))
            normalized: list[ReportBullet] = []
            for bullet in bullets:
                urls = [normalize_url(url) for url in bullet.source_urls]
                if not urls or not set(urls).issubset(known_urls):
                    raise ValueError(f"{section} contains an uncited or unknown URL")
                normalized.append(bullet.model_copy(update={"source_urls": urls}))
            updates[section] = normalized
        normalized_brief = brief.model_copy(update=updates)
        section_issues = validate_report_sections(normalized_brief, known_urls)
        if section_issues:
            raise ValueError(
                "report output is incomplete or insufficiently evidenced: "
                + "; ".join(section_issues)
            )
        return normalized_brief

    async def _synthesize(self, state: GraphState) -> dict[str, object]:
        started_at = monotonic()
        request = state["request"]
        all_distillations = self._merge_distillations(
            state.get("distillations", []), state.get("retained_distillations", [])
        )
        synthesis_limit = min(
            MAX_WEEKLY_SYNTHESIS_DISTILLATIONS,
            max(1, request.max_sources + 10),
        )
        distillations = all_distillations[:synthesis_limit]
        selected_urls = {normalize_url(item.source_url) for item in distillations}
        claims = self._merge_claims(
            [
                claim
                for claim in state.get("claims", [])
                if any(normalize_url(url) in selected_urls for url in claim.source_urls)
            ]
            + [
                claim
                for item in state.get("retained_distillations", [])
                if normalize_url(item.source_url) in selected_urls
                for claim in item.claims
            ]
        )
        self._emit(
            "synthesis",
            "Synthesizing cited report",
            distillation_count=len(distillations),
            claim_count=len(claims),
            retained_distillation_count=len(all_distillations)
            - len(state.get("distillations", [])),
            synthesis_limit=synthesis_limit,
        )
        article_quality_issues = {
            normalize_url(item.source_url): validate_article_distillation_quality(item)
            for item in distillations
        }
        incomplete_articles = {
            url: issues for url, issues in article_quality_issues.items() if issues
        }
        if incomplete_articles:
            raise ProviderError(
                "incomplete_article_insights", error_code="incomplete_article_insights"
            )
        source_urls = {
            normalize_url(source.url)
            for source in self._merge_sources(
                state.get("sources", []), state.get("retained_sources", [])
            )
        }
        validate_claim_citations(claims, source_urls, request.as_of)
        known_urls = set(source_urls)
        source_by_url = {
            normalize_url(source.url): source
            for source in self._merge_sources(
                state.get("sources", []), state.get("retained_sources", [])
            )
        }
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
        if not distillations or not claims:
            synthesis_error = "missing_evidence"
        elif not self._reserve_llm_call(sum(len(item.summary) for item in distillations)):
            synthesis_error = "budget_exceeded"
        else:
            try:
                since = self._run_since(request, state["topic"])
                prompt_version = (
                    DAILY_BRIEF_PROMPT_VERSION
                    if request.cadence is ResearchCadence.DAILY
                    else WEEKLY_BRIEF_PROMPT_VERSION
                )
                brief = await self.llm.synthesize(
                    state["run_id"],
                    distillations,
                    covered_from=since,
                    covered_until=request.as_of,
                    prompt_version=prompt_version,
                )
                synthesis_call = self._llm_metadata()
                brief = self._validate_report_bullets(brief, claims, source_urls)
                brief = brief.model_copy(
                    update={
                        "summary": with_draft_prefix(brief.summary),
                        "review_state": ReviewState.DRAFT,
                        "source_urls": sorted(known_urls),
                        "signal_event_ids": [event.event_id for event in events],
                        "prompt_version": prompt_version,
                    }
                )
                self.repository.record_brief(brief)
                self._emit(
                    "output",
                    "Draft brief saved to Neon",
                    run_id=state["run_id"],
                    source_count=len(known_urls),
                    claim_count=len(claims),
                )
            except (ProviderError, ValueError) as error:
                synthesis_call = self._llm_metadata()
                synthesis_error = self._error_code(error) or "synthesis_failed"
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
            if synthesis_error == "missing_evidence":
                raise ProviderError(
                    "no retained or freshly extracted evidence",
                    error_code=synthesis_error,
                )
            raise ProviderError(synthesis_error, error_code=synthesis_error)
        return {"brief": brief, "partial_reasons": list(state.get("partial_reasons", []))}

    async def _validate(self, state: GraphState) -> dict[str, ValidationReport]:
        started_at = monotonic()
        request = state["request"]
        self._emit(
            "validate",
            "Running deterministic validation",
            run_id=state["run_id"],
        )
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
            sources=self._merge_sources(
                state.get("sources", []), state.get("retained_sources", [])
            ),
            claims=state.get("claims", []),
            as_of=request.as_of,
            model_id=model_id,
            lane_statuses=state.get("lane_statuses", {}),
            source_hashes=state.get("source_hashes", []),
            prompt_version=PROMPT_VERSION,
            minimum_sources=(
                1 if request.validation_profile in {"canary", "global-canary"} else 10
            ),
            minimum_claims=(
                1 if request.validation_profile in {"canary", "global-canary"} else 5
            ),
            tool_call_count=(
                sum(
                    1
                    for call in self.repository.get_run_tool_calls(state["run_id"])
                    if call.get("status") == "succeeded"
                )
                if isinstance(self.llm, LaneResearchLike)
                and not state.get("repair_mode", False)
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
                and not state.get("repair_mode", False)
                else None
            ),
            distillations=self._merge_distillations(
                state.get("distillations", []), state.get("retained_distillations", [])
            ),
            required_geographies=(
                STRICT_GLOBAL_GEOGRAPHIES
                if request.validation_profile in {"full", "global-canary"}
                else set()
            ),
            required_regions=(
                {
                    region
                    for region, pack in state["topic"].region_packs.items()
                    if pack.required
                }
                if request.validation_profile in {"full", "global-canary"}
                else set()
            ),
            required_lanes=set() if state.get("repair_mode", False) else None,
            brief=brief,
            provider_error_codes=provider_error_codes_from_run(
                sources=self._merge_sources(
                    state.get("sources", []), state.get("retained_sources", [])
                ),
                steps=self.repository.get_run_steps(state["run_id"]),
                tool_calls=self.repository.get_run_tool_calls(state["run_id"]),
            ),
        )
        self.repository.record_validation(report)
        self._emit(
            "validate",
            "Validation result saved to Neon",
            status=report.status.value,
            citation_coverage=report.citation_coverage,
            source_count=report.unique_source_count,
            claim_count=report.claim_count,
        )
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
