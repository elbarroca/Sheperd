from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from psycopg import InternalError, OperationalError

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DecisionScore,
    DistillationQualityStatus,
    EvidenceStatus,
    ExtractionStatus,
    PageType,
    PublicationDateBasis,
    ReportBullet,
    ResearchRunRequest,
    RunKind,
    RunStatus,
    SignalEvent,
    SourceCandidate,
    ValidationCheck,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.db import (
    MIGRATION_VERSION,
    InMemoryRepository,
    PostgresRepository,
    run_migrations,
)


def test_task4_migration_adds_structured_audit_indexes_without_raw_storage() -> None:
    migration = (
        Path(__file__).parents[1] / "migrations" / "0008_audit_surfaces.sql"
    ).read_text(encoding="utf-8")

    assert "ADD COLUMN IF NOT EXISTS sanitized_args JSONB" in migration
    assert "agent_tool_calls_run_lane_idx" in migration
    assert "source_snapshots_run_hash_idx" in migration
    assert "article_distillations_run_evidence_idx" in migration
    assert "claims_run_evidence_idx" in migration
    assert "signal_events_run_evidence_idx" in migration
    assert "vector" not in migration.lower()
    assert "CREATE TABLE" not in migration.upper()


def test_fresh_migrations_apply_in_order_without_checkpoint_tables_or_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Cursor:
        def __init__(self) -> None:
            self.rows: list[tuple[object, ...]] = []
            self.statements: list[str] = []

        def __enter__(self) -> Cursor:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def execute(self, statement: str, _: tuple[object, ...] = ()) -> None:
            self.statements.append(statement)
            if statement.startswith("SELECT version"):
                self.rows = []

        def fetchall(self) -> list[tuple[object, ...]]:
            return self.rows

    class Connection:
        def __init__(self) -> None:
            self.cursor_instance = Cursor()

        def __enter__(self) -> Connection:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def cursor(self) -> Cursor:
            return self.cursor_instance

        def commit(self) -> None:
            return None

    connection = Connection()
    monkeypatch.setattr("psycopg.connect", lambda *_args, **_kwargs: connection)
    migrations_dir = Path(__file__).parents[1] / "migrations"

    applied = run_migrations("postgresql://no-credential-needed", migrations_dir)

    expected = [path.name for path in sorted(migrations_dir.glob("*.sql"))]
    assert applied == expected
    redaction = (migrations_dir / "0007_redact_checkpoint_transients.sql").read_text(
        encoding="utf-8"
    )
    assert "to_regclass('public.checkpoint_blobs')" in redaction
    assert "to_regclass('public.checkpoints')" in redaction
    assert "to_regclass('public.checkpoint_writes')" in redaction


def test_migrations_enforce_the_exact_gemma_database_policy() -> None:
    migrations_dir = Path(__file__).parents[1] / "migrations"
    migration_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(migrations_dir.glob("*.sql"))
    )

    assert "DEFAULT 'openrouter/free'" not in migration_text
    strict_migration = (migrations_dir / "0009_strict_gemma_policy.sql").read_text(
        encoding="utf-8"
    )
    assert (
        "ALTER COLUMN model_id SET DEFAULT 'google/gemma-4-26b-a4b-it:free'"
        in strict_migration
    )
    assert "IS DISTINCT FROM 'google/gemma-4-26b-a4b-it:free'" in strict_migration


def test_0016_adds_repair_lineage_snapshots_and_complete_event_contract() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "0016_repair_lineage_event_contract.sql"
    ).read_text(encoding="utf-8")

    assert MIGRATION_VERSION == "0016_repair_lineage_event_contract"
    assert not migration.startswith("BEGIN;")
    assert not migration.rstrip().endswith("COMMIT;")
    assert "ADD COLUMN IF NOT EXISTS run_kind" in migration
    assert "ADD COLUMN IF NOT EXISTS parent_run_id" in migration
    assert "ADD COLUMN IF NOT EXISTS repair_round" in migration
    assert "ADD COLUMN IF NOT EXISTS source_snapshot JSONB" in migration
    assert "ADD COLUMN IF NOT EXISTS published_at_snapshot TIMESTAMPTZ" in migration
    assert "ADD COLUMN IF NOT EXISTS retrieved_at_snapshot TIMESTAMPTZ" in migration
    assert "snapshot_basis" in migration
    assert "'legacy_backfill'" in migration
    assert "published_at_snapshot = s.published_at" in migration
    assert "retrieved_at_snapshot = s.retrieved_at" in migration
    assert "COALESCE(s.published_at, s.retrieved_at)" not in migration
    for column in (
        "headline",
        "what_changed",
        "published_at",
        "retrieved_at",
        "period_status",
        "period_basis",
        "eligible_for_weekly",
        "region",
        "lane",
        "evidence_locator",
        "impact",
        "risk",
        "opportunity",
        "next_step",
        "limitations",
    ):
        assert f"ADD COLUMN IF NOT EXISTS {column}" in migration


def test_in_memory_run_lineage_and_source_snapshots_are_parent_scoped() -> None:
    repository = InMemoryRepository()
    parent_request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("parent", parent_request)
    repair_request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=1,
    )
    repository.create_run("repair-p-parent-r1", repair_request)
    original = SourceCandidate(
        url="https://example.com/source",
        title="Original title",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
    )
    repository.record_source(original, run_id="parent")
    repository.record_source(
        original.model_copy(update={"title": "Mutable canonical title"}),
        run_id="repair-p-parent-r1",
    )
    for run_id in ("parent", "repair-p-parent-r1"):
        repository.record_brief(
            WeeklyBrief(
                run_id=run_id,
                title=f"Brief {run_id}",
                covered_from=datetime(2026, 8, 18, tzinfo=UTC),
                covered_until=datetime(2026, 8, 19, tzinfo=UTC),
                summary="Draft.",
            )
        )

    repair_run = repository.get_run("repair-p-parent-r1")
    assert repair_run is not None
    assert repair_run["run_kind"] == "repair"
    assert repair_run["parent_run_id"] == "parent"
    assert repair_run["repair_round"] == 1
    assert repository.get_run_sources("parent")[0].title == "Original title"
    assert [run["run_id"] for run in repository.list_runs()] == ["parent"]
    assert {
        run["run_id"] for run in repository.list_runs(include_repairs=True)
    } == {"parent", "repair-p-parent-r1"}
    assert [brief.run_id for brief in repository.list_briefs()] == ["parent"]


