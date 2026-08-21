from __future__ import annotations

import asyncio
import json
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import BaseTool

import sheperd_research.providers.openrouter as openrouter_module
from sheperd_research.contracts import ArticleDistillation, ClaimDraft, SourceCandidate
from sheperd_research.providers.capabilities import CapabilityReport, ModelCapability
from sheperd_research.providers.errors import ProviderError
from sheperd_research.providers.openrouter import OpenRouterProvider
from sheperd_research.providers.tavily import TavilyProvider
from sheperd_research.settings import STRICT_OPENROUTER_MODEL
from sheperd_research.topics import load_topic_configs


def _live_capability_report() -> CapabilityReport:
    return CapabilityReport(
        requested_models=(STRICT_OPENROUTER_MODEL,),
        eligible_models=(STRICT_OPENROUTER_MODEL,),
        capabilities=(
            ModelCapability(
                model=STRICT_OPENROUTER_MODEL,
                free=True,
                supports_tools=True,
                supports_structured_outputs=True,
            ),
        ),
        skipped_models=(),
        require_tools=True,
        manifest_hash="manifest-1",
        source="live",
        checked_at=datetime(2026, 8, 20, tzinfo=UTC),
    )


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


class MessageTimeoutAgent:
    async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
        raise RuntimeError("timeout")


class TimeoutRateLimitAgent:
    async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
        raise TimeoutError("429 rate limit")


class WrappedTimeoutRateLimitAgent:
    async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
        raise RuntimeError("wrapped provider error") from TimeoutError("429 rate limit")


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


def test_free_fallback_advances_after_primary_rate_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    fallback_model = "nvidia/nemotron-3-super-120b-a12b:free"
    provider.model_chain = (STRICT_OPENROUTER_MODEL, fallback_model)
    provider.allow_free_fallbacks = True
    provider._model_for = lambda model: model

    class SuccessfulFallbackAgent:
        async def ainvoke(self, payload: object, **_: object) -> dict[str, object]:
            del payload
            return {
                "structured_response": {"ok": True},
                "messages": [
                    SimpleNamespace(
                        response_metadata={
                            "model_name": fallback_model,
                            "id": "fallback-request",
                            "token_usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 4,
                                "total_tokens": 14,
                            },
                        },
                        usage_metadata={},
                        tool_calls=[
                            {
                                "id": "schema-1",
                                "name": "HealthOutput",
                                "args": {"ok": True},
                            }
                        ],
                    ),
                    ToolMessage(
                        content='{"ok": true}',
                        tool_call_id="schema-1",
                        status="success",
                    ),
                ],
            }

    def create_for_model(*, model: object, **_: object) -> object:
        if model == STRICT_OPENROUTER_MODEL:
            return RateLimitedAgent()
        return SuccessfulFallbackAgent()

    monkeypatch.setattr(openrouter_module, "create_agent", create_for_model)

    result = asyncio.run(provider.health_check())

    assert result == fallback_model
    assert [item["requested_model"] for item in provider.call_history] == [
        STRICT_OPENROUTER_MODEL,
        fallback_model,
    ]
    assert provider.call_history[-1]["fallback_reason"] == (
        f"{STRICT_OPENROUTER_MODEL}:rate_limit"
    )


def test_free_fallback_advances_after_tool_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    fallback_model = "nvidia/nemotron-nano-9b-v2:free"
    provider.model_chain = (STRICT_OPENROUTER_MODEL, fallback_model)
    provider.allow_free_fallbacks = True
    provider._model_for = lambda model: model

    class InvalidToolAgent:
        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            return {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {"id": "unknown-1", "name": "unknown_tool", "args": {}}
                        ],
                    ),
                    ToolMessage(
                        content='{"ok": true}',
                        tool_call_id="unknown-1",
                        status="success",
                    ),
                ]
            }

    class SuccessfulAgent:
        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            return {
                "structured_response": {"ok": True},
                "messages": [
                    SimpleNamespace(
                        response_metadata={
                            "model_name": fallback_model,
                            "id": "fallback-tool-request",
                            "token_usage": {"total_tokens": 10},
                        },
                        usage_metadata={},
                        tool_calls=[
                            {
                                "id": "schema-1",
                                "name": "HealthOutput",
                                "args": {"ok": True},
                            }
                        ],
                    ),
                    ToolMessage(
                        content='{"ok": true}',
                        tool_call_id="schema-1",
                        status="success",
                    ),
                ],
            }

    def create_for_model(*, model: object, **_: object) -> object:
        return InvalidToolAgent() if model == STRICT_OPENROUTER_MODEL else SuccessfulAgent()

    monkeypatch.setattr(openrouter_module, "create_agent", create_for_model)

    assert asyncio.run(provider.health_check()) == fallback_model
    assert provider.call_history[0]["error_code"] == "tool_failure"
    assert provider.call_history[-1]["fallback_reason"] == (
        f"{STRICT_OPENROUTER_MODEL}:tool_failure"
    )


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


