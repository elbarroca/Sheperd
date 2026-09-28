from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, cast
from urllib.parse import urlsplit

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

import sheperd_research.workflow as workflow_module
from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DecisionScore,
    DistillationQualityStatus,
    EvidenceStatus,
    ExtractionStatus,
    InsightStatus,
    LaneDiscoveryPacket,
    LaneDiscoveryResult,
    PageType,
    PeriodStatus,
    PublicationDateBasis,
    ReportBullet,
    ResearchRunRequest,
    RunKind,
    RunStatus,
    SourceCandidate,
    TopicConfig,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.providers.errors import ProviderError
from sheperd_research.validators import can_extract_url, normalize_url
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
        headline="A public port development",
        event_type="port",
        summary=summary,
        key_points=["Reported point one.", "Reported point two.", "Reported point three."],
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
        prompt_version="distill-v7-reader",
        decision_score=DecisionScore(
            sheperd_relevance=30,
            operational_impact=25,
            actionability=20,
            recency=15,
            source_authority=10,
            total=100,
        ),
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
        return {
            source.url: f"Published: 2026-08-18\nEvidence for {source.title}"
            for source in sources
        }


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
        del since, until, exclude_domains
        sources: list[SourceCandidate] = []
        content: dict[str, str] = {}
        for query in queries:
            found = await tavily.search(query, max_results=max_results)
            domain = include_domains[0]
            scoped_sources: list[SourceCandidate] = []
            for source in found:
                host = (urlsplit(source.url).hostname or "").removeprefix("www.")
                keep_url = host in include_domains or host == "linkedin.com"
                scoped_sources.append(
                    source.model_copy(
                        update={
                            "url": (
                                source.url
                                if keep_url
                                else f"https://{domain}/{query.replace(' ', '-')}"
                            ),
                            "publisher": source.publisher if keep_url else domain,
                            "geographies": list(geographies),
                        }
                    )
                )
            found = scoped_sources
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
            update={
                "key_points": [
                    content,
                    "The source provides public evidence.",
                    "The evidence is bounded to this article.",
                ]
            }
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
    events = repository.get_run_signal_events("run-1")
    assert len(events) == 2
    assert {event.source_urls[0] for event in events} == {
        claimed_source.url,
        source_without_claim.url,
    }
    assert all(event.headline == "A public port development" for event in events)
    assert all(event.event_type == "port" for event in events)
    assert all(event.evidence_locator for event in events)


def test_synthesis_never_uses_event_date_as_a_missing_publication_date() -> None:
    source = SourceCandidate(
        url="https://example.com/undated-article",
        page_type=PageType.ARTICLE,
        direct_content=True,
        extraction_status=ExtractionStatus.SUCCEEDED,
        lane="us-ports",
        region="us",
        geographies=["West Coast"],
    )
    distillation = _complete_distillation(source.url).model_copy(
        update={
            "event_at": datetime(2026, 8, 18, tzinfo=UTC),
            "event_at_locator": "paragraph 2",
        }
    )
    repository = InMemoryRepository()
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
        max_sources=1,
        validation_profile="canary",
    )
    repository.create_run("undated-event", request)
    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())

    asyncio.run(
        workflow._synthesize(
            {
                "run_id": "undated-event",
                "request": request,
                "topic": workflow.topic_configs[request.topic_set],
                "sources": [source],
                "distillations": [distillation],
                "claims": distillation.claims,
            }
        )
    )

    event = repository.get_run_signal_events("undated-event")[0]
    assert event.period_status.value == "undated"
    assert event.period_basis.value == "unknown"
    assert event.eligible_for_weekly is False


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
    assert len(repository.signal_events) == first.distillation_count
    assert repository.briefs[first.run_id].signal_event_ids
    assert repository.briefs[first.run_id].review_state.value == "draft"
    assert first.distillation_count == first.source_count


def test_repair_preserves_incomplete_history_and_writes_a_new_complete_run() -> None:
    repository = InMemoryRepository()
    parent_request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
    )
    source = SourceCandidate(
        url="https://www.fmc.gov/repair-source",
        title="Repair source",
        publisher="fmc.gov",
        lane="regulatory",
        geographies=["Regulatory"],
    )
    repository.create_run("old-run", parent_request)
    repository.record_source(source, run_id="old-run")
    repository.record_distillation(
        "old-run",
        ArticleDistillation(source_url=source.url, summary="Legacy summary."),
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="old-run",
        repair_round=1,
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


def test_repair_reextracts_legacy_seed_as_a_run_evidence_source() -> None:
    class RecordingRepairTavily(FakeTavily):
        def __init__(self) -> None:
            self.extracted_seed_flags: list[bool] = []

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            self.extracted_seed_flags.extend(source.is_seed for source in sources)
            return await super().extract(sources)

    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(
        url="https://www.fmc.gov/legacy-seed",
        title="Legacy seed source",
        publisher="fmc.gov",
        lane="regulatory",
        geographies=["Regulatory"],
        is_seed=True,
    )
    repository.record_source(source, run_id="parent")
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
    )
    tavily = RecordingRepairTavily()

    result = asyncio.run(
        ResearchWorkflow(repository, tavily, FakeLLM()).repair(
            request,
            repository.get_run_sources("parent"),
            "repair-p-parent-r1",
        )
    )

    assert tavily.extracted_seed_flags == [False]
    assert result.status is RunStatus.SUCCEEDED