def test_run_source_period_eligibility_requires_direct_complete_scored_evidence() -> None:
    repository = InMemoryRepository()
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 28, tzinfo=UTC),
    )
    repository.create_run("eligibility", request)
    score = DecisionScore(
        sheperd_relevance=30,
        operational_impact=25,
        actionability=20,
        recency=15,
        source_authority=10,
        total=100,
    )
    direct = SourceCandidate(
        url="https://example.com/direct",
        published_at=datetime(2026, 8, 25, tzinfo=UTC),
        extraction_status=ExtractionStatus.SUCCEEDED,
        page_type=PageType.ARTICLE,
        direct_content=True,
        publication_date_basis=PublicationDateBasis.PAGE,
        lane="us-ports",
        region="us",
    )
    archive = direct.model_copy(
        update={
            "url": "https://example.com/news",
            "page_type": PageType.ARCHIVE,
            "direct_content": False,
        }
    )
    unscored = direct.model_copy(update={"url": "https://example.com/unscored"})
    feed = direct.model_copy(update={"url": "https://example.com/comments/feed"})
    for source in (direct, archive, unscored, feed):
        repository.record_source(source, run_id="eligibility")
    for source in (direct, archive, feed):
        repository.record_distillation(
            "eligibility",
            ArticleDistillation(
                source_url=source.url,
                summary="Complete decision packet.",
                quality_status=DistillationQualityStatus.COMPLETE,
                decision_score=score,
                insight_packet={"decision_score": score.model_dump(mode="json")},
            ),
        )

    repository.set_run_source_periods(
        "eligibility",
        datetime(2026, 8, 21, tzinfo=UTC),
        datetime(2026, 8, 28, tzinfo=UTC),
    )

    periods = repository.get_run_source_periods("eligibility")
    assert periods[direct.url]["eligible_for_weekly"] is True
    assert periods[archive.url]["period_status"] == "in_period"
    assert periods[archive.url]["eligible_for_weekly"] is False
    assert periods[unscored.url]["eligible_for_weekly"] is False
    assert periods[feed.url]["eligible_for_weekly"] is False


def test_postgres_period_eligibility_reads_the_immutable_snapshot_and_packet() -> None:
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute") as execute:
        repository.set_run_source_periods(
            "run-1",
            datetime(2026, 8, 21, tzinfo=UTC),
            datetime(2026, 8, 28, tzinfo=UTC),
        )

    query = execute.call_args.args[0]
    assert "rs.source_snapshot ->> 'direct_content'" in query
    assert "rs.source_snapshot ->> 'page_type'" in query
    assert "rs.source_snapshot ->> 'publication_date_basis'" in query
    assert "ad.insight_packet -> 'decision_score'" in query
    assert "/feed" in query


def test_postgres_persists_repair_lineage_and_run_source_snapshot() -> None:
    repository = PostgresRepository(Mock(), neon_branch_id="main")
    request = ResearchRunRequest(
        topic_set="dnd-port",
        context_version="commit:manifest",
        research_timezone="Europe/Lisbon",
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent",
        repair_round=2,
    )
    source = SourceCandidate(
        url="https://example.com/source?token=secret",
        title="Snapshot title",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
        retrieved_at=datetime(2026, 8, 19, tzinfo=UTC),
        lane="us-ports",
    )

    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.create_run("repair-run", request)
        repository.record_source(source, run_id="repair-run")

    create_query, create_params = execute.call_args_list[0].args
    assert "run_kind, parent_run_id, repair_round" in create_query
    assert create_params[8] == "workflow-v4-reader"
    assert create_params[-3:] == (RunKind.REPAIR, "parent", 2)
    persisted_request = json.loads(create_params[2])
    assert persisted_request["context_version"] == "commit:manifest"
    assert persisted_request["research_timezone"] == "Europe/Lisbon"

    snapshot_query, snapshot_params = execute.call_args_list[2].args
    assert "source_snapshot" in snapshot_query
    assert "published_at_snapshot" in snapshot_query
    assert "retrieved_at_snapshot" in snapshot_query
    assert "FROM research_runs" in snapshot_query
    snapshot = json.loads(snapshot_params[4])
    assert snapshot["url"] == "https://example.com/source"
    assert snapshot["title"] == "Snapshot title"
    assert snapshot_params[5] == source.published_at
    assert snapshot_params[6] == source.retrieved_at
    assert snapshot_params[7] == "captured"


def test_postgres_signal_event_round_trip_uses_complete_contract() -> None:
    repository = PostgresRepository(Mock())
    event = SignalEvent(
        event_id="event-1",
        run_id="run-1",
        event_type="port",
        summary="A port update.",
        headline="Port update",
        what_changed="The port changed its published operating guidance.",
        published_at=datetime(2026, 8, 18, tzinfo=UTC),
        retrieved_at=datetime(2026, 8, 19, tzinfo=UTC),
        period_status="in_period",
        period_basis="published_at",
        eligible_for_weekly=True,
        region="us",
        lane="us-ports",
        source_urls=["https://example.com/source"],
        evidence_locator="paragraph 2",
        impact="Operators may need to adjust.",
        risk="Not observed: no material risk was established.",
        opportunity="Not observed: no opportunity was established.",
        next_step="Monitor the port update.",
        limitations=["One public source."],
    )

    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.record_signal_events([event])
    assert "headline, what_changed" in execute.call_args.args[0]
    assert "limitations" in execute.call_args.args[0]

    row = (
        event.event_id,
        event.event_type,
        event.summary,
        event.geographies,
        event.ports,
        event.carriers,
        event.event_at,
        event.source_urls,
        event.evidence_status.value,
        event.headline,
        event.what_changed,
        event.published_at,
        event.retrieved_at,
        event.period_status.value,
        event.period_basis.value,
        event.eligible_for_weekly,
        event.region,
        event.lane,
        event.evidence_locator,
        event.impact,
        event.risk,
        event.opportunity,
        event.next_step,
        event.limitations,
    )
    with patch.object(repository, "_execute", return_value=[row]):
        loaded = repository.get_run_signal_events("run-1")

    assert loaded == [event]