def test_timeout_message_does_not_trigger_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, model, **__: MessageTimeoutAgent(),
    )

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(provider.health_check())

    assert len(provider.call_history) == 1
    assert provider.call_history[0]["error_code"] == "provider_error"


def test_timeout_typed_rate_limit_does_not_trigger_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, model, **__: TimeoutRateLimitAgent(),
    )

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(provider.health_check())

    assert len(provider.call_history) == 1
    assert provider.call_history[0]["error_code"] == "rate_limit"


def test_chained_rate_limit_fails_without_timeout_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, model, **__: WrappedTimeoutRateLimitAgent(),
    )

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(provider.health_check())

    assert len(provider.call_history) == 1
    assert provider.call_history[0]["error_code"] == "rate_limit"


def test_paid_fallback_is_rejected() -> None:
    with pytest.raises(ProviderError, match="FALLBACK_MODELS must be empty"):
        OpenRouterProvider(
            "secret",
            STRICT_OPENROUTER_MODEL,
            fallback_models=("openai/gpt-4o",),
            capability_report=_live_capability_report(),
        )


def test_whitespace_fallback_is_rejected_before_normalization() -> None:
    with pytest.raises(ProviderError, match="FALLBACK_MODELS must be empty"):
        OpenRouterProvider(
            "secret",
            STRICT_OPENROUTER_MODEL,
            fallback_models=(" , ",),
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


def test_openrouter_provider_requires_explicit_tool_capability_evidence() -> None:
    with pytest.raises(ProviderError, match="tool support"):
        OpenRouterProvider(
            "secret",
            STRICT_OPENROUTER_MODEL,
            capability_report=CapabilityReport(
                requested_models=(STRICT_OPENROUTER_MODEL,),
                eligible_models=(STRICT_OPENROUTER_MODEL,),
                capabilities=(
                    ModelCapability(
                        model=STRICT_OPENROUTER_MODEL,
                        free=True,
                        supports_tools=True,
                        supports_structured_outputs=True,
                    ),
                ),
                skipped_models=(),
                require_tools=False,
                manifest_hash="manifest-1",
                source="live",
                checked_at=datetime(2026, 8, 20, tzinfo=UTC),
            ),
        )


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
                    geographies=["Regulatory"],
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
    receipts = result.metadata["attempts"][0]["tool_call_receipts"]
    assert all("query" not in receipt for receipt in receipts)
    assert all("urls" not in receipt for receipt in receipts)


def test_discovery_persists_failed_tavily_tool_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TavilyFailure:
        async def search(self, *_: object, **__: object) -> list[SourceCandidate]:
            raise ProviderError(
                "Tavily plan usage limit reached",
                error_code="plan_usage_limit",
            )

        async def extract(self, _: list[SourceCandidate]) -> dict[str, str]:
            return {}

    class FailingAgent:
        def __init__(self, tools: list[object]) -> None:
            self.tools = {tool.name: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            await self.tools["tavily_search"].ainvoke({"query": "configured"})
            return {}

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, tools, **_: FailingAgent(tools),
    )

    with pytest.raises(ProviderError, match="OpenRouter discovery:regulatory failed"):
        asyncio.run(
            provider.discover_lane(
                "regulatory",
                ["configured"],
                ("Regulatory",),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=["fmc.gov"],
                exclude_domains=[],
                max_results=1,
                tavily=TavilyFailure(),
            )
        )

    attempt = provider.call_history[0]
    assert attempt["error_code"] == "plan_usage_limit"
    assert attempt["tool_calls"] == 1
    assert attempt["tool_call_receipts"][0]["tool_name"] == "tavily_search"
    assert attempt["tool_call_receipts"][0]["error_code"] == "plan_usage_limit"
    assert attempt["tool_call_receipts"][0]["status"] == "failed"


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


def test_discovery_rejects_a_model_invented_url(monkeypatch: pytest.MonkeyPatch) -> None:
    class InventedUrlAgent:
        def __init__(self, tools: list[BaseTool]) -> None:
            self.tools = {tool.name: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            search = await self.tools["tavily_search"].ainvoke({"query": "configured"})
            urls = [item["url"] for item in json.loads(search)["sources"]]
            extract = await self.tools["tavily_extract"].ainvoke({"urls": urls})
            return {
                "structured_response": {
                    "source_urls": ["https://invented.example/article"],
                    "selected_queries": ["configured"],
                    "evidence_notes": ["fixture"],
                },
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "id": "search-1",
                                "name": "tavily_search",
                                "args": {"query": "configured"},
                            },
                            {
                                "id": "extract-1",
                                "name": "tavily_extract",
                                "args": {"urls": urls},
                            },
                        ],
                    ),
                    ToolMessage(content=search, tool_call_id="search-1"),
                    ToolMessage(content=extract, tool_call_id="extract-1"),
                    SimpleNamespace(
                        response_metadata={"model_name": STRICT_OPENROUTER_MODEL},
                        usage_metadata={},
                        tool_calls=[],
                    ),
                ],
            }

    class TavilyStub:
        async def search(self, _: str, **__: object) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://known.example/article",
                    publisher="known.example",
                    published_at=datetime(2026, 8, 10, tzinfo=UTC),
                    geographies=["Regulatory"],
                )
            ]

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            return {source.url: "fixture" for source in sources}

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(
        openrouter_module,
        "create_agent",
        lambda *, tools, **_: InventedUrlAgent(tools),
    )

    with pytest.raises(ProviderError, match="introduced an unknown source URL"):
        asyncio.run(
            provider.discover_lane(
                "regulatory",
                ["configured"],
                ("Regulatory",),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=[],
                exclude_domains=[],
                max_results=1,
                tavily=TavilyStub(),
            )
        )


