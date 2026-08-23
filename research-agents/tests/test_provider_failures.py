from __future__ import annotations

import asyncio
from contextvars import ContextVar
from types import TracebackType

import httpx
import pytest
from pydantic import BaseModel

import sheperd_research.providers.openrouter as openrouter_module
from sheperd_research.contracts import SourceCandidate
from sheperd_research.providers.errors import ProviderError
from sheperd_research.providers.openrouter import BriefOutput, OpenRouterProvider
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


def valid_article_response(source_url: str) -> dict[str, object]:
    return {
        "summary": "A source-bound summary.",
        "key_points": ["A reported point.", "A second reported point."],
        "what_happened": "The source reports a public development.",
        "why_it_matters": "The development changes the operating picture.",
        "risk_assessment": {
            "status": "not_observed",
            "statement": "No supported material risk was observed in this source.",
            "why_it_matters": "The source does not establish a material risk.",
            "next_step": "Check an independent source for risk evidence.",
        },
        "opportunity_assessment": {
            "status": "not_observed",
            "statement": "No supported commercial opportunity was observed in this source.",
            "why_it_matters": "The source does not establish a commercial opportunity.",
            "next_step": "Check an independent source for opportunity evidence.",
        },
        "uncertainties": ["The source may not cover the full market."],
        "next_steps": ["Compare the report with an independent source."],
        "claims": [
            {"claim": "A reported point.", "source_urls": [source_url]},
        ],
        "limitations": ["Public source only."],
        "source_language": "en",
        "summary_original": "A source-bound summary.",
        "key_points_original": ["A reported point.", "A second reported point."],
        "evidence_excerpts": ["A reported point."],
        "evidence_locators": ["paragraph 1"],
    }


def test_tavily_rate_limit_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_client(monkeypatch, [response(429, {"error": "rate limit"})])

    with pytest.raises(ProviderError, match="rate limit") as raised:
        asyncio.run(TavilyProvider("secret").search("ports"))
    assert raised.value.error_code == "rate_limit"


@pytest.mark.parametrize(
    ("outcome", "error_code"),
    [
        (
            httpx.ReadTimeout(
                "timed out",
                request=httpx.Request("POST", "https://api.tavily.com/search"),
            ),
            "timeout",
        ),
        (
            httpx.ConnectError(
                "connection failed",
                request=httpx.Request("POST", "https://api.tavily.com/search"),
            ),
            "provider_unavailable",
        ),
        (response(503, {"error": "unavailable"}), "provider_unavailable"),
    ],
)
def test_tavily_transport_failures_have_stable_error_codes(
    monkeypatch: pytest.MonkeyPatch,
    outcome: httpx.Response | BaseException,
    error_code: str,
) -> None:
    patch_client(monkeypatch, [outcome])

    with pytest.raises(ProviderError) as raised:
        asyncio.run(TavilyProvider("secret").search("ports"))

    assert raised.value.error_code == error_code
    assert raised.value.attempts[0]["error_code"] == error_code


def test_tavily_malformed_response_shape_preserves_a_stable_error_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_client(monkeypatch, [response(200, [])])

    with pytest.raises(ProviderError, match="invalid response") as raised:
        asyncio.run(TavilyProvider("secret").search("ports"))

    assert raised.value.error_code == "malformed_output"
    assert raised.value.attempts[0]["error_code"] == "malformed_output"


def test_tavily_malformed_nested_result_entries_are_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_client(monkeypatch, [response(200, {"results": [{"title": "Missing URL"}]})])
    with pytest.raises(ProviderError, match="invalid result") as raised:
        asyncio.run(TavilyProvider("secret").search("ports"))
    assert raised.value.error_code == "malformed_output"

    patch_client(monkeypatch, [response(200, {"results": [{"url": "https://example.com/article"}]})])
    with pytest.raises(ProviderError, match="invalid result") as extract_raised:
        asyncio.run(
            TavilyProvider("secret").extract(
                [SourceCandidate(url="https://example.com/article")]
            )
        )
    assert extract_raised.value.error_code == "malformed_output"


