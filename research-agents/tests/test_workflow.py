from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, cast

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DistillationQualityStatus,
    EvidenceStatus,
    ExtractionStatus,
    InsightStatus,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    ReportBullet,
    ResearchRunRequest,
    SourceCandidate,
    TopicConfig,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.providers.errors import ProviderError
from sheperd_research.validators import can_extract_url
from sheperd_research.workflow import LANES, ResearchWorkflow, checkpoint_serializer


def _not_observed_insight(subject: str) -> ArticleInsight:
    return ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement=f"No supported {subject} was observed in this source.",
        why_it_matters=f"This source does not provide enough evidence for a {subject} conclusion.",
        next_step=f"Review an independent source for {subject} evidence.",
    )


def _complete_distillation(
    source_url: str, *, summary: str = "Source summary."
) -> ArticleDistillation:
    claim = ClaimDraft(
        claim="A reported port signal exists.",
        source_urls=[source_url],
    )
    return ArticleDistillation(
        source_url=source_url,
        summary=summary,
        key_points=["Reported point one.", "Reported point two."],
        what_happened="The source reports a public port development.",
        why_it_matters="The development may affect the operating picture.",
        risk_assessment=_not_observed_insight("material risk"),
        opportunity_assessment=_not_observed_insight("commercial opportunity"),
        uncertainties=["The source may not cover the full market."],
        next_steps=["Compare the report with an independent source."],
        evidence_excerpts=["A reported port signal exists."],
        claims=[claim],
        limitations=["Public report only."],
        quality_status=DistillationQualityStatus.COMPLETE,
        model_id="google/gemma-4-26b-a4b-it:free",
    )


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
        distillation = _complete_distillation(
            source.url,
            summary=f"Summary of {source.title}.",
        )
        return distillation.model_copy(
            update={"key_points": [content, "The source provides public evidence."]}
        )

    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        **_: object,
    ) -> WeeklyBrief:
        source_urls = [item.source_url for item in distillations]

        def bullet(text: str) -> ReportBullet:
            return ReportBullet(
                text=text,
                source_urls=source_urls,
                why_it_matters="This is relevant to the operating picture.",
                next_step="Monitor the cited evidence.",
            )

        return WeeklyBrief(
            run_id=run_id,
            title="Weekly port intelligence",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="A cited draft.",
            signal_event_ids=[],
            source_urls=source_urls,
            model_id="google/gemma-4-26b-a4b-it:free",
            executive_bullets=[bullet("Executive signal.")],
            developments=[bullet("Development signal.")],
            risks=[bullet("Risk signal.")],
            opportunities=[bullet("Opportunity signal.")],
            uncertainties=[bullet("Uncertainty signal.")],
            follow_up_questions=["What should be monitored next?"],
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


class CrossRunCollisionTavily(FakeTavily):
    async def search(self, query: str, **_: object) -> list[SourceCandidate]:
        return [
            SourceCandidate(
                url="https://www.fmc.gov/cross-run-source",
                title=f"{query} update",
                publisher="fmc.gov",
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


class UnsafeModelSourceLLM(FakeLLM):
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
        unsafe_url = "https://www.fmc.gov/model?subscriber=true"
        unsafe_source = result.sources[0].model_copy(update={"url": unsafe_url})
        return result.model_copy(
            update={
                "packet": result.packet.model_copy(update={"source_urls": [unsafe_url]}),
                "sources": [unsafe_source],
                "content": {unsafe_url: "paywalled model content"},
            }
        )


def test_validate_report_bullets_rejects_empty_sections_instead_of_fallback() -> None:
    source = SourceCandidate(url="https://example.com/source")
    brief = WeeklyBrief(
        run_id="run-1",
        title="Empty report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="A report with empty sections.",
    )
    claim = ClaimDraft(claim="A cited claim.", source_urls=[source.url])

    with pytest.raises(ValueError, match="report output is incomplete"):
        ResearchWorkflow._validate_report_bullets(brief, [claim], {source.url})


def test_synthesis_accepts_bullets_citing_known_sources_without_claims() -> None:
    claimed_source = SourceCandidate(url="https://example.com/claimed")
    source_without_claim = SourceCandidate(url="https://example.com/context")
    claim = ClaimDraft(claim="A cited claim.", source_urls=[claimed_source.url])

    class SourceContextLLM(FakeLLM):
        async def synthesize(
            self,
            run_id: str,
            distillations: list[ArticleDistillation],
            **kwargs: object,
        ) -> WeeklyBrief:
            brief = await super().synthesize(run_id, distillations, **kwargs)
            context_bullet = ReportBullet(
                text="Context source informs the report.",
                source_urls=[source_without_claim.url],
                why_it_matters="It provides relevant context.",
                next_step="Review it alongside the claim.",
            )
            return brief.model_copy(
                update={
                    "executive_bullets": [context_bullet],
                    "developments": [context_bullet],
                    "risks": [context_bullet],
                    "opportunities": [context_bullet],
                    "uncertainties": [context_bullet],
                }
            )

    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), SourceContextLLM())
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        validation_profile="canary",
    )
    result = asyncio.run(
        workflow._synthesize(
            {
                "run_id": "run-1",
                "request": request,
                "topic": workflow.topic_configs[request.topic_set],
                "sources": [claimed_source, source_without_claim],
                "content": {},
                "distillations": [
                    _complete_distillation(
                        claimed_source.url,
                        summary="Claimed source summary.",
                    ).model_copy(update={"claims": [claim]}),
                    _complete_distillation(
                        source_without_claim.url,
                        summary="Context source summary.",
                    ),
                ],
                "claims": [claim],
            }
        )
    )

    assert cast(WeeklyBrief, result["brief"]).executive_bullets[0].source_urls == [
        source_without_claim.url
    ]


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