def test_discovery_rejects_unverifiable_tavily_scope_metadata() -> None:
    source = SourceCandidate(
        url="https://www.fmc.gov/article",
        publisher="fmc.gov",
        published_at=datetime(2026, 8, 10, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="geography"):
        OpenRouterProvider._validate_discovery_source(
            source,
            geographies=("Regulatory",),
            since=datetime(2026, 8, 1, tzinfo=UTC),
            until=datetime(2026, 8, 20, tzinfo=UTC),
            include_domains=["fmc.gov"],
            exclude_domains=[],
        )


def test_discovery_accepts_undated_tavily_source() -> None:
    source = SourceCandidate(
        url="https://www.fmc.gov/readingroom/example",
        publisher="fmc.gov",
        geographies=["Regulatory"],
    )

    validated = OpenRouterProvider._validate_discovery_source(
        source,
        geographies=("Regulatory",),
        since=datetime(2026, 8, 1, tzinfo=UTC),
        until=datetime(2026, 8, 20, tzinfo=UTC),
        include_domains=["fmc.gov"],
        exclude_domains=[],
    )

    assert validated.published_at is None


def test_discovery_maps_live_tavily_fmc_result_to_catalog_geography() -> None:
    source = TavilyProvider._source_from_result(
        {
            "url": "https://www.fmc.gov/newsroom/example",
            "title": "FMC update",
            "published_date": "2026-08-10T00:00:00Z",
        },
        "latest U.S. demurrage detention FMC court carrier terminal update",
    )

    enriched = OpenRouterProvider._enrich_discovery_geographies(
        source,
        ("Regulatory", "United States"),
        ["latest U.S. demurrage detention FMC court carrier terminal update"],
        ["fmc.gov"],
    )
    validated = OpenRouterProvider._validate_discovery_source(
        enriched,
        geographies=("Regulatory", "United States"),
        since=datetime(2026, 8, 1, tzinfo=UTC),
        until=datetime(2026, 8, 20, tzinfo=UTC),
        include_domains=[],
        exclude_domains=[],
    )

    assert validated.geographies == ["Regulatory", "United States"]


def test_discovery_maps_every_configured_query_family_from_domain_evidence() -> None:
    topics = load_topic_configs(Path(__file__).resolve().parents[1] / "config/topics.yml")
    queries = topics["dnd-port"].queries
    domain_cases = (
        ("fmc.gov", "Regulatory"),
        ("ecfr.gov", "Regulatory"),
        ("federalregister.gov", "Regulatory"),
        ("cadc.uscourts.gov", "Regulatory"),
        ("justice.gov", "Regulatory"),
        ("ftc.gov", "Regulatory"),
        ("portoflosangeles.org", "West Coast"),
        ("polb.com", "West Coast"),
        ("oaklandca.gov", "West Coast"),
        ("nwseaportalliance.com", "West Coast"),
        ("portseattle.org", "West Coast"),
        ("portoftacoma.com", "West Coast"),
        ("gaports.com", "East Coast"),
        ("scspa.com", "East Coast"),
        ("panynj.gov", "East Coast"),
        ("portofvirginia.com", "East Coast"),
        ("porthouston.com", "Gulf"),
        ("puertomanzanillo.com.mx", "Mexico"),
        ("puertolazarocardenas.com.mx", "Mexico"),
        ("puertodeveracruz.com.mx", "Mexico"),
        ("puertoaltamira.com.mx", "Mexico"),
        ("anam.gob.mx", "Mexico"),
        ("gob.mx", "Mexico"),
        ("transport.ec.europa.eu", "Europe"),
        ("emsa.europa.eu", "Europe"),
        ("ec.europa.eu", "Europe"),
        ("portofrotterdam.com", "Europe"),
        ("portofantwerpbruges.com", "Europe"),
        ("hamburg-port-authority.de", "Europe"),
        ("valenciaport.com", "Europe"),
        ("portdebarcelona.cat", "Europe"),
        ("portoffelixstowe.co.uk", "Europe"),
        ("peelports.com", "Europe"),
    )
    non_geographic_domains = (
        "imo.org",
        "unctad.org",
        "worldbank.org",
        "portwatch.imf.org",
        "wto.org",
        "courtlistener.com",
        "gcaptain.com",
        "container-news.com",
        "theloadstar.com",
        "splash247.com",
    )

    assert set(topics["dnd-port"].include_domains) == {
        *[case[0] for case in domain_cases],
        *non_geographic_domains,
    }
    for host, expected_geography in domain_cases:
        enriched = OpenRouterProvider._enrich_discovery_geographies(
            SourceCandidate(url=f"https://www.{host}/example"),
            (
                "Regulatory",
                "United States",
                "West Coast",
                "East Coast",
                "Gulf",
                "Mexico",
                "Europe",
            ),
            queries,
            topics["dnd-port"].include_domains,
        )

        assert expected_geography in enriched.geographies

    query_cases = (
        (queries[0], set()),
        (queries[1], set()),
        (queries[2], set()),
        (queries[3], set()),
        (queries[4], set()),
    )
    assert len(queries) == len(query_cases)
    for query, expected_geographies in query_cases:
        enriched = OpenRouterProvider._enrich_discovery_geographies(
            SourceCandidate(url="https://news.example/article", topics=[query]),
            (
                "Regulatory",
                "United States",
                "West Coast",
                "East Coast",
                "Gulf",
                "Mexico",
                "Europe",
            ),
            queries,
            ["news.example"],
        )

        assert set(enriched.geographies) == expected_geographies

    carrier_or_media_hosts = ("maersk.com", "gcaptain.com")
    for host in carrier_or_media_hosts:
        enriched = OpenRouterProvider._enrich_discovery_geographies(
            SourceCandidate(url=f"https://www.{host}/article", topics=[queries[2]]),
            ("Regulatory", "United States", "West Coast", "East Coast", "Gulf", "Mexico"),
            queries,
            [host],
        )

        assert enriched.geographies == []

    assert not {
        "apmterminals.com",
        "maersk.com",
        "hapag-lloyd.com",
    }.intersection(topics["dnd-port"].include_domains)

    houston = OpenRouterProvider._enrich_discovery_geographies(
        SourceCandidate(
            url="https://www.porthouston.com/example",
            topics=[queries[2]],
        ),
        ("East Coast", "Gulf"),
        queries,
        topics["dnd-port"].include_domains,
    )
    assert houston.geographies == ["Gulf"]


def test_missing_topics_config_uses_the_configured_allowlist(tmp_path: Path) -> None:
    configured = load_topic_configs(Path(__file__).resolve().parents[1] / "config/topics.yml")
    fallback = load_topic_configs(tmp_path / "missing.yml")

    assert fallback["dnd-port"].include_domains == configured["dnd-port"].include_domains
    assert fallback["dnd-port"].exclude_domains == configured["dnd-port"].exclude_domains


def test_scoped_topics_fail_closed_without_mandatory_exclusions(tmp_path: Path) -> None:
    topic_path = tmp_path / "topics.yml"
    topic_path.write_text(
        "\n".join(
            [
                "topics:",
                "  dnd-port:",
                "    description: scoped topic",
                "    queries:",
                "      - latest los angeles port update",
                "    geographies:",
                "      - West Coast",
                "    include_domains:",
                "      - portoflosangeles.org",
                "    exclude_domains: []",
                "    lookback_days: 14",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="mandatory exclusions"):
        load_topic_configs(topic_path)


def test_runnable_topics_fail_closed_without_geographies_or_allowlist(tmp_path: Path) -> None:
    topic_path = tmp_path / "topics.yml"
    topic_path.write_text(
        "\n".join(
            [
                "topics:",
                "  dnd-port:",
                "    description: scoped topic",
                "    queries:",
                "      - latest los angeles port update",
                "    geographies: []",
                "    include_domains: []",
                "    exclude_domains:",
                "      - linkedin.com",
                "    lookback_days: 14",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty geographies"):
        load_topic_configs(topic_path)


def test_runnable_topics_fail_closed_without_allowlist(tmp_path: Path) -> None:
    topic_path = tmp_path / "topics.yml"
    topic_path.write_text(
        "\n".join(
            [
                "topics:",
                "  dnd-port:",
                "    description: scoped topic",
                "    queries:",
                "      - latest los angeles port update",
                "    geographies:",
                "      - West Coast",
                "    include_domains: []",
                "    exclude_domains:",
                "      - linkedin.com",
                "    lookback_days: 14",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="include_domains allowlist"):
        load_topic_configs(topic_path)


def test_tool_receipts_fail_closed_on_malformed_and_unpaired_messages() -> None:
    result = {
        "messages": [
            SimpleNamespace(
                tool_calls=[
                    {
                        "id": "search-1",
                        "name": "tavily_search",
                        "args": {"query": "configured"},
                    },
                    "malformed",
                    {
                        "id": "search-2",
                        "name": "tavily_search",
                        "args": {"query": "configured"},
                    },
                    {
                        "id": "search-3",
                        "name": "tavily_search",
                        "args": {"query": "configured"},
                    },
                    {
                        "id": "search-4",
                        "name": "tavily_search",
                        "args": {"query": "configured"},
                    },
                ]
            ),
            SimpleNamespace(tool_calls="malformed"),
            ToolMessage(content='{"sources": []}', tool_call_id="search-1"),
            ToolMessage(content='{"unexpected": true}', tool_call_id="search-2"),
            SimpleNamespace(
                tool_call_id="search-3",
                content='{"sources": []}',
                status=None,
            ),
            ToolMessage(content='{"sources": []}', tool_call_id="unpaired"),
        ]
    }

    receipts = OpenRouterProvider._tool_call_receipts(result)

    assert all(receipt["status"] == "failed" for receipt in receipts[1:])
    assert any(receipt["tool_name"] == "unknown" for receipt in receipts)
    assert next(receipt for receipt in receipts if receipt["call_id"] == "search-2")[
        "status"
    ] == "failed"
    assert next(receipt for receipt in receipts if receipt["call_id"] == "search-4")[
        "status"
    ] == "failed"


@pytest.mark.parametrize("result", [None, {}, {"messages": "malformed"}])
def test_tool_receipts_record_malformed_top_level_results(result: object) -> None:
    receipts = OpenRouterProvider._tool_call_receipts(result)

    assert len(receipts) == 1
    assert receipts[0]["tool_name"] == "unknown"
    assert receipts[0]["status"] == "failed"
    assert "content" not in receipts[0]


def test_invoke_agent_preserves_unknown_and_malformed_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class InvalidReceiptAgent:
        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            return {
                "messages": [
                    SimpleNamespace(
                        tool_calls=[
                            {"id": "unknown-1", "name": "unknown_tool", "args": {}},
                            "malformed",
                        ],
                    ),
                    ToolMessage(content='{"ok": true}', tool_call_id="unknown-1"),
                    ToolMessage(content='{"ok": true}', tool_call_id="unpaired-1"),
                ]
            }

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: InvalidReceiptAgent())

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(
            provider._invoke_structured(
                openrouter_module.HealthOutput,
                "health",
                prompt_version="health-v1",
                operation="health",
            )
        )

    metadata = provider.call_history[-1]
    receipts = metadata["tool_call_receipts"]
    assert metadata["tool_calls"] == 3
    assert isinstance(receipts, list)
    assert all(receipt["status"] == "failed" for receipt in receipts)


def test_invoke_agent_records_malformed_top_level_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MalformedResultAgent:
        async def ainvoke(self, *_: object, **__: object) -> object:
            return "malformed"

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(openrouter_module, "create_agent", lambda **_: MalformedResultAgent())

    with pytest.raises(ProviderError, match="OpenRouter health failed"):
        asyncio.run(
            provider._invoke_structured(
                openrouter_module.HealthOutput,
                "health",
                prompt_version="health-v1",
                operation="health",
            )
        )

    assert provider.call_history[-1]["tool_calls"] == 1


@pytest.mark.parametrize(
    ("tool_name", "payload"),
    [
        ("tavily_search", {"query": "configured", "sources": [1]}),
        (
            "tavily_search",
            {
                "query": "configured",
                "sources": [{"url": "https://www.fmc.gov/example"}],
            },
        ),
        ("tavily_search", {"query": "configured", "sources": [], "extra": True}),
        (
            "tavily_extract",
            {"extracted_urls": [1], "extracted_count": 1},
        ),
        (
            "tavily_extract",
            {"extracted_urls": ["https://www.fmc.gov/example"], "extracted_count": 0},
        ),
        (
            "tavily_extract",
            {"extracted_urls": [], "extracted_count": False},
        ),
        (
            "tavily_extract",
            {"extracted_urls": [], "extracted_count": 0, "extra": True},
        ),
    ],
)
def test_tool_receipts_reject_malformed_success_payloads(
    tool_name: str,
    payload: dict[str, object],
) -> None:
    result = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"id": "call-1", "name": tool_name, "args": {}}],
            ),
            ToolMessage(content=json.dumps(payload), tool_call_id="call-1"),
        ]
    }

    assert OpenRouterProvider._tool_call_receipts(result)[0]["status"] == "failed"


def test_tool_receipts_accept_undated_search_results() -> None:
    result = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call-1",
                        "name": "tavily_search",
                        "args": {"query": "configured"},
                    }
                ],
            ),
            ToolMessage(
                content=json.dumps(
                    {
                        "query": "configured",
                        "sources": [
                            {
                                "url": "https://www.fmc.gov/example",
                                "title": "FMC source",
                                "publisher": "www.fmc.gov",
                                "published_at": None,
                                "snippet": "Public source",
                            }
                        ],
                    }
                ),
                tool_call_id="call-1",
                status="success",
            ),
        ]
    }

    receipt = OpenRouterProvider._tool_call_receipts(result)[0]
    assert receipt["status"] == "succeeded"
    assert receipt["result_count"] == 1


