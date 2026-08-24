from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from sheperd_research.cli import _parser
from sheperd_research.contracts import (
    ResearchRunRequest,
    ReviewState,
    RunStatus,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.web import create_app


def _brief(run_id: str) -> WeeklyBrief:
    return WeeklyBrief(
        run_id=run_id,
        title=run_id,
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Summary.",
        review_state=ReviewState.DRAFT,
    )


def _seed_run(
    repository: InMemoryRepository,
    run_id: str,
    status: RunStatus,
    validation_status: ValidationStatus,
) -> None:
    repository.create_run(run_id, ResearchRunRequest(topic_set="dnd-port"))
    repository.update_run_status(run_id, status)
    repository.record_validation(ValidationReport(run_id=run_id, status=validation_status))
    repository.record_brief(_brief(run_id))


def test_failed_validation_runs_are_archived_and_hidden_by_default() -> None:
    repository = InMemoryRepository()
    _seed_run(repository, "ready-run", RunStatus.SUCCEEDED, ValidationStatus.PASS)
    _seed_run(repository, "failed-run", RunStatus.PARTIAL, ValidationStatus.FAILED)

    client = TestClient(create_app(repository))

    active = client.get("/api/reports/weekly")
    archived = client.get("/api/reports/weekly?archive_scope=archived")
    all_reports = client.get("/api/reports/weekly?archive_scope=all")

    assert [report["run_id"] for report in active.json()["reports"]] == ["ready-run"]
    assert archived.json()["reports"][0]["run_id"] == "failed-run"
    assert archived.json()["reports"][0]["archived"] is True
    assert archived.json()["reports"][0]["archive_reason"] == "validation_failed"
    assert {report["run_id"] for report in all_reports.json()["reports"]} == {
        "ready-run",
        "failed-run",
    }


def test_archived_report_detail_requires_explicit_scope() -> None:
    repository = InMemoryRepository()
    _seed_run(repository, "failed-run", RunStatus.PARTIAL, ValidationStatus.FAILED)
    client = TestClient(create_app(repository))

    assert client.get("/api/reports/weekly/failed-run").status_code == 404
    assert client.get(
        "/api/reports/weekly/failed-run?archive_scope=archived"
    ).status_code == 200
    assert client.get(
        "/api/reports/weekly/failed-run/markdown?archive_scope=archived"
    ).status_code == 200


def test_terminal_failure_is_archived_without_deleting_evidence() -> None:
    repository = InMemoryRepository()
    repository.create_run("failed-run", ResearchRunRequest(topic_set="dnd-port"))

    repository.update_run_status("failed-run", RunStatus.FAILED, "provider failure")

    run = repository.get_run("failed-run")
    assert run is not None
    assert run["archived_at"] is not None
    assert run["archive_reason"] == "run_failed"


def test_audit_endpoint_reports_archive_counts_without_secrets() -> None:
    repository = InMemoryRepository()
    _seed_run(repository, "failed-run", RunStatus.PARTIAL, ValidationStatus.FAILED)

    response = TestClient(create_app(repository)).get("/api/audit")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"]["archived"] == 1
    assert payload["reports"]["active"] == 0
    assert "api_key" not in response.text.lower()


def test_audit_command_is_available_as_json() -> None:
    args = _parser().parse_args(["audit", "--json"])

    assert args.command == "audit"
    assert args.json is True


def test_revalidate_command_is_available_with_active_scope() -> None:
    args = _parser().parse_args(["revalidate", "--scope", "active", "--json"])

    assert args.command == "revalidate"
    assert args.scope == "active"
    assert args.json is True
