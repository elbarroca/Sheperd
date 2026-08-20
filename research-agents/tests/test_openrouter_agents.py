from __future__ import annotations

import asyncio
import json
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

import sheperd_research.providers.openrouter as openrouter_module
from sheperd_research.contracts import SourceCandidate
from sheperd_research.providers.capabilities import CapabilityReport
from sheperd_research.providers.errors import ProviderError
from sheperd_research.providers.openrouter import OpenRouterProvider
from sheperd_research.settings import STRICT_OPENROUTER_MODEL


def _live_capability_report() -> CapabilityReport:
    return CapabilityReport(
        requested_models=(STRICT_OPENROUTER_MODEL,),
        eligible_models=(STRICT_OPENROUTER_MODEL,),
        skipped_models=(),
        manifest_hash="manifest-1",
        source="live",
        checked_at=datetime(2026, 8, 20, tzinfo=UTC),
    )


def _stub_provider() -> OpenRouterProvider:
    provider = object.__new__(OpenRouterProvider)
    provider.model_name = STRICT_OPENROUTER_MODEL
    provider.model_chain = (STRICT_OPENROUTER_MODEL,)
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


class RateLimitedAgent:
    async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
        raise ProviderError("429 rate limit")


class TimeoutThenSuccessAgent:
    def __init__(self) -> None:
        self.calls = 0

    async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("timeout")
        return {
            "structured_response": {"ok": True},
            "messages": [
                SimpleNamespace(
                    response_metadata={
                        "model_name": STRICT_OPENROUTER_MODEL,
                        "id": "request-2",
                        "token_usage": {
                            "prompt_tokens": 10,
                            "completion_tokens": 4,
                            "total_tokens": 14,
                        },
                    },
                    usage_metadata={},
                    tool_calls=[],
                )
            ],
        }


def test_rate_limit_fails_without_retry_or_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, model, **__: RateLimitedAgent(),
    )

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(provider.health_check())

    assert [item["requested_model"] for item in provider.call_history] == [
        STRICT_OPENROUTER_MODEL
    ]
    assert provider.call_history[0]["error_code"] == "rate_limit"


def test_timeout_retry_records_two_attempts_for_gemma_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    provider._model_for = lambda model: model
    agent = TimeoutThenSuccessAgent()

    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(openrouter_module.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, model, **__: agent,
    )

    result = asyncio.run(provider.health_check())

    assert result == STRICT_OPENROUTER_MODEL
    assert [item["attempt"] for item in provider.call_history] == [1, 2]
    assert [item["requested_model"] for item in provider.call_history] == [
        STRICT_OPENROUTER_MODEL,
        STRICT_OPENROUTER_MODEL,
    ]
    assert provider.call_history[-1]["request_id"] == "request-2"
    assert provider.call_history[-1]["total_tokens"] == 14


def test_paid_fallback_is_rejected() -> None:
    with pytest.raises(ProviderError, match="FALLBACK_MODELS must be empty"):
        OpenRouterProvider(
            "secret",
            STRICT_OPENROUTER_MODEL,
            fallback_models=("openai/gpt-4o",),
            capability_report=_live_capability_report(),
        )


def test_openrouter_provider_disables_openrouter_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: dict[str, object] = {}

    class FakeChatOpenRouter:
        def __init__(self, **kwargs: object) -> None:
            created.update(kwargs)

    monkeypatch.setitem(
        sys.modules,
        "langchain_openrouter",
        SimpleNamespace(ChatOpenRouter=FakeChatOpenRouter),
    )

    OpenRouterProvider(
        "secret",
        STRICT_OPENROUTER_MODEL,
        capability_report=_live_capability_report(),
    )

    assert created["openrouter_provider"] == {
        "require_parameters": True,
        "allow_fallbacks": False,
    }


def test_openrouter_provider_requires_live_capability_report() -> None:
    with pytest.raises(ProviderError, match="live capability report"):
        OpenRouterProvider("secret", STRICT_OPENROUTER_MODEL)