@pytest.mark.parametrize(
    ("message", "error_code"),
    [
        ("Tavily extraction timed out", "timeout"),
        ("Tavily map did not resolve a direct article", "source_access"),
    ],
)
def test_repair_persists_provider_extraction_failure_for_the_new_run(
    message: str,
    error_code: str,
) -> None:
    class FailingRepairTavily(FakeTavily):
        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            raise ProviderError(message, error_code=error_code)

    repository = InMemoryRepository()
    repository.create_run("old-run", ResearchRunRequest(topic_set="dnd-port"))
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="old-run",
        repair_round=1,
    )
    source = SourceCandidate(url="https://www.fmc.gov/failed-repair-source")
    repository.record_source(source, run_id="old-run")

    result = asyncio.run(
        ResearchWorkflow(repository, FailingRepairTavily(), FakeLLM()).repair(
            request,
            [source],
            "repair-run",
        )
    )

    assert result.status.value == "failed"
    assert result.error == message
    assert result.error_code == error_code
    assert repository.get_run("repair-run")["error"] == error_code
    repaired_sources = repository.get_run_sources("repair-run")
    assert len(repaired_sources) == 1
    assert repaired_sources[0].extraction_status is ExtractionStatus.FAILED
    assert repaired_sources[0].extraction_error_code == error_code


def test_repair_clones_complete_evidence_and_redistills_only_incomplete_sources() -> None:
    class RecordingRepairTavily(FakeTavily):
        def __init__(self) -> None:
            self.extracted_urls: list[str] = []

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            self.extracted_urls.extend(source.url for source in sources)
            return await super().extract(sources)

    repository = InMemoryRepository()
    parent_request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("parent", parent_request)
    complete_source = SourceCandidate(
        url="https://www.fmc.gov/complete",
        title="Complete source title",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
        search_published_at=datetime(2026, 8, 18, tzinfo=UTC),
        publication_date_basis=PublicationDateBasis.SEARCH,
        publication_date_locator="tavily.search.published_date",
        page_type=PageType.ARTICLE,
        direct_content=True,
        extraction_status=ExtractionStatus.SUCCEEDED,
    )
    incomplete_source = SourceCandidate(url="https://www.fmc.gov/incomplete")
    for source in (complete_source, incomplete_source):
        repository.record_source(source, run_id="parent")
    repository.record_snapshot("parent", complete_source, "complete body")
    complete_distillation = _complete_distillation(complete_source.url)
    repository.record_distillation("parent", complete_distillation)
    repository.record_claims("parent", complete_distillation.claims)
    repository.record_distillation(
        "parent",
        ArticleDistillation(
            source_url=incomplete_source.url,
            summary="Legacy incomplete packet.",
        ),
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=2,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
    )
    tavily = RecordingRepairTavily()

    result = asyncio.run(
        ResearchWorkflow(repository, tavily, FakeLLM()).repair(
            request,
            [complete_source, incomplete_source],
            "repair-p-parent-r1",
        )
    )

    assert result.status is RunStatus.SUCCEEDED
    assert result.source_count == 2
    assert result.distillation_count == 2
    assert tavily.extracted_urls == [incomplete_source.url]
    assert len(repository.get_run_sources(result.run_id)) == 2
    assert len(repository.get_run_snapshot_hashes(result.run_id)) == 2
    repaired_distillations = repository.get_run_distillations(result.run_id)
    assert len(repaired_distillations) == 2
    assert next(
        item for item in repaired_distillations if item.source_url == complete_source.url
    ).headline == complete_distillation.headline
    assert len(repository.get_run_signal_events(result.run_id)) == 2


