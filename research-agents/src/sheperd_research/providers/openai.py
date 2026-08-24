from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from contextvars import ContextVar
from datetime import UTC, datetime

from langchain.agents.structured_output import ProviderStrategy
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, SecretStr

from ..progress import ProgressSink
from .capabilities import CapabilityReport, ModelCapability
from .errors import ProviderError
from .openrouter import (
    OPENROUTER_TIMEOUT_SECONDS,
    OpenRouterProvider,
    OutputT,
)

DEFAULT_OPENAI_MODEL = "gpt-5.6-luna"
DEFAULT_OPENAI_MAX_CONCURRENT_REQUESTS = 2
OPENAI_TIMEOUT_SECONDS = OPENROUTER_TIMEOUT_SECONDS
OPENAI_MAX_OUTPUT_TOKENS = 6_000
_OPENAI_MODEL_PATTERN = re.compile(r"^(?:gpt|o\d|chatgpt)-[a-z0-9][a-z0-9._-]*$")


def is_openai_model(value: str) -> bool:
    return bool(_OPENAI_MODEL_PATTERN.fullmatch(value))


def _capability_report(model: str) -> CapabilityReport:
    capability = ModelCapability(
        model=model,
        free=False,
        supports_tools=True,
        supports_structured_outputs=True,
        name=model,
    )
    manifest_hash = hashlib.sha256(
        json.dumps(
            {
                "provider": "openai",
                "model": model,
                "tools": True,
                "structured_outputs": True,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return CapabilityReport(
        requested_models=(model,),
        eligible_models=(model,),
        capabilities=(capability,),
        skipped_models=(),
        require_tools=True,
        manifest_hash=manifest_hash,
        source="configured",
        checked_at=datetime.now(UTC),
    )


class OpenAIProvider(OpenRouterProvider):
    """OpenAI-backed implementation of the existing bounded agent workflow."""

    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_OPENAI_MODEL,
        *,
        fallback_models: Sequence[str] = (),
        capability_report: CapabilityReport | None = None,
        max_output_tokens: int = OPENAI_MAX_OUTPUT_TOKENS,
        timeout_seconds: int = OPENAI_TIMEOUT_SECONDS,
        max_concurrent_requests: int = DEFAULT_OPENAI_MAX_CONCURRENT_REQUESTS,
        allow_free_fallbacks: bool = False,
        progress: ProgressSink | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenAI API key is required")
        if model != DEFAULT_OPENAI_MODEL:
            raise ProviderError(f"OPENAI_MODEL must be {DEFAULT_OPENAI_MODEL}")
        if fallback_models:
            raise ProviderError("OpenAI provider does not support model fallbacks")
        if max_output_tokens < 1:
            raise ValueError("OpenAI output-token budget must be positive")
        if timeout_seconds < 1:
            raise ValueError("OpenAI timeout must be positive")
        if max_concurrent_requests < 1:
            raise ValueError("OpenAI concurrency must be positive")

        self.model_name = model
        self.model_chain = (model,)
        self.allow_free_fallbacks = False
        self.max_output_tokens = max_output_tokens
        report = capability_report or _capability_report(model)
        self.capability_report = report
        self.capability_manifest_hash = report.manifest_hash
        self.timeout_seconds = timeout_seconds
        self.max_concurrent_requests = max_concurrent_requests
        self._progress = progress
        self._rate_limit_seen = False
        self._agent_semaphore = None
        self._serial_request_lock = None
        self.last_call_metadata: dict[str, object] = {}
        self._api_key = SecretStr(api_key)
        self._models: dict[str, BaseChatModel] = {}
        self.call_history: list[dict[str, object]] = []
        self._task_last_call_metadata: ContextVar[dict[str, object] | None] = ContextVar(
            f"openai_last_call_metadata_{id(self)}",
            default=None,
        )
        self._task_attempts: ContextVar[tuple[dict[str, object], ...]] = ContextVar(
            f"openai_attempts_{id(self)}",
            default=(),
        )
        self._model = self._model_for(model)

    def _model_for(self, model: str) -> BaseChatModel:
        if model != self.model_name:
            raise ProviderError("OpenAI model is not the configured model")
        cached = self._models.get(model)
        if cached is not None:
            return cached
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as error:
            raise ProviderError("langchain-openai is not installed") from error
        created: BaseChatModel = ChatOpenAI(
            model=model,
            api_key=self._api_key,
            # GPT-5.6 Luna requires the Responses API when reasoning is used
            # together with function tools.
            use_responses_api=True,
            temperature=0,
            timeout=self.timeout_seconds,
            max_completion_tokens=self.max_output_tokens,
            reasoning_effort="medium",
            verbosity="high",
            max_retries=0,
        )
        self._models[model] = created
        return created

    def _structured_response_strategy(
        self, schema: type[OutputT]
    ) -> ProviderStrategy[OutputT]:
        return ProviderStrategy(
            self._strict_schema(schema),
            strict=True,
        )

    @staticmethod
    def _strict_schema(schema: type[BaseModel]) -> dict[str, object]:
        """Make Pydantic's nullable/default-compatible schema OpenAI-strict."""
        def normalize(value: object) -> object:
            if isinstance(value, dict):
                normalized = {
                    key: normalize(child)
                    for key, child in value.items()
                    if key not in {"default", "examples"}
                }
                properties = normalized.get("properties")
                if isinstance(properties, dict):
                    normalized["required"] = list(properties)
                    normalized["additionalProperties"] = False
                return normalized
            if isinstance(value, list):
                return [normalize(child) for child in value]
            return value

        normalized = normalize(schema.model_json_schema())
        if not isinstance(normalized, dict):
            raise TypeError("OpenAI structured schema must be an object")
        return normalized

    @staticmethod
    def _require_resolved_model(metadata: dict[str, object], requested_model: str) -> str:
        resolved_model = metadata.get("resolved_model")
        if not isinstance(resolved_model, str) or not resolved_model.strip():
            raise ProviderError("OpenAI response missing resolved model metadata")
        if resolved_model != requested_model and not resolved_model.startswith(
            f"{requested_model}-"
        ):
            raise ProviderError("OpenAI response resolved to an unexpected model")
        return resolved_model

    def _record_attempt(
        self,
        metadata: dict[str, object],
        attempt_sink: list[dict[str, object]] | None = None,
    ) -> None:
        metadata = {"provider": self.provider_name, **metadata}
        super()._record_attempt(metadata, attempt_sink)

    @classmethod
    def _should_retry(
        cls, error: BaseException, *, model_name: str, attempt: int
    ) -> bool:
        del model_name
        return attempt < 2 and cls._error_code(error) in {
            "timeout",
            "malformed_output",
            "missing_tool_call",
            "tool_failure",
        }
