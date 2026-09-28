from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    SourceCandidate,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.db import InMemoryRepository
from sheperd_research.exporters.obsidian import (
    export_reviewed_brief,
    render_weekly_markdown,
)
from sheperd_research.exporters.regional_indexes import generate_regional_indexes


def test_export_rejects_unreviewed_brief(tmp_path: Path) -> None:
    brief = WeeklyBrief(
        run_id="run-1",
        title="Draft report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Draft summary.",
        signal_event_ids=[],
        source_urls=["https://example.com/article"],
        review_state=ReviewState.DRAFT,
    )

    with pytest.raises(PermissionError, match="reviewed"):
        export_reviewed_brief(brief, tmp_path / "report.md")


def test_export_writes_only_approved_brief(tmp_path: Path) -> None:
    brief = WeeklyBrief(
        run_id="run-2",
        title="Approved report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="DRAFT - HUMAN REVIEW REQUIRED\n\nReviewed summary.",
        signal_event_ids=[],
        source_urls=["https://example.com/article"],
        review_state=ReviewState.APPROVED,
    )

    validation = ValidationReport(
        run_id="run-2",
        status=ValidationStatus.PASS,
        source_count=10,
        unique_source_count=10,
        claim_count=5,
        cited_claim_count=5,
        citation_coverage=1.0,
    )

    destination = export_reviewed_brief(
        brief,
        tmp_path / "report.md",
        validation=validation,
    )

    assert destination.read_text(encoding="utf-8").startswith("---\n")
    assert "status: approved" in destination.read_text(encoding="utf-8")
    assert "DRAFT - HUMAN REVIEW REQUIRED" not in destination.read_text(encoding="utf-8")


def test_export_rejects_approved_brief_with_partial_validation(tmp_path: Path) -> None:
    brief = WeeklyBrief(
        run_id="run-3",
        title="Partial report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Reviewed summary.",
        source_urls=["https://example.com/article"],
        review_state=ReviewState.APPROVED,
    )
    validation = ValidationReport(run_id="run-3", status=ValidationStatus.PARTIAL)

    with pytest.raises(PermissionError, match="passing validation"):
        export_reviewed_brief(brief, tmp_path / "report.md", validation=validation)


def test_weekly_markdown_renderer_is_reader_first_and_hides_audit_details() -> None:
    source = SourceCandidate(
        url="https://example.com/article",
        title="Article title",
        publisher="Example",
        region="us",
        language_code="es",
        extraction_status="succeeded",
    )
    claim = ClaimDraft(
        claim="A port signal changed.",
        original_claim="Cambió una señal portuaria.",
        source_urls=[source.url],
        evidence_excerpt="Bounded excerpt.",
        citation_status="cited",
    )
    brief = WeeklyBrief(
        run_id="full-report",
        title="Full report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Executive summary.",
        source_urls=[source.url],
        limitations=["One limitation."],
        review_state=ReviewState.DRAFT,
        executive_bullets=[ReportBullet(text="Executive signal.", source_urls=[source.url])],
        developments=[ReportBullet(text="Development.", source_urls=[source.url])],
        risks=[
            ReportBullet(
                text="Risk.",
                source_urls=[source.url],
                why_it_matters="It may change the operating picture.",
                next_step="Monitor the source.",
            )
        ],
        opportunities=[
            ReportBullet(
                text="Opportunity.",
                source_urls=[source.url],
                why_it_matters="It may create an opening.",
                next_step="Validate the signal.",
            )
        ],
        uncertainties=[
            ReportBullet(
                text="Uncertainty.",
                source_urls=[source.url],
                why_it_matters="The evidence remains incomplete.",
                next_step="Seek a confirming source.",
            )
        ],
        follow_up_questions=["What should be monitored next?"],
    )
    markdown = render_weekly_markdown(
        brief,
        validation=ValidationReport(
            run_id="full-report",
            status=ValidationStatus.PARTIAL,
            source_count=1,
            claim_count=1,
            cited_claim_count=1,
            citation_coverage=1.0,
        ),
        sources=[source],
        distillations=[
            ArticleDistillation(
                source_url=source.url,
                summary="English summary.",
                summary_original="Resumen original.",
                key_points=["Key point."],
                source_language="es",
                translation_status="succeeded",
                claims=[claim],
            )
        ],
        claims=[claim],
        source_hashes={source.url: "hash-1"},
    )

    assert "## Executive summary" in markdown
    assert "## Report status" in markdown
    assert "## Three things to know" in markdown
    assert "## Top action" in markdown
    assert "## All new findings" in markdown
    assert "## Background context" in markdown
    assert "## Source index and validation" in markdown
    assert source.url in markdown
    assert "Resumen original." not in markdown
    assert "Bounded excerpt." not in markdown
    assert "hash-1" not in markdown
    assert "Agent steps" not in markdown
    assert "Tool receipts" not in markdown
    assert "Locator:" not in markdown
    assert "prompt" not in markdown.lower()
    assert "SECRET RAW ARTICLE BODY" not in markdown
    assert markdown.index("## Three things to know") < markdown.index("## Top action")
    assert markdown.index("## Top action") < markdown.index("## Executive summary")
    assert markdown.index("<!-- pdf-page-break -->") > markdown.index(
        "## Executive summary"
    )


def test_regional_index_contains_structured_evidence_without_raw_body(tmp_path: Path) -> None:
    repository = InMemoryRepository()
    request = ResearchRunRequest(topic_set="dnd-port")
    repository.create_run("index-run", request)
    source = SourceCandidate(
        url="https://example.com/article",
        title="French port update",
        publisher="example.com",
        region="europe",
        language_code="fr",
        geographies=["Europe"],
    )
    claim = ClaimDraft(
        claim="A port signal was reported.",
        original_claim="Un signal portuaire a été signalé.",
        source_urls=[source.url],
        evidence_excerpt="A bounded excerpt.",
        citation_status="cited",
    )
    repository.record_source(source)
    repository.record_snapshot("index-run", source, "RAW ARTICLE BODY MUST NOT EXPORT")
    repository.record_distillation(
        "index-run",
        ArticleDistillation(
            source_url=source.url,
            summary="Normalized English summary.",
            summary_original="Résumé original.",
            key_points=["English point"],
            key_points_original=["Point original"],
            source_language="fr",
            claims=[claim],
        ),
    )
    repository.record_claims("index-run", [claim])

    result = generate_regional_indexes(
        repository,
        tmp_path,
        run_id="index-run",
        regions="all",
    )

    index = (tmp_path / "Europe/index.md").read_text(encoding="utf-8")
    manifest = (tmp_path / "manifest.json").read_text(encoding="utf-8")
    assert result["status"] == "partial"
    assert "Normalized English summary." in index
    assert "Résumé original." in index
    assert "RAW ARTICLE BODY MUST NOT EXPORT" not in index
    assert "Europe/index.md" in manifest