def test_repair_clones_complete_evidence_from_a_prior_failed_child() -> None:
    class RecordingRepairTavily(FakeTavily):
        def __init__(self) -> None:
            self.extracted_urls: list[str] = []

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            self.extracted_urls.extend(source.url for source in sources)
            return await super().extract(sources)

    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(
        url="https://www.fmc.gov/complete-child-evidence",
        title="Complete child evidence",
        page_type=PageType.ARTICLE,
        direct_content=True,
        extraction_status=ExtractionStatus.SUCCEEDED,
    )
    repository.record_source(source, run_id="parent")
    repository.create_run(
        "prior-child",
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind=RunKind.REPAIR,
            parent_run_id="parent",
            repair_round=1,
        ),
    )
    repository.record_source(source, run_id="prior-child")
    repository.record_snapshot("prior-child", source, "complete body")
    distillation = _complete_distillation(source.url)
    repository.record_distillation("prior-child", distillation)
    repository.record_claims("prior-child", distillation.claims)
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=2,
    )
    tavily = RecordingRepairTavily()

    result = asyncio.run(
        ResearchWorkflow(repository, tavily, FakeLLM()).repair(
            request,
            repository.get_run_sources("prior-child"),
            "next-child",
            evidence_run_id="prior-child",
        )
    )

    assert result.status is RunStatus.SUCCEEDED
    assert tavily.extracted_urls == []
    assert len(repository.get_run_distillations("next-child")) == 1


def test_repair_redistills_a_legacy_packet_missing_the_reader_score() -> None:
    class RecordingRepairTavily(FakeTavily):
        def __init__(self) -> None:
            self.extracted_urls: list[str] = []

        async def extract(self, sources: list[SourceCandidate]) -> dict[str, str]:
            self.extracted_urls.extend(source.url for source in sources)
            return await super().extract(sources)

    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(
        url="https://www.fmc.gov/legacy-complete",
        title="Legacy complete source",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
        search_published_at=datetime(2026, 8, 18, tzinfo=UTC),
        publication_date_basis=PublicationDateBasis.SEARCH,
        publication_date_locator="tavily.search.published_date",
        page_type=PageType.ARTICLE,
        direct_content=True,
        extraction_status=ExtractionStatus.SUCCEEDED,
        lane="regulatory",
        region="regulatory",
        geographies=["Regulatory"],
    )
    legacy = _complete_distillation(source.url).model_copy(
        update={
            "prompt_version": "distill-v6-insight",
            "decision_score": None,
            "insight_packet": {},
        }
    )
    repository.record_source(source, run_id="parent")
    repository.record_snapshot("parent", source, "legacy body")
    repository.record_distillation("parent", legacy)
    repository.record_claims("parent", legacy.claims)
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
    )
    tavily = RecordingRepairTavily()

    result = asyncio.run(
        ResearchWorkflow(repository, tavily, FakeLLM()).repair(
            request,
            [source],
            "repair-p-parent-r1",
        )
    )

    assert result.status is RunStatus.SUCCEEDED
    assert tavily.extracted_urls == [source.url]
    repaired = repository.get_run_distillations(result.run_id)
    assert len(repaired) == 1
    assert repaired[0].decision_score is not None


def test_repair_replaces_a_navigation_parent_with_one_direct_child() -> None:
    parent_url = "https://example.com/news"
    child_url = "https://example.com/news/direct-update"

    class ForeignKeyRepository(InMemoryRepository):
        def record_snapshot(
            self,
            run_id: str,
            source: SourceCandidate,
            content: str,
        ) -> None:
            if normalize_url(source.url) not in self.sources:
                raise RuntimeError("run source references an unknown canonical source")
            super().record_snapshot(run_id, source, content)

    class ResolvingRepairTavily(FakeTavily):
        async def resolve_sources(
            self,
            sources: list[SourceCandidate],
            content: dict[str, str],
            *,
            since: datetime,
            until: datetime,
        ) -> tuple[list[SourceCandidate], dict[str, str]]:
            del content, since, until
            assert [source.url for source in sources] == [parent_url]
            child = sources[0].model_copy(
                update={
                    "url": child_url,
                    "title": "Direct update",
                    "published_at": datetime(2026, 8, 18, tzinfo=UTC),
                    "page_published_at": datetime(2026, 8, 18, tzinfo=UTC),
                    "publication_date_basis": PublicationDateBasis.PAGE,
                    "publication_date_locator": "Published: 2026-08-18",
                    "page_type": PageType.ARTICLE,
                    "direct_content": True,
                    "parent_navigation_url": parent_url,
                }
            )
            return [child], {child_url: "Published: 2026-08-18\nDirect evidence."}

    repository = ForeignKeyRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    parent = SourceCandidate(
        url=parent_url,
        title="News archive",
        lane="us-ports",
        region="us",
        geographies=["West Coast"],
    )
    repository.record_source(parent, run_id="parent")
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        include_topic_seeds=False,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
    )

    result = asyncio.run(
        ResearchWorkflow(repository, ResolvingRepairTavily(), FakeLLM()).repair(
            request,
            [parent],
            "repair-p-parent-r1",
        )
    )

    assert result.status is RunStatus.SUCCEEDED
    repaired_sources = repository.get_run_sources(result.run_id)
    assert [source.url for source in repaired_sources] == [child_url]
    assert repaired_sources[0].parent_navigation_url == parent_url
    assert repaired_sources[0].direct_content is True


