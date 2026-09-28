from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
from test_workflow import FakeLLM, FakeTavily, _complete_distillation

from sheperd_research.cli import _parser
from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    PageType,
    PublicationDateBasis,
    ResearchRunRequest,
    ReviewState,
    SignalEvent,
    SourceCandidate,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository, PostgresRepository
from sheperd_research.providers.errors import ProviderError
from sheperd_research.workflow import ResearchWorkflow


class RecordingLlm(FakeLLM):
    def __init__(self) -> None:
        self.critic_claims: list[ClaimDraft] = []
        self.synthesis_urls: list[str] = []

    async def critic(
        self,
        claims: list[ClaimDraft],
        source_urls: set[str],
        **_: object,
    ) -> list[ClaimDraft]:
        del source_urls
        self.critic_claims = list(claims)
        return claims

    async def synthesize(
        self,
        run_id: str,
        distillations: list[ArticleDistillation],
        **kwargs: object,
    ) -> WeeklyBrief:
        self.synthesis_urls = [item.source_url for item in distillations]
        return await super().synthesize(run_id, distillations, **kwargs)


def test_parser_accepts_strict_daily_weekly_and_monthly_rollup_commands() -> None:
    daily = _parser().parse_args(
        [
            "run",
            "--topic-set",
            "dnd-port",
            "--cadence",
            "daily",
            "--strict",
            "--json",
            "--run-id",
            "daily-run",
            "--as-of",
            "2026-08-20T00:00:00Z",
        ]
    )
    weekly = _parser().parse_args(
        [
            "run",
            "--topic-set",
            "dnd-port",
            "--cadence",
            "weekly",
            "--strict",
            "--json",
            "--run-id",
            "weekly-run",
            "--as-of",
            "2026-08-20T00:00:00Z",
        ]
    )
    rollup = _parser().parse_args(["rollup", "--month", "2026-08", "--json"])

    assert daily.cadence == "daily"
    assert weekly.cadence == "weekly"
    assert daily.strict is True
    assert daily.json is True
    assert rollup.month == "2026-08"
    assert rollup.json is True


def test_daily_run_persists_a_draft_brief_without_approval() -> None:
    repository = InMemoryRepository()
    llm = RecordingLlm()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)
    request = ResearchRunRequest(
        topic_set="dnd-port",
        cadence="daily",
        as_of=datetime(2026, 8, 20, tzinfo=UTC),
        max_sources=3,
        include_topic_seeds=False,
        validation_profile="canary",
    )

    result = asyncio.run(workflow.run(request))

    brief = repository.get_brief(result.run_id)
    assert result.status.value == "succeeded"
    assert brief is not None
    assert brief.prompt_version == "daily-brief-v7-reader"
    assert brief.review_state is ReviewState.DRAFT
    assert brief.summary.startswith("DRAFT - HUMAN REVIEW REQUIRED")
    assert repository.review_decisions == []
    assert set(result.lane_statuses) == {"regulatory", "us-ports", "mexico"}


def test_weekly_run_combines_retained_seven_day_evidence_with_fresh_discovery() -> None:
    as_of = datetime(2026, 8, 20, tzinfo=UTC)
    repository = InMemoryRepository()
    retained_request = ResearchRunRequest(
        topic_set="dnd-port",
        cadence="daily",
        as_of=as_of - timedelta(days=2),
        validation_profile="canary",
    )
    repository.create_run("daily-run", retained_request)
    retained_source = SourceCandidate(
        url="https://www.fmc.gov/retained-evidence",
        title="Retained evidence",
        publisher="fmc.gov",
        published_at=as_of - timedelta(days=2),
        retrieved_at=as_of - timedelta(days=2),
        topics=["dnd-port"],
        geographies=["West Coast"],
        lane="us-ports",
        evidence_status=EvidenceStatus.VERIFIED,
        direct_content=True,
        page_type=PageType.OFFICIAL_DOCUMENT,
        search_published_at=as_of - timedelta(days=2),
        publication_date_basis=PublicationDateBasis.SEARCH,
        publication_date_locator="tavily.search.published_date",
    )
    retained_claim = ClaimDraft(
        claim="A retained port signal remains material.",
        source_urls=[retained_source.url],
        evidence_status=EvidenceStatus.VERIFIED,
        evidence_excerpt="A retained port signal remains material.",
    )
    repository.record_source(retained_source)
    repository.record_snapshot("daily-run", retained_source, "retained evidence")
    repository.record_distillation(
        "daily-run",
        _complete_distillation(
            retained_source.url,
            summary="Retained summary.",
        ).model_copy(
            update={
                "claims": [retained_claim],
                "published_at": retained_source.published_at,
            }
        ),
    )
    repository.record_claims("daily-run", [retained_claim])

    llm = RecordingLlm()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)
    result = asyncio.run(
        workflow.run(
            ResearchRunRequest(
                topic_set="dnd-port",
                cadence="weekly",
                as_of=as_of,
                max_sources=3,
                include_topic_seeds=False,
                validation_profile="canary",
            )
        )
    )

    assert result.status.value == "succeeded"
    assert retained_source.url in llm.synthesis_urls
    assert any(
        retained_source.url in claim.source_urls for claim in llm.critic_claims
    )
    assert repository.validations[result.run_id].unique_source_count == 3
    assert len(repository.get_run_snapshot_hashes(result.run_id)) == 3
    persisted_claims = repository.list_claims(run_id=result.run_id)
    assert persisted_claims
    assert all(claim.evidence_status is not EvidenceStatus.VERIFIED for claim in persisted_claims)