def test_discovery_rejects_a_failed_extra_tool_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TavilyStub:
        async def search(self, _: str, **__: object) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://www.fmc.gov/example-agent-source",
                    publisher="fmc.gov",
                    published_at=datetime(2026, 8, 10, tzinfo=UTC),
                    geographies=["Regulatory"],
                )
            ]

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            return {source.url: "fixture" for source in sources}

    class ExtraFailedCallAgent:
        def __init__(self, tools: list[BaseTool]) -> None:
            self.tools = {tool.name: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            query = "configured"
            search = await self.tools["tavily_search"].ainvoke({"query": query})
            url = json.loads(search)["sources"][0]["url"]
            extract = await self.tools["tavily_extract"].ainvoke({"urls": [url]})
            with pytest.raises(ValueError, match="configured lane scope"):
                await self.tools["tavily_search"].ainvoke({"query": "outside scope"})
            return {
                "structured_response": {
                    "source_urls": [url],
                    "selected_queries": [query],
                    "evidence_notes": ["fixture"],
                },
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "id": "search-1",
                                "name": "tavily_search",
                                "args": {"query": query},
                            },
                            {
                                "id": "extract-1",
                                "name": "tavily_extract",
                                "args": {"urls": [url]},
                            },
                            {
                                "id": "search-2",
                                "name": "tavily_search",
                                "args": {"query": "outside scope"},
                            },
                        ],
                    ),
                    ToolMessage(content=search, tool_call_id="search-1"),
                    ToolMessage(content=extract, tool_call_id="extract-1"),
                    ToolMessage(
                        content='{"error":"outside scope"}',
                        tool_call_id="search-2",
                        status="error",
                    ),
                    SimpleNamespace(
                        response_metadata={"model_name": STRICT_OPENROUTER_MODEL},
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
        lambda *, tools, **_: ExtraFailedCallAgent(tools),
    )

    with pytest.raises(ProviderError, match="OpenRouter discovery:regulatory failed"):
        asyncio.run(
            provider.discover_lane(
                "regulatory",
                ["configured"],
                ("Regulatory",),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=["fmc.gov"],
                exclude_domains=[],
                max_results=1,
                tavily=TavilyStub(),
            )
        )