def test_repair_fails_instead_of_truncating_parent_sources() -> None:
    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    sources = [
        SourceCandidate(url=f"https://www.fmc.gov/source-{index}")
        for index in range(2)
    ]
    for source in sources:
        repository.record_source(source, run_id="parent")
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=1,
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
    )

    result = asyncio.run(
        ResearchWorkflow(repository, FakeTavily(), FakeLLM()).repair(
            request,
            sources,
            "repair-p-parent-r1",
        )
    )

    assert result.status is RunStatus.FAILED
    assert result.error == "parent source count exceeds max_sources"
    assert repository.get_run_sources(result.run_id) == []


def test_canary_discovery_query_limit_bounds_each_lane() -> None:
    class RecordingLLM(FakeLLM):
        def __init__(self) -> None:
            self.queries_by_lane: dict[str, list[str]] = {}
            self.geographies_by_lane: dict[str, tuple[str, ...]] = {}
            self.domains_by_lane: dict[str, list[str]] = {}

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            self.queries_by_lane[lane] = list(queries)
            self.geographies_by_lane[lane] = geographies
            self.domains_by_lane[lane] = list(kwargs["include_domains"])
            domain = self.domains_by_lane[lane][0]
            source = SourceCandidate(
                url=f"https://{domain}/{lane}",
                publisher=domain,
                published_at=datetime(2026, 8, 18, tzinfo=UTC),
                geographies=[geographies[0]],
            )
            return LaneDiscoveryResult(
                packet=LaneDiscoveryPacket(
                    source_urls=[source.url],
                    selected_queries=queries,
                    evidence_notes=["fixture"],
                ),
                sources=[source],
                content={source.url: "fixture evidence"},
            )

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
    assert "regulation" in llm.queries_by_lane["regulatory"][0]
    assert "United States" in llm.queries_by_lane["us-ports"][0]
    assert "Mexico" in llm.queries_by_lane["mexico"][0]
    assert llm.geographies_by_lane == {
        "regulatory": ("Regulatory", "United States"),
        "us-ports": ("West Coast", "East Coast", "Gulf"),
        "mexico": ("Mexico", "Europe"),
    }
    assert "fmc.gov" in llm.domains_by_lane["regulatory"]
    assert "portoflosangeles.org" not in llm.domains_by_lane["regulatory"]
    assert "portoflosangeles.org" in llm.domains_by_lane["us-ports"]
    assert "fmc.gov" not in llm.domains_by_lane["us-ports"]
    assert "puertomanzanillo.com.mx" in llm.domains_by_lane["mexico"]
    assert "portofrotterdam.com" not in llm.domains_by_lane["mexico"]
    assert "fmc.gov" not in llm.domains_by_lane["mexico"]
    assert "theloadstar.com" not in {
        domain
        for domains in llm.domains_by_lane.values()
        for domain in domains
    }


def test_us_mexico_scope_limits_discovery_inputs() -> None:
    class RecordingLLM(FakeLLM):
        def __init__(self) -> None:
            self.queries_by_lane: dict[str, list[str]] = {}
            self.geographies_by_lane: dict[str, tuple[str, ...]] = {}
            self.domains_by_lane: dict[str, list[str]] = {}

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            self.queries_by_lane[lane] = list(queries)
            self.geographies_by_lane[lane] = geographies
            self.domains_by_lane[lane] = list(kwargs["include_domains"])
            return await super().discover_lane(
                lane,
                queries,
                geographies,
                **kwargs,
            )

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
        research_scope="us-mexico",
        new_findings_only=True,
    )

    asyncio.run(
        workflow._discover_lanes(
            {
                "run_id": "us-mexico-scope",
                "request": request,
                "topic": workflow.topic_configs["dnd-port"],
            }
        )
    )

    assert llm.geographies_by_lane == {
        "regulatory": ("Regulatory", "United States"),
        "us-ports": ("West Coast", "East Coast", "Gulf"),
        "mexico": ("Mexico",),
    }
    assert all(
        "Europe" not in geographies and "Canada" not in geographies
        for geographies in llm.geographies_by_lane.values()
    )
    assert "latest Europe" not in " ".join(
        query
        for queries in llm.queries_by_lane.values()
        for query in queries
    )
    assert "portofrotterdam.com" not in {
        domain
        for domains in llm.domains_by_lane.values()
        for domain in domains
    }


