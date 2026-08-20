from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Sequence
from contextvars import ContextVar
from datetime import datetime
from time import monotonic
from typing import Protocol, TypeVar, cast

import httpx
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy, ToolStrategy
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from ..contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    ReportBullet,
    SourceCandidate,
    WeeklyBrief,
    is_free_model,
)
from ..settings import STRICT_OPENROUTER_MODEL, strict_openrouter_policy_error
from ..validators import can_extract_url, normalize_url
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
MAX_DISCOVERY_TOOL_CALLS = 6
MAX_DISCOVERY_RECURSION = 12
NATIVE_STRUCTURED_MODELS = frozenset(
    {
        "google/gemma-4-26b-a4b-it:free",
        "dots-studio/dots-3-note-preview:free",
        "openai/gpt-oss-20b:free",
        "z-ai/glm-5.2:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
    }
)
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

    summary: str = Field(max_length=700)
    key_points: list[str] = Field(max_length=4)
    entities: list[str] = Field(default_factory=list, max_length=12)
    signals: list[str] = Field(default_factory=list, max_length=8)
    claims: list[ClaimDraft] = Field(max_length=3)
    limitations: list[str] = Field(max_length=3)


class BriefOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(max_length=160)
    summary: str = Field(max_length=1_200)
    signal_event_ids: list[str] = Field(default_factory=list, max_length=100)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    evidence_status: EvidenceStatus = EvidenceStatus.MIXED
    executive_bullets: list[ReportBullet] = Field(default_factory=list, max_length=6)
    developments: list[ReportBullet] = Field(default_factory=list, max_length=12)
    risks: list[ReportBullet] = Field(default_factory=list, max_length=8)
    opportunities: list[ReportBullet] = Field(default_factory=list, max_length=8)
    uncertainties: list[ReportBullet] = Field(default_factory=list, max_length=8)
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
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenRouter API key is required")
        policy_error = strict_openrouter_policy_error(
            model,
            (),
            raw_fallback_config=fallback_models,
        )
        if policy_error is not None:
            raise ProviderError(policy_error)
        if capability_report is None or capability_report.source != "live":
            raise ProviderError("OpenRouter provider requires a live capability report")
        if not capability_report.require_tools:
            raise ProviderError("OpenRouter capability report must prove tool support")
        if capability_report.requested_models != (STRICT_OPENROUTER_MODEL,):
            raise ProviderError("OpenRouter capability report must target the strict Gemma model")
        if capability_report.eligible_models != (STRICT_OPENROUTER_MODEL,):
            raise ProviderError("configured strict model failed capability checks")
        capability_evidence = capability_report.evidence_for(STRICT_OPENROUTER_MODEL)
        if capability_evidence is None:
            raise ProviderError("OpenRouter capability report is missing Gemma evidence")
        if (
            not capability_evidence.free
            or not capability_evidence.supports_tools
            or not capability_evidence.supports_structured_outputs
            or capability_evidence.reason is not None
        ):
            raise ProviderError("configured strict model failed capability checks")
        configured_chain = (model,)
        if any(not is_free_model(candidate) for candidate in configured_chain):
            raise ProviderError(f"OpenRouter model must be {STRICT_OPENROUTER_MODEL}")
        if max_output_tokens < 1:
            raise ValueError("OpenRouter output-token budget must be positive")
        if timeout_seconds < 1:
            raise ValueError("OpenRouter timeout must be positive")
        if max_concurrent_requests < 1:
            raise ValueError("OpenRouter concurrency must be positive")
        self.model_name = model
        self.model_chain = (STRICT_OPENROUTER_MODEL,)
        self.max_output_tokens = max_output_tokens
        self.capability_manifest_hash = capability_report.manifest_hash
        self.capability_report = capability_report
        self.timeout_seconds = timeout_seconds
        self.max_concurrent_requests = max_concurrent_requests
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
        message = f"{type(error).__name__} {error}".lower()
        if (
            "429" in message
            or "rate limit" in message
            or "rate_limit" in message
            or "too many requests" in message
            or "toomanyrequests" in message
        ):
            return "rate_limit"
        if OpenRouterProvider._is_transport_timeout(error):
            return "timeout"
        if "unsupported" in message or "not implemented" in message:
            return "unsupported_capability"
        if "malformed" in message or "validation" in message or "json" in message:
            return "malformed_output"
        if "required tool" in message or "missing tool" in message:
            return "missing_tool_call"
        if any(code in message for code in ("408", "409", "500", "502", "503", "504")):
            return "provider_unavailable"
        return "provider_error"

    @classmethod
    def _should_retry(cls, error: BaseException, *, model_name: str, attempt: int) -> bool:
        return (
            model_name == STRICT_OPENROUTER_MODEL
            and attempt < 2
            and cls._is_transport_timeout(error)
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
    def _require_strict_resolved_model(metadata: dict[str, object]) -> str:
        resolved_model = metadata.get("resolved_model")
        if not isinstance(resolved_model, str) or not resolved_model.strip():
            raise ProviderError("OpenRouter response missing resolved model metadata")
        if resolved_model != STRICT_OPENROUTER_MODEL:
            raise ProviderError(
                f"OpenRouter resolved model must be {STRICT_OPENROUTER_MODEL}"
            )
        return resolved_model

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

        if not isinstance(result, dict):
            return []
        messages = result.get("messages")
        if not isinstance(messages, list):
            return []

        receipts: list[dict[str, object]] = []
        by_call_id: dict[str, dict[str, object]] = {}
        for message in messages:
            raw_calls = getattr(message, "tool_calls", [])
            if not isinstance(raw_calls, list):
                continue
            for raw_call in raw_calls:
                if not isinstance(raw_call, dict):
                    continue
                call_id = str(raw_call.get("id") or f"call-{len(receipts) + 1}")
                name = str(raw_call.get("name") or "unknown")
                arguments = raw_call.get("args")
                if not isinstance(arguments, dict):
                    arguments = {}
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
            if (
                not isinstance(tool_message_call_id, str)
                or tool_message_call_id not in by_call_id
            ):
                continue
            receipt = by_call_id[tool_message_call_id]
            content = getattr(message, "content", "")
            content_text = (
                content if isinstance(content, str) else json.dumps(content, default=str)
            )
            receipt["result_hash"] = hashlib.sha256(content_text.encode()).hexdigest()
            receipt["status"] = (
                "failed" if getattr(message, "status", None) == "error" else "succeeded"
            )
            try:
                parsed = json.loads(content_text)
            except (TypeError, json.JSONDecodeError):
                parsed = None
            if isinstance(parsed, dict):
                if isinstance(parsed.get("sources"), list):
                    receipt["result_count"] = len(parsed["sources"])
                elif isinstance(parsed.get("extracted_urls"), list):
                    receipt["result_count"] = len(parsed["extracted_urls"])
                elif parsed.get("error"):
                    receipt["status"] = "failed"
        return receipts

    async def _invoke_legacy_structured(
        self,
        schema: type[OutputT],
        prompt: str,
        *,
        prompt_version: str,
        operation: str,
    ) -> OutputT:
        last_error: BaseException | None = None
        for attempt in range(1, 3):
            started_at = monotonic()
            try:
                try:
                    runnable = self._model.with_structured_output(
                        schema,
                        method="json_schema",
                        strict=True,
                        include_raw=True,
                    )
                except TypeError as error:
                    if "unexpected keyword" not in str(error).lower():
                        raise
                    runnable = self._model.with_structured_output(schema)
                result = await runnable.ainvoke(prompt)
                raw: object = result
                parsed: object = result
                if isinstance(result, dict) and "parsed" in result:
                    raw = result.get("raw")
                    parsed = result.get("parsed")
                    if result.get("parsing_error") is not None or parsed is None:
                        raise ValueError("malformed output")
                output = schema.model_validate(parsed)
                metadata = self._metadata_from_raw(raw)
                resolved_model = self._require_strict_resolved_model(metadata)
                metadata.update(
                    {
                        "requested_model": getattr(self, "model_name", STRICT_OPENROUTER_MODEL),
                        "resolved_model": resolved_model,
                        "prompt_version": prompt_version,
                        "operation": operation,
                        "attempt": attempt,
                        "latency_ms": max(0, int((monotonic() - started_at) * 1000)),
                        "error_code": None,
                        "output_hash": self._output_hash(output),
                        "capability_manifest_hash": getattr(
                            self, "capability_manifest_hash", None
                        ),
                    }
                )
                self._record_attempt(metadata)
                return output
            except Exception as error:
                last_error = error
                metadata = {
                    "requested_model": getattr(self, "model_name", STRICT_OPENROUTER_MODEL),
                    "resolved_model": None,
                    "prompt_version": prompt_version,
                    "operation": operation,
                    "attempt": attempt,
                    "latency_ms": max(0, int((monotonic() - started_at) * 1000)),
                    "error_code": self._error_code(error),
                    "error_type": type(error).__name__,
                    "output_hash": None,
                    "capability_manifest_hash": getattr(
                        self, "capability_manifest_hash", None
                    ),
                }
                self._record_attempt(metadata)
                if self._should_retry(
                    error,
                    model_name=getattr(self, "model_name", STRICT_OPENROUTER_MODEL),
                    attempt=attempt,
                ):
                    await asyncio.sleep(0.2)
                    continue
                if isinstance(error, ValueError) or not isinstance(error, ProviderError):
                    raise ProviderError(f"OpenRouter {operation} failed") from error
                raise
        raise ProviderError(f"OpenRouter {operation} failed") from last_error

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
    ) -> OutputT:
        last_error: BaseException | None = None
        model_name = self.model_chain[0]
        for attempt in range(1, 3):
            started_at = monotonic()
            tool_receipts: list[dict[str, object]] = []
            try:
                strategy = (
                    ToolStrategy(schema, handle_errors=False)
                    if tools
                    else (
                        ProviderStrategy(schema)
                        if model_name in NATIVE_STRUCTURED_MODELS
                        else ToolStrategy(schema, handle_errors=False)
                    )
                )
                agent = create_agent(
                    model=self._model_for(model_name),
                    tools=list(tools),
                    system_prompt=(
                        "Return only the requested structured response. "
                        "Do not reveal reasoning or add unsupported facts."
                    ),
                    response_format=strategy,
                )
                result = await self._invoke_agent_request(
                    agent,
                    {
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                all_receipts = self._tool_call_receipts(result)
                tool_names = {tool.name for tool in tools}
                tool_receipts = [
                    receipt
                    for receipt in all_receipts
                    if receipt.get("tool_name") in tool_names
                ]
                if tool_latency_by_input is not None:
                    for receipt in tool_receipts:
                        input_hash = receipt.get("input_hash")
                        if isinstance(input_hash, str) and input_hash in tool_latency_by_input:
                            receipt["latency_ms"] = tool_latency_by_input[input_hash]
                called_tools = {
                    str(receipt["tool_name"])
                    for receipt in tool_receipts
                    if receipt.get("status") != "failed"
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
                resolved_model = self._require_strict_resolved_model(metadata)
                metadata.update(
                    {
                        "requested_model": model_name,
                        "resolved_model": resolved_model,
                        "prompt_version": prompt_version,
                        "operation": operation,
                        "attempt": attempt,
                        "model_index": 0,
                        "fallback_reason": None,
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
                metadata = {
                    "requested_model": model_name,
                    "resolved_model": None,
                    "prompt_version": prompt_version,
                    "operation": operation,
                    "attempt": attempt,
                    "model_index": 0,
                    "fallback_reason": None,
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
                self._record_attempt(metadata, attempt_sink)
                if error_code == "rate_limit":
                    self._rate_limit_seen = True
                if self._should_retry(error, model_name=model_name, attempt=attempt):
                    await asyncio.sleep(0.2)
                    continue
                raise ProviderError(f"OpenRouter {operation} failed") from error
        raise ProviderError(f"OpenRouter {operation} failed") from last_error

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
    ) -> OutputT:
        if not hasattr(self, "model_chain"):
            return await self._invoke_legacy_structured(
                schema,
                prompt,
                prompt_version=prompt_version,
                operation=operation,
            )
        return await self._invoke_agent(
            schema,
            prompt,
            prompt_version=prompt_version,
            operation=operation,
            tools=tools,
            required_tools=required_tools,
            attempt_sink=attempt_sink,
            tool_latency_by_input=tool_latency_by_input,
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
        tool_errors: list[str] = []
        tool_latency_by_input: dict[str, int] = {}
        attempt_sink: list[dict[str, object]] = []
        self._reset_task_call_state()

        def discovery_error(message: str) -> ProviderError:
            return ProviderError(message, attempts=list(attempt_sink))

        async def run_search(query: str) -> str:
            if query not in queries:
                raise ValueError("discovery query is outside the configured lane scope")
            if query in search_calls:
                tool_latency_by_input.setdefault(self._tool_input_hash(query, ()), 0)
                return json.dumps({"query": query, "reused": True})
            if len(search_calls) >= len(queries):
                raise ValueError("discovery search-call budget exceeded")
            search_calls.add(query)
            input_hash = self._tool_input_hash(query, ())
            started = monotonic()
            try:
                found = await tavily.search(
                    query,
                    since=since,
                    until=until,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    max_results=min(max(1, max_results), MAX_DISCOVERY_SOURCES),
                )
            except Exception as error:
                tool_errors.append(error.__class__.__name__)
                raise
            finally:
                tool_latency_by_input[input_hash] = max(
                    0, int((monotonic() - started) * 1000)
                )
            for source in found:
                if can_extract_url(source.url):
                    known_sources.setdefault(normalize_url(source.url), source)
            return json.dumps(
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
                        for source in found[:MAX_DISCOVERY_SOURCES]
                        if can_extract_url(source.url)
                    ],
                }
            )

        async def run_extract(urls: list[str]) -> str:
            normalized = [normalize_url(url) for url in urls]
            if any(url not in known_sources for url in normalized):
                raise ValueError("extraction URL was not returned by Tavily Search")
            input_hash = self._tool_input_hash(None, normalized)
            started = monotonic()
            try:
                extracted = await tavily.extract(
                    [known_sources[url] for url in normalized[:MAX_DISCOVERY_SOURCES]]
                )
            except Exception as error:
                tool_errors.append(error.__class__.__name__)
                raise
            finally:
                tool_latency_by_input[input_hash] = max(
                    0, int((monotonic() - started) * 1000)
                )
            for url, content in extracted.items():
                if content.strip():
                    captured_content[normalize_url(url)] = content.strip()
            return json.dumps(
                {
                    "extracted_urls": sorted(captured_content),
                    "extracted_count": len(captured_content),
                }
            )

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
                prompt_version="discovery-v2",
                operation=f"discovery:{lane}",
                tools=tools,
                required_tools=("tavily_search", "tavily_extract"),
                attempt_sink=attempt_sink,
                tool_latency_by_input=tool_latency_by_input,
            )
        except ProviderError as error:
            error.attempts = list(attempt_sink)
            raise
        known_urls = set(known_sources)
        missing_queries = sorted(set(queries) - search_calls)
        if missing_queries:
            raise discovery_error(
                "discovery agent skipped configured query families: "
                + ", ".join(missing_queries)
            )
        if not captured_content:
            raise discovery_error("discovery agent did not extract any source content")
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
            "extracted_count": len(content),
            "tool_errors": tool_errors,
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
            return self._require_strict_resolved_model(metadata)
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenRouter health check failed") from error

    async def distill(
        self,
        source: SourceCandidate,
        content: str,
        *,
        prompt_version: str = "distill-v4",
    ) -> ArticleDistillation:
        self._reset_task_call_state()
        prompt = (
            "You are an evidence distiller for maritime and D&D intelligence. "
            "Use only the supplied public source; do not use outside knowledge. "
            "User-provided seed links remain unverified until independently supported. "
            "Do not provide legal advice. Return only the requested structured fields.\n\n"
            "Rules: keep the summary concise; return no more than three short "
            "key_points, entities, signals, three claims, and three limitations; "
            "include limitations and access gaps; mark unsupported or inferred claims "
            "unverified; use the source URL exactly as provided for every citation; "
            "never invent a citation, date, number, entity, or event.\n\n"
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
            return ArticleDistillation(
                source_url=source.url,
                summary=output.summary,
                key_points=output.key_points[:MAX_KEY_POINTS_PER_SOURCE],
                entities=output.entities,
                signals=output.signals,
                claims=output.claims[:MAX_CLAIMS_PER_SOURCE],
                limitations=output.limitations,
                published_at=source.published_at,
                model_id=self._require_strict_resolved_model(metadata),
                prompt_version=prompt_version,
            )
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
        prompt_version: str = "weekly-brief-v4",
    ) -> WeeklyBrief:
        self._reset_task_call_state()
        evidence = "\n\n".join(
            f"URL: {item.source_url}\nSUMMARY: {item.summary}\nCLAIMS: "
            f"{[claim.claim for claim in item.claims]}"
            for item in distillations
        )
        prompt = (
            "Create a concise weekly maritime intelligence brief using only the "
            "source-bound evidence below. Write an executive summary suitable for "
            "a dashboard: short bullets first, then material developments, risks, "
            "opportunities, uncertainty, and follow-up questions. Separate facts "
            "from inference and limitations. Do not provide legal advice. Preserve "
            "source-linked signal IDs and never invent citations. Every factual "
            "bullet must cite one or more supplied URLs. Return structured fields.\n\n"
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
                model_id=self._require_strict_resolved_model(metadata),
                prompt_version=prompt_version,
                executive_bullets=output.executive_bullets,
                developments=output.developments,
                risks=output.risks,
                opportunities=output.opportunities,
                uncertainties=output.uncertainties,
                follow_up_questions=output.follow_up_questions,
            )
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("OpenRouter synthesis failed") from error
