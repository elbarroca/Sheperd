from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    ResearchRunRequest,
    ReviewState,
    SignalEvent,
    SourceCandidate,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.web import create_app


def test_dashboard_exposes_read_only_run_source_and_brief_views() -> None:
    repository = InMemoryRepository()
    repository.create_run(
        "run-1",
        ResearchRunRequest(
            topic_set="dnd-port",
            seed_urls=["https://user:secret@example.com/seed"],
        ),
    )
    repository.record_source(
        SourceCandidate(
            url="https://example.com/article",
            title="Port update",
            publisher="Example",
            retrieved_at=datetime(2026, 8, 19, tzinfo=UTC),
            source_kind="test",
            geographies=["West Coast"],
        ),
    )
    source = repository.sources["https://example.com/article"]
    repository.record_snapshot("run-1", source, "persisted source body")
    claim = ClaimDraft(
        claim="The port reported a delay.",
        source_urls=[source.url],
    )
    repository.record_distillation(
        "run-1",
        ArticleDistillation(
            source_url=source.url,
            summary="A persisted source distillation.",
            claims=[claim],
        ),
    )
    repository.record_claims("run-1", [claim])
    repository.record_signal_events(
        [
            SignalEvent(
                event_id="signal-1",
                run_id="run-1",
                event_type="port-delay",
                summary="The port reported a delay.",
                source_urls=[source.url],
            )
        ]
    )
    repository.record_step(
        "run-1",
        "validation",
        "pass",
        {
            "citation_coverage": 1.0,
            "prompt": "must not reach the browser",
            "reasoning": "must not reach the browser",
        },
        input_hash="input-hash",
        output_hash="output-hash",
        duration_ms=7,
    )
    repository.record_brief(
        WeeklyBrief(
            run_id="run-1",
            title="Weekly brief",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="DRAFT - HUMAN REVIEW REQUIRED\n\nSummary.",
            source_urls=["https://example.com/article"],
            review_state=ReviewState.DRAFT,
        )
    )

    client = TestClient(create_app(repository))

    assert client.get("/").status_code == 200
    assert client.get("/sources?query=Port").status_code == 200
    assert client.get("/sources?geography=West%20Coast").status_code == 200
    assert client.get("/briefs").status_code == 200
    run_page = client.get("/runs/run-1")
    assert run_page.status_code == 200
    assert "input-hash" in run_page.text
    runs_response = client.get("/api/runs")
    assert runs_response.status_code == 200
    assert client.get("/api/sources?geography=West%20Coast").status_code == 200
    assert client.get("/api/distillations?run_id=run-1").status_code == 200
    assert client.get("/api/claims?run_id=run-1&limit=1").status_code == 200
    assert client.get("/api/signals?run_id=run-1").status_code == 200
    run_response = client.get("/api/runs/run-1")
    assert run_response.status_code == 200
    public_run = run_response.json()["run"]
    assert public_run["run_id"] == "run-1"
    assert public_run["topic_set"] == "dnd-port"
    assert public_run["status"] == "running"
    assert public_run["migration_version"]
    assert "request" not in public_run
    assert "user:secret@example.com" not in run_response.text
    assert "metadata" not in run_response.json()["steps"][0]
    assert "must not reach the browser" not in run_response.text
    assert client.get("/api/health").status_code == 200
    catalog = client.get("/api/source-catalog")
    assert catalog.status_code == 200
    assert catalog.json()["coverage_weights"]["us"] == 0.6
    assert catalog.json()["sources"][0]["source_id"]
    weekly = client.get("/api/reports/weekly")
    assert weekly.status_code == 200
    assert weekly.json()["count"] == 1
    weekly_report = weekly.json()["reports"][0]
    assert "request" not in weekly_report["run"]
    assert "user:secret@example.com" not in weekly.text
    assert weekly_report["source_hashes"]
    assert weekly_report["claims"][0]["claim"] == claim.claim
    assert weekly_report["signals"][0]["event_id"] == "signal-1"
    assert weekly_report["distillations"][0]["summary"] == "A persisted source distillation."
    assert client.get("/api/reports/weekly/run-1").status_code == 200
    audit = client.get("/api/runs/run-1/audit")
    assert audit.status_code == 200
    assert "request" not in audit.json()["run"]
    assert "user:secret@example.com" not in audit.text
    assert audit.json()["metrics"]["step_count"] == 1
    assert client.get("/api/reports/monthly").status_code == 200


def test_api_sources_honors_offset_pagination() -> None:
    repository = InMemoryRepository()
    repository.record_source(SourceCandidate(url="https://example.com/one", title="One"))
    repository.record_source(SourceCandidate(url="https://example.com/two", title="Two"))

    client = TestClient(create_app(repository))

    response = client.get("/api/sources?limit=1&offset=1")

    assert response.status_code == 200
    assert [source["title"] for source in response.json()["sources"]] == ["Two"]
    assert client.post("/review").status_code == 404
