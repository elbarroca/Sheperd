from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from sheperd_research.contracts import (
    ReviewState,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.exporters.obsidian import export_reviewed_brief


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