def test_too_many_requests_is_recorded_as_rate_limit() -> None:
    class TooManyRequestsResponseError(RuntimeError):
        pass

    assert OpenRouterProvider._error_code(TooManyRequestsResponseError()) == "rate_limit"


def test_discovery_requires_model_issued_tavily_tool_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TavilyStub:
        searches = 0
        extractions = 0

        async def search(self, query: str, **_: object) -> list[SourceCandidate]:
            self.searches += 1
            return [
                SourceCandidate(
                    url="https://www.fmc.gov/example-agent-source",
                    title="FMC fixture",
                    publisher="fmc.gov",
                    published_at=datetime(2026, 8, 19, tzinfo=UTC),
                    snippet=query,
                )
            ]

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            self.extractions += 1
            return {source.url: "Public evidence fixture." for source in sources}

    class DiscoveryAgent:
        def __init__(self, tools: list[object]) -> None:
            self.tools = {vars(tool)["name"]: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            query = "latest FMC enforcement"
            search_call = {
                "id": "search-1",
                "name": "tavily_search",
                "args": {"query": query},
            }
            search_result = await self.tools["tavily_search"].ainvoke({"query": query})
            urls = json.loads(search_result)["sources"]
            extract_call = {
                "id": "extract-1",
                "name": "tavily_extract",
                "args": {"urls": [item["url"] for item in urls]},
            }
            extract_result = await self.tools["tavily_extract"].ainvoke(
                extract_call["args"]
            )
            return {
                "structured_response": {
                    "source_urls": ["https://www.fmc.gov/example-agent-source"],
                    "selected_queries": [query],
                    "evidence_notes": ["Public fixture source."],
                },
                "messages": [
                    SimpleNamespace(tool_calls=[search_call]),
                    SimpleNamespace(
                        tool_call_id="search-1",
                        content=search_result,
                        status="success",
                    ),
                    SimpleNamespace(tool_calls=[extract_call]),
                    SimpleNamespace(
                        tool_call_id="extract-1",
                        content=extract_result,
                        status="success",
                    ),
                    SimpleNamespace(
                        response_metadata={
                            "model_name": STRICT_OPENROUTER_MODEL,
                            "id": "request-3",
                            "token_usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 4,
                                "total_tokens": 14,
                            },
                        },
                        usage_metadata={},
                        tool_calls=[],
                    ),
                ],
            }

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, tools, **_: DiscoveryAgent(tools),
    )

    tavily = TavilyStub()
    result = asyncio.run(
        provider.discover_lane(
            "regulatory",
            ["latest FMC enforcement"],
            ("Regulatory",),
            since=datetime(2026, 8, 1, tzinfo=UTC),
            until=datetime(2026, 8, 20, tzinfo=UTC),
            include_domains=["fmc.gov"],
            exclude_domains=["linkedin.com"],
            max_results=1,
            tavily=tavily,
        )
    )

    assert len(result.sources) == 1
    assert len(result.content) == 1
    assert tavily.searches == 1
    assert tavily.extractions == 1
    assert result.metadata["agent_call"]["tool_calls"] == 2


def test_discovery_rejects_a_zero_tool_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class ZeroToolAgent:
        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            return {
                "structured_response": {
                    "source_urls": [],
                    "selected_queries": [],
                    "evidence_notes": [],
                },
                "messages": [],
            }

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: ZeroToolAgent())

    with pytest.raises(ProviderError, match="OpenRouter discovery:regulatory failed"):
        asyncio.run(
            provider.discover_lane(
                "regulatory",
                ["latest FMC enforcement"],
                ("Regulatory",),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=["fmc.gov"],
                exclude_domains=["linkedin.com"],
                max_results=1,
                tavily=object(),
            )
        )
    assert provider.call_history[-1]["error_code"] == "missing_tool_call"