def test_new_findings_only_skips_trailing_evidence() -> None:
    class NoRetentionRepository(InMemoryRepository):
        def get_trailing_evidence(
            self, **_: object
        ) -> tuple[list[SourceCandidate], list[ArticleDistillation]]:
            raise AssertionError(
                "new-findings-only runs must not load trailing evidence"
            )

    request = ResearchRunRequest(
        topic_set="dnd-port",
        new_findings_only=True,
    )
    workflow = ResearchWorkflow(NoRetentionRepository(), FakeTavily(), FakeLLM())

    assert workflow._retained_evidence(request) == ([], [])


def test_discovery_retries_retryable_provider_failure() -> None:
    class RetryLLM(FakeLLM):
        def __init__(self) -> None:
            self.calls = 0

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            self.calls += 1
            if self.calls == 1:
                raise ProviderError("discovery returned no usable evidence")
            return await super().discover_lane(
                lane,
                queries,
                geographies,
                **kwargs,
            )

    llm = RetryLLM()
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

    _, sources, _, error, _, metadata = asyncio.run(
        workflow._discover_lane(LANES[0], request, workflow.topic_configs["dnd-port"])
    )

    assert error is None
    assert llm.calls == 2
    assert sources
    assert metadata["discovery_retry"] == {"initial_error_code": "provider_error"}


def test_full_discovery_follows_up_for_missing_lane_coverage() -> None:
    class CoverageLLM(FakeLLM):
        def __init__(self) -> None:
            self.calls: list[list[str]] = []
            self.domain_calls: list[list[str]] = []

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            del lane, geographies
            self.domain_calls.append(list(kwargs["include_domains"]))
            self.calls.append(list(queries))
            selected_geographies = (
                ["Regulatory"]
                if len(self.calls) == 1
                else [query.split(maxsplit=1)[0] for query in queries]
            )
            sources = [
                SourceCandidate(
                    url=f"https://www.fmc.gov/coverage-{len(self.calls)}-{index}",
                    publisher="fmc.gov",
                    published_at=datetime(2026, 8, 18, tzinfo=UTC),
                    geographies=[geography],
                )
                for index, geography in enumerate(selected_geographies)
            ]
            return LaneDiscoveryResult(
                packet=LaneDiscoveryPacket(
                    source_urls=[source.url for source in sources],
                    selected_queries=queries,
                ),
                sources=sources,
                content={source.url: "fixture evidence" for source in sources},
                metadata={
                    "selection_basis": (
                        "model_structured"
                        if len(self.calls) == 1
                        else "captured_tool_evidence_fallback"
                    )
                },
            )

    llm = CoverageLLM()
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        llm,
        discovery_query_limit=None,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
        max_sources=30,
        include_topic_seeds=False,
        validation_profile="full",
    )

    lane, sources, _, error, _, metadata = asyncio.run(
        workflow._discover_lane(
            LANES[0], request, workflow.topic_configs["dnd-port"]
        )
    )

    assert lane == "regulatory"
    assert error is None
    assert len(llm.calls) == 2
    assert {query.split(maxsplit=1)[0] for query in llm.calls[1]} == {
        "Canada",
        "Europe",
    }
    assert {geography for source in sources for geography in source.geographies} >= {
        "Canada",
        "Europe",
    }
    assert metadata["coverage_follow_up"] is True
    assert metadata["selection_basis"] == "captured_tool_evidence_fallback"
    assert "fmc.gov" in llm.domain_calls[0]
    assert "fmc.gov" not in llm.domain_calls[1]
    assert "tc.canada.ca" in llm.domain_calls[1]
    assert "ec.europa.eu" in llm.domain_calls[1]
    assert "theloadstar.com" in llm.domain_calls[1]


def test_failed_coverage_follow_up_preserves_initial_lane_evidence() -> None:
    class CoverageFailureLLM(FakeLLM):
        def __init__(self) -> None:
            self.calls = 0

        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            self.calls += 1
            if self.calls > 1:
                raise ProviderError("coverage follow-up unavailable")
            result = await super().discover_lane(
                lane,
                queries,
                geographies,
                **kwargs,
            )
            return result.model_copy(
                update={
                    "sources": [
                        source.model_copy(update={"geographies": ["West Coast"]})
                        for source in result.sources
                    ]
                }
            )

    llm = CoverageFailureLLM()
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        llm,
        discovery_query_limit=None,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
        max_sources=30,
        include_topic_seeds=False,
        validation_profile="full",
        research_scope="us-mexico",
    )

    lane, sources, _, error, _, metadata = asyncio.run(
        workflow._discover_lane(LANES[1], request, workflow.topic_configs["dnd-port"])
    )

    assert lane == "us-ports"
    assert error is None
    assert len(sources) == 8
    assert llm.calls == 3
    assert metadata["coverage_follow_up_error"] == "provider_error"
    assert metadata["coverage_follow_up_targets"] == ["East Coast", "Gulf"]