def test_postgres_run_source_reads_use_the_immutable_snapshot() -> None:
    repository = PostgresRepository(Mock())
    retrieved_at = datetime(2026, 8, 19, tzinfo=UTC)
    snapshot = SourceCandidate(
        url="https://example.com/snapshot",
        title="Captured title",
        published_at=None,
        retrieved_at=retrieved_at,
        lane="regulatory",
    ).model_dump(mode="json")
    row = (
        snapshot,
        None,
        retrieved_at,
        "succeeded",
        None,
        "undated",
        "unknown",
        False,
    )

    with patch.object(repository, "_execute", return_value=[row]) as execute:
        loaded = repository.get_run_sources("run-1")

    query = execute.call_args.args[0]
    assert "rs.source_snapshot" in query
    assert "rs.published_at_snapshot" in query
    assert loaded[0].title == "Captured title"
    assert loaded[0].published_at is None
    assert loaded[0].retrieved_at == retrieved_at


def test_in_memory_clone_run_evidence_preserves_parent_hashes_and_packets() -> None:
    repository = InMemoryRepository()
    parent_request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("parent", parent_request)
    child_request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="repair",
        run_kind="repair",
        parent_run_id="parent",
        repair_round=1,
    )
    repository.create_run("child", child_request)
    source = SourceCandidate(
        url="https://example.com/source",
        extraction_status=ExtractionStatus.SUCCEEDED,
    )
    claim = ClaimDraft(claim="A cited claim.", source_urls=[source.url])
    distillation = ArticleDistillation(
        source_url=source.url,
        summary="Complete summary.",
        key_points=["Point one.", "Point two."],
        claims=[claim],
    )
    repository.record_source(source, run_id="parent")
    repository.record_snapshot("parent", source, "immutable body")
    repository.record_distillation("parent", distillation)
    repository.record_claims("parent", [claim])

    repository.clone_run_evidence("parent", "child", [source.url])

    assert repository.get_run_sources("child") == repository.get_run_sources("parent")
    assert repository.get_run_snapshot_hashes("child") == repository.get_run_snapshot_hashes(
        "parent"
    )
    assert repository.get_run_distillations("child") == [distillation]
    assert repository.get_run_claims("child") == [claim]


def test_in_memory_retention_copies_latest_snapshot_receipt_without_content() -> None:
    repository = InMemoryRepository()
    repository.create_run("origin", ResearchRunRequest(topic_set="dnd-port"))
    repository.create_run("weekly", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/source")
    repository.record_source(source, run_id="origin")
    repository.record_snapshot("origin", source, "immutable source body")
    origin_hash = repository.get_run_snapshot_hashes("origin")[0]

    copied_hash = repository.copy_latest_source_snapshot("weekly", source.url)

    assert copied_hash == origin_hash
    assert repository.get_run_snapshot_hashes("weekly") == [origin_hash]
    assert "content" not in repository.source_snapshots[("weekly", source.url)]


def test_postgres_retention_copies_latest_snapshot_receipt_append_only() -> None:
    repository = PostgresRepository(Mock())
    expected_hash = "a" * 64
    with patch.object(
        repository,
        "_execute",
        side_effect=[[(expected_hash,)]],
    ) as execute:
        copied_hash = repository.copy_latest_source_snapshot(
            "weekly",
            "https://example.com/source?secret=redacted",
        )

    query, params = execute.call_args.args
    assert copied_hash == expected_hash
    assert "INSERT INTO source_snapshots" in query
    assert "SELECT %s, normalized_url, content_hash, content_length, retrieved_at" in query
    assert "DELETE" not in query.upper()
    assert params == (
        "weekly",
        "https://example.com/source",
        "weekly",
    )


def test_audit_separates_raw_legacy_defects_from_resolved_repair_parents() -> None:
    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/source")
    repository.record_source(source, run_id="parent")
    repository.record_distillation(
        "parent",
        ArticleDistillation(source_url=source.url, summary="Legacy packet."),
    )
    child_request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="repair",
        run_kind="repair",
        parent_run_id="parent",
        repair_round=1,
    )
    repository.create_run("child", child_request)
    repository.update_run_status("child", RunStatus.SUCCEEDED)
    repository.record_validation(
        ValidationReport(
            run_id="child",
            status=ValidationStatus.PASS,
            checks=[
                ValidationCheck(
                    name="reader_source_contract",
                    status=ValidationStatus.PASS,
                    observed=1,
                    expected=1,
                    message="direct dated scored article contract",
                )
            ],
        )
    )

    history = repository.audit_summary()["history_quality"]

    assert history["raw_defect_parent_count"] == 1
    assert history["resolved_parent_count"] == 1
    assert history["unresolved_parent_count"] == 0
    assert history["unresolved_parent_ids"] == []


def test_audit_does_not_treat_a_legacy_pass_as_reader_contract_repair() -> None:
    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/source")
    repository.record_source(source, run_id="parent")
    repository.record_distillation(
        "parent",
        ArticleDistillation(source_url=source.url, summary="Legacy packet."),
    )
    repository.create_run(
        "child",
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind="repair",
            parent_run_id="parent",
            repair_round=1,
        ),
    )
    repository.update_run_status("child", RunStatus.SUCCEEDED)
    repository.record_validation(
        ValidationReport(run_id="child", status=ValidationStatus.PASS)
    )

    history = repository.audit_summary()["history_quality"]

    assert history["resolved_parent_count"] == 0
    assert history["unresolved_parent_count"] == 1
    assert history["unresolved_parent_ids"] == ["parent"]


