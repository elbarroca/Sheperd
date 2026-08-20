from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    ResearchRunRequest,
    SourceCandidate,
    TopicConfig,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.providers.errors import ProviderError
from sheperd_research.validators import can_extract_url
from sheperd_research.workflow import ResearchWorkflow, checkpoint_serializer


class FakeTavily:
    async def search(self, query: str, **_: object) -> list[SourceCandidate]:
        return [
            SourceCandidate(
                url=f"https://www.fmc.gov/{query.replace(' ', '-')}",
                title=f"{query} update",
                publisher="fmc.gov",
                published_at=datetime(2026, 8, 18, tzinfo=UTC),
                topics=["dnd"],
                geographies=["West Coast"],
            )
        ]

    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
        return {source.url: f"Evidence for {source.title}" for source in sources}


class FakeLLM:
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
        tavily: FakeTavily,
    ) -> LaneDiscoveryResult:
        del since, until, include_domains, exclude_domains
        sources: list[SourceCandidate] = []
        content: dict[str, str] = {}
        for query in queries:
            found = await tavily.search(query, max_results=max_results)
            found = [
                source.model_copy(update={"geographies": list(geographies)})
                for source in found
            ]
            extractable = [source for source in found if can_extract_url(source.url)]
            sources.extend(extractable)
            content.update(await tavily.extract(extractable))
        if not content:
            raise ProviderError("discovery agent did not extract any source content")
        return LaneDiscoveryResult(
            packet=LaneDiscoveryPacket(
                source_urls=[source.url for source in sources],
                selected_queries=queries,
                evidence_notes=["fixture"],
            ),
            sources=sources,
            content=content,
            metadata={
                "agent_call": {"tool_calls": 2},
                "attempts": [
                    {
                        "tool_call_receipts": [
                            {
                                "call_id": f"{lane}-search",
                                "call_index": 0,
                                "tool_name": "tavily_search",
                                "status": "succeeded",
                                "input_hash": f"{lane}-search",
                            },
                            {
                                "call_id": f"{lane}-extract",
                                "call_index": 1,
                                "tool_name": "tavily_extract",
                                "status": "succeeded",
                                "input_hash": f"{lane}-extract",
                            },
                        ]
                    }
                ],
            },
        )

    async def distill(
        self,
        source: SourceCandidate,
        content: str,
        **_: object,
    ) -> ArticleDistillation:
        return ArticleDistillation(
            source_url=source.url,
            summary=f"Summary of {source.title}.",
            key_points=[content],
            claims=[ClaimDraft(claim="A reported port signal exists.", source_urls=[source.url])],
            limitations=["Public report only."],
            model_id="google/gemma-4-26b-a4b-it:free",
        )

    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        **_: object,
    ) -> WeeklyBrief:
        return WeeklyBrief(
            run_id=run_id,
            title="Weekly port intelligence",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="A cited draft.",
            signal_event_ids=[],
            source_urls=[item.source_url for item in distillations],
            model_id="google/gemma-4-26b-a4b-it:free",
        )


class LargeBodyTavily(FakeTavily):
    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
        return {source.url: "evidence " * 10_000 for source in sources}


class EmptyExtractTavily(FakeTavily):
    calls = 0

    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
        self.calls += 1
        return {}


class NonExtractableTavily(FakeTavily):
    async def search(self, query: str, **_: object) -> list[SourceCandidate]:
        return [
            SourceCandidate(
                url="https://www.linkedin.com/company/example",
                title=f"{query} update",
                publisher="LinkedIn",
                published_at=datetime(2026, 8, 18, tzinfo=UTC),
                topics=["dnd"],
                geographies=["West Coast"],
            )
        ]


class WrongModelLLM(FakeLLM):
    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        **_: object,
    ) -> WeeklyBrief:
        brief = await super().synthesize(run_id, distillations, **_)
        return brief.model_copy(update={"model_id": "offline-fixture"})


