from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import sheperd_research.pdf as pdf_module
from sheperd_research.contracts import PeriodBasis, PeriodStatus
from sheperd_research.costs import estimate_run_cost
from sheperd_research.pdf import markdown_to_print_html, render_pdf, verify_pdf
from sheperd_research.periods import classify_period, weekly_window


def test_period_classification_is_explicit_and_publication_based() -> None:
    covered_from = datetime(2026, 8, 19, tzinfo=UTC)
    covered_until = datetime(2026, 8, 26, tzinfo=UTC)
    as_of = datetime(2026, 8, 26, 12, tzinfo=UTC)

    in_period = classify_period(
        datetime(2026, 8, 20, tzinfo=UTC),
        covered_from=covered_from,
        covered_until=covered_until,
        as_of=as_of,
    )
    background = classify_period(
        datetime(2026, 8, 18, tzinfo=UTC),
        covered_from=covered_from,
        covered_until=covered_until,
        as_of=as_of,
    )
    undated = classify_period(
        None,
        covered_from=covered_from,
        covered_until=covered_until,
        as_of=as_of,
    )
    future = classify_period(
        datetime(2026, 8, 27, tzinfo=UTC),
        covered_from=covered_from,
        covered_until=covered_until,
        as_of=as_of,
    )

    assert (in_period.status, in_period.basis, in_period.eligible_for_weekly) == (
        PeriodStatus.IN_PERIOD,
        PeriodBasis.PUBLISHED_AT,
        True,
    )
    assert background.status is PeriodStatus.BACKGROUND
    assert not background.eligible_for_weekly
    assert undated.status is PeriodStatus.UNDATED
    assert future.status is PeriodStatus.FUTURE


def test_weekly_window_respects_local_calendar_midnight() -> None:
    as_of = datetime(2026, 8, 26, 17, tzinfo=ZoneInfo("Europe/Lisbon"))

    covered_from, covered_until = weekly_window(as_of, "Europe/Lisbon")

    assert covered_from == datetime(2026, 8, 18, 23, tzinfo=UTC)
    assert covered_until == datetime(2026, 8, 26, 16, tzinfo=UTC)


def test_cost_estimate_counts_aggregate_search_calls_and_extracted_urls() -> None:
    estimate = estimate_run_cost(
        [
            {"input_tokens": 1_000, "output_tokens": 500},
        ],
        [
            {"tool_name": "tavily_search", "calls": 2, "status": "succeeded"},
            {
                "tool_name": "tavily_extract",
                "result_count": 5,
                "status": "succeeded",
            },
        ],
    )

    tavily = estimate["tavily"]
    assert isinstance(tavily, dict)
    assert tavily["credits"] == 3
    assert estimate["input_tokens"] == 1_000
    assert estimate["output_tokens"] == 500


def test_print_html_escapes_content_and_preserves_source_links() -> None:
    rendered = markdown_to_print_html(
        "# Report\n\nUnsafe <tag>. `hash-value` [Source](https://example.com/article)"
    )

    assert "&lt;tag&gt;" in rendered
    assert "<code>hash-value</code>" in rendered
    assert '<a href="https://example.com/article">Source</a>' in rendered
    assert "@page" in rendered


def test_print_html_renders_tables_and_explicit_page_breaks() -> None:
    rendered = markdown_to_print_html(
        "| Gate | State |\n"
        "| --- | --- |\n"
        "| Validation | pass |\n\n"
        "<!-- pdf-page-break -->\n\n"
        "## Audit appendix"
    )

    assert '<table class="status-table">' in rendered
    assert "<th>Gate</th>" in rendered
    assert "<td>pass</td>" in rendered
    assert '<div class="page-break"></div>' in rendered
    assert "break-before: page" in rendered