def test_discovery_fails_when_an_agent_extraction_returns_no_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TavilyStub:
        async def search(self, _: str, **__: object) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://www.fmc.gov/example-agent-source",
                    publisher="fmc.gov",
                    published_at=datetime(2026, 8, 10, tzinfo=UTC),
                    geographies=["Regulatory"],
                )
            ]

        async def extract(self, _: list[SourceCandidate]) -> dict[str, str]:
            return {}

    class ExtractionFailureAgent:
        def __init__(self, tools: list[BaseTool]) -> None:
            self.tools = {tool.name: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            query = "configured"
            search = await self.tools["tavily_search"].ainvoke({"query": query})
            url = json.loads(search)["sources"][0]["url"]
            with pytest.raises(ValueError, match="incomplete content"):
                await self.tools["tavily_extract"].ainvoke({"urls": [url]})
            return {
                "structured_response": {
                    "source_urls": [url],
                    "selected_queries": [query],
                    "evidence_notes": ["fixture"],
                },
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {"id": "search-1", "name": "tavily_search", "args": {"query": query}},
                            {"id": "extract-1", "name": "tavily_extract", "args": {"urls": [url]}},
                        ],
                    ),
                    ToolMessage(content=search, tool_call_id="search-1"),
                    ToolMessage(
                        content='{"error":"incomplete"}',
                        tool_call_id="extract-1",
                        status="error",
                    ),
                    SimpleNamespace(
                        response_metadata={"model_name": STRICT_OPENROUTER_MODEL},
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
        lambda *, tools, **_: ExtractionFailureAgent(tools),
    )

    with pytest.raises(ProviderError, match="OpenRouter discovery:regulatory failed"):
        asyncio.run(
            provider.discover_lane(
                "regulatory",
                ["configured"],
                ("Regulatory",),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=["fmc.gov"],
                exclude_domains=[],
                max_results=1,
                tavily=TavilyStub(),
            )
        )