def test_repair_preserves_incomplete_history_and_writes_a_new_complete_run() -> None:
    repository = InMemoryRepository()
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="canary",
    )
    source = SourceCandidate(
        url="https://www.fmc.gov/repair-source",
        title="Repair source",
        publisher="fmc.gov",
        lane="regulatory",
        geographies=["Regulatory"],
    )
    repository.create_run("old-run", request)
    repository.record_source(source)
    repository.record_distillation(
        "old-run",
        ArticleDistillation(source_url=source.url, summary="Legacy summary."),
    )

    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())
    result = asyncio.run(workflow.repair(request, [source], "repair-run"))

    assert result.status.value == "succeeded"
    assert repository.get_run("old-run") is not None
    assert len(repository.get_run_distillations("old-run")) == 1
    repaired = repository.get_run_distillations("repair-run")
    assert len(repaired) == 1
    assert repaired[0].quality_status is DistillationQualityStatus.COMPLETE
    assert repository.get_brief("repair-run") is not None


def test_canary_discovery_query_limit_bounds_each_lane() -> None:
    class RecordingLLM(FakeLLM):
        def __init__(self) -> None:
            self.queries_by_lane: dict[str, list[str]] = {}
            self.geographies_by_lane: dict[str, tuple[str, ...]] = {}

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            self.queries_by_lane[lane] = list(queries)
            self.geographies_by_lane[lane] = geographies
            return await super().discover_lane(lane, queries, geographies, **kwargs)

    llm = RecordingLLM()
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        llm,
        discovery_query_limit=1,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=3,
        validation_profile="canary",
    )

    asyncio.run(
        workflow._discover_lanes(
            {
                "run_id": "canary-query-limit",
                "request": request,
                "topic": workflow.topic_configs["dnd-port"],
            }
        )
    )

    assert set(llm.queries_by_lane) == {"regulatory", "us-ports", "mexico"}
    assert all(len(queries) == 1 for queries in llm.queries_by_lane.values())
    assert llm.geographies_by_lane == {
        "regulatory": ("Regulatory", "United States"),
        "us-ports": ("West Coast", "East Coast", "Gulf"),
        "mexico": ("Mexico", "Europe"),
    }


def test_research_keeps_three_lanes_and_covers_mexico_and_europe() -> None:
    assert [lane.name for lane in LANES] == ["regulatory", "us-ports", "mexico"]
    assert set(LANES[-1].geographies) == {"Mexico", "Europe"}

    topic = ResearchWorkflow(InMemoryRepository(), FakeTavily(), FakeLLM()).topic_configs[
        "dnd-port"
    ]
    assert "Europe" in topic.geographies
    assert any("Europe" in query for query in topic.queries)


def test_malformed_and_unsupported_seed_urls_are_quarantined_without_validation_errors() -> None:
    topic = TopicConfig(
        name="dnd-port",
        description="Fixture topic",
        queries=["regulatory"],
        geographies=["Mexico", "Europe"],
        include_domains=["example.com"],
        exclude_domains=["linkedin.com"],
    )

    sources, metadata = ResearchWorkflow._safe_seed_sources(
        ["https://", "ftp://example.com/article", "https://[invalid"],
        topic,
        "dnd-port",
    )

    assert sources == []
    assert metadata["accepted_seed_count"] == 0
    assert metadata["quarantined_seed_count"] == 3
    assert set(metadata["quarantined_seed_reasons"]) >= {
        "unsupported_scheme",
        "missing_host",
        "malformed_url",
    }


