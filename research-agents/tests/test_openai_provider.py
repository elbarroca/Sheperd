from __future__ import annotations

import pytest

from sheperd_research.providers.errors import ProviderError
from sheperd_research.providers.openai import (
    DEFAULT_OPENAI_MODEL,
    OpenAIProvider,
    is_openai_model,
)


def test_openai_model_policy_accepts_openai_ids_only() -> None:
    assert is_openai_model(DEFAULT_OPENAI_MODEL)
    assert not is_openai_model("openrouter/free")
    assert not is_openai_model("google/gemma-4-26b-a4b-it:free")


def test_openai_provider_requires_luna() -> None:
    with pytest.raises(ProviderError, match="gpt-5.6-luna"):
        OpenAIProvider("test-key", model="gpt-5.4-nano")


def test_openai_provider_constructs_chat_openai_without_network() -> None:
    provider = OpenAIProvider("test-key")

    assert provider.provider_name == "openai"
    assert provider.model_chain == (DEFAULT_OPENAI_MODEL,)
    assert provider.capability_report.source == "configured"
    assert provider.capability_report.eligible_models == (DEFAULT_OPENAI_MODEL,)
    assert provider._model.__class__.__name__ == "ChatOpenAI"
    assert provider._model.model_name == DEFAULT_OPENAI_MODEL
    assert provider._model.use_responses_api is True
    assert provider._model.max_tokens == provider.max_output_tokens
    assert provider.max_concurrent_requests == 2


def test_openai_provider_rejects_model_fallbacks() -> None:
    with pytest.raises(ProviderError, match="does not support model fallbacks"):
        OpenAIProvider("test-key", fallback_models=(DEFAULT_OPENAI_MODEL,))


def test_openai_provider_retries_malformed_output_once() -> None:
    error = ValueError("malformed structured output")

    assert OpenAIProvider._should_retry(error, model_name=DEFAULT_OPENAI_MODEL, attempt=1)
    assert not OpenAIProvider._should_retry(
        error, model_name=DEFAULT_OPENAI_MODEL, attempt=2
    )


def test_openai_provider_retries_incomplete_tool_contract_once() -> None:
    error = ProviderError(
        "required tool call missing: tavily_extract",
        error_code="missing_tool_call",
    )

    assert OpenAIProvider._should_retry(
        error, model_name=DEFAULT_OPENAI_MODEL, attempt=1
    )
    assert not OpenAIProvider._should_retry(
        error, model_name=DEFAULT_OPENAI_MODEL, attempt=2
    )


def test_openai_provider_classifies_tool_scope_value_errors() -> None:
    assert OpenAIProvider._error_code(
        ValueError("Tavily search returned no sources inside the configured policy")
    ) == "tool_failure"
