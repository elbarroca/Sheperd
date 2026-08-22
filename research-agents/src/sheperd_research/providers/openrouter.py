from __future__ import annotations

import asyncio
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from datetime import datetime
from time import monotonic
from typing import Protocol, TypeVar, cast
from urllib.parse import urlsplit

import httpx
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from ..contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DistillationQualityStatus,
    EvidenceStatus,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    ReportBullet,
    SourceCandidate,
    TranslationStatus,
    WeeklyBrief,
)
from ..progress import ProgressSink
from ..settings import (
    STRICT_OPENROUTER_MODEL,
    free_openrouter_policy_error,
    is_free_openrouter_model,
    strict_openrouter_policy_error,
)
from ..source_catalog import authoritative_geography_domain_catalog
from ..validators import (
    can_extract_url,
    normalize_url,
    url_policy_error,
    validate_article_distillation_quality,
)
from .capabilities import CapabilityReport
from .errors import ProviderError

OPENROUTER_TIMEOUT_SECONDS = 60
OPENROUTER_TIMEOUT_MILLISECONDS = OPENROUTER_TIMEOUT_SECONDS * 1000
OPENROUTER_MAX_OUTPUT_TOKENS = 3_000
DEFAULT_MAX_CONCURRENT_REQUESTS = 2
MAX_SOURCE_CONTENT_CHARS = 8_000
MAX_CLAIMS_PER_SOURCE = 4
MAX_KEY_POINTS_PER_SOURCE = 8
MAX_DISCOVERY_SOURCES = 8
MAX_DISCOVERY_TOOL_CALLS = 20
MAX_DISCOVERY_INPUT_CHARS = 20_000
MAX_DISCOVERY_RECURSION = 24
FALLBACKABLE_ERROR_CODES = frozenset(
    {
        "rate_limit",
        "provider_unavailable",
        "timeout",
        "unsupported_capability",
        "malformed_output",
        "missing_tool_call",
        "tool_failure",
        "agent_loop",
        "model_unavailable",
    }
)
GEOGRAPHY_DOMAIN_CATALOG = authoritative_geography_domain_catalog()
AGENT_NAMES = {
    "discovery:regulatory": "regulatory_research_agent",
    "discovery:us-ports": "us_ports_research_agent",
    "discovery:mexico": "mexico_europe_research_agent",
    "distillation": "source_distillation_agent",
    "critic": "critic_agent",
    "synthesis": "weekly_synthesis_agent",
    "discovery:port-operations": "port_operations_research_agent",
    "discovery:global-market": "global_market_research_agent",
}
OutputT = TypeVar("OutputT", bound=BaseModel)


class TavilyToolProvider(Protocol):
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


class AgentRunnable(Protocol):
    async def ainvoke(self, payload: dict[str, object], **kwargs: object) -> object: ...


class SearchToolInput(BaseModel):
    query: str = Field(min_length=1, max_length=400)


class ExtractToolInput(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=MAX_DISCOVERY_SOURCES)


class ArticleOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=700)
    key_points: list[str] = Field(min_length=2, max_length=4)
    what_happened: str = Field(min_length=1, max_length=700)
    why_it_matters: str = Field(min_length=1, max_length=700)
    risk_assessment: ArticleInsight
    opportunity_assessment: ArticleInsight
    uncertainties: list[str] = Field(min_length=1, max_length=4)
    next_steps: list[str] = Field(min_length=1, max_length=4)
    entities: list[str] = Field(default_factory=list, max_length=12)
    signals: list[str] = Field(default_factory=list, max_length=8)
    claims: list[ClaimDraft] = Field(min_length=1, max_length=3)
    limitations: list[str] = Field(min_length=1, max_length=3)
    source_language: str = "und"
    summary_original: str = ""
    key_points_original: list[str] = Field(default_factory=list, max_length=4)
    translation_status: TranslationStatus = TranslationStatus.NOT_NEEDED
    evidence_excerpts: list[str] = Field(default_factory=list, max_length=8)
    evidence_locators: list[str] = Field(default_factory=list, max_length=8)