class OutOfScopeDiscoveryLLM(FakeLLM):
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
        tavily: FakeTavily,
    ) -> LaneDiscoveryResult:
        result = await super().discover_lane(
            lane,
            queries,
            geographies,
            since=since,
            until=until,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            max_results=max_results,
            tavily=tavily,
        )
        return result.model_copy(
            update={
                "sources": [
                    source.model_copy(update={"geographies": ["Unverifiable"]})
                    for source in result.sources
                ]
            }
        )


def test_workflow_records_a_cited_draft_and_is_idempotent() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=3,
        validation_profile="canary",
    )

    first = asyncio.run(workflow.run(request))
    source_count = len(repository.sources)
    claim_count = len(repository.claims)
    second = asyncio.run(workflow.run(request, run_id=first.run_id))

    assert first.status == "succeeded"
    assert second.run_id == first.run_id
    assert len(repository.sources) == source_count
    assert len(repository.claims) == claim_count
    assert len(repository.signal_events) == claim_count
    assert repository.briefs[first.run_id].signal_event_ids
    assert repository.briefs[first.run_id].review_state.value == "draft"
    assert first.distillation_count == first.source_count


def test_workflow_quarantines_unsafe_seeds_and_retains_safe_seed_only_sources() -> None:
    topic_seed_urls = [
        "https://gcaptain.com/example?subscriber=true",
        "https://www.linkedin.com/posts/example",
    ]
    request_seed_urls = [
        "https://www.fmc.gov/articles/example",
    ]
    topic = TopicConfig(
        name="dnd-port",
        description="Fixture topic",
        queries=["regulatory", "west", "east gulf", "mexico"],
        seed_urls=topic_seed_urls,
        geographies=["West Coast", "East Coast", "Gulf", "Mexico"],
        include_domains=["fmc.gov"],
        exclude_domains=["linkedin.com"],
    )
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(
        repository,
        FakeTavily(),
        FakeLLM(),
        topic_configs={"dnd-port": topic},
    )

    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=10,
                seed_urls=request_seed_urls,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "succeeded"
    assert result.source_count == 5
    assert result.distillation_count == 4
    safe_seed = repository.sources["https://www.fmc.gov/articles/example"]
    assert safe_seed.is_seed is True
    assert safe_seed.source_kind == "seed-only"
    assert all(
        item.source_url != "https://www.fmc.gov/articles/example"
        for item in repository.distillations.values()
    )
    assert "https://gcaptain.com/example?subscriber=true" not in repository.sources
    assert "https://www.linkedin.com/posts/example" not in repository.sources
    discovery_step = next(step for step in repository.steps if step["agent_name"] == "discovery")
    metadata = cast(dict[str, object], discovery_step["metadata"])
    assert metadata["accepted_seed_count"] == 1
    assert metadata["quarantined_seed_count"] == 2


def test_llm_input_budget_matches_provider_source_truncation() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(
        repository,
        LargeBodyTavily(),
        FakeLLM(),
        max_llm_input_chars=9_000,
    )
    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=1,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "succeeded"
    assert result.error is None


def test_checkpoint_pause_resume_uses_an_explicit_contract_allowlist() -> None:
    async def execute() -> None:
        repository = InMemoryRepository()
        request = ResearchRunRequest(
            topic_set="dnd-port",
            max_sources=3,
            as_of=datetime(2026, 8, 19, tzinfo=UTC),
            validation_profile="canary",
        )
        checkpointer = InMemorySaver(serde=checkpoint_serializer())
        workflow = ResearchWorkflow(
            repository,
            FakeTavily(),
            FakeLLM(),
            checkpointer=checkpointer,
        )
        repository.create_run("paused-run", request)
        graph = workflow._build_graph(checkpointer)
        config: RunnableConfig = {"configurable": {"thread_id": "paused-run"}}
        initial = {
            "run_id": "paused-run",
            "request": request,
            "topic": workflow.topic_configs["dnd-port"],
            "partial_reasons": [],
        }

        paused = cast(
            dict[str, object],
            await cast(Any, graph).ainvoke(initial, config=config, interrupt_after=["extract"]),
        )
        resumed = cast(
            dict[str, object],
            await cast(Any, graph).ainvoke(None, config=config),
        )

        assert paused.get("content") is not None
        assert resumed.get("brief") is not None

    asyncio.run(execute())