def test_audit_keeps_source_less_raw_defects_out_of_the_repair_gate() -> None:
    repository = InMemoryRepository()
    repository.create_run("raw-only", ResearchRunRequest(topic_set="dnd-port"))

    history = repository.audit_summary()["history_quality"]

    assert history["raw_defect_parent_count"] == 1
    assert history["resolved_parent_count"] == 0
    assert history["unresolved_parent_count"] == 0
    assert history["unresolved_parent_ids"] == []


def test_audit_keeps_unenrolled_source_defects_out_of_the_repair_gate() -> None:
    repository = InMemoryRepository()
    repository.create_run("raw-only", ResearchRunRequest(topic_set="dnd-port"))
    repository.record_source(
        SourceCandidate(url="https://example.com/source"),
        run_id="raw-only",
    )

    history = repository.audit_summary()["history_quality"]

    assert history["raw_defect_parent_count"] == 1
    assert history["repair_parent_count"] == 0
    assert history["unresolved_parent_count"] == 0
    assert history["unresolved_parent_ids"] == []


def test_postgres_history_gate_uses_reader_contract_and_validated_child() -> None:
    repository = PostgresRepository(Mock())
    with patch.object(
        repository,
        "_execute",
        side_effect=[
            [(0,) * 14],
            [("neondb", "schema_migrations", "16")],
            [(MIGRATION_VERSION,)],
            [(0, 0, 0, 0, 0)],
            [],
        ],
    ) as execute:
        repository.audit_summary()

    history_query = execute.call_args_list[-1].args[0]
    assert "source_snapshot ->> 'direct_content'" in history_query
    assert "source_snapshot ->> 'page_type'" in history_query
    assert "source_snapshot ->> 'publication_date_basis'" in history_query
    assert "ad.prompt_version LIKE 'distill-v7%%'" in history_query
    assert "decision_score" in history_query
    assert "reader_source_contract" in history_query
    assert "child.parent_run_id = parent.run_id" in history_query
    assert "/feed" in history_query


def test_postgres_clone_run_evidence_is_append_only_and_parent_scoped() -> None:
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.clone_run_evidence(
            "parent",
            "child",
            ["https://example.com/source?token=secret"],
        )

    assert execute.call_count == 4
    queries = [call.args[0] for call in execute.call_args_list]
    assert "INSERT INTO run_sources" in queries[0]
    assert "INSERT INTO source_snapshots" in queries[1]
    assert "INSERT INTO article_distillations" in queries[2]
    assert "INSERT INTO claims" in queries[3]
    assert all("DELETE" not in query.upper() for query in queries)
    assert all(call.args[1][:2] == ("child", "parent") for call in execute.call_args_list)
    assert execute.call_args_list[0].args[1][2] == ["https://example.com/source"]


def test_postgres_health_blocks_stale_or_missing_schema_migration() -> None:
    repository = PostgresRepository(Mock(), neon_branch_id="branch-1")

    with patch.object(
        repository,
        "_execute",
        side_effect=[
            [("neondb", "schema_migrations", "16.0")],
            [("0012_article_insight_quality",)],
        ],
    ):
        stale = repository.health()

    assert stale["status"] == "blocked"
    assert stale["database"] == "neondb"
    assert stale["migration_version"] == "0012_article_insight_quality"
    assert stale["expected_migration_version"] == MIGRATION_VERSION
    assert "schema_migration_stale" in stale["blocking_reasons"]
    assert "user" not in stale

    with patch.object(
        repository,
        "_execute",
        return_value=[("neondb", None, "16.0")],
    ):
        missing = repository.health()

    assert missing["status"] == "blocked"
    assert missing["migration_version"] is None
    assert "schema_migration_missing" in missing["blocking_reasons"]


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


def test_in_memory_repository_exposes_structured_step_audit_and_source_hashes() -> None:
    repository = InMemoryRepository()
    request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("audit-run", request)
    source = SourceCandidate(url="https://example.com/audit")
    repository.record_source(source)
    repository.record_snapshot("audit-run", source, "hashed evidence")
    repository.record_step(
        "audit-run",
        "critic",
        "succeeded",
        {
            "call": {
                "requested_model": "google/gemma-4-26b-a4b-it:free",
                "resolved_model": "google/gemma-4-26b-a4b-it:free",
                "prompt_version": "critic-v4",
                "request_id": "request-1",
                "input_tokens": 11,
                "output_tokens": 7,
                "total_tokens": 18,
                "tool_calls": 0,
            }
        },
        lane="system",
        attempt=1,
        duration_ms=25,
        input_hash="input-hash",
        output_hash="output-hash",
    )

    step = repository.get_run_steps("audit-run")[0]

    assert step["requested_model"] == "google/gemma-4-26b-a4b-it:free"
    assert step["resolved_model"] == "google/gemma-4-26b-a4b-it:free"
    assert step["prompt_version"] == "critic-v4"
    assert step["total_tokens"] == 18
    assert repository.get_run_snapshot_hashes("audit-run")


def test_repositories_redact_raw_step_metadata_before_persistence() -> None:
    metadata = {
        "source_count": 1,
        "selection_basis": "captured_tool_evidence_fallback",
        "prompt": "PROMPT_SECRET",
        "reasoning": "REASONING_SECRET",
        "article_body": "BODY_SECRET",
        "api_key": "KEY_SECRET",
        "call": {
            "requested_model": "google/gemma-4-26b-a4b-it:free",
            "prompt_version": "critic-v4",
            "input_tokens": 11,
            "tool_call_receipts": [
                {
                    "tool_name": "tavily_search",
                    "query": "QUERY_SECRET",
                    "input_hash": "input-hash",
                    "result_count": 2,
                    "status": "succeeded",
                }
            ],
            "prompt": "NESTED_PROMPT_SECRET",
        },
        "attempts": [{"reasoning": "NESTED_REASONING_SECRET"}],
    }

    repository = InMemoryRepository()
    repository.record_step("run-1", "critic", "succeeded", metadata)

    stored = json.dumps(repository.get_run_steps("run-1")[0]["metadata"])

    assert '"source_count": 1' in stored
    assert "captured_tool_evidence_fallback" in stored
    assert "critic-v4" in stored
    assert "tavily_search" in stored
    for secret in (
        "PROMPT_SECRET",
        "REASONING_SECRET",
        "BODY_SECRET",
        "KEY_SECRET",
        "QUERY_SECRET",
        "NESTED_PROMPT_SECRET",
        "NESTED_REASONING_SECRET",
    ):
        assert secret not in stored

    postgres = PostgresRepository(Mock())
    with patch.object(postgres, "_execute", return_value=[]) as execute:
        postgres.record_step("run-1", "critic", "succeeded", metadata)

    persisted = json.loads(execute.call_args.args[1][3])
    assert persisted["source_count"] == 1
    assert persisted["selection_basis"] == "captured_tool_evidence_fallback"
    assert persisted["call"]["prompt_version"] == "critic-v4"
    assert "prompt" not in persisted
    assert "reasoning" not in persisted
    assert "api_key" not in persisted