def test_tool_receipts_parse_langchain_ai_messages() -> None:
    result = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "search-1",
                        "name": "tavily_search",
                        "args": {"query": "fmc enforcement"},
                    },
                    {
                        "id": "extract-1",
                        "name": "tavily_extract",
                        "args": {"urls": ["https://www.fmc.gov/example"]},
                    },
                ],
            ),
            ToolMessage(
                content=(
                    '{"query": "fmc enforcement", "sources": [{'
                    '"url": "https://www.fmc.gov/example", '
                    '"title": "FMC example", "publisher": "fmc.gov", '
                    '"published_at": "2026-08-10T00:00:00Z", "snippet": "Update"}]}'
                ),
                tool_call_id="search-1",
            ),
            ToolMessage(
                content=(
                    '{"extracted_urls": ["https://www.fmc.gov/example"], '
                    '"extracted_count": 1}'
                ),
                tool_call_id="extract-1",
            ),
        ]
    }

    receipts = OpenRouterProvider._tool_call_receipts(result)

    assert [receipt["tool_name"] for receipt in receipts] == [
        "tavily_search",
        "tavily_extract",
    ]
    assert [receipt["status"] for receipt in receipts] == ["succeeded", "succeeded"]
    assert receipts[1]["url_count"] == 1


def test_create_agent_names_all_six_workers(monkeypatch: pytest.MonkeyPatch) -> None:
    class TavilyStub:
        async def search(self, query: str, **_: object) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://www.fmc.gov/example-agent-source",
                    title="FMC fixture",
                    publisher="fmc.gov",
                    published_at=datetime(2026, 8, 19, tzinfo=UTC),
                    snippet=query,
                    geographies=["Regulatory", "us-ports", "mexico"],
                )
            ]

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            return {source.url: "Public evidence fixture." for source in sources}

    names: list[str] = []

    class Agent:
        def __init__(self, name: str, tools: list[BaseTool]) -> None:
            self.name = name
            self.tools = {tool.name: tool for tool in tools}

        async def ainvoke(self, *_: object, **__: object) -> dict[str, object]:
            response = SimpleNamespace(
                response_metadata={
                    "model_name": STRICT_OPENROUTER_MODEL,
                    "token_usage": {"prompt_tokens": 1, "completion_tokens": 1},
                },
                usage_metadata={},
                tool_calls=[],
            )
            if self.tools:
                search = await self.tools["tavily_search"].ainvoke({"query": "configured"})
                urls = [item["url"] for item in json.loads(search)["sources"]]
                extract = await self.tools["tavily_extract"].ainvoke({"urls": urls})
                return {
                    "structured_response": {
                        "source_urls": urls,
                        "selected_queries": ["configured"],
                        "evidence_notes": ["fixture"],
                    },
                    "messages": [
                        AIMessage(
                            content="",
                            tool_calls=[
                                {
                                    "id": "search-1",
                                    "name": "tavily_search",
                                    "args": {"query": "configured"},
                                },
                                {
                                    "id": "extract-1",
                                    "name": "tavily_extract",
                                    "args": {"urls": urls},
                                },
                            ],
                        ),
                        ToolMessage(content=search, tool_call_id="search-1"),
                        ToolMessage(content=extract, tool_call_id="extract-1"),
                        response,
                    ],
                }
            structured_response: dict[str, object]
            if self.name == "source_distillation_agent":
                structured_response = {
                    "summary": "Source-bound summary.",
                    "key_points": ["Reported point."],
                    "claims": [],
                    "limitations": [],
                }
            elif self.name == "critic_agent":
                structured_response = {"claims": []}
            else:
                structured_response = {"title": "Weekly", "summary": "Cited draft."}
            return {"structured_response": structured_response, "messages": [response]}

    def create_named_agent(*, name: str, tools: list[BaseTool], **_: object) -> Agent:
        names.append(name)
        return Agent(name, tools)

    provider = _stub_provider()
    provider._model_for = lambda model: model
    monkeypatch.setattr(openrouter_module, "create_agent", create_named_agent)
    tavily = TavilyStub()
    for lane in ("regulatory", "us-ports", "mexico"):
        asyncio.run(
            provider.discover_lane(
                lane,
                ["configured"],
                (lane,),
                since=datetime(2026, 8, 1, tzinfo=UTC),
                until=datetime(2026, 8, 20, tzinfo=UTC),
                include_domains=[],
                exclude_domains=[],
                max_results=1,
                tavily=tavily,
            )
        )
    source = SourceCandidate(url="https://www.fmc.gov/example-agent-source")
    asyncio.run(provider.distill(source, "body"))
    asyncio.run(provider.critic([], {source.url}))
    asyncio.run(
        provider.synthesize(
            "run-1",
            [
                ArticleDistillation(
                    source_url=source.url,
                    summary="Source-bound summary.",
                    claims=[ClaimDraft(claim="Reported point.", source_urls=[source.url])],
                )
            ],
            covered_from=datetime(2026, 8, 13, tzinfo=UTC),
            covered_until=datetime(2026, 8, 20, tzinfo=UTC),
        )
    )

    assert names == [
        "regulatory_research_agent",
        "us_ports_research_agent",
        "mexico_europe_research_agent",
        "source_distillation_agent",
        "critic_agent",
        "weekly_synthesis_agent",
    ]
