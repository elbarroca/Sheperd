from __future__ import annotations

import asyncio
from contextvars import ContextVar
from types import TracebackType

import httpx
import pytest
from pydantic import BaseModel

from sheperd_research.contracts import SourceCandidate
from sheperd_research.providers.errors import ProviderError
from sheperd_research.providers.openrouter import OpenRouterProvider
from sheperd_research.providers.tavily import TavilyProvider
from sheperd_research.settings import STRICT_OPENROUTER_MODEL


def _stub_provider() -> OpenRouterProvider:
    provider = object.__new__(OpenRouterProvider)
    provider.model_name = STRICT_OPENROUTER_MODEL
    provider.call_history = []
    provider.last_call_metadata = {}
    provider.timeout_seconds = 60
    provider.max_output_tokens = 3000
    provider.capability_manifest_hash = "manifest-1"
    provider._task_last_call_metadata = ContextVar(
        f"test_last_call_metadata_{id(provider)}",
        default=None,
    )
    provider._task_attempts = ContextVar(
        f"test_attempts_{id(provider)}",
        default=(),
    )
    return provider


class FakeAsyncClient:
    def __init__(self, outcomes: list[httpx.Response | BaseException]) -> None:
        self.outcomes = outcomes

    async def __aenter__(self) -> FakeAsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def post(self, *_: object, **__: object) -> httpx.Response:
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def response(status_code: int, payload: object) -> httpx.Response:
    return httpx.Response(
        status_code,
        json=payload,
        request=httpx.Request("POST", "https://api.tavily.com/test"),
    )


def patch_client(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[httpx.Response | BaseException],
) -> None:
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **_: FakeAsyncClient(outcomes),
    )


def test_tavily_rate_limit_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_client(monkeypatch, [response(429, {"error": "rate limit"})])

    with pytest.raises(ProviderError, match="rate limit"):
        asyncio.run(TavilyProvider("secret").search("ports"))


def test_tavily_retries_are_rejected_by_strict_policy() -> None:
    with pytest.raises(ProviderError, match="retries are disabled"):
        asyncio.run(TavilyProvider("secret", max_retries=1).search("ports"))


def test_tavily_malformed_search_and_extract_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_client(monkeypatch, [response(200, {"results": "invalid"})])
    with pytest.raises(ProviderError, match="invalid results"):
        asyncio.run(TavilyProvider("secret").search("ports"))

    patch_client(monkeypatch, [response(200, {"results": "invalid"})])
    with pytest.raises(ProviderError, match="invalid results"):
        asyncio.run(
            TavilyProvider("secret").extract(
                [SourceCandidate(url="https://example.com/article")]
            )
        )


def test_tavily_extract_chunks_batches_at_twenty_urls() -> None:
    calls: list[list[str]] = []

    class BatchingProvider(TavilyProvider):
        async def _post(self, endpoint: str, payload: dict[str, object]) -> dict[str, object]:
            assert endpoint == "extract"
            urls = payload["urls"]
            assert isinstance(urls, list)
            calls.append([str(url) for url in urls])
            return {"results": []}

    sources = [
        SourceCandidate(url=f"https://example.com/article-{index}")
        for index in range(21)
    ]

    with pytest.raises(ProviderError, match="incomplete content"):
        asyncio.run(BatchingProvider("secret").extract(sources))
    assert [len(batch) for batch in calls] == [20, 1]


class MalformedStructuredOutput:
    async def ainvoke(self, _: str) -> dict[str, object]:
        return {"summary": "missing required fields"}


class FakeModel:
    def with_structured_output(self, _: type[BaseModel]) -> MalformedStructuredOutput:
        return MalformedStructuredOutput()


def test_openrouter_malformed_structured_output_is_explicit() -> None:
    provider = _stub_provider()
    provider._model = FakeModel()

    with pytest.raises(ProviderError, match="distillation failed"):
        asyncio.run(
            provider.distill(
                SourceCandidate(url="https://example.com/article"),
                "source body",
            )
        )


class CapturedStructuredOutput:
    def __init__(self, result: dict[str, object]) -> None:
        self.result = result
        self.prompt = ""

    async def ainvoke(self, prompt: str) -> dict[str, object]:
        self.prompt = prompt
        return self.result


class CapturingModel:
    def __init__(self, output: CapturedStructuredOutput) -> None:
        self.output = output

    def with_structured_output(self, _: type[BaseModel]) -> CapturedStructuredOutput:
        return self.output


class RawResponse:
    response_metadata = {
        "model_name": STRICT_OPENROUTER_MODEL,
        "id": "request-1",
        "token_usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
    }


class StrictStructuredOutput:
    async def ainvoke(self, _: str) -> dict[str, object]:
        return {
            "raw": RawResponse(),
            "parsed": {
                "summary": "A source-bound summary.",
                "key_points": ["A reported point."],
                "claims": [],
                "limitations": [],
            },
            "parsing_error": None,
        }


class StrictCapturingModel:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def with_structured_output(
        self, _: type[BaseModel], **kwargs: object
    ) -> StrictStructuredOutput:
        self.kwargs = kwargs
        return StrictStructuredOutput()


def test_openrouter_uses_strict_schema_and_records_resolved_model() -> None:
    model = StrictCapturingModel()
    provider = _stub_provider()
    provider._model = model

    result = asyncio.run(
        provider.distill(
            SourceCandidate(url="https://example.com/article"),
            "source body",
            prompt_version="distill-test-v1",
        )
    )

    assert model.kwargs == {"method": "json_schema", "strict": True, "include_raw": True}
    assert result.model_id == STRICT_OPENROUTER_MODEL
    assert provider.last_call_metadata["request_id"] == "request-1"
    assert provider.last_call_metadata["total_tokens"] == 20


def test_openrouter_distillation_prompt_is_source_bound() -> None:
    source = SourceCandidate(url="https://example.com/article", is_seed=True)
    output = CapturedStructuredOutput(
        {
            "raw": RawResponse(),
            "parsed": {
                "summary": "A source-bound summary.",
                "key_points": ["A reported point."],
                "claims": [{"claim": "A reported point.", "source_urls": [source.url]}],
                "limitations": ["Public source only."],
            },
            "parsing_error": None,
        }
    )
    provider = _stub_provider()
    provider._model = CapturingModel(output)

    asyncio.run(provider.distill(source, "source body"))

    assert "User-provided seed links remain unverified" in output.prompt
    assert "source URL exactly as provided" in output.prompt
    assert "Do not provide legal advice" in output.prompt