def test_postgres_brief_summaries_recompute_readiness_from_persisted_evidence() -> None:
    repository = PostgresRepository(Mock())
    covered_at = datetime(2026, 8, 19, tzinfo=UTC)
    row = (
        "run-1",
        "Stored ready summary",
        covered_at,
        covered_at,
        "draft",
        "full",
        RunStatus.SUCCEEDED.value,
        ValidationStatus.PASS.value,
        1,
        1,
        1,
        0,
        ["global"],
        ["en"],
        ["regulatory"],
        ["google/gemma-4-26b-a4b-it:free"],
        covered_at,
        None,
        None,
        1,
        0,
        0.0,
        5,
        5,
        "review_required",
        ["incomplete_article_insights"],
        False,
        0.0,
    )

    with (
        patch.object(repository, "_execute", return_value=[row]),
        patch.object(repository, "get_brief", side_effect=AssertionError("N+1 brief hydrate")),
        patch.object(repository, "get_run_sources", side_effect=AssertionError("N+1 sources")),
        patch.object(
            repository,
            "get_run_distillations",
            side_effect=AssertionError("N+1 distillations"),
        ),
    ):
        summaries = repository.list_brief_summaries()

    assert summaries[0]["readiness_status"] == "review_required"
    assert summaries[0]["decision_ready"] is False
    assert summaries[0]["article_count"] == 1
    assert summaries[0]["complete_article_count"] == 0
    blocking_reasons = summaries[0]["blocking_reasons"]
    assert isinstance(blocking_reasons, list)
    assert "incomplete_article_insights" in blocking_reasons
    assert summaries[0]["quality_ready"] is False
    assert summaries[0]["report_section_count"] == 5
    assert summaries[0]["report_section_completeness"] == 0.0


def test_postgres_brief_summary_aggregates_are_scoped_to_the_report_page() -> None:
    repository = PostgresRepository(Mock())
    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.list_brief_summaries(limit=2, offset=4)

    query = execute.call_args.args[0]
    assert "page_briefs AS" in query
    assert "JOIN page_briefs page_source" in query
    assert "JOIN page_briefs page_distillation" in query
    assert "JOIN page_briefs page_claim" in query
    assert "JOIN page_briefs page_signal" in query
    assert "JOIN page_briefs page_article" in query
    assert "/feed" in query
    assert (
        "AND NOT (lower(trim(trailing '/' from split_part(adq.normalized_url"
        in query
    )


def test_postgres_report_count_excludes_repair_runs_by_default() -> None:
    repository = PostgresRepository(Mock())
    with patch.object(repository, "_execute", return_value=[(0,)]) as execute:
        repository.count_brief_summaries(ready_only=True)

    assert "rr.run_kind = 'research'" in execute.call_args.args[0]
    assert "/feed" in execute.call_args.args[0]


def test_postgres_trailing_evidence_reads_run_snapshots() -> None:
    repository = PostgresRepository(Mock())
    since = datetime(2026, 8, 12, tzinfo=UTC)
    until = datetime(2026, 8, 19, tzinfo=UTC)
    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.get_trailing_evidence(
            topic_set="dnd-port",
            since=since,
            until=until,
        )

    query = execute.call_args.args[0]
    assert "JOIN run_sources rs" in query
    assert "rs.source_snapshot" in query
    assert "rs.published_at_snapshot" in query
    assert "rs.retrieved_at_snapshot" in query
    assert " s.published_at," not in query


def test_postgres_read_snapshot_reuses_one_read_only_transaction() -> None:
    connection = MagicMock()
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.description = True
    cursor.fetchall.return_value = [(1,)]
    connection.cursor.return_value = cursor
    repository = PostgresRepository(connection)

    with repository.read_snapshot():
        assert repository._execute("SELECT 1") == [(1,)]
        assert repository._execute("SELECT 2") == [(1,)]

    assert [call.args[0] for call in cursor.execute.call_args_list] == [
        "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY",
        "SELECT 1",
        "SELECT 2",
    ]
    connection.commit.assert_not_called()


def test_postgres_brief_summaries_restore_provider_blocking_reasons() -> None:
    repository = PostgresRepository(Mock())
    covered_at = datetime(2026, 8, 19, tzinfo=UTC)
    row = (
        "provider-failed-run",
        "Provider failed summary",
        covered_at,
        covered_at,
        "draft",
        "full",
        RunStatus.FAILED.value,
        ValidationStatus.FAILED.value,
        1,
        0,
        0,
        0,
        ["global"],
        ["en"],
        ["regulatory"],
        ["google/gemma-4-26b-a4b-it:free"],
        covered_at,
        covered_at,
        "validation_failed",
        1,
        0,
        0.0,
        0,
        5,
        "review_required",
        ["run_not_succeeded", "validation_not_passed"],
        False,
        0.0,
    )
    checks = [
        {
            "name": "provider_error_codes",
            "status": "failed",
            "observed": "provider_unavailable,rate_limit,timeout",
            "expected": "none",
            "message": "provider/extraction error codes persisted in run evidence",
        }
    ]

    def execute(query: str, _params: tuple[object, ...] = ()) -> list[tuple[object, ...]]:
        return [(*row, checks)] if "vc.checks" in query else [row]

    with (
        patch.object(repository, "_execute", side_effect=execute),
        patch.object(repository, "get_validation", side_effect=AssertionError("N+1 validation")),
    ):
        summary = repository.list_brief_summaries()[0]

    provider_blocking_reasons = summary["blocking_reasons"]
    assert isinstance(provider_blocking_reasons, list)
    assert {
        "provider_rate_limit",
        "provider_timeout",
        "provider_unavailable",
    }.issubset(provider_blocking_reasons)