def test_workflow_records_step_hashes_and_latency() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())

    asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=3,
                validation_profile="canary",
            )
        )
    )

    named_steps = {str(step["agent_name"]): step for step in repository.steps}
    for name in ("discovery", "extraction", "distillation", "critic", "synthesis", "validation"):
        step = named_steps[name]
        assert isinstance(step["duration_ms"], int)
        assert step["input_hash"]
        assert step["output_hash"]


def test_workflow_fails_closed_when_extraction_is_incomplete() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, EmptyExtractTavily(), FakeLLM())

    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=1,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "failed"
    assert result.error and "did not extract any source content" in result.error


def test_workflow_rejects_out_of_scope_discovery_results() -> None:
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        OutOfScopeDiscoveryLLM(),
    )

    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=1,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "failed"
    assert result.error and "outside lane geography" in result.error


def test_workflow_does_not_fallback_to_direct_tavily_extraction() -> None:
    tavily = EmptyExtractTavily()
    workflow = ResearchWorkflow(InMemoryRepository(), tavily, FakeLLM())
    source = SourceCandidate(url="https://example.com/agent-only")

    try:
        asyncio.run(
            workflow._extract(
                {
                    "run_id": "run-1",
                    "sources": [source],
                    "content": {},
                    "partial_reasons": [],
                }
            )
        )
    except ProviderError as error:
        assert "extraction missing content" in str(error)
    else:
        raise AssertionError("workflow unexpectedly accepted missing agent extraction")

    assert tavily.calls == 0


def test_workflow_fails_when_non_extractable_source_has_no_body() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, NonExtractableTavily(), FakeLLM())

    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=1,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "failed"
    assert result.error and "did not extract any source content" in result.error


def test_record_step_preserves_provider_attempt_and_input_correlation() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())

    workflow._record_step(
        "run-1",
        "distillation",
        "succeeded",
        {
            "attempts": [
                {
                    "attempt": 1,
                    "record_attempt": 1,
                    "input_hash": "input-a",
                    "output_hash": "output-a",
                    "source_url": "https://example.com/a",
                },
                {
                    "attempt": 1,
                    "record_attempt": 2,
                    "input_hash": "input-b",
                    "output_hash": "output-b",
                    "source_url": "https://example.com/b",
                },
            ]
        },
    )

    first = repository.steps[0]
    second = repository.steps[1]
    assert first["attempt"] == 1
    assert second["attempt"] == 2
    assert cast(dict[str, object], first["metadata"])["provider_attempt"] == 1
    assert cast(dict[str, object], second["metadata"])["provider_attempt"] == 1
    assert first["input_hash"] == "input-a"
    assert second["input_hash"] == "input-b"


def test_workflow_fails_when_validation_does_not_pass() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), WrongModelLLM())

    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=1,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status == "failed"
    assert result.validation_status.value == "blocked"
    assert result.error and "validation" in result.error


def test_discovery_schedules_all_three_lanes_concurrently() -> None:
    class ConcurrentLLM(FakeLLM):
        def __init__(self) -> None:
            self.in_flight = 0
            self.maximum_in_flight = 0

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
            tavily: FakeTavily,
        ) -> LaneDiscoveryResult:
            self.in_flight += 1
            self.maximum_in_flight = max(self.maximum_in_flight, self.in_flight)
            try:
                await asyncio.sleep(0.01)
                return await super().discover_lane(
                    lane,
                    queries,
                    geographies,
                    since=since,
                    until=until,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    max_results=max_results,
                    tavily=tavily,
                )
            finally:
                self.in_flight -= 1

    repository = InMemoryRepository()
    llm = ConcurrentLLM()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)
    request = ResearchRunRequest(topic_set="dnd-port", max_sources=3, validation_profile="canary")

    asyncio.run(
        workflow._discover_lanes(
            {
                "run_id": "run-1",
                "request": request,
                "topic": workflow.topic_configs[request.topic_set],
            }
        )
    )

    assert llm.maximum_in_flight == 3
