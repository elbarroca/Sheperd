from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock, patch

from psycopg import OperationalError

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    ReportBullet,
    ResearchRunRequest,
    RunStatus,
    SignalEvent,
    SourceCandidate,
)
from sheperd_research.db import InMemoryRepository, PostgresRepository


def test_repository_filters_and_exposes_run_artifacts() -> None:
    repository = InMemoryRepository()
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
    )
    repository.create_run("run-1", request)
    repository.update_run_status("run-1", RunStatus.SUCCEEDED)
    repository.record_step(
        "run-1",
        "discovery:us-ports",
        "succeeded",
        {"source_count": 1},
        lane="us-ports",
        duration_ms=12,
        input_hash="input",
        output_hash="output",
    )
    source = SourceCandidate(
        url="https://example.com/article",
        title="Port update",
        publisher="Example",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
        retrieved_at=datetime(2026, 8, 19, tzinfo=UTC),
        source_kind="test",
        geographies=["West Coast"],
        lane="us-ports",
        evidence_status=EvidenceStatus.UNVERIFIED,
    )
    repository.record_source(source)
    repository.record_snapshot("run-1", source, "evidence")
    claim = ClaimDraft(
        claim="A port signal exists.",
        source_urls=[source.url],
    )
    repository.record_distillation(
        "run-1",
        ArticleDistillation(
            source_url=source.url,
            summary="A source summary.",
            claims=[claim],
            content_hash="distillation-hash",
        ),
    )
    repository.record_claims("run-1", [claim])
    repository.record_signal_events(
        [
            SignalEvent(
                event_id="event-1",
                run_id="run-1",
                event_type="source-linked-claim",
                summary=claim.claim,
                source_urls=[source.url],
            )
        ]
    )

    assert repository.list_runs(topic_set="dnd-port", status=RunStatus.SUCCEEDED)
    assert repository.list_sources(geography="West Coast", lane="us-ports") == [source]
    assert repository.get_run_steps("run-1")[0]["duration_ms"] == 12
    assert repository.get_run_distillations("run-1")[0].claims[0].claim == claim.claim
    assert repository.get_run_signal_events("run-1")[0].event_id == "event-1"


def test_repository_keeps_report_sections_and_monthly_rollups() -> None:
    repository = InMemoryRepository()
    repository.create_run("run-2", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/monthly", lane="mexico")
    repository.record_source(source)
    repository.record_snapshot("run-2", source, "monthly evidence")
    repository.record_signal_events(
        [
            SignalEvent(
                event_id="event-2",
                run_id="run-2",
                event_type="signal",
                summary="Monthly signal",
                event_at=datetime(2026, 8, 19, tzinfo=UTC),
                geographies=["Mexico"],
                source_urls=[source.url],
            )
        ]
    )
    from sheperd_research.contracts import WeeklyBrief

    repository.record_brief(
        WeeklyBrief(
            run_id="run-2",
            title="Monthly-backed brief",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="Draft.",
            executive_bullets=[ReportBullet(text="Signal", source_urls=[source.url])],
        )
    )

    brief = repository.get_brief("run-2")
    assert brief is not None
    assert brief.executive_bullets[0].text == "Signal"
    assert repository.monthly_rollup()[0] == {
        "month": "2026-08-01",
        "signals": 1,
        "runs": 1,
        "geographies": ["Mexico"],
    }


def test_in_memory_source_upsert_promotes_existing_source_for_seed() -> None:
    repository = InMemoryRepository()
    normal = SourceCandidate(
        url="https://example.com/article",
        source_kind="discovery",
        evidence_status=EvidenceStatus.VERIFIED,
    )
    seed = SourceCandidate(
        url=normal.url,
        source_kind="trade-media",
        is_seed=True,
        evidence_status=EvidenceStatus.VERIFIED,
    )

    repository.record_source(normal)
    repository.record_source(seed)
    repository.record_source(normal)

    stored = repository.sources[normal.url]
    assert stored.is_seed is True
    assert stored.source_kind == "seed-only"
    assert stored.evidence_status is EvidenceStatus.UNVERIFIED


def test_in_memory_source_upsert_preserves_normal_source_without_seed() -> None:
    repository = InMemoryRepository()
    first = SourceCandidate(
        url="https://example.com/article",
        title="First source",
        source_kind="discovery",
        evidence_status=EvidenceStatus.VERIFIED,
    )
    replacement = SourceCandidate(
        url=first.url,
        title="Replacement source",
        source_kind="trade-media",
        evidence_status=EvidenceStatus.UNVERIFIED,
    )

    repository.record_source(first)
    repository.record_source(replacement)

    assert repository.sources[first.url] == first


def test_postgres_source_upsert_promotes_seed_metadata() -> None:
    repository = PostgresRepository(Mock())
    normal = SourceCandidate(
        url="https://example.com/article",
        source_kind="discovery",
        evidence_status=EvidenceStatus.VERIFIED,
    )
    seed = SourceCandidate(
        url=normal.url,
        source_kind="trade-media",
        is_seed=True,
        evidence_status=EvidenceStatus.VERIFIED,
    )

    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.record_source(normal)
        repository.record_source(seed)

    query = execute.call_args_list[1].args[0]
    params = execute.call_args_list[1].args[1]
    assert "WHEN sources.is_seed OR EXCLUDED.is_seed THEN 'seed-only'" in query
    assert "WHEN sources.is_seed OR EXCLUDED.is_seed THEN 'unverified'" in query
    assert "ELSE sources.source_kind" in query
    assert "ELSE sources.evidence_status" in query
    assert params[6] == "seed-only"
    assert params[11] is True
    assert params[12] is EvidenceStatus.UNVERIFIED


def test_postgres_repository_reconnects_once_after_connection_loss() -> None:
    disconnected = Mock()
    disconnected.cursor.side_effect = OperationalError("SSL connection is closed")
    replacement = Mock()
    cursor = Mock(description=None)
    cursor_context = MagicMock()
    cursor_context.__enter__.return_value = cursor
    cursor_context.__exit__.return_value = False
    replacement.cursor.return_value = cursor_context

    with patch("psycopg.connect", return_value=replacement) as connect:
        repository = PostgresRepository(
            disconnected,
            "main",
            "postgresql://example.test/neondb",
        )
        assert repository._execute("SELECT 1") == []

    connect.assert_called_once()
    replacement.commit.assert_called_once()
