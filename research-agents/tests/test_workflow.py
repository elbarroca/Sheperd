from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from langgraph.checkpoint.memory import InMemorySaver

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    ResearchRunRequest,
    SourceCandidate,
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
                url=f"https://example.com/{query.replace(' ', '-')}",
                title=f"{query} update",
                publisher="Example",
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
        del geographies, since, until, include_domains, exclude_domains
        sources: list[SourceCandidate] = []
        content: dict[str, str] = {}
        for query in queries:
            found = await tavily.search(query, max_results=max_results)
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
    async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
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
        config = {"configurable": {"thread_id": "paused-run"}}
        initial = {
            "run_id": "paused-run",
            "request": request,
            "topic": workflow.topic_configs["dnd-port"],
            "partial_reasons": [],
        }

        paused = await graph.ainvoke(initial, config, interrupt_after=["extract"])
        resumed = await graph.ainvoke(None, config)

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

    first, second = repository.steps
    assert first["attempt"] == 1
    assert second["attempt"] == 2
    assert first["metadata"]["provider_attempt"] == 1
    assert second["metadata"]["provider_attempt"] == 1
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