def test_postgres_brief_summaries_validate_report_section_text_and_counts() -> None:
    repository = PostgresRepository(Mock())
    covered_at = datetime(2026, 8, 19, tzinfo=UTC)
    row: tuple[object, ...] = (
        "run-1",
        "Stored ready summary",
        covered_at,
        covered_at,
        "draft",
        "full",
        RunStatus.SUCCEEDED.value,
        ValidationStatus.PASS.value,
        1,
        1,
        1,
        0,
        ["global"],
        ["en"],
        ["regulatory"],
        ["google/gemma-4-26b-a4b-it:free"],
        covered_at,
        None,
        None,
        1,
        1,
        1.0,
        4,
        5,
        "review_required",
        ["empty_report_section"],
        False,
        0.8,
        [],
    )

    with patch.object(repository, "_execute", return_value=[row]) as execute:
        summary = repository.list_brief_summaries()[0]

    query = execute.call_args.args[0]
    assert "bullet.value ->> 'text'" in query
    assert "CASE WHEN (" in query
    raw_section_count = (
        "jsonb_array_length(\n"
        "                           COALESCE(wb.executive_bullets"
    )
    assert raw_section_count not in query
    assert summary["article_count"] == 1
    assert summary["report_sections_complete"] == 4
    assert summary["report_section_count"] == 5
    assert summary["report_section_completeness"] == 0.8


def test_postgres_brief_summaries_return_production_ready_section_metrics() -> None:
    repository = PostgresRepository(Mock())
    covered_at = datetime(2026, 8, 19, tzinfo=UTC)
    row: tuple[object, ...] = (
        "ready-run",
        "Production-shaped ready summary",
        covered_at,
        covered_at,
        "approved",
        "full",
        RunStatus.SUCCEEDED.value,
        ValidationStatus.PASS.value,
        3,
        3,
        5,
        1,
        ["global"],
        ["en"],
        ["regulatory"],
        ["google/gemma-4-26b-a4b-it:free"],
        covered_at,
        None,
        None,
        3,
        3,
        1.0,
        5,
        5,
        "decision_ready",
        [],
        True,
        1.0,
        [],
        1.0,
    )

    with patch.object(repository, "_execute", return_value=[row]):
        summary = repository.list_brief_summaries(ready_only=True)[0]

    assert summary["decision_ready"] is True
    assert summary["readiness_status"] == "decision_ready"
    assert summary["quality_ready"] is True
    assert summary["article_count"] == 3
    assert summary["complete_article_count"] == 3
    assert summary["report_sections_complete"] == 5
    assert summary["report_section_count"] == 5
    assert summary["report_section_completeness"] == 1.0


def test_postgres_brief_summaries_scope_article_completeness_to_non_seed_sources() -> None:
    repository = PostgresRepository(Mock())
    covered_at = datetime(2026, 8, 19, tzinfo=UTC)
    row: tuple[object, ...] = (
        "scoped-run",
        "Scoped ready summary",
        covered_at,
        covered_at,
        "approved",
        "full",
        RunStatus.SUCCEEDED.value,
        ValidationStatus.PASS.value,
        1,
        3,
        1,
        0,
        ["global"],
        ["en"],
        ["regulatory"],
        ["google/gemma-4-26b-a4b-it:free"],
        covered_at,
        None,
        None,
        1,
        1,
        1.0,
        5,
        5,
        "decision_ready",
        [],
        True,
        1.0,
        [],
    )

    with patch.object(repository, "_execute", return_value=[row]) as execute:
        summary = repository.list_brief_summaries(ready_only=True)[0]

    query = execute.call_args.args[0]
    assert "count(DISTINCT adq.normalized_url) FILTER" in query
    assert "rsa.normalized_url = adq.normalized_url" in query
    assert "AND NOT sa.is_seed" in query
    assert "complete_article_count" in query
    assert summary["article_count"] == 1
    assert summary["complete_article_count"] == 1
    assert summary["article_insight_completeness"] == 1.0
    assert summary["source_distillation_coverage"] == 1.0


def test_repositories_reject_new_oversized_evidence_excerpt_writes() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/oversized-write",
        summary="Summary.",
        evidence_excerpts=["word " * 41],
    )

    with pytest.raises(ValueError, match="evidence_excerpts entries"):
        InMemoryRepository().record_distillation("run-1", distillation)

    postgres = PostgresRepository(Mock())
    with (
        pytest.raises(ValueError, match="evidence_excerpts entries"),
        patch.object(postgres, "_execute") as execute,
    ):
        postgres.record_distillation("run-1", distillation)
    execute.assert_not_called()