def test_print_html_marks_report_tables_for_print_widths() -> None:
    event_table = markdown_to_print_html(
        "| Date | Event | Type | Region / lane | Evidence | Source |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| 2026-08-26 | Update | port | us / us-ports | mixed | https://example.com |"
    )
    evidence_table = markdown_to_print_html(
        "| Source | Published | Period | Eligible | Snapshot hash |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Example | 2026-08-26 | in_period | yes | abc |"
    )
    source_index = markdown_to_print_html(
        "| Source | Publisher | Published | Date basis | Use | Validation |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| Example | Example | 2026-08-26 | page | current | validated |"
    )
    compact_articles = markdown_to_print_html(
        "| Article | Published | Priority | Region / lane |\n"
        "| --- | --- | --- | --- |\n"
        "| Example | 2026-08-26 | 70 | mexico / mexico |"
    )

    assert '<table class="event-table">' in event_table
    assert '<table class="evidence-table">' in evidence_table
    assert ".event-table" in event_table
    assert ".evidence-table" in evidence_table
    assert '<table class="source-index-table">' in source_index
    assert ".source-index-table" in source_index
    assert '<table class="compact-article-table">' in compact_articles
    assert ".compact-article-table th:nth-child(2) { width: 16%; }" in compact_articles


def test_print_html_uses_custom_report_and_source_styles() -> None:
    rendered = markdown_to_print_html(
        "# USA + Mexico report\n\n"
        "### New finding\n\n"
        "Source: [Authority](https://example.com/article)"
    )

    assert '<div class="report-kicker">SHEPERD / SOURCE-BOUND INTELLIGENCE</div>' in rendered
    assert '<article class="finding-card">' in rendered
    assert '<span class="source-label">SOURCE</span>' in rendered
    assert ".finding-card" in rendered
    assert ".source-line" in rendered


def test_print_html_keeps_escaped_pipes_inside_table_cells() -> None:
    rendered = markdown_to_print_html(
        "| Source | Publisher | Published | Date basis | Use | Validation |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| [Agenda \\| Regular meeting](https://example.com/agenda) | "
        "Example | 2026-08-26 | search | current | validated |"
    )

    assert rendered.count("<td>") == 6
    assert "Agenda | Regular meeting" in rendered
    assert "Agenda \\| Regular meeting" not in rendered


def test_print_html_omits_yaml_frontmatter_from_the_first_page() -> None:
    rendered = markdown_to_print_html(
        "---\n"
        'title: "Internal report"\n'
        "owner: research-agents\n"
        "content_hash: secret-metadata\n"
        "---\n\n"
        "# Visible report"
    )

    assert "Visible report" in rendered
    assert "secret-metadata" not in rendered
    assert "owner: research-agents" not in rendered


def test_verify_pdf_rejects_non_pdf_content(tmp_path: Path) -> None:
    path = tmp_path / "invalid.pdf"
    path.write_bytes(b"%PDF-1.4\nnot a rendered document")

    with pytest.raises(RuntimeError, match=r"pdf_(?:verification|page_count)_failed"):
        verify_pdf(path)


def test_render_pdf_disables_browser_header_footer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> object:
        commands.append(command)
        return object()

    monkeypatch.setattr(pdf_module.subprocess, "run", fake_run)
    monkeypatch.setattr(pdf_module, "verify_pdf", lambda _: {"valid": True})

    render_pdf("# Report", tmp_path / "report.pdf", chrome_binary="/chrome")

    assert "--no-pdf-header-footer" in commands[0]


def test_verify_pdf_rejects_browser_header_footer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "browser-chrome.pdf"
    path.write_bytes(b"%PDF-1.4\n")
    monkeypatch.setattr(pdf_module, "_pdfinfo_page_count", lambda _: 1)
    monkeypatch.setattr(
        pdf_module,
        "_extract_pdf_text",
        lambda _: "ﬁle:///tmp/sheperd-pdf-example/report.html 1/1",
    )

    with pytest.raises(RuntimeError, match="pdf_verification_failed"):
        verify_pdf(path)


def test_pdf_text_fallback_uses_native_pdfkit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "report.pdf"
    path.write_bytes(b"%PDF-1.4\n")

    def fake_which(binary: str) -> str | None:
        return "/usr/bin/osascript" if binary == "osascript" else None

    def fake_run(command: list[str], **_: object) -> object:
        assert command[:3] == ["/usr/bin/osascript", "-l", "JavaScript"]
        assert "PDFKit" in command[4]
        return type("Result", (), {"stdout": "Visible report text"})()

    monkeypatch.setattr(pdf_module.shutil, "which", fake_which)
    monkeypatch.setattr(pdf_module.subprocess, "run", fake_run)

    assert pdf_module._extract_pdf_text(path) == "Visible report text"
