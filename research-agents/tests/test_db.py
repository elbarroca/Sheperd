from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
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
    assert persisted["call"]["prompt_version"] == "critic-v4"
    assert "prompt" not in persisted
    assert "reasoning" not in persisted
    assert "api_key" not in persisted


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