def test_weekly_retention_skips_sources_without_reader_provenance() -> None:
    as_of = datetime(2026, 8, 20, tzinfo=UTC)
    repository = InMemoryRepository()
    prior_request = ResearchRunRequest(
        topic_set="dnd-port",
        cadence="daily",
        as_of=as_of - timedelta(days=2),
        validation_profile="canary",
    )
    repository.create_run("legacy-run", prior_request)
    source = SourceCandidate(
        url="https://www.fmc.gov/legacy-retained-evidence",
        published_at=as_of - timedelta(days=2),
        retrieved_at=as_of - timedelta(days=2),
        lane="us-ports",
    )
    repository.record_source(source)
    repository.record_snapshot("legacy-run", source, "legacy retained evidence")
    repository.record_distillation(
        "legacy-run",
        _complete_distillation(source.url).model_copy(
            update={"published_at": source.published_at}
        ),
    )

    workflow = ResearchWorkflow(repository, FakeTavily(), RecordingLlm())
    retained_sources, retained_distillations = workflow._retained_evidence(
        ResearchRunRequest(
            topic_set="dnd-port",
            cadence="weekly",
            as_of=as_of,
            max_sources=3,
            include_topic_seeds=False,
            validation_profile="canary",
        )
    )

    assert retained_sources == []
    assert retained_distillations == []


def test_synthesis_is_blocked_when_only_seed_or_no_evidence_exists() -> None:
    repository = InMemoryRepository()
    llm = RecordingLlm()
    workflow = ResearchWorkflow(repository, FakeTavily(), llm)
    request = ResearchRunRequest(
        topic_set="dnd-port",
        cadence="daily",
        as_of=datetime(2026, 8, 20, tzinfo=UTC),
        validation_profile="canary",
        include_topic_seeds=False,
    )
    seed = SourceCandidate(
        url="https://www.fmc.gov/seed-only",
        is_seed=True,
        source_kind="seed-only",
    )

    with pytest.raises(ProviderError, match="no retained or freshly extracted evidence"):
        asyncio.run(
            workflow._synthesize(
                {
                    "run_id": "seed-only-run",
                    "request": request,
                    "topic": workflow.topic_configs[request.topic_set],
                    "sources": [seed],
                    "distillations": [],
                    "claims": [],
                }
            )
        )

    assert llm.synthesis_urls == []
    assert repository.get_brief("seed-only-run") is None


def test_monthly_rollup_groups_date_lane_geography_authority_signal_and_evidence() -> None:
    repository = InMemoryRepository()
    as_of = datetime(2026, 8, 20, tzinfo=UTC)
    request = ResearchRunRequest(topic_set="dnd-port", as_of=as_of)
    repository.create_run("rollup-run", request)
    source = SourceCandidate(
        url="https://www.fmc.gov/monthly",
        publisher="fmc.gov",
        published_at=datetime(2026, 8, 19, tzinfo=UTC),
        lane="regulatory",
        geographies=["United States"],
        evidence_status=EvidenceStatus.VERIFIED,
    )
    repository.record_source(source)
    repository.record_snapshot("rollup-run", source, "monthly evidence")
    repository.record_signal_events(
        [
            SignalEvent(
                event_id="rollup-event",
                run_id="rollup-run",
                event_type="regulatory",
                summary="Monthly signal",
                event_at=datetime(2026, 8, 19, 14, 0, tzinfo=UTC),
                geographies=["United States"],
                source_urls=[source.url],
                evidence_status=EvidenceStatus.VERIFIED,
            )
        ]
    )

    assert repository.monthly_rollup(
        since=datetime(2026, 8, 1, tzinfo=UTC),
        until=datetime(2026, 9, 1, tzinfo=UTC),
    ) == [
        {
            "month": "2026-08-01",
            "date": "2026-08-19",
            "lane": "regulatory",
            "geography": "United States",
            "authority": "fmc.gov",
            "signal": "regulatory",
            "evidence": "verified",
            "signals": 1,
            "runs": 1,
        }
    ]


def test_monthly_rollup_buckets_aware_events_in_utc_without_changing_range_filters() -> None:
    repository = InMemoryRepository()
    repository.create_run(
        "utc-rollup-run",
        ResearchRunRequest(topic_set="dnd-port", as_of=datetime(2026, 8, 1, tzinfo=UTC)),
    )
    source = SourceCandidate(url="https://example.com/utc-boundary")
    repository.record_source(source)
    repository.record_signal_events(
        [
            SignalEvent(
                event_id="utc-rollup-event",
                run_id="utc-rollup-run",
                event_type="timezone",
                summary="UTC boundary signal",
                event_at=datetime(
                    2026, 8, 1, 0, 30, tzinfo=timezone(timedelta(hours=14))
                ),
                geographies=["UTC test"],
                source_urls=[source.url],
            )
        ]
    )
    since = datetime(2026, 7, 31, tzinfo=UTC)
    until = datetime(2026, 8, 1, tzinfo=UTC)

    assert repository.monthly_rollup(since=since, until=until) == [
        {
            "month": "2026-07-01",
            "date": "2026-07-31",
            "lane": "unassigned",
            "geography": "UTC test",
            "authority": "Unknown publisher",
            "signal": "timezone",
            "evidence": "unverified",
            "signals": 1,
            "runs": 1,
        }
    ]

    postgres = PostgresRepository(Mock())
    with patch.object(postgres, "_execute", return_value=[]) as execute:
        assert postgres.monthly_rollup(since=since, until=until) == []
    query, params = execute.call_args.args
    assert "AT TIME ZONE 'UTC'" in query
    assert "event_rows.event_timestamp >= %s" in query
    assert "event_rows.event_timestamp <= %s" in query
    assert params == (since, until, 100, 0)
