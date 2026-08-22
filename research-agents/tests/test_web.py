from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DistillationQualityStatus,
    ExtractionStatus,
    InsightStatus,
    ReportBullet,
    ResearchCadence,
    ResearchRunRequest,
    ReviewState,
    SignalEvent,
    SourceCandidate,
    ValidationReport,
    ValidationStatus,
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
    assert weekly_report["readiness_status"] == "review_required"
    assert "incomplete_article_insights" in weekly_report["blocking_reasons"]
    assert client.get("/api/reports/weekly/run-1").status_code == 200
    report_detail = client.get("/api/reports/weekly/run-1").json()
    assert report_detail["quality"]["article_insight_completeness"] == 0.0
    assert report_detail["readiness_status"] == "review_required"
    audit = client.get("/api/runs/run-1/audit")
    assert audit.status_code == 200
    assert "request" not in audit.json()["run"]
    assert "user:secret@example.com" not in audit.text
    assert audit.json()["metrics"]["step_count"] == 1
    assert audit.json()["metrics"]["report_section_completeness"] == 0.0
    monthly = client.get("/api/reports/monthly")
    assert monthly.status_code == 200
    assert monthly.json()["rollups"][0]["geographies"] == ["West Coast"]

    repository.create_run(
        "daily-run",
        ResearchRunRequest(topic_set="dnd-port", cadence=ResearchCadence.DAILY),
    )
    repository.record_brief(
        WeeklyBrief(
            run_id="daily-run",
            title="Daily brief",
            covered_from=datetime(2026, 8, 19, tzinfo=UTC),
            covered_until=datetime(2026, 8, 20, tzinfo=UTC),
            summary="DRAFT - HUMAN REVIEW REQUIRED\n\nDaily summary.",
            review_state=ReviewState.DRAFT,
        )
    )
    daily = client.get("/api/reports/daily")
    assert daily.status_code == 200
    assert [report["run_id"] for report in daily.json()["reports"]] == ["daily-run"]


def test_api_sources_honors_offset_pagination() -> None:
    repository = InMemoryRepository()
    repository.record_source(SourceCandidate(url="https://example.com/one", title="One"))
    repository.record_source(SourceCandidate(url="https://example.com/two", title="Two"))

    client = TestClient(create_app(repository))

    response = client.get("/api/sources?limit=1&offset=1")

    assert response.status_code == 200
    assert [source["title"] for source in response.json()["sources"]] == ["Two"]
    assert client.post("/review").status_code == 404


def test_source_explorer_returns_paged_source_evidence_and_facets() -> None:
    repository = InMemoryRepository()
    repository.create_run(
        "explorer-run",
        ResearchRunRequest(topic_set="dnd-port"),
    )
    source = repository.record_source(
        SourceCandidate(
            url="https://example.com/explorer",
            title="Explorer article",
            publisher="Example",
            region="europe",
            language_code="fr",
            lane="global-market",
            source_type="trade_media",
            authority_tier="secondary",
        )
    )
    repository.record_snapshot("explorer-run", source, "bounded article body")
    claim = ClaimDraft(
        claim="The source reports a port signal.",
        source_urls=[source.url],
        evidence_excerpt="Bounded evidence.",
        citation_status="cited",
    )
    repository.record_distillation(
        "explorer-run",
        ArticleDistillation(
            source_url=source.url,
            summary="English summary.",
            summary_original="Résumé original.",
            source_language="fr",
            key_points=["Point one"],
            claims=[claim],
        ),
    )
    repository.record_claims("explorer-run", [claim])

    client = TestClient(create_app(repository))
    explorer = client.get("/api/sources/explorer?page=1&page_size=1")

    assert explorer.status_code == 200
    payload = explorer.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 1
    assert payload["total"] == 1
    assert payload["has_more"] is False
    assert payload["items"][0]["source"]["url"] == source.url
    assert payload["items"][0]["distillation"]["summary"] == "English summary."
    assert payload["items"][0]["claims"][0]["claim"] == claim.claim
    assert payload["items"][0]["source_hash"]

    facets = client.get("/api/sources/facets")
    assert facets.status_code == 200
    assert "europe" in facets.json()["regions"]
    assert "fr" in facets.json()["languages"]