def test_workflow_persists_quarantined_seed_leads_without_processing_them() -> None:
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
    assert result.source_count == 4
    assert result.distillation_count == 4
    safe_seed = repository.sources["https://www.fmc.gov/articles/example"]
    assert safe_seed.is_seed is True
    assert safe_seed.source_kind == "seed-only"
    quarantined_urls = {
        "https://gcaptain.com/example",
        "https://www.linkedin.com/posts/example",
    }
    for url in quarantined_urls:
        quarantined = repository.sources[url]
        assert quarantined.is_seed is True
        assert quarantined.source_kind == "seed-only"
        assert quarantined.evidence_status is EvidenceStatus.UNVERIFIED
    assert all(
        item.source_url != "https://www.fmc.gov/articles/example"
        for item in repository.distillations.values()
    )
    assert all(
        source_url not in quarantined_urls
        for _, source_url in repository.source_snapshots
    )
    assert all(
        source_url not in quarantined_urls
        for _, source_url in repository.distillations
    )
    report = repository.validations[result.run_id]
    assert report.source_count == 4
    assert report.unique_source_count == 4
    discovery_step = next(step for step in repository.steps if step["agent_name"] == "discovery")
    metadata = cast(dict[str, object], discovery_step["metadata"])
    assert metadata["accepted_seed_count"] == 1
    assert metadata["quarantined_seed_count"] == 2


def test_workflow_blocks_seed_provenance_across_runs() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, CrossRunCollisionTavily(), FakeLLM())
    seed_request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        seed_urls=["https://www.fmc.gov/cross-run-source"],
        validation_profile="canary",
    )

    asyncio.run(workflow.run(seed_request, run_id="seed-run"))
    discovery_result = asyncio.run(
        workflow.run(seed_request.model_copy(update={"seed_urls": []}), run_id="discovery-run")
    )

    source_url = "https://www.fmc.gov/cross-run-source"
    assert repository.sources[source_url].is_seed is True
    assert discovery_result.distillation_count == 0
    assert ("seed-run", source_url) not in repository.source_snapshots
    assert ("discovery-run", source_url) not in repository.source_snapshots
    assert ("seed-run", source_url) not in repository.distillations
    assert ("discovery-run", source_url) not in repository.distillations


def test_llm_input_budget_matches_provider_source_truncation() -> None:
    class FullCoverageLLM(FakeLLM):
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
            if lane != "regulatory":
                return result
            return result.model_copy(
                update={
                    "sources": [
                        source.model_copy(
                            update={
                                "geographies": [
                                    "Regulatory",
                                    "United States",
                                    "West Coast",
                                    "East Coast",
                                    "Gulf",
                                    "Mexico",
                                    "Europe",
                                ]
                            }
                        )
                        for source in result.sources
                    ]
                }
            )

    repository = InMemoryRepository()
    workflow = ResearchWorkflow(
        repository,
        LargeBodyTavily(),
        FullCoverageLLM(),
        max_llm_input_chars=10_000,
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


def test_workflow_rejects_policy_invalid_model_sources_before_persistence() -> None:
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), UnsafeModelSourceLLM())

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
    assert repository.sources == {}
    assert repository.source_snapshots == {}


def test_workflow_does_not_fallback_to_direct_tavily_extraction() -> None:
    tavily = EmptyExtractTavily()
    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, tavily, FakeLLM())
    source = SourceCandidate(url="https://example.com/agent-only")

    try:
        asyncio.run(
            workflow._extract(
                {
                    "run_id": "run-1",
                    "sources": [source],
                    "content": {source.url: " "},
                    "partial_reasons": [],
                }
            )
        )
    except ProviderError as error:
        assert "extraction missing content" in str(error)
    else:
        raise AssertionError("workflow unexpectedly accepted missing agent extraction")

    assert tavily.calls == 0
    assert repository.source_snapshots == {}
    associated_sources = repository.get_run_sources("run-1")
    assert len(associated_sources) == 1
    assert associated_sources[0].extraction_status is ExtractionStatus.FAILED
    assert associated_sources[0].extraction_error_code == "missing_content"


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


def test_workflow_reports_discovery_and_persistence_events() -> None:
    events: list[tuple[str, str, dict[str, object]]] = []

    class Progress:
        def emit(self, event: str, message: str, **details: object) -> None:
            events.append((event, message, details))

    repository = InMemoryRepository()
    workflow = ResearchWorkflow(
        repository,
        FakeTavily(),
        FakeLLM(),
        progress=Progress(),
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="canary",
    )

    asyncio.run(
        workflow._discover_lanes(
            {
                "run_id": "run-progress",
                "request": request,
                "topic": workflow.topic_configs[request.topic_set],
            }
        )
    )

    event_names = {event for event, _, _ in events}
    assert "discovery" in event_names
    assert "persist" in event_names