def test_discovery_resolves_sources_before_lane_validation_and_persistence() -> None:
    class ResolvingTavily(FakeTavily):
        called = False

        async def resolve_sources(
            self,
            sources: list[SourceCandidate],
            content: dict[str, str],
            **_: object,
        ) -> tuple[list[SourceCandidate], dict[str, str]]:
            self.called = True
            return (
                [
                    source.model_copy(
                        update={
                            "page_type": PageType.ARTICLE,
                            "direct_content": True,
                            "search_published_at": source.published_at,
                            "publication_date_basis": PublicationDateBasis.SEARCH,
                        }
                    )
                    for source in sources
                ],
                content,
            )

    tavily = ResolvingTavily()
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        tavily,
        FakeLLM(),
        discovery_query_limit=1,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
        max_sources=3,
        validation_profile="canary",
    )

    _, sources, _, error, _, _ = asyncio.run(
        workflow._discover_lane(LANES[0], request, workflow.topic_configs["dnd-port"])
    )

    assert error is None
    assert tavily.called is True
    assert all(source.direct_content for source in sources)


def test_canary_mexico_lane_rejects_europe_only_sources() -> None:
    class EuropeOnlyLLM(FakeLLM):
        async def discover_lane(self, *args: object, **kwargs: object) -> LaneDiscoveryResult:
            result = await super().discover_lane(*args, **kwargs)  # type: ignore[arg-type]
            return result.model_copy(
                update={
                    "sources": [
                        source.model_copy(update={"geographies": ["Europe"]})
                        for source in result.sources
                    ]
                }
            )

    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        EuropeOnlyLLM(),
        discovery_query_limit=1,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
        max_sources=3,
        validation_profile="canary",
    )

    _, sources, _, error, _, _ = asyncio.run(
        workflow._discover_lane(LANES[-1], request, workflow.topic_configs["dnd-port"])
    )

    assert sources == []
    assert error is not None


def test_validation_uses_persisted_run_period_classification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_id = "persisted-period-validation"
    request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="canary",
    )
    repository = InMemoryRepository()
    repository.create_run(run_id, request)
    stale_source = SourceCandidate(
        url="https://www.fmc.gov/persisted-period",
        period_status=PeriodStatus.IN_PERIOD,
        eligible_for_weekly=False,
    )
    repository.record_source(
        stale_source.model_copy(update={"eligible_for_weekly": True}),
        run_id=run_id,
    )
    repository.record_source(
        stale_source.model_copy(
            update={
                "url": "https://www.fmc.gov/in-period-but-ineligible",
                "period_status": PeriodStatus.IN_PERIOD,
                "eligible_for_weekly": False,
            }
        ),
        run_id=run_id,
    )
    captured: dict[str, object] = {}

    def capture_validation(**kwargs: Any) -> ValidationReport:
        captured.update(kwargs)
        return ValidationReport(
            run_id=run_id,
            status=ValidationStatus.PASS,
        )

    monkeypatch.setattr(
        workflow_module,
        "build_validation_report",
        capture_validation,
    )
    workflow = ResearchWorkflow(repository, FakeTavily(), FakeLLM())

    asyncio.run(
        workflow._validate(
            {
                "run_id": run_id,
                "request": request,
                "topic": workflow.topic_configs["dnd-port"],
                "sources": [
                    stale_source,
                    stale_source.model_copy(
                        update={"url": "https://www.fmc.gov/in-period-but-ineligible"}
                    ),
                ],
                "retained_sources": [],
                "claims": [],
                "source_hashes": [],
                "lane_statuses": {},
                "distillations": [],
                "signal_events": [],
            }
        )
    )

    validation_sources = cast(list[SourceCandidate], captured["sources"])
    assert validation_sources[0].eligible_for_weekly is True
    assert captured["eligible_weekly_source_count"] == 1