def test_in_memory_ready_only_rejects_stale_invalid_report_bullets() -> None:
    repository = InMemoryRepository()
    run_id = "invalid-brief-run"
    source_url = "https://example.com/valid-source"
    request = ResearchRunRequest(
        topic_set="dnd-port",
        as_of=datetime(2026, 8, 19, tzinfo=UTC),
    )
    source = SourceCandidate(
        url=source_url,
        extraction_status=ExtractionStatus.SUCCEEDED,
    )
    claim = ClaimDraft(
        claim="The source reports a development.",
        source_urls=[source_url],
    )
    insight = ArticleInsight(
        status="not_observed",
        statement="No supported risk was observed.",
        why_it_matters="The source does not establish a risk.",
        next_step="Review an independent source.",
    )

    repository.create_run(run_id, request)
    repository.update_run_status(run_id, RunStatus.SUCCEEDED)
    repository.record_source(source)
    repository.record_snapshot(run_id, source, "source content")
    repository.record_distillation(
        run_id,
        ArticleDistillation(
            source_url=source_url,
            summary="Complete summary.",
            key_points=["Point one.", "Point two."],
            claims=[claim],
            what_happened="The source reports a development.",
            why_it_matters="It changes the operating picture.",
            risk_assessment=insight,
            opportunity_assessment=insight,
            uncertainties=["The source has limited scope."],
            next_steps=["Review an independent source."],
            evidence_locators=["paragraph 1"],
            quality_status="complete",
        ),
    )
    repository.record_brief(
        WeeklyBrief(
            run_id=run_id,
            title="Invalid bullets",
            covered_from=datetime(2026, 8, 18, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="Summary.",
            executive_bullets=[ReportBullet(text="Executive.", source_urls=[source_url])],
            developments=[ReportBullet(text="Development.", source_urls=[source_url])],
            risks=[
                ReportBullet(
                    text="Risk.",
                    source_urls=[source_url],
                    why_it_matters="unknown",
                    next_step="Monitor.",
                )
            ],
            opportunities=[
                ReportBullet(
                    text="Opportunity.",
                    source_urls=[source_url],
                    why_it_matters="Opportunity context.",
                    next_step="Monitor.",
                )
            ],
            uncertainties=[
                ReportBullet(
                    text="Uncertainty.",
                    source_urls=[source_url],
                    why_it_matters="Uncertainty context.",
                    next_step="Monitor.",
                )
            ],
            follow_up_questions=["What next?"],
        )
    )
    repository.record_validation(
        ValidationReport(run_id=run_id, status=ValidationStatus.PASS)
    )

    assert repository.list_briefs(ready_only=True) == []
    assert repository.list_brief_summaries(ready_only=True) == []


def test_validation_revalidation_replaces_report_metadata_without_replacing_steps() -> None:
    first_report = ValidationReport(
        run_id="run-1",
        status=ValidationStatus.BLOCKED,
        model_id="google/gemma-4-26b-a4b-it:free",
    )
    memory = InMemoryRepository()
    memory.record_step("run-1", "critic", "succeeded", {"status": "first"})
    memory.record_step("run-1", "critic", "failed", {"status": "replacement"})
    memory.record_validation(first_report)
    replacement = first_report.model_copy(update={"status": ValidationStatus.PASS})
    memory.record_validation(replacement)
    assert memory.steps[0]["status"] == "succeeded"
    assert memory.get_validation("run-1") is replacement

    repository = PostgresRepository(Mock())
    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.record_step("run-1", "critic", "succeeded", {"status": "first"})
        repository.record_validation(first_report)

    queries = [entry.args[0] for entry in execute.call_args_list]
    assert "ON CONFLICT (run_id, agent_name, attempt) DO NOTHING" in queries[0]
    assert "ON CONFLICT (run_id) DO UPDATE" in queries[1]
    assert "checks = EXCLUDED.checks" in queries[1]


def test_postgres_validation_load_restores_persisted_blocking_reasons() -> None:
    checks = [
        {
            "name": "provider_error_codes",
            "status": "failed",
            "observed": "provider_unavailable,rate_limit,timeout",
            "expected": "none",
            "message": "provider/extraction error codes persisted in run evidence",
        }
    ]
    row = (
        "provider-failed-run",
        ValidationStatus.FAILED.value,
        1,
        1,
        0,
        0,
        0.0,
        ["regulatory"],
        checks,
        "google/gemma-4-26b-a4b-it:free",
        "validation-v1",
        datetime(2026, 8, 19, tzinfo=UTC),
        "validation-hash",
    )
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute", return_value=[row]):
        report = repository.get_validation("provider-failed-run")

    assert report is not None
    assert {
        "provider_rate_limit",
        "provider_timeout",
        "provider_unavailable",
    }.issubset(report.blocking_reasons)


def test_postgres_source_persistence_uses_sanitized_url() -> None:
    source = SourceCandidate(
        url="https://safe.example/article?api_key=KEY_SECRET&token=TOKEN_SECRET"
    )
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute", return_value=[]) as execute:
        repository.record_source(source)

    params = execute.call_args.args[1]
    assert params[0] == "https://safe.example/article"
    assert params[1] == "https://safe.example/article"
    assert "KEY_SECRET" not in json.dumps(params, default=str)
    assert "TOKEN_SECRET" not in json.dumps(params, default=str)


def test_postgres_failed_source_has_run_membership_without_a_snapshot() -> None:
    source = SourceCandidate(
        url="https://example.com/failed-extraction",
        extraction_status=ExtractionStatus.FAILED,
        extraction_error_code="provider_unavailable",
    )
    repository = PostgresRepository(Mock())

    with patch.object(
        repository,
        "_execute",
        side_effect=[[("discovery", False, "unverified")], []],
    ) as execute:
        repository.record_source(source, run_id="failed-run")

    association_query, association_params = execute.call_args_list[1].args
    assert "INSERT INTO run_sources" in association_query
    assert association_params[:2] == ("failed-run", source.url)
    assert association_params[2:4] == (
        ExtractionStatus.FAILED,
        "provider_unavailable",
    )
    assert json.loads(association_params[4])["url"] == source.url
    assert association_params[7] == "captured"

    row = (
        source.url,
        source.title,
        source.publisher,
        source.published_at,
        source.retrieved_at,
        source.source_kind,
        source.snippet,
        source.topics,
        source.geographies,
        source.lane,
        source.is_seed,
        source.evidence_status.value,
        source.region,
        source.language_code,
        source.language_confidence,
        source.authority_tier,
        source.catalog_source_id,
        source.source_type,
        source.freshness_status.value,
        source.freshness_days,
        source.extraction_status.value,
        source.extraction_error_code,
        source.normalized_title_en,
        source.normalized_snippet_en,
    )
    with patch.object(repository, "_execute", return_value=[row]) as execute:
        loaded = repository.get_run_sources("failed-run")

    assert "FROM run_sources" in execute.call_args.args[0]
    assert loaded[0].extraction_status is ExtractionStatus.FAILED
    assert loaded[0].extraction_error_code == "provider_unavailable"


def test_postgres_public_source_reads_strip_sensitive_query_values() -> None:
    row = (
        "https://safe.example/article?api_key=KEY_SECRET&token=TOKEN_SECRET",
        "Article",
        "Example",
        datetime(2026, 8, 19, tzinfo=UTC),
        datetime(2026, 8, 20, tzinfo=UTC),
        "discovery",
        "Snippet",
        [],
        ["Europe"],
        "mexico",
        False,
        "unverified",
    )
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute", return_value=[row]):
        listed = repository.list_sources()
    with patch.object(repository, "_execute", return_value=[row]):
        run_sources = repository.get_run_sources("run-1")

    assert listed[0].url == "https://safe.example/article"
    assert run_sources[0].url == "https://safe.example/article"
    serialized = json.dumps(listed + run_sources, default=str)
    assert "KEY_SECRET" not in serialized
    assert "TOKEN_SECRET" not in serialized


def test_postgres_repository_persists_sanitized_tool_arguments() -> None:
    repository = PostgresRepository(Mock())

    with patch.object(repository, "_execute", side_effect=[[(7,)], []]) as execute:
        repository.record_tool_calls(
            "audit-run",
            "discovery:regulatory",
            1,
            "regulatory",
            [
                {
                    "call_index": 0,
                    "tool_name": "tavily_search",
                    "sanitized_args": {"query": "fmc enforcement", "url_count": 0},
                    "input_hash": "input-hash",
                    "result_hash": "result-hash",
                    "result_count": 2,
                    "latency_ms": 31,
                    "status": "succeeded",
                }
            ],
        )

    query = execute.call_args_list[1].args[0]

    assert "sanitized_args" in query
    assert execute.call_args_list[1].args[1][9] == '{"query": "fmc enforcement", "url_count": 0}'


def test_postgres_source_insert_binds_every_source_field() -> None:
    repository = PostgresRepository(Mock())
    source = SourceCandidate(url="https://example.com/source")

    with patch.object(
        repository,
        "_execute",
        return_value=[("discovery", False, "unverified")],
    ) as execute:
        repository.record_source(source)

    query, params = execute.call_args.args
    assert query.count("%s") == len(params) == 25


def test_tool_call_persistence_redacts_sensitive_queries_and_urls() -> None:
    receipt = {
        "call_index": 0,
        "tool_name": "tavily_search",
        "query": "article_body: BODY_SECRET",
        "urls": [
            "https://safe.example/article?ref=raw-content",
            "https://user:PASSWORD_SECRET@private.example/article",
            "javascript:prompt('PROMPT_SECRET')",
        ],
        "sanitized_args": {
            "query": "prompt: PROMPT_SECRET",
            "urls": [
                "https://safe.example/article?ref=raw-content",
                "https://user:PASSWORD_SECRET@private.example/article",
                "javascript:prompt('PROMPT_SECRET')",
            ],
        },
        "input_hash": "input-hash",
        "result_hash": "result-hash",
        "result_count": 2,
        "latency_ms": 31,
        "status": "succeeded",
    }

    in_memory = InMemoryRepository()
    in_memory.record_tool_calls("audit-run", "discovery:regulatory", 1, "regulatory", [receipt])
    stored = in_memory.get_run_tool_calls("audit-run")[0]
    stored_json = json.dumps(stored)

    assert stored["sanitized_args"] == {"query": "[redacted]", "url_count": 1}
    assert "https://safe.example/article" not in stored_json
    for secret in ("BODY_SECRET", "PASSWORD_SECRET", "PROMPT_SECRET"):
        assert secret not in stored_json
    assert stored["input_hash"] == "input-hash"
    assert stored["result_count"] == 2
    assert stored["latency_ms"] == 31
    assert stored["status"] == "succeeded"

    postgres = PostgresRepository(Mock())
    with patch.object(postgres, "_execute", side_effect=[[(7,)], []]) as execute:
        postgres.record_tool_calls(
            "audit-run", "discovery:regulatory", 1, "regulatory", [receipt]
        )

    params = execute.call_args_list[1].args[1]
    assert json.loads(params[8]) == ["https://safe.example/article"]
    assert json.loads(params[9]) == {"query": "[redacted]", "url_count": 1}
    persisted_json = json.dumps(params)
    for secret in ("BODY_SECRET", "PASSWORD_SECRET", "PROMPT_SECRET"):
        assert secret not in persisted_json
    assert params[10] == "input-hash"
    assert params[12] == 2
    assert params[13] == 31
    assert params[14] == "succeeded"


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
        "date": "2026-08-19",
        "lane": "mexico",
        "geography": "Mexico",
        "authority": "Unknown publisher",
        "signal": "signal",
        "evidence": "unverified",
        "signals": 1,
        "runs": 1,
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


def test_postgres_source_upsert_returns_merged_seed_metadata() -> None:
    repository = PostgresRepository(Mock())
    normal = SourceCandidate(
        url="https://example.com/article",
        source_kind="discovery",
        evidence_status=EvidenceStatus.VERIFIED,
    )
    seed = normal.model_copy(update={"is_seed": True, "source_kind": "trade-media"})

    with patch.object(
        repository,
        "_execute",
        side_effect=[[], [("seed-only", True, "unverified")]],
    ):
        repository.record_source(normal)
        merged = repository.record_source(seed)

    assert merged.is_seed is True
    assert merged.source_kind == "seed-only"
    assert merged.evidence_status is EvidenceStatus.UNVERIFIED


def test_postgres_repository_reconnects_once_after_connection_loss() -> None:
    disconnected = Mock()
    disconnected.cursor.side_effect = OperationalError("SSL connection is closed")
    disconnected.rollback.side_effect = OperationalError(
        "another command is already in progress"
    )
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
    disconnected.rollback.assert_not_called()
    disconnected.close.assert_called_once()
    replacement.commit.assert_called_once()


def test_postgres_repository_reconnects_after_aborted_transaction() -> None:
    disconnected = Mock()
    disconnected.cursor.side_effect = InternalError("temporary disk quota failure")
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

    disconnected.rollback.assert_called_once()
    connect.assert_called_once()
    replacement.commit.assert_called_once()