def test_tavily_rotates_to_secondary_key_after_primary_quota_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_headers: list[object] = []

    class CapturingClient(FakeAsyncClient):
        async def post(self, url: object, **kwargs: object) -> httpx.Response:
            captured_headers.append(kwargs.get("headers"))
            return await super().post(url, **kwargs)

    outcomes = [
        response(432, {"detail": "blocked"}),
        response(
            200,
            {
                "results": [
                    {
                        "url": "https://example.com/article",
                        "title": "Example",
                        "content": "A public source",
                    }
                ]
            },
        ),
    ]
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: CapturingClient(outcomes))

    provider = TavilyProvider(
        "primary-secret",
        secondary_api_key="secondary-secret",
    )
    results = asyncio.run(provider.search("ports"))

    assert len(results) == 1
    assert captured_headers == [
        {"Authorization": "Bearer primary-secret"},
        {"Authorization": "Bearer secondary-secret"},
    ]
    assert [attempt["key_slot"] for attempt in provider.call_history] == [1, 2]
    assert provider.call_history[0]["status"] == "failed"
    assert provider.call_history[0]["error_code"] == "plan_usage_limit"
    assert provider.call_history[1]["status"] == "succeeded"
    assert all("secret" not in str(attempt) for attempt in provider.call_history)


def test_tavily_does_not_rotate_for_malformed_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_headers: list[object] = []

    class CapturingClient(FakeAsyncClient):
        async def post(self, url: object, **kwargs: object) -> httpx.Response:
            captured_headers.append(kwargs.get("headers"))
            return await super().post(url, **kwargs)

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **_: CapturingClient([response(200, {"results": "invalid"})]),
    )

    provider = TavilyProvider(
        "primary-secret",
        secondary_api_key="secondary-secret",
    )
    with pytest.raises(ProviderError, match="invalid results"):
        asyncio.run(provider.search("ports"))

    assert captured_headers == [{"Authorization": "Bearer primary-secret"}]
    assert len(provider.call_history) == 1
    assert provider.call_history[0]["key_slot"] == 1


def test_tavily_records_both_failed_key_slots_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_client(
        monkeypatch,
        [response(432, {"detail": "blocked"}), response(429, {"detail": "limited"})],
    )
    provider = TavilyProvider(
        "primary-secret",
        secondary_api_key="secondary-secret",
    )

    with pytest.raises(ProviderError, match="plan usage limit") as raised:
        asyncio.run(provider.search("ports"))

    assert len(raised.value.attempts) == 2
    assert [attempt["key_slot"] for attempt in raised.value.attempts] == [1, 2]
    assert all(
        secret not in str(raised.value.attempts)
        for secret in ("primary-secret", "secondary-secret")
    )


@pytest.mark.parametrize(
    ("status_code", "message", "error_code"),
    [
        (432, "plan usage limit", "plan_usage_limit"),
        (433, "pay-as-you-go limit", "payg_limit"),
    ],
)
def test_tavily_usage_limits_are_explicit(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    message: str,
    error_code: str,
) -> None:
    patch_client(monkeypatch, [response(status_code, {"detail": "blocked"})])

    with pytest.raises(ProviderError, match=message) as raised:
        asyncio.run(TavilyProvider("secret").search("ports"))
    assert raised.value.error_code == error_code


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


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {"results": [{"url": "https://example.com/article", "raw_content": "   "}]},
            "blank content",
        ),
        (
            {"results": [{"url": "https://example.com/other", "raw_content": "body"}]},
            "unrequested URL",
        ),
    ],
)
def test_tavily_malformed_extract_result_content_is_explicit(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    message: str,
) -> None:
    patch_client(monkeypatch, [response(200, payload)])

    with pytest.raises(ProviderError, match=message) as raised:
        asyncio.run(
            TavilyProvider("secret").extract(
                [SourceCandidate(url="https://example.com/article")]
            )
        )

    assert raised.value.error_code == "malformed_output"


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


def test_tavily_search_uses_basic_depth_for_discovery_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class CapturingClient(FakeAsyncClient):
        async def post(self, url: object, **kwargs: object) -> httpx.Response:
            captured["url"] = url
            captured["headers"] = kwargs.get("headers")
            captured["json"] = kwargs.get("json")
            return response(200, {"results": []})

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **_: CapturingClient([]),
    )

    asyncio.run(
        TavilyProvider("secret", project_id="project-1").search(
            "ports",
            include_domains=["fmc.gov"],
            exclude_domains=["linkedin.com"],
        )
    )

    assert captured["url"] == "https://api.tavily.com/search"
    assert captured["headers"] == {
        "Authorization": "Bearer secret",
        "X-Project-ID": "project-1",
    }
    assert captured["json"] == {
        "query": "ports",
        "search_depth": "basic",
        "max_results": 5,
        "include_answer": False,
        "include_raw_content": False,
        "include_domains": ["fmc.gov"],
        "exclude_domains": ["linkedin.com"],
    }


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


def test_synthesis_schema_rejects_bullets_without_why_or_next_step() -> None:
    with pytest.raises(ValueError):
        BriefOutput(
            title="Weekly",
            summary="Cited summary.",
            executive_bullets=[
                {
                    "text": "A source-backed development.",
                    "source_urls": ["https://example.com/article"],
                    "evidence_status": "unverified",
                }
            ],
        )