def test_weekly_summaries_are_ready_first_and_paginated() -> None:
    repository = InMemoryRepository()
    for run_id, status, validation_status in (
        ("draft-run", "partial", ValidationStatus.PARTIAL),
        ("ready-run", "succeeded", ValidationStatus.PASS),
    ):
        repository.create_run(run_id, ResearchRunRequest(topic_set="dnd-port"))
        repository.update_run_status(run_id, status)  # type: ignore[arg-type]
        repository.record_validation(
            ValidationReport(run_id=run_id, status=validation_status)
        )
        repository.record_brief(
            WeeklyBrief(
                run_id=run_id,
                title=run_id,
                covered_from=datetime(2026, 8, 12, tzinfo=UTC),
                covered_until=datetime(
                    2026, 8, 19 if run_id == "ready-run" else 20, tzinfo=UTC
                ),
                summary="Summary.",
                review_state=ReviewState.DRAFT,
            )
        )

    source = repository.record_source(
        SourceCandidate(
            url="https://example.com/ready",
            title="Ready source",
            extraction_status=ExtractionStatus.SUCCEEDED,
        )
    )
    repository.record_snapshot("ready-run", source, "bounded source body")
    claim = ClaimDraft(claim="A supported development.", source_urls=[source.url])
    repository.record_claims("ready-run", [claim])
    repository.record_distillation(
        "ready-run",
        ArticleDistillation(
            source_url=source.url,
            summary="A complete summary.",
            key_points=["Point one.", "Point two."],
            what_happened="The source reports a development.",
            why_it_matters="It changes the operating picture.",
            risk_assessment=ArticleInsight(
                status=InsightStatus.NOT_OBSERVED,
                statement="No supported risk was observed.",
                why_it_matters="The source does not establish a risk.",
                next_step="Check an independent source.",
            ),
            opportunity_assessment=ArticleInsight(
                status=InsightStatus.NOT_OBSERVED,
                statement="No supported opportunity was observed.",
                why_it_matters="The source does not establish an opportunity.",
                next_step="Check an independent source.",
            ),
            uncertainties=["Coverage is limited to this source."],
            next_steps=["Review an independent source."],
            claims=[claim],
            quality_status=DistillationQualityStatus.COMPLETE,
        ),
    )
    bullet = ReportBullet(
        text="A supported development.",
        source_urls=[source.url],
        why_it_matters="It changes the operating picture.",
        next_step="Review an independent source.",
    )
    repository.record_brief(
        WeeklyBrief(
            run_id="ready-run",
            title="ready-run",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="Summary.",
            source_urls=[source.url],
            executive_bullets=[bullet],
            developments=[bullet],
            risks=[bullet],
            opportunities=[bullet],
            uncertainties=[bullet],
            follow_up_questions=["What independent evidence follows?"],
            review_state=ReviewState.DRAFT,
        )
    )

    client = TestClient(create_app(repository))
    response = client.get("/api/reports/weekly?limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["limit"] == 1
    assert payload["offset"] == 0
    assert payload["has_more"] is True
    assert payload["reports"][0]["run_id"] == "ready-run"


def test_markdown_preview_contains_evidence_without_raw_body() -> None:
    repository = InMemoryRepository()
    repository.create_run("markdown-run", ResearchRunRequest(topic_set="dnd-port"))
    source = repository.record_source(
        SourceCandidate(
            url="https://example.com/markdown",
            title="Markdown source",
            publisher="Example",
            region="us",
        )
    )
    repository.record_snapshot("markdown-run", source, "SECRET RAW ARTICLE BODY")
    claim = ClaimDraft(
        claim="A cited development occurred.",
        source_urls=[source.url],
        evidence_excerpt="Short evidence.",
        citation_status="cited",
    )
    repository.record_distillation(
        "markdown-run",
        ArticleDistillation(
            source_url=source.url,
            summary="Article summary.",
            key_points=["Key point"],
            claims=[claim],
        ),
    )
    repository.record_claims("markdown-run", [claim])
    repository.record_brief(
        WeeklyBrief(
            run_id="markdown-run",
            title="Markdown brief",
            covered_from=datetime(2026, 8, 12, tzinfo=UTC),
            covered_until=datetime(2026, 8, 19, tzinfo=UTC),
            summary="Executive summary.",
            source_urls=[source.url],
            review_state=ReviewState.DRAFT,
        )
    )

    response = TestClient(create_app(repository)).get(
        "/api/reports/weekly/markdown-run/markdown"
    )

    assert response.status_code == 200
    assert "## Article findings" in response.text
    assert "Article summary." in response.text
    assert "Short evidence." in response.text
    assert "SECRET RAW ARTICLE BODY" not in response.text