class AgentReportBullet(BaseModel):
    """Strict synthesis-only bullet; legacy persisted bullets stay backward-compatible."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=600)
    source_urls: list[str] = Field(min_length=1, max_length=8)
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    why_it_matters: str = Field(min_length=1, max_length=600)
    next_step: str = Field(min_length=1, max_length=600)


class BriefOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(max_length=160)
    summary: str = Field(max_length=1_200)
    signal_event_ids: list[str] = Field(default_factory=list, max_length=100)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    executive_bullets: list[AgentReportBullet] = Field(default_factory=list, max_length=6)
    developments: list[AgentReportBullet] = Field(default_factory=list, max_length=12)
    risks: list[AgentReportBullet] = Field(default_factory=list, max_length=8)
    opportunities: list[AgentReportBullet] = Field(default_factory=list, max_length=8)
    uncertainties: list[AgentReportBullet] = Field(default_factory=list, max_length=8)
    follow_up_questions: list[str] = Field(default_factory=list)


class CriticOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: list[ClaimDraft]


class HealthOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


class OpenRouterProvider:
    def __init__(
        self,
        api_key: str,
        model: str = STRICT_OPENROUTER_MODEL,
        *,
        fallback_models: Sequence[str] = (),
        capability_report: CapabilityReport | None = None,
        max_output_tokens: int = OPENROUTER_MAX_OUTPUT_TOKENS,
        capability_manifest_hash: str | None = None,
        timeout_seconds: int = OPENROUTER_TIMEOUT_SECONDS,
        max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS,
        allow_free_fallbacks: bool = False,
        progress: ProgressSink | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenRouter API key is required")
        policy_error = (
            free_openrouter_policy_error(
                model,
                fallback_models,
                raw_fallback_config=fallback_models,
            )
            if allow_free_fallbacks
            else strict_openrouter_policy_error(
                model,
                (),
                raw_fallback_config=fallback_models,
            )
        )
        if policy_error is not None:
            raise ProviderError(policy_error)
        if capability_report is None or capability_report.source != "live":
            raise ProviderError("OpenRouter provider requires a live capability report")
        if not capability_report.require_tools:
            raise ProviderError("OpenRouter capability report must prove tool support")
        configured_chain = tuple(dict.fromkeys((model, *fallback_models)))
        if capability_report.requested_models != configured_chain:
            raise ProviderError("OpenRouter capability report does not match model chain")
        if not capability_report.eligible_models:
            raise ProviderError("configured free model chain has no eligible models")
        for eligible_model in capability_report.eligible_models:
            capability_evidence = capability_report.evidence_for(eligible_model)
            if (
                capability_evidence is None
                or not capability_evidence.free
                or not capability_evidence.supports_tools
                or not capability_evidence.supports_structured_outputs
                or capability_evidence.reason is not None
            ):
                raise ProviderError("configured model failed capability checks")
        if not is_free_openrouter_model(model):
            raise ProviderError("OpenRouter primary model must be a :free model")
        if not allow_free_fallbacks:
            if configured_chain != (STRICT_OPENROUTER_MODEL,):
                raise ProviderError("strict OpenRouter mode permits Gemma only")
            if capability_report.eligible_models != (STRICT_OPENROUTER_MODEL,):
                raise ProviderError("configured strict model failed capability checks")
        if max_output_tokens < 1:
            raise ValueError("OpenRouter output-token budget must be positive")
        if timeout_seconds < 1:
            raise ValueError("OpenRouter timeout must be positive")
        if max_concurrent_requests < 1:
            raise ValueError("OpenRouter concurrency must be positive")
        self.model_name = model
        self.model_chain = tuple(capability_report.eligible_models)
        self.allow_free_fallbacks = allow_free_fallbacks
        self.max_output_tokens = max_output_tokens
        self.capability_manifest_hash = capability_report.manifest_hash
        self.capability_report = capability_report
        self.timeout_seconds = timeout_seconds
        self.max_concurrent_requests = max_concurrent_requests
        self._progress = progress
        self._rate_limit_seen = False
        self._agent_semaphore: asyncio.Semaphore | None = None
        self._serial_request_lock: asyncio.Lock | None = None
        self.last_call_metadata: dict[str, object] = {}
        self._api_key = SecretStr(api_key)
        self._models: dict[str, BaseChatModel] = {}
        self.call_history: list[dict[str, object]] = []
        self._task_last_call_metadata: ContextVar[dict[str, object] | None] = ContextVar(
            f"openrouter_last_call_metadata_{id(self)}",
            default=None,
        )
        self._task_attempts: ContextVar[tuple[dict[str, object], ...]] = ContextVar(
            f"openrouter_attempts_{id(self)}",
            default=(),
        )
        self._model = self._model_for(self.model_chain[0])

    def _model_for(self, model: str) -> BaseChatModel:
        model_chain = getattr(self, "model_chain", (self.model_name,))
        if model not in model_chain or not is_free_openrouter_model(model):
            raise ProviderError("OpenRouter model is not in the eligible free model chain")
        cached = self._models.get(model)
        if cached is not None:
            return cached
        try:
            from langchain_openrouter import ChatOpenRouter
        except ImportError as error:
            raise ProviderError("langchain-openrouter is not installed") from error
        created: BaseChatModel = ChatOpenRouter(
            model=model,
            api_key=self._api_key,
            temperature=0,
            timeout=int(getattr(self, "timeout_seconds", OPENROUTER_TIMEOUT_SECONDS) * 1000),
            max_tokens=self.max_output_tokens,
            max_retries=0,
            reasoning={"effort": "none", "exclude": True},
            openrouter_provider={"require_parameters": True, "allow_fallbacks": False},
        )
        self._models[model] = created
        return created

    @staticmethod
    def _metadata_from_raw(raw: object) -> dict[str, object]:
        response_metadata = getattr(raw, "response_metadata", {})
        usage_metadata = getattr(raw, "usage_metadata", {})
        if not isinstance(response_metadata, dict):
            response_metadata = {}
        if not isinstance(usage_metadata, dict):
            usage_metadata = {}
        usage = response_metadata.get("token_usage")
        if not isinstance(usage, dict):
            usage = usage_metadata
        output_details = usage.get("completion_tokens_details") or usage.get(
            "output_token_details"
        )
        if not isinstance(output_details, dict):
            output_details = {}
        return {
            "resolved_model": response_metadata.get("model_name")
            or response_metadata.get("model")
            or response_metadata.get("model_id"),
            "request_id": response_metadata.get("id")
            or response_metadata.get("request_id"),
            "input_tokens": usage.get("prompt_tokens") or usage.get("input_tokens"),
            "output_tokens": usage.get("completion_tokens")
            or usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "reasoning_tokens": output_details.get("reasoning_tokens")
            or output_details.get("reasoning"),
            "finish_reason": response_metadata.get("finish_reason"),
        }

    @staticmethod
    def _error_code(error: BaseException) -> str:
        chain = OpenRouterProvider._error_chain(error)
        explicit_codes = {
            getattr(item, "error_code", None)
            for item in chain
            if isinstance(getattr(item, "error_code", None), str)
        }
        for code in ("rate_limit", "plan_usage_limit", "payg_limit"):
            if code in explicit_codes:
                return code
        message = " ".join(
            f"{type(item).__name__} {item}" for item in chain
        ).lower()
        if any(
            any(
                marker in f"{type(item).__name__} {item}".lower()
                for marker in (
                    "429",
                    "rate limit",
                    "rate_limit",
                    "too many requests",
                    "toomanyrequests",
                )
            )
            or getattr(item, "status_code", None) == 429
            or getattr(getattr(item, "response", None), "status_code", None) == 429
            for item in chain
        ):
            return "rate_limit"
        if OpenRouterProvider._is_transport_timeout(error):
            return "timeout"
        if any(
            marker in message
            for marker in ("graphrecursion", "recursion limit", "recursion_limit")
        ):
            return "agent_loop"
        if "notfoundresponse" in message or "status 404" in message or " 404" in message:
            return "model_unavailable"
        if any(
            marker in message
            for marker in (
                "unexpected tool call",
                "agent tool call did not succeed",
                "tool-call budget exceeded",
                "tool call budget exceeded",
            )
        ):
            return "tool_failure"
        if "unsupported" in message or "not implemented" in message:
            return "unsupported_capability"
        if "malformed" in message or "validation" in message or "json" in message:
            return "malformed_output"
        if "required tool" in message or "missing tool" in message:
            return "missing_tool_call"
        if any(code in message for code in ("408", "409", "500", "502", "503", "504")):
            return "provider_unavailable"
        return "provider_error"

    @staticmethod
    def _error_observability(error: BaseException) -> dict[str, object]:
        request_id: str | None = None
        retry_after_seconds: int | float | None = None
        status_code: int | None = None

        def header(headers: object, *names: str) -> str | None:
            if not isinstance(headers, Mapping):
                return None
            lowered = {
                str(key).lower(): value
                for key, value in headers.items()
            }
            for name in names:
                value = lowered.get(name.lower())
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return None

        for item in OpenRouterProvider._error_chain(error):
            if request_id is None:
                for attribute in ("request_id", "requestId"):
                    value = getattr(item, attribute, None)
                    if isinstance(value, str) and value.strip():
                        request_id = value.strip()
                        break
            response = getattr(item, "response", None)
            observed_status = getattr(item, "status_code", None)
            if not isinstance(observed_status, int) and response is not None:
                observed_status = getattr(response, "status_code", None)
            if status_code is None and isinstance(observed_status, int):
                status_code = observed_status
            headers = getattr(response, "headers", None)
            if headers is None:
                headers = getattr(item, "headers", None)
            if request_id is None:
                request_id = header(
                    headers,
                    "x-request-id",
                    "request-id",
                    "openrouter-request-id",
                )
            if retry_after_seconds is None:
                raw_retry_after = header(headers, "retry-after")
                if raw_retry_after is not None:
                    try:
                        parsed = float(raw_retry_after)
                    except ValueError:
                        parsed = None
                    if parsed is not None and math.isfinite(parsed) and parsed >= 0:
                        retry_after_seconds = (
                            int(parsed) if parsed.is_integer() else parsed
                        )

        return {
            "request_id": request_id,
            "retry_after_seconds": retry_after_seconds,
            "status_code": status_code,
        }

    @classmethod
    def _should_retry(cls, error: BaseException, *, model_name: str, attempt: int) -> bool:
        error_code = cls._error_code(error)
        return (
            is_free_openrouter_model(model_name)
            and attempt < 2
            and error_code in {"timeout", "malformed_output"}
        )

    @staticmethod
    def _error_chain(error: BaseException) -> tuple[BaseException, ...]:
        seen: set[int] = set()
        stack: list[BaseException] = [error]
        chain: list[BaseException] = []
        while stack:
            current = stack.pop()
            marker = id(current)
            if marker in seen:
                continue
            seen.add(marker)
            chain.append(current)
            cause = getattr(current, "__cause__", None)
            context = getattr(current, "__context__", None)
            if isinstance(cause, BaseException):
                stack.append(cause)
            if isinstance(context, BaseException):
                stack.append(context)
        return tuple(chain)

    @classmethod
    def _is_transport_timeout(cls, error: BaseException) -> bool:
        return any(
            isinstance(item, (asyncio.TimeoutError, TimeoutError, httpx.TimeoutException))
            for item in cls._error_chain(error)
        )

    @staticmethod
    def _output_hash(output: BaseModel) -> str:
        encoded = json.dumps(output.model_dump(mode="json"), sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _tool_input_hash(query: str | None, urls: Sequence[str]) -> str:
        return hashlib.sha256(
            json.dumps(
                {"query": query, "urls": list(urls)},
                sort_keys=True,
            ).encode()
        ).hexdigest()

    @staticmethod
    def _matches_domain(host: str, domains: Sequence[str]) -> bool:
        return any(
            host == domain.lower().removeprefix("www.")
            or host.endswith(f".{domain.lower().removeprefix('www.')}")
            for domain in domains
        )

    @classmethod
    def _enrich_discovery_geographies(
        cls,
        source: SourceCandidate,
        allowed_geographies: tuple[str, ...],
        configured_queries: Sequence[str],
        configured_domains: Sequence[str],
    ) -> SourceCandidate:
        del configured_queries
        host = (urlsplit(normalize_url(source.url)).hostname or "").lower()
        allowed = {value.casefold(): value for value in allowed_geographies}
        verified = {
            geography.casefold()
            for geography in source.geographies
            if geography.casefold() in allowed
        }
        domain_verified: set[str] = set()
        for domain, geographies in GEOGRAPHY_DOMAIN_CATALOG.items():
            if cls._matches_domain(host, (domain,)) and cls._matches_domain(
                host, configured_domains
            ):
                domain_verified.update(
                    geography.casefold()
                    for geography in geographies
                    if geography.casefold() in allowed
                )
        if domain_verified:
            verified = domain_verified
        return source.model_copy(
            update={"geographies": sorted(allowed[geography] for geography in verified)}
        )

    @classmethod
    def _validate_discovery_source(
        cls,
        source: SourceCandidate,
        *,
        geographies: tuple[str, ...],
        since: datetime,
        until: datetime,
        include_domains: Sequence[str],
        exclude_domains: Sequence[str],
    ) -> SourceCandidate:
        if url_policy_error(source.url, excluded_domains=exclude_domains) is not None:
            raise ValueError("Tavily returned a source rejected by URL policy")
        try:
            normalized_url = normalize_url(source.url)
        except ValueError as error:
            raise ValueError("Tavily returned a malformed source URL") from error
        host = (urlsplit(normalized_url).hostname or "").lower().removeprefix("www.")
        if not host:
            raise ValueError("Tavily returned a source without a host")
        if cls._matches_domain(host, exclude_domains):
            raise ValueError("Tavily returned an excluded source domain")
        if include_domains and not cls._matches_domain(host, include_domains):
            raise ValueError("Tavily returned a source outside allowed domains")
        publisher = source.publisher.lower().removeprefix("www.")
        if publisher != host:
            raise ValueError("Tavily returned unverifiable publisher metadata")
        if source.published_at is not None and not since <= source.published_at <= until:
            raise ValueError("Tavily returned a source outside the configured date window")
        allowed_geographies = {value.lower() for value in geographies}
        observed_geographies = {value.lower() for value in source.geographies}
        if not observed_geographies.intersection(allowed_geographies):
            raise ValueError("Tavily returned unverifiable source geography")
        return source.model_copy(update={"url": normalized_url})

    def _reset_task_call_state(self) -> None:
        self._task_last_call_metadata.set(None)
        self._task_attempts.set(())

    def current_call_metadata(self) -> dict[str, object]:
        metadata_value = self._task_last_call_metadata.get()
        metadata = dict(metadata_value) if isinstance(metadata_value, dict) else {}
        attempts = [dict(item) for item in self._task_attempts.get()]
        if attempts:
            metadata["attempts"] = attempts
        return metadata

    @staticmethod
    def _require_resolved_model(
        metadata: dict[str, object], requested_model: str
    ) -> str:
        resolved_model = metadata.get("resolved_model")
        if not isinstance(resolved_model, str) or not resolved_model.strip():
            raise ProviderError("OpenRouter response missing resolved model metadata")
        if resolved_model != requested_model:
            raise ProviderError("OpenRouter response resolved to an unexpected model")
        if not is_free_openrouter_model(resolved_model):
            raise ProviderError("OpenRouter response resolved to a paid model")
        return resolved_model

    @classmethod
    def _require_strict_resolved_model(cls, metadata: dict[str, object]) -> str:
        return cls._require_resolved_model(metadata, STRICT_OPENROUTER_MODEL)

    def _record_attempt(
        self,
        metadata: dict[str, object],
        attempt_sink: list[dict[str, object]] | None = None,
    ) -> None:
        recorded = dict(metadata)
        self.last_call_metadata = recorded
        attempts = list(self._task_attempts.get())
        attempts.append(recorded)
        self._task_last_call_metadata.set(recorded)
        self._task_attempts.set(tuple(attempts))
        history = getattr(self, "call_history", None)
        if isinstance(history, list):
            history.append(recorded)
        if attempt_sink is not None:
            attempt_sink.append(recorded)
        progress = getattr(self, "_progress", None)
        if progress is not None:
            fallback_reason = recorded.get("fallback_reason")
            event = (
                "route"
                if fallback_reason
                else "error"
                if recorded.get("error_code")
                else "agent"
            )
            progress.emit(
                event,
                "OpenRouter model reroute"
                if fallback_reason
                else "OpenRouter agent attempt",
                operation=recorded.get("operation", "unknown"),
                model=recorded.get("requested_model", "unknown"),
                resolved_model=recorded.get("resolved_model", "unknown"),
                attempt=recorded.get("attempt", "unknown"),
                status="failed" if recorded.get("error_code") else "succeeded",
                tool_calls=recorded.get("tool_calls", 0),
                latency_ms=recorded.get("latency_ms", "unknown"),
                error=recorded.get("error_code") or "none",
                request_id=recorded.get("request_id"),
                retry_after_seconds=recorded.get("retry_after_seconds"),
            )

    async def _invoke_agent_request(
        self,
        agent: object,
        payload: dict[str, object],
    ) -> object:
        async def invoke() -> object:
            return await cast(AgentRunnable, agent).ainvoke(
                payload,
                config={"recursion_limit": MAX_DISCOVERY_RECURSION},
            )

        if getattr(self, "_rate_limit_seen", False):
            lock = getattr(self, "_serial_request_lock", None)
            if lock is None:
                lock = asyncio.Lock()
                self._serial_request_lock = lock
            async with lock:
                return await invoke()

        semaphore = getattr(self, "_agent_semaphore", None)
        if semaphore is None:
            semaphore = asyncio.Semaphore(
                getattr(self, "max_concurrent_requests", DEFAULT_MAX_CONCURRENT_REQUESTS)
            )
            self._agent_semaphore = semaphore
        async with semaphore:
            return await invoke()

    @staticmethod
    def _tool_call_receipts(result: object) -> list[dict[str, object]]:
        """Return redacted tool-call receipts without storing tool output."""

        malformed_result = [
            {
                "call_id": "malformed-result",
                "call_index": 0,
                "tool_name": "unknown",
                "url_count": 0,
                "status": "failed",
                "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
            }
        ]
        if not isinstance(result, dict):
            return malformed_result
        messages = result.get("messages")
        if not isinstance(messages, list):
            return malformed_result

        receipts: list[dict[str, object]] = []
        by_call_id: dict[str, dict[str, object]] = {}
        for message_index, message in enumerate(messages):
            raw_calls = getattr(message, "tool_calls", None)
            if raw_calls is None:
                continue
            if not isinstance(raw_calls, list):
                receipts.append(
                    {
                        "call_id": f"malformed-{message_index}",
                        "call_index": len(receipts),
                        "tool_name": "unknown",
                        "url_count": 0,
                        "status": "failed",
                        "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
                    }
                )
                continue
            for call_index, raw_call in enumerate(raw_calls):
                if not isinstance(raw_call, dict):
                    receipts.append(
                        {
                            "call_id": f"malformed-{message_index}-{call_index}",
                            "call_index": len(receipts),
                            "tool_name": "unknown",
                            "url_count": 0,
                            "status": "failed",
                            "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
                        }
                    )
                    continue
                raw_call_id = raw_call.get("id")
                name = raw_call.get("name")
                arguments = raw_call.get("args")
                if (
                    not isinstance(raw_call_id, str)
                    or not raw_call_id
                    or not isinstance(name, str)
                    or not name
                    or not isinstance(arguments, dict)
                    or raw_call_id in by_call_id
                ):
                    receipts.append(
                        {
                            "call_id": raw_call_id
                            if isinstance(raw_call_id, str) and raw_call_id
                            else f"malformed-{message_index}-{call_index}",
                            "call_index": len(receipts),
                            "tool_name": name if isinstance(name, str) and name else "unknown",
                            "url_count": 0,
                            "status": "failed",
                            "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
                        }
                    )
                    continue
                call_id = raw_call_id
                urls = arguments.get("urls")
                normalized_urls: list[str] = []
                if isinstance(urls, list):
                    for url in urls:
                        if not isinstance(url, str) or not url.startswith(
                            ("http://", "https://")
                        ):
                            continue
                        try:
                            normalized_urls.append(normalize_url(url))
                        except ValueError:
                            continue
                query = arguments.get("query")
                receipt: dict[str, object] = {
                    "call_id": call_id,
                    "call_index": len(receipts),
                    "tool_name": name,
                    "url_count": len(normalized_urls),
                    "status": "requested",
                    "input_hash": OpenRouterProvider._tool_input_hash(
                        query if isinstance(query, str) else None,
                        normalized_urls,
                    ),
                }
                receipts.append(receipt)
                by_call_id[call_id] = receipt

        for message in messages:
            tool_message_call_id: object = getattr(message, "tool_call_id", None)
            if not isinstance(tool_message_call_id, str):
                if isinstance(message, ToolMessage):
                    receipts.append(
                        {
                            "call_id": f"unpaired-{len(receipts) + 1}",
                            "call_index": len(receipts),
                            "tool_name": "unknown",
                            "url_count": 0,
                            "status": "failed",
                            "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
                        }
                    )
                continue
            if tool_message_call_id not in by_call_id:
                receipts.append(
                    {
                        "call_id": tool_message_call_id,
                        "call_index": len(receipts),
                        "tool_name": "unknown",
                        "url_count": 0,
                        "status": "failed",
                        "input_hash": OpenRouterProvider._tool_input_hash(None, ()),
                    }
                )
                continue
            receipt = by_call_id[tool_message_call_id]
            content = getattr(message, "content", "")
            content_text = (
                content if isinstance(content, str) else json.dumps(content, default=str)
            )
            receipt["result_hash"] = hashlib.sha256(content_text.encode()).hexdigest()
            receipt["status"] = (
                "succeeded"
                if getattr(message, "status", None) in {"success", "succeeded"}
                else "failed"
            )
            try:
                parsed = json.loads(content_text)
            except (TypeError, json.JSONDecodeError):
                parsed = None
                receipt["status"] = "failed"
            if not isinstance(parsed, dict):
                receipt["status"] = "failed"
                continue
            if receipt["tool_name"] == "tavily_search":
                sources = parsed.get("sources")
                source_fields = {"url", "title", "publisher", "published_at", "snippet"}
                if (
                    set(parsed) == {"query", "sources"}
                    and isinstance(parsed.get("query"), str)
                    and isinstance(sources, list)
                    and all(
                        isinstance(source, dict)
                        and set(source) == source_fields
                        and all(
                            isinstance(source[field], str)
                            for field in source_fields
                            if field != "published_at"
                        )
                        and (
                            source["published_at"] is None
                            or isinstance(source["published_at"], str)
                        )
                        for source in sources
                    )
                ):
                    receipt["result_count"] = len(sources)
                elif (
                    set(parsed) == {"query", "reused"}
                    and parsed.get("reused") is True
                    and isinstance(parsed.get("query"), str)
                ):
                    receipt["result_count"] = 0
                else:
                    receipt["status"] = "failed"
            elif receipt["tool_name"] == "tavily_extract":
                extracted_urls = parsed.get("extracted_urls")
                extracted_count = parsed.get("extracted_count")
                if (
                    set(parsed) == {"extracted_urls", "extracted_count"}
                    and isinstance(extracted_urls, list)
                    and all(isinstance(url, str) for url in extracted_urls)
                    and isinstance(extracted_count, int)
                    and not isinstance(extracted_count, bool)
                    and extracted_count == len(extracted_urls)
                ):
                    receipt["result_count"] = extracted_count
                else:
                    receipt["status"] = "failed"
            else:
                receipt["status"] = "failed"
        for receipt in receipts:
            if receipt["status"] == "requested":
                receipt["status"] = "failed"
        return receipts

    @staticmethod
    def _structured_response(result: object, operation: str) -> object:
        if not isinstance(result, dict):
            raise ProviderError(f"OpenRouter {operation} returned malformed output")
        parsed = result.get("structured_response")
        if parsed is None:
            raise ProviderError(f"OpenRouter {operation} returned malformed output")
        return parsed

    @staticmethod
    def _last_message(result: object) -> object:
        if not isinstance(result, dict):
            return result
        messages = result.get("messages")
        if isinstance(messages, list):
            for message in reversed(messages):
                response_metadata = getattr(message, "response_metadata", None)
                if isinstance(response_metadata, dict) and any(
                    key in response_metadata
                    for key in ("model_name", "model", "model_id", "id", "request_id")
                ):
                    return message
            for message in reversed(messages):
                if hasattr(message, "response_metadata") or hasattr(message, "usage_metadata"):
                    return message
        return result

    async def _invoke_agent(
        self,
        schema: type[OutputT],
        prompt: str,
        *,
        prompt_version: str,
        operation: str,
        tools: Sequence[BaseTool] = (),
        required_tools: Sequence[str] = (),
        attempt_sink: list[dict[str, object]] | None = None,
        tool_latency_by_input: dict[str, int] | None = None,
        tool_provider_metadata_by_input: dict[str, dict[str, object]] | None = None,
        tool_failure_sink: list[dict[str, object]] | None = None,
        runtime_tool_receipts: list[dict[str, object]] | None = None,
    ) -> OutputT:
        last_error: BaseException | None = None
        last_error_code: str | None = None
        model_chain = tuple(getattr(self, "model_chain", (self.model_name,)))
        allow_free_fallbacks = bool(getattr(self, "allow_free_fallbacks", False))
        fallback_reason: str | None = None
        corrective_retry = False
        for model_index, model_name in enumerate(model_chain):
            for attempt in range(1, 3):
                started_at = monotonic()
                tool_receipts: list[dict[str, object]] = []
                runtime_receipt_start = (
                    len(runtime_tool_receipts) if runtime_tool_receipts is not None else 0
                )
                try:
                    progress = getattr(self, "_progress", None)
                    if progress is not None:
                        progress.emit(
                            "agent",
                            "LangChain agent started",
                            agent=AGENT_NAMES.get(operation, operation),
                            model=model_name,
                            attempt=attempt,
                            tool_count=len(tools),
                        )
                    strategy = ToolStrategy(schema, handle_errors=False)
                    agent = create_agent(
                        model=self._model_for(model_name),
                        tools=list(tools),
                        system_prompt=(
                            "Return only the requested structured response. "
                            "Do not reveal reasoning or add unsupported facts."
                        ),
                        response_format=strategy,
                        name=AGENT_NAMES.get(operation),
                    )
                    result = await self._invoke_agent_request(
                        agent,
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": (
                                        f"{prompt}\n\nCORRECTIVE RETRY: The previous response "
                                        "was malformed. Return every required field with "
                                        "non-empty structured values and no extra fields."
                                        if corrective_retry
                                        else prompt
                                    ),
                                }
                            ],
                        },
                    )
                    structured_tool_names = {
                        schema.__name__,
                        schema.__name__.lower(),
                    }
                    tool_receipts = [
                        receipt
                        for receipt in self._tool_call_receipts(result)
                        if receipt.get("tool_name") not in structured_tool_names
                    ]
                    if not tool_receipts and runtime_tool_receipts is not None:
                        tool_receipts = [
                            dict(receipt)
                            for receipt in runtime_tool_receipts[runtime_receipt_start:]
                        ]
                    if tool_failure_sink is not None:
                        tool_failure_sink.clear()
                    tool_names = {tool.name for tool in tools}
                    for receipt in tool_receipts:
                        if receipt.get("tool_name") not in tool_names:
                            receipt["status"] = "failed"
                    unknown_tools = {
                        str(receipt.get("tool_name"))
                        for receipt in tool_receipts
                        if receipt.get("tool_name") not in tool_names
                    }
                    if unknown_tools:
                        raise ProviderError(
                            "unexpected tool call: " + ", ".join(sorted(unknown_tools))
                        )
                    if any(receipt.get("status") != "succeeded" for receipt in tool_receipts):
                        raise ProviderError("agent tool call did not succeed")
                    if tool_latency_by_input is not None:
                        for receipt in tool_receipts:
                            input_hash = receipt.get("input_hash")
                            if isinstance(input_hash, str) and input_hash in tool_latency_by_input:
                                receipt["latency_ms"] = tool_latency_by_input[input_hash]
                    if tool_provider_metadata_by_input is not None:
                        for receipt in tool_receipts:
                            input_hash = receipt.get("input_hash")
                            metadata = (
                                tool_provider_metadata_by_input.get(input_hash)
                                if isinstance(input_hash, str)
                                else None
                            )
                            if isinstance(metadata, dict):
                                receipt.update(metadata)
                    called_tools = {
                        str(receipt["tool_name"])
                        for receipt in tool_receipts
                        if receipt.get("status") == "succeeded"
                    }
                    missing_tools = sorted(set(required_tools) - called_tools)
                    if missing_tools:
                        raise ProviderError(
                            "required tool call missing: " + ", ".join(missing_tools)
                        )
                    output = schema.model_validate(
                        self._structured_response(result, operation)
                    )
                    raw = self._last_message(result)
                    metadata = self._metadata_from_raw(raw)
                    resolved_model = self._require_resolved_model(metadata, model_name)
                    output_tokens = metadata.get("output_tokens")
                    if isinstance(output_tokens, int) and output_tokens > self.max_output_tokens:
                        raise ProviderError("OpenRouter output-token budget exceeded")
                    metadata.update(
                        {
                            "requested_model": model_name,
                            "resolved_model": resolved_model,
                            "prompt_version": prompt_version,
                            "operation": operation,
                            "attempt": attempt,
                            "model_index": model_index,
                            "fallback_reason": fallback_reason,
                            "tool_calls": len(tool_receipts),
                            "tool_call_receipts": tool_receipts,
                            "required_tools": list(required_tools),
                            "latency_ms": max(0, int((monotonic() - started_at) * 1000)),
                            "error_code": None,
                            "output_hash": self._output_hash(output),
                            "capability_manifest_hash": getattr(
                                self, "capability_manifest_hash", None
                            ),
                        }
                    )
                    self._record_attempt(metadata, attempt_sink)
                    return output
                except Exception as error:
                    last_error = error
                    error_code = self._error_code(error)
                    last_error_code = error_code
                    if not tool_receipts and runtime_tool_receipts is not None:
                        tool_receipts = [
                            dict(receipt)
                            for receipt in runtime_tool_receipts[runtime_receipt_start:]
                        ]
                    if tool_failure_sink:
                        for failure in tool_failure_sink:
                            matching = next(
                                (
                                    receipt
                                    for receipt in tool_receipts
                                    if receipt.get("tool_name") == failure.get("tool_name")
                                    and receipt.get("status") == "failed"
                                ),
                                None,
                            )
                            if matching is None:
                                tool_receipts.append(dict(failure))
                            elif failure.get("error_code"):
                                matching["error_code"] = failure["error_code"]
                        tool_failure_sink.clear()
                    metadata = {
                        "requested_model": model_name,
                        "resolved_model": None,
                        "prompt_version": prompt_version,
                        "operation": operation,
                        "attempt": attempt,
                        "model_index": model_index,
                        "fallback_reason": fallback_reason,
                        "tool_calls": len(tool_receipts),
                        "tool_call_receipts": tool_receipts,
                        "required_tools": list(required_tools),
                        "latency_ms": max(0, int((monotonic() - started_at) * 1000)),
                        "error_code": error_code,
                        "error_type": type(error).__name__,
                        "output_hash": None,
                        "capability_manifest_hash": getattr(
                            self, "capability_manifest_hash", None
                        ),
                    }
                    metadata.update(self._error_observability(error))
                    self._record_attempt(metadata, attempt_sink)
                    if error_code == "rate_limit":
                        self._rate_limit_seen = True
                    if self._should_retry(error, model_name=model_name, attempt=attempt):
                        corrective_retry = error_code == "malformed_output"
                        await asyncio.sleep(0.2)
                        continue
                    next_model_available = model_index + 1 < len(model_chain)
                    if (
                        allow_free_fallbacks
                        and next_model_available
                        and error_code in FALLBACKABLE_ERROR_CODES
                    ):
                        fallback_reason = f"{model_name}:{error_code}"
                        break
                    raise ProviderError(
                        f"OpenRouter {operation} failed",
                        attempts=list(self._task_attempts.get()),
                        error_code=error_code,
                    ) from error
        raise ProviderError(
            f"OpenRouter {operation} failed; free model chain exhausted",
            attempts=list(self._task_attempts.get()),
            error_code=last_error_code,
        ) from last_error

    async def _invoke_structured(
        self,
        schema: type[OutputT],
        prompt: str,
        *,
        prompt_version: str,
        operation: str,
        tools: Sequence[BaseTool] = (),
        required_tools: Sequence[str] = (),
        attempt_sink: list[dict[str, object]] | None = None,
        tool_latency_by_input: dict[str, int] | None = None,
        tool_provider_metadata_by_input: dict[str, dict[str, object]] | None = None,
        tool_failure_sink: list[dict[str, object]] | None = None,
        runtime_tool_receipts: list[dict[str, object]] | None = None,
    ) -> OutputT:
        return await self._invoke_agent(
            schema,
            prompt,
            prompt_version=prompt_version,
            operation=operation,
            tools=tools,
            required_tools=required_tools,
            attempt_sink=attempt_sink,
            tool_latency_by_input=tool_latency_by_input,
            tool_provider_metadata_by_input=tool_provider_metadata_by_input,
            tool_failure_sink=tool_failure_sink,
            runtime_tool_receipts=runtime_tool_receipts,
        )

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
        tavily: TavilyToolProvider,
    ) -> LaneDiscoveryResult:
        known_sources: dict[str, SourceCandidate] = {}
        captured_content: dict[str, str] = {}
        search_calls: set[str] = set()
        search_results_by_query: dict[str, list[SourceCandidate]] = {}
        requested_extraction_urls: set[str] = set()
        tool_errors: list[str] = []
        filtered_source_rejections: list[str] = []
        tool_latency_by_input: dict[str, int] = {}
        tool_provider_metadata_by_input: dict[str, dict[str, object]] = {}
        tool_failure_receipts: list[dict[str, object]] = []
        runtime_tool_receipts: list[dict[str, object]] = []
        attempt_sink: list[dict[str, object]] = []
        tool_calls = 0
        tool_input_chars = 0
        self._reset_task_call_state()

        def discovery_error(message: str) -> ProviderError:
            return ProviderError(message, attempts=list(attempt_sink))

        def reserve_tool_call(input_chars: int) -> None:
            nonlocal tool_calls, tool_input_chars
            tool_calls += 1
            tool_input_chars += input_chars
            if tool_calls > MAX_DISCOVERY_TOOL_CALLS:
                raise ValueError("discovery tool-call budget exceeded")
            if tool_input_chars > MAX_DISCOVERY_INPUT_CHARS:
                raise ValueError("discovery tool-input budget exceeded")

        def record_tool_failure(
            tool_name: str,
            input_hash: str,
            url_count: int,
            latency_ms: int,
            error: BaseException,
            provider_metadata: dict[str, object] | None = None,
        ) -> None:
            error_code = getattr(error, "error_code", None)
            if not isinstance(error_code, str):
                error_code = self._error_code(error)
            receipt: dict[str, object] = {
                    "call_id": f"provider-failure-{len(tool_failure_receipts) + 1}",
                    "call_index": len(tool_failure_receipts),
                    "tool_name": tool_name,
                    "url_count": url_count,
                    "status": "failed",
                    "input_hash": input_hash,
                    "result_hash": None,
                    "result_count": 0,
                    "latency_ms": latency_ms,
                    "error_code": error_code,
                }
            if provider_metadata:
                receipt.update(provider_metadata)
            tool_failure_receipts.append(receipt)

        def record_tool_success(
            tool_name: str,
            input_hash: str,
            url_count: int,
            latency_ms: int,
            result_text: str,
            result_count: int,
            provider_metadata: dict[str, object] | None = None,
        ) -> None:
            runtime_tool_receipts.append(
                {
                    "call_id": f"runtime-{len(runtime_tool_receipts) + 1}",
                    "call_index": len(runtime_tool_receipts),
                    "tool_name": tool_name,
                    "url_count": url_count,
                    "status": "succeeded",
                    "input_hash": input_hash,
                    "result_hash": hashlib.sha256(result_text.encode()).hexdigest(),
                    "result_count": result_count,
                    "latency_ms": latency_ms,
                    **(provider_metadata or {}),
                }
            )

        def provider_key_metadata() -> dict[str, object]:
            raw = getattr(tavily, "last_call_metadata", {})
            if not isinstance(raw, dict):
                return {}
            metadata: dict[str, object] = {}
            for key in ("key_slot", "key_count"):
                value = raw.get(key)
                if isinstance(value, int) and not isinstance(value, bool):
                    metadata[f"provider_key_{key.removeprefix('key_')}"] = value
            return metadata

        async def run_search(query: str) -> str:
            input_hash = self._tool_input_hash(query, ())
            started = monotonic()
            failure: BaseException | None = None
            try:
                if query not in queries:
                    raise ValueError("discovery query is outside the configured lane scope")
                reserve_tool_call(len(query))
                if query in search_calls:
                    cached_sources = search_results_by_query.get(query, [])
                    result_text = json.dumps(
                        {
                            "query": query,
                            "sources": [
                                {
                                    "url": normalize_url(source.url),
                                    "title": source.title,
                                    "publisher": source.publisher,
                                    "published_at": source.published_at.isoformat()
                                    if source.published_at
                                    else None,
                                    "snippet": source.snippet[:500],
                                }
                                for source in cached_sources[:MAX_DISCOVERY_SOURCES]
                                if can_extract_url(source.url)
                            ],
                        }
                    )
                    record_tool_success(
                        "tavily_search",
                        input_hash,
                        len(cached_sources),
                        max(0, int((monotonic() - started) * 1000)),
                        result_text,
                        len(cached_sources),
                    )
                    return result_text
                if len(search_calls) >= len(queries):
                    raise ValueError("discovery search-call budget exceeded")
                found = await tavily.search(
                    query,
                    since=since,
                    until=until,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    max_results=min(max(1, max_results), MAX_DISCOVERY_SOURCES),
                )
                valid_sources: list[SourceCandidate] = []
                for source in found:
                    try:
                        valid_sources.append(
                            self._validate_discovery_source(
                                self._enrich_discovery_geographies(
                                    source,
                                    geographies,
                                    queries,
                                    include_domains,
                                ),
                                geographies=geographies,
                                since=since,
                                until=until,
                                include_domains=include_domains,
                                exclude_domains=exclude_domains,
                            )
                        )
                    except ValueError as error:
                        filtered_source_rejections.append(str(error))
                if not valid_sources:
                    raise ValueError(
                        "Tavily search returned no sources inside the configured policy"
                    )
                search_calls.add(query)
                search_results_by_query[query] = valid_sources
            except Exception as error:
                failure = error
                tool_errors.append(error.__class__.__name__)
                raise
            finally:
                latency_ms = max(0, int((monotonic() - started) * 1000))
                tool_latency_by_input[input_hash] = latency_ms
                provider_metadata = provider_key_metadata()
                if provider_metadata:
                    tool_provider_metadata_by_input[input_hash] = provider_metadata
                if failure is not None:
                    record_tool_failure(
                        "tavily_search",
                        input_hash,
                        0,
                        latency_ms,
                        failure,
                        provider_metadata,
                    )
            for source in valid_sources:
                if can_extract_url(source.url):
                    known_sources.setdefault(normalize_url(source.url), source)
            result_text = json.dumps(
                {
                    "query": query,
                    "sources": [
                        {
                            "url": normalize_url(source.url),
                            "title": source.title,
                            "publisher": source.publisher,
                            "published_at": source.published_at.isoformat()
                            if source.published_at
                            else None,
                            "snippet": source.snippet[:500],
                        }
                        for source in valid_sources[:MAX_DISCOVERY_SOURCES]
                        if can_extract_url(source.url)
                    ],
                }
            )
            record_tool_success(
                "tavily_search",
                input_hash,
                len(valid_sources),
                max(0, int((monotonic() - started) * 1000)),
                result_text,
                len(valid_sources),
                provider_metadata,
            )
            return result_text

        async def run_extract(urls: list[str]) -> str:
            input_hash = self._tool_input_hash(None, urls)
            started = monotonic()
            failure: BaseException | None = None
            try:
                normalized = [normalize_url(url) for url in urls]
                reserve_tool_call(sum(len(url) for url in normalized))
                if normalized and all(url in captured_content for url in normalized):
                    result_text = json.dumps(
                        {
                            "extracted_urls": sorted(captured_content),
                            "extracted_count": len(captured_content),
                        }
                    )
                    record_tool_success(
                        "tavily_extract",
                        input_hash,
                        len(normalized),
                        max(0, int((monotonic() - started) * 1000)),
                        result_text,
                        len(captured_content),
                    )
                    return result_text
                if any(url not in known_sources for url in normalized):
                    raise ValueError("extraction URL was not returned by Tavily Search")
                requested_extraction_urls.update(normalized)
                extracted = await tavily.extract(
                    [known_sources[url] for url in normalized[:MAX_DISCOVERY_SOURCES]]
                )
                normalized_extracted = {
                    normalize_url(url): content.strip()
                    for url, content in extracted.items()
                    if isinstance(url, str) and isinstance(content, str) and content.strip()
                }
                missing_content = [url for url in normalized if url not in normalized_extracted]
                if missing_content:
                    raise ValueError("Tavily extraction returned incomplete content")
            except Exception as error:
                failure = error
                tool_errors.append(error.__class__.__name__)
                raise
            finally:
                latency_ms = max(0, int((monotonic() - started) * 1000))
                tool_latency_by_input[input_hash] = latency_ms
                provider_metadata = provider_key_metadata()
                if provider_metadata:
                    tool_provider_metadata_by_input[input_hash] = provider_metadata
                if failure is not None:
                    record_tool_failure(
                        "tavily_extract",
                        input_hash,
                        len(urls),
                        latency_ms,
                        failure,
                        provider_metadata,
                    )
            captured_content.update(normalized_extracted)
            result_text = json.dumps(
                {
                    "extracted_urls": sorted(captured_content),
                    "extracted_count": len(captured_content),
                }
            )
            record_tool_success(
                "tavily_extract",
                input_hash,
                len(normalized),
                max(0, int((monotonic() - started) * 1000)),
                result_text,
                len(normalized_extracted),
                provider_metadata,
            )
            return result_text

        search_tool = StructuredTool.from_function(
            coroutine=run_search,
            name="tavily_search",
            description=(
                "Search only the configured lane queries with Tavily. "
                "Use this before extraction."
            ),
            args_schema=SearchToolInput,
        )
        extract_tool = StructuredTool.from_function(
            coroutine=run_extract,
            name="tavily_extract",
            description=(
                "Extract clean content only from URLs previously returned by "
                "tavily_search."
            ),
            args_schema=ExtractToolInput,
        )
        tools = [search_tool, extract_tool]
        prompt = (
            f"You are the bounded {lane} discovery worker. Research only these configured "
            f"geographies: {list(geographies)}. You must call tavily_search for every "
            "configured query family, then call tavily_extract for URLs returned by search "
            "before returning your structured packet. Use no outside retrieval. "
            "Do not invent URLs, dates, publishers, or claims. Select only public, "
            "non-LinkedIn sources returned by the tools. Return the selected source URLs, "
            "the exact selected queries, and short evidence notes. Do not reveal reasoning.\n\n"
            f"CONFIGURED QUERIES: {queries}\nLANE: {lane}\n"
            f"DATE WINDOW: {since.isoformat()} through {until.isoformat()}\n"
            "Tool contract: search arguments are restricted to CONFIGURED QUERIES; extraction "
            "arguments must use URLs returned by tavily_search."
        )
        try:
            packet = await self._invoke_structured(
                LaneDiscoveryPacket,
                prompt,
                prompt_version="discovery-v3-multilingual",
                operation=f"discovery:{lane}",
                tools=tools,
                required_tools=("tavily_search", "tavily_extract"),
                attempt_sink=attempt_sink,
                tool_latency_by_input=tool_latency_by_input,
                tool_provider_metadata_by_input=tool_provider_metadata_by_input,
                tool_failure_sink=tool_failure_receipts,
                runtime_tool_receipts=runtime_tool_receipts,
            )
        except ProviderError as error:
            if tool_calls > MAX_DISCOVERY_TOOL_CALLS:
                raise discovery_error("discovery tool-call budget exceeded") from error
            if tool_input_chars > MAX_DISCOVERY_INPUT_CHARS:
                raise discovery_error("discovery tool-input budget exceeded") from error
            error.attempts = list(attempt_sink)
            raise
        if tool_calls > MAX_DISCOVERY_TOOL_CALLS:
            raise discovery_error("discovery tool-call budget exceeded")
        if tool_input_chars > MAX_DISCOVERY_INPUT_CHARS:
            raise discovery_error("discovery tool-input budget exceeded")
        if tool_errors:
            raise discovery_error("discovery tool execution failed")
        known_urls = set(known_sources)
        missing_queries = sorted(set(queries) - search_calls)
        if missing_queries:
            raise discovery_error(
                "discovery agent skipped configured query families: "
                + ", ".join(missing_queries)
            )
        if not captured_content:
            raise discovery_error("discovery agent did not extract any source content")
        if any(url not in captured_content for url in requested_extraction_urls):
            raise discovery_error("discovery extraction returned incomplete content")
        selected_urls = [normalize_url(url) for url in packet.source_urls]
        if any(url not in known_urls for url in selected_urls):
            raise discovery_error("OpenRouter discovery introduced an unknown source URL")
        if any(query not in queries for query in packet.selected_queries):
            raise discovery_error("OpenRouter discovery introduced an unknown query")
        selected_urls = list(dict.fromkeys(selected_urls or list(captured_content)))[:max_results]
        missing_extractions = [url for url in selected_urls if url not in captured_content]
        if missing_extractions:
            raise discovery_error(
                "discovery agent selected sources without successful extraction"
            )
        sources = [known_sources[url] for url in selected_urls]
        content = {
            url: captured_content[url]
            for url in selected_urls
            if url in captured_content
        }
        metadata = {
            "lane": lane,
            "search_calls": len(search_calls),
            "tool_calls": tool_calls,
            "tool_input_chars": tool_input_chars,
            "extracted_count": len(content),
            "tool_errors": tool_errors,
            "filtered_source_count": len(filtered_source_rejections),
            "filtered_source_reasons": sorted(set(filtered_source_rejections)),
            "agent_call": dict(attempt_sink[-1]) if attempt_sink else {},
            "attempts": list(attempt_sink),
        }
        return LaneDiscoveryResult(
            packet=packet.model_copy(update={"source_urls": selected_urls}),
            sources=sources,
            content=content,
            metadata=metadata,
        )

    async def health_check(self) -> str:
        self._reset_task_call_state()
        try:
            result = await self._invoke_structured(
                HealthOutput,
                "Return {\"ok\": true} if you can respond with the requested schema.",
                prompt_version="health-v1",
                operation="health",
            )
            output = HealthOutput.model_validate(result)
            if not output.ok:
                raise ProviderError("OpenRouter health response was not affirmative")
            metadata = self.current_call_metadata()
            requested_model = metadata.get("requested_model")
            if not isinstance(requested_model, str):
                requested_model = self.model_name
            return self._require_resolved_model(metadata, requested_model)
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenRouter health check failed") from error

    async def distill(
        self,
        source: SourceCandidate,
        content: str,
        *,
        prompt_version: str = "distill-v6-insight",
    ) -> ArticleDistillation:
        self._reset_task_call_state()
        prompt = (
            "You are an evidence distiller for maritime and D&D intelligence. "
            "Use only the supplied public source; do not use outside knowledge. "
            "User-provided seed links remain unverified until independently supported. "
            "Do not provide legal advice. Return only the requested structured fields.\n\n"
            "Rules: keep the summary concise; detect the source language; preserve an "
            "original-language summary and key points, then provide normalized English "
            "fields; return at least two short key_points, one or more claims, entities, "
            "signals, and limitations; provide what_happened, why_it_matters, at least "
            "one uncertainty, and at least one next_step; provide both a risk_assessment "
            "and opportunity_assessment using status supported, not_observed, or "
            "uncertain; when evidence does not support a risk or opportunity, use "
            "not_observed with an explicit evidence-gap statement rather than inventing "
            "a conclusion; "
            "include limitations and access gaps; mark unsupported or inferred claims "
            "unverified; use the source URL exactly as provided for every citation; "
            "never invent a citation, date, number, entity, or event. Evidence excerpts "
            "must be <=320 characters and <=40 words and must be copied from the source; "
            "supported risk and opportunity assessments require an evidence excerpt or "
            "locator. Return no null, blank, placeholder, or omitted required field.\n\n"
            f"SOURCE URL: {source.url}\nTITLE: {source.title}\n"
            f"PUBLISHER: {source.publisher}\nCONTENT:\n{content[:MAX_SOURCE_CONTENT_CHARS]}"
        )
        try:
            output = await self._invoke_structured(
                ArticleOutput,
                prompt,
                prompt_version=prompt_version,
                operation="distillation",
            )
            metadata = self.current_call_metadata()
            translation_status = output.translation_status
            if (
                output.source_language not in {"en", "und"}
                and translation_status is TranslationStatus.NOT_NEEDED
            ):
                translation_status = TranslationStatus.FAILED
            distillation = ArticleDistillation(
                source_url=source.url,
                summary=output.summary,
                key_points=output.key_points[:MAX_KEY_POINTS_PER_SOURCE],
                entities=output.entities,
                signals=output.signals,
                claims=output.claims[:MAX_CLAIMS_PER_SOURCE],
                limitations=output.limitations,
                published_at=source.published_at,
                model_id=self._require_resolved_model(
                    metadata,
                    str(metadata.get("requested_model", self.model_name)),
                ),
                prompt_version=prompt_version,
                source_language=output.source_language,
                summary_original=output.summary_original or output.summary,
                key_points_original=output.key_points_original or output.key_points,
                translation_status=translation_status,
                evidence_excerpts=output.evidence_excerpts,
                evidence_locators=output.evidence_locators,
                what_happened=output.what_happened,
                why_it_matters=output.why_it_matters,
                risk_assessment=output.risk_assessment,
                opportunity_assessment=output.opportunity_assessment,
                uncertainties=output.uncertainties,
                next_steps=output.next_steps,
                quality_status=DistillationQualityStatus.COMPLETE,
                evidence_status=(
                    EvidenceStatus.PARTIALLY_SUPPORTED
                    if output.source_language not in {"en", "und"}
                    and translation_status is TranslationStatus.FAILED
                    else EvidenceStatus.MIXED
                ),
            )
            quality_issues = validate_article_distillation_quality(distillation)
            if quality_issues:
                raise ProviderError(
                    "article insight packet incomplete: " + ", ".join(quality_issues)
                )
            return distillation
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenRouter distillation failed") from error

    async def critic(
        self,
        claims: list[ClaimDraft],
        source_urls: set[str],
        *,
        prompt_version: str = "critic-v4",
    ) -> list[ClaimDraft]:
        self._reset_task_call_state()
        prompt = (
            "You are the single bounded evidence critic. Review the claims below for "
            "unsupported inference, conflicts, stale wording, and citation gaps. "
            "Return the same claims with corrected evidence status and conflicts. "
            "Do not add facts or sources. Every source URL must be from the known set. "
            "A user-provided seed alone cannot support a verified claim.\n\n"
            f"KNOWN SOURCES: {sorted(source_urls)}\nCLAIMS: "
            f"{[claim.model_dump(mode='json') for claim in claims]}"
        )
        try:
            output = await self._invoke_structured(
                CriticOutput,
                prompt,
                prompt_version=prompt_version,
                operation="critic",
            )
            for claim in output.claims:
                if any(url not in source_urls for url in claim.source_urls):
                    raise ProviderError("OpenRouter critic introduced an unknown citation")
            return output.claims
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError(f"OpenRouter {prompt_version} failed") from error

    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        *,
        covered_from: datetime,
        covered_until: datetime,
        prompt_version: str = "weekly-brief-v6-decision",
    ) -> WeeklyBrief:
        self._reset_task_call_state()
        cadence_label = "daily" if prompt_version.startswith("daily-") else "weekly"
        evidence_blocks: list[str] = []
        for item in distillations:
            risk = (
                item.risk_assessment.model_dump(mode="json")
                if item.risk_assessment
                else "not recorded"
            )
            opportunity = (
                item.opportunity_assessment.model_dump(mode="json")
                if item.opportunity_assessment
                else "not recorded"
            )
            evidence_blocks.append(
                f"URL: {item.source_url}\nSUMMARY: {item.summary}\n"
                f"WHAT HAPPENED: {item.what_happened}\n"
                f"WHY IT MATTERS: {item.why_it_matters}\nRISK: {risk}\n"
                f"OPPORTUNITY: {opportunity}\nNEXT STEPS: {item.next_steps}\n"
                f"UNCERTAINTIES: {item.uncertainties}\nCLAIMS: "
                f"{[claim.model_dump(mode='json') for claim in item.claims]}"
            )
        evidence = "\n\n".join(evidence_blocks)
        prompt = (
            f"Create a concise {cadence_label} maritime intelligence brief using only the "
            "source-bound evidence below. Write an executive summary suitable for "
            "a dashboard: short bullets first, then material developments, risks, "
            "opportunities, uncertainty, and follow-up questions. Separate facts "
            "from inference and limitations. Do not provide legal advice. Preserve "
            "source-linked signal IDs and never invent citations. Every factual "
            "bullet must cite one or more supplied URLs and include non-empty "
            "why_it_matters and next_step fields. Return non-empty structured "
            "fields for executive_bullets, developments, risks, opportunities, "
            "uncertainties, and follow_up_questions. If the supplied evidence does "
            "not support a material item, include an explicit evidence-backed absence "
            "statement with a supplied citation instead of inventing an item or leaving "
            "the section empty. Every risks, opportunities, and uncertainties bullet "
            "must include non-empty why_it_matters and next_step fields.\n\n"
            f"RUN ID: {run_id}\nEVIDENCE:\n{evidence[:30000]}"
        )
        try:
            output = await self._invoke_structured(
                BriefOutput,
                prompt,
                prompt_version=prompt_version,
                operation="synthesis",
            )
            metadata = self.current_call_metadata()
            return WeeklyBrief(
                run_id=run_id,
                title=output.title,
                covered_from=covered_from,
                covered_until=covered_until,
                summary=output.summary,
                signal_event_ids=output.signal_event_ids,
                source_urls=[item.source_url for item in distillations],
                limitations=output.limitations,
                evidence_status=output.evidence_status,
                model_id=self._require_resolved_model(
                    metadata,
                    str(metadata.get("requested_model", self.model_name)),
                ),
                prompt_version=prompt_version,
                executive_bullets=[
                    ReportBullet.model_validate(item.model_dump())
                    for item in output.executive_bullets
                ],
                developments=[
                    ReportBullet.model_validate(item.model_dump())
                    for item in output.developments
                ],
                risks=[
                    ReportBullet.model_validate(item.model_dump())
                    for item in output.risks
                ],
                opportunities=[
                    ReportBullet.model_validate(item.model_dump())
                    for item in output.opportunities
                ],
                uncertainties=[
                    ReportBullet.model_validate(item.model_dump())
                    for item in output.uncertainties
                ],
                follow_up_questions=output.follow_up_questions,
            )
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenRouter synthesis failed") from error