def test_discovery_excludes_retained_sources_from_the_fresh_source_budget() -> None:
    workflow = ResearchWorkflow(
        InMemoryRepository(),
        FakeTavily(),
        FakeLLM(),
        discovery_query_limit=1,
    )
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=3,
        include_topic_seeds=False,
        validation_profile="canary",
    )
    regulatory_query = workflow.topic_configs["dnd-port"].queries[0]
    retained = SourceCandidate(
        url=f"https://www.fmc.gov/{regulatory_query.replace(' ', '-')}",
        lane="regulatory",
    )

    result = asyncio.run(
        workflow._discover_lanes(
            {
                "run_id": "retained-budget",
                "request": request,
                "topic": workflow.topic_configs["dnd-port"],
                "retained_sources": [retained],
            }
        )
    )
    fresh_sources = cast(list[SourceCandidate], result["sources"])

    assert len(fresh_sources) == 2
    assert retained.url not in {source.url for source in fresh_sources}


def test_retained_evidence_is_capped_by_the_run_source_budget() -> None:
    class TrailingRepository(InMemoryRepository):
        def get_trailing_evidence(self, **_: object) -> tuple[
            list[SourceCandidate], list[ArticleDistillation]
        ]:
            sources = [
                SourceCandidate(
                    url=f"https://www.fmc.gov/retained-{index}",
                    lane=LANES[index % len(LANES)].name,
                    direct_content=True,
                    page_type=PageType.OFFICIAL_DOCUMENT,
                )
                for index in range(5)
            ]
            return sources, [
                _complete_distillation(source.url) for source in sources
            ]

    workflow = ResearchWorkflow(TrailingRepository(), FakeTavily(), FakeLLM())
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=3,
        validation_profile="canary",
    )

    sources, distillations = workflow._retained_evidence(request)

    assert len(sources) == 3
    assert len(distillations) == 3
    assert {source.url for source in sources} == {
        distillation.source_url for distillation in distillations
    }


def test_retained_evidence_reserves_budget_for_a_missing_lane() -> None:
    class TrailingRepository(InMemoryRepository):
        def get_trailing_evidence(self, **_: object) -> tuple[
            list[SourceCandidate], list[ArticleDistillation]
        ]:
            sources = [
                SourceCandidate(
                    url=f"https://www.fmc.gov/{lane}-{index}",
                    lane=lane,
                    direct_content=True,
                    page_type=PageType.OFFICIAL_DOCUMENT,
                )
                for index, lane in enumerate(
                    ["regulatory", "regulatory", "mexico", "mexico"]
                )
            ]
            return sources, [
                _complete_distillation(source.url) for source in sources
            ]

    workflow = ResearchWorkflow(TrailingRepository(), FakeTavily(), FakeLLM())
    request = ResearchRunRequest(
        topic_set="dnd-port",
        max_sources=3,
        validation_profile="canary",
    )

    sources, distillations = workflow._retained_evidence(request)

    assert {source.lane for source in sources} == {"regulatory", "mexico"}
    assert len(distillations) == 2


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
        include_domains=[
            "fmc.gov",
            "portoflosangeles.org",
            "puertomanzanillo.com.mx",
        ],
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


def test_critic_uses_small_structured_output_batches() -> None:
    class RecordingCritic(FakeLLM):
        provider_name = "fixture"

        def __init__(self) -> None:
            self.batch_sizes: list[int] = []

        async def critic(
            self,
            claims: list[ClaimDraft],
            source_urls: set[str],
            **_: object,
        ) -> list[ClaimDraft]:
            assert source_urls == {"https://example.com/article"}
            self.batch_sizes.append(len(claims))
            return claims

    repository = InMemoryRepository()
    request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("critic-run", request)
    source = SourceCandidate(url="https://example.com/article")
    claims = [
        ClaimDraft(claim=f"Supported claim {index}.", source_urls=[source.url])
        for index in range(13)
    ]
    llm = RecordingCritic()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)

    result = asyncio.run(
        workflow._critic(
            cast(
                workflow_module.GraphState,
                {
                    "run_id": "critic-run",
                    "request": request,
                    "sources": [source],
                    "claims": claims,
                },
            )
        )
    )

    assert sorted(llm.batch_sizes) == [6, 7]
    assert len(cast(list[ClaimDraft], result["claims"])) == 13


def test_critic_retries_only_a_failed_structured_output_batch() -> None:
    class FlakyCritic(FakeLLM):
        provider_name = "fixture"

        def __init__(self) -> None:
            self.batch_sizes: list[int] = []
            self.failed_large_batch = False

        async def critic(
            self,
            claims: list[ClaimDraft],
            source_urls: set[str],
            **_: object,
        ) -> list[ClaimDraft]:
            assert source_urls == {"https://example.com/article"}
            self.batch_sizes.append(len(claims))
            if len(claims) == 7 and not self.failed_large_batch:
                self.failed_large_batch = True
                raise ProviderError("malformed output", error_code="malformed_output")
            return claims

    repository = InMemoryRepository()
    request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("critic-retry-run", request)
    source = SourceCandidate(url="https://example.com/article")
    claims = [
        ClaimDraft(claim=f"Supported claim {index}.", source_urls=[source.url])
        for index in range(8)
    ]
    llm = FlakyCritic()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)

    result = asyncio.run(
        workflow._critic(
            cast(
                workflow_module.GraphState,
                {
                    "run_id": "critic-retry-run",
                    "request": request,
                    "sources": [source],
                    "claims": claims,
                },
            )
        )
    )

    assert sorted(llm.batch_sizes) == [1, 7, 7]
    assert len(cast(list[ClaimDraft], result["claims"])) == 8