class RawResponse:
    response_metadata = {
        "model_name": STRICT_OPENROUTER_MODEL,
        "id": "request-1",
        "token_usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
    }


class CapturingAgent:
    def __init__(self, result: dict[str, object]) -> None:
        self.result = result
        self.prompt = ""

    async def ainvoke(self, payload: dict[str, object], **_: object) -> dict[str, object]:
        messages = payload["messages"]
        assert isinstance(messages, list)
        message = messages[0]
        assert isinstance(message, dict)
        self.prompt = str(message["content"])
        return self.result


def test_openrouter_uses_create_agent_schema_and_records_resolved_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: dict[str, object] = {}
    agent = CapturingAgent(
        {
            "structured_response": {
                **valid_article_response("https://example.com/article"),
            },
            "messages": [RawResponse()],
        }
    )
    provider = _stub_provider()
    provider._model_for = lambda _: object()
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda **kwargs: created.update(kwargs) or agent,
    )

    result = asyncio.run(
        provider.distill(
            SourceCandidate(url="https://example.com/article"),
            "source body",
            prompt_version="distill-test-v1",
        )
    )

    assert type(created["response_format"]).__name__ == "ToolStrategy"
    assert created["name"] == "source_distillation_agent"
    assert result.model_id == STRICT_OPENROUTER_MODEL
    assert provider.last_call_metadata["request_id"] == "request-1"
    assert provider.last_call_metadata["total_tokens"] == 20


def test_malformed_distillation_retries_with_a_corrective_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[str] = []
    source_url = "https://example.com/article"
    outcomes: list[dict[str, object]] = [
        {
            "structured_response": {"summary": "incomplete"},
            "messages": [RawResponse()],
        },
        {
            "structured_response": valid_article_response(source_url),
            "messages": [RawResponse()],
        },
    ]

    class SequenceAgent:
        async def ainvoke(
            self,
            payload: dict[str, object],
            **_: object,
        ) -> dict[str, object]:
            messages = payload["messages"]
            assert isinstance(messages, list)
            prompts.append(str(messages[0]))
            return outcomes.pop(0)

    provider = _stub_provider()
    provider._model_for = lambda _: object()
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: SequenceAgent())

    result = asyncio.run(
        provider.distill(SourceCandidate(url=source_url), "source body")
    )

    assert result.quality_status.value == "complete"
    assert len(prompts) == 2
    assert "CORRECTIVE RETRY" in prompts[1]
    assert [item["attempt"] for item in provider.call_history] == [1, 2]


def test_semantic_article_quality_failure_retries_with_a_corrective_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts: list[str] = []
    source_url = "https://example.com/article"
    malformed_article = {
        **valid_article_response(source_url),
        "claims": [{"claim": "unknown", "source_urls": [source_url]}],
        "evidence_excerpts": ["tbd"],
        "evidence_locators": ["unknown"],
    }
    outcomes: list[dict[str, object]] = [
        {
            "structured_response": malformed_article,
            "messages": [RawResponse()],
        },
        {
            "structured_response": valid_article_response(source_url),
            "messages": [RawResponse()],
        },
    ]

    class SequenceAgent:
        async def ainvoke(
            self,
            payload: dict[str, object],
            **_: object,
        ) -> dict[str, object]:
            messages = payload["messages"]
            assert isinstance(messages, list)
            prompts.append(str(messages[0]))
            return outcomes.pop(0)

    provider = _stub_provider()
    provider._model_for = lambda _: object()
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: SequenceAgent())

    result = asyncio.run(
        provider.distill(SourceCandidate(url=source_url), "source body")
    )

    assert result.quality_status.value == "complete"
    assert len(prompts) == 2
    assert "CORRECTIVE RETRY" in prompts[1]
    assert [item["attempt"] for item in provider.call_history] == [1, 2]
    assert provider.call_history[0]["error_code"] == "malformed_output"


def test_openrouter_distillation_prompt_is_source_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = SourceCandidate(url="https://example.com/article", is_seed=True)
    agent = CapturingAgent(
        {
            "structured_response": {
                **valid_article_response(source.url),
            },
            "messages": [RawResponse()],
        }
    )
    provider = _stub_provider()
    provider._model_for = lambda _: object()
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: agent)

    asyncio.run(provider.distill(source, "source body"))

    assert "User-provided seed links remain unverified" in agent.prompt
    assert "source URL exactly as provided" in agent.prompt
    assert "Do not provide legal advice" in agent.prompt
