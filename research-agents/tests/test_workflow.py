from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from langgraph.checkpoint.memory import InMemorySaver

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    ResearchRunRequest,
    SourceCandidate,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
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
    assert result.error and "extraction" in result.error


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