def test_distillation_retries_only_a_failed_source_packet() -> None:
    class FlakyDistiller(FakeLLM):
        def __init__(self) -> None:
            self.calls = 0

        async def distill(
            self,
            source: SourceCandidate,
            content: str,
            **kwargs: object,
        ) -> ArticleDistillation:
            self.calls += 1
            if self.calls == 1:
                raise ProviderError("malformed output", error_code="malformed_output")
            return await super().distill(source, content, **kwargs)

    repository = InMemoryRepository()
    request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("distill-retry-run", request)
    source = SourceCandidate(url="https://example.com/article", title="Article")
    llm = FlakyDistiller()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)

    result = asyncio.run(
        workflow._distill(
            cast(
                workflow_module.GraphState,
                {
                    "run_id": "distill-retry-run",
                    "request": request,
                    "sources": [source],
                    "content": {source.url: "Published: 2026-08-18\nEvidence."},
                },
            )
        )
    )

    assert llm.calls == 2
    assert len(cast(list[ArticleDistillation], result["distillations"])) == 1


def test_weekly_window_includes_the_start_of_the_calendar_day() -> None:
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 25, 12, 22, tzinfo=UTC),
    )
    topic = TopicConfig(
        name="dnd-port",
        description="Fixture topic",
        queries=["port update"],
    )

    assert ResearchWorkflow._run_since(request, topic) == datetime(
        2026, 8, 18, tzinfo=UTC
    )


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


def test_workflow_persists_partial_report_after_discovery_lane_failure() -> None:
    class PartialDiscoveryLLM(FakeLLM):
        async def discover_lane(
            self,
            lane: str,
            queries: list[str],
            geographies: tuple[str, ...],
            **kwargs: Any,
        ) -> LaneDiscoveryResult:
            if lane == "mexico":
                raise ProviderError(
                    "Mexico article access failed",
                    error_code="source_access",
                )
            return await super().discover_lane(
                lane,
                queries,
                geographies,
                **kwargs,
            )

    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), PartialDiscoveryLLM())
    run_id = "partial-discovery-run"
    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=3,
                include_topic_seeds=False,
                validation_profile="canary",
                as_of=datetime(2026, 8, 19, tzinfo=UTC),
            ),
            run_id=run_id,
        )
    )

    assert result.status is RunStatus.FAILED
    assert repository.get_brief(run_id) is not None
    validation = repository.get_validation(run_id)
    assert validation is not None
    assert validation.status is not ValidationStatus.PASS
    assert len(repository.get_run_distillations(run_id)) >= 2
    assert {step["agent_name"] for step in repository.get_run_steps(run_id)} >= {
        "synthesis",
        "validation",
    }


def test_workflow_persists_source_packet_draft_when_synthesis_fails() -> None:
    class FailingSynthesisLLM(FakeLLM):
        async def synthesize(
            self,
            run_id: str,
            distillations: list[ArticleDistillation],
            **kwargs: object,
        ) -> WeeklyBrief:
            del run_id, distillations, kwargs
            raise ProviderError(
                "synthesis citation contract failed",
                error_code="malformed_output",
            )

    repository = InMemoryRepository()
    workflow = ResearchWorkflow(repository, FakeTavily(), FailingSynthesisLLM())
    run_id = "source-packet-fallback-run"
    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                max_sources=3,
                include_topic_seeds=False,
                validation_profile="canary",
                as_of=datetime(2026, 8, 19, tzinfo=UTC),
            ),
            run_id=run_id,
        )
    )

    assert result.status is RunStatus.FAILED
    brief = repository.get_brief(run_id)
    assert brief is not None
    assert brief.summary.startswith("DRAFT - HUMAN REVIEW REQUIRED")
    assert any("malformed_output" in limitation for limitation in brief.limitations)
    assert repository.get_validation(run_id) is not None
    synthesis_step = next(
        step
        for step in repository.get_run_steps(run_id)
        if step["agent_name"] == "synthesis"
    )
    assert synthesis_step["status"] == "failed"


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
