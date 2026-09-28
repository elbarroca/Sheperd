from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import date, datetime
from pathlib import Path

from ..contracts import (
    ArticleDistillation,
    ClaimDraft,
    ReaderArticle,
    ReaderReport,
    ReviewState,
    SignalEvent,
    SourceCandidate,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from ..reader import build_reader_report
from ..validators import REQUIRED_DRAFT_PREFIX, content_hash


def _clean_summary(value: str) -> str:
    summary = value.strip()
    if summary.startswith(REQUIRED_DRAFT_PREFIX):
        return summary[len(REQUIRED_DRAFT_PREFIX) :].lstrip()
    return summary


def _lines(values: Iterable[str], *, empty: str = "- None recorded.") -> str:
    rows = [f"- {value}" for value in values if value.strip()]
    return "\n".join(rows) or empty


def _date(value: object) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
    return str(value or "unknown")


def canonical_report_hash(
    brief: WeeklyBrief,
    *,
    validation: ValidationReport | None,
    sources: Sequence[SourceCandidate],
    distillations: Sequence[ArticleDistillation],
    claims: Sequence[ClaimDraft],
    signals: Sequence[SignalEvent],
    source_hashes: dict[str, str],
    run: dict[str, object] | None,
) -> str:
    payload = {
        "brief": brief.model_dump(mode="json"),
        "validation": validation.model_dump(mode="json") if validation else None,
        "sources": [item.model_dump(mode="json") for item in sources],
        "distillations": [item.model_dump(mode="json") for item in distillations],
        "claims": [item.model_dump(mode="json") for item in claims],
        "signals": [item.model_dump(mode="json") for item in signals],
        "source_hashes": source_hashes,
        "run": run,
    }
    return content_hash(json.dumps(payload, default=str, sort_keys=True))


def _table_value(value: object) -> str:
    return str(value or "unknown").replace("|", "\\|").replace("\n", " ")


def _reader_article_cards(articles: Sequence[ReaderArticle]) -> str:
    cards: list[str] = []
    for index, article in enumerate(articles, start=1):
        score = (
            f"{article.score.total}/100 ({article.score.priority})"
            if article.score is not None
            else "not scored"
        )
        lines = [
            f"### {index}. {article.headline}",
            f"- Priority: {score}",
            f"- Publisher: {article.publisher}",
            f"- Published: {_date(article.published_at)}",
            f"- Region / lane: {article.region} / {article.lane}",
            "",
            "#### Three key points",
            _lines(article.key_points),
            "",
            f"What changed: {article.what_changed}",
            "",
            f"Why SheperD cares: {article.why_sheperd_cares}",
            "",
            f"Recommended action: {article.recommended_action}",
        ]
        if article.risk:
            lines.extend(["", f"Risk: {article.risk}"])
        if article.opportunity:
            lines.extend(["", f"Opportunity: {article.opportunity}"])
        if article.limitations:
            lines.extend(["", f"Limitations: {'; '.join(article.limitations)}"])
        lines.extend(["", f"Source: [{article.publisher}]({article.source_url})"])
        cards.append("\n".join(lines))
        if index % 2 == 0 and index < len(articles):
            cards.append("<!-- pdf-page-break -->")
    return "\n\n".join(cards) or "- No validated current-week articles."


def _reader_three_things(report: ReaderReport) -> str:
    articles = [*report.ranked_articles, *report.watchlist]
    rows: list[str] = []
    for index, thing in enumerate(report.three_things):
        if index < len(articles):
            article = articles[index]
            rows.append(
                f"- {thing} Source: [{article.publisher}]({article.source_url})"
            )
        else:
            rows.append(f"- {thing}")
    return "\n".join(rows) or "- None recorded."


def _reader_compact_table(articles: Sequence[ReaderArticle]) -> str:
    rows = [
        "| Article | Published | Priority | Region / lane |",
        "| --- | --- | --- | --- |",
    ]
    for article in articles:
        priority = article.score.total if article.score is not None else "unscored"
        rows.append(
            f"| [{_table_value(article.headline)}]({article.source_url}) | "
            f"{_table_value(_date(article.published_at))} | {priority} | "
            f"{_table_value(article.region)} / {_table_value(article.lane)} |"
        )
    return "\n".join(rows) if articles else "- None."


def _reader_source_index(report: ReaderReport) -> str:
    rows = [
        "| Source | Publisher | Published | Date basis | Use | Validation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for source in report.source_index:
        rows.append(
            f"| [{_table_value(source.title)}]({source.url}) | "
            f"{_table_value(source.publisher)} | {_table_value(_date(source.published_at))} | "
            f"{source.date_basis.value} | "
            f"{'current' if source.eligible_for_weekly else 'background'} | "
            f"{source.validation_status} |"
        )
    return "\n".join(rows) if report.source_index else "- No sources recorded."


def _run_request_field(
    run: dict[str, object] | None,
    field: str,
    default: object,
) -> object:
    request = (run or {}).get("request")
    if isinstance(request, dict):
        return request.get(field, default)
    return getattr(request, field, default)


def render_weekly_markdown(
    brief: WeeklyBrief,
    *,
    validation: ValidationReport | None = None,
    sources: list[SourceCandidate] | None = None,
    distillations: list[ArticleDistillation] | None = None,
    claims: list[ClaimDraft] | None = None,
    source_hashes: dict[str, str] | None = None,
    signals: Sequence[SignalEvent] | None = None,
    steps: list[dict[str, object]] | None = None,
    tool_calls: list[dict[str, object]] | None = None,
    run: dict[str, object] | None = None,
    status: str | None = None,
    canonical_hash: str | None = None,
    reader_report: ReaderReport | None = None,
) -> str:
    """Render the ranked reader report without raw bodies or audit internals."""
    resolved_sources = sources or []
    resolved_distillations = distillations or []
    resolved_claims = claims or []
    resolved_hashes = source_hashes or {}
    resolved_signals = list(signals or [])
    report_status = status or (
        "approved" if brief.review_state is ReviewState.APPROVED else "draft"
    )
    summary = _clean_summary(brief.summary)
    report_hash = canonical_hash or canonical_report_hash(
        brief,
        validation=validation,
        sources=resolved_sources,
        distillations=resolved_distillations,
        claims=resolved_claims,
        signals=resolved_signals,
        source_hashes=resolved_hashes,
        run=run,
    )
    projection = reader_report or build_reader_report(
        brief,
        validation=validation,
        sources=resolved_sources,
        distillations=resolved_distillations,
        canonical_hash=report_hash,
        readiness_status=(
            "decision_ready"
            if report_status == "approved"
            and validation is not None
            and validation.status is ValidationStatus.PASS
            else "review_required"
        ),
    )
    current_articles = [*projection.ranked_articles, *projection.watchlist]
    research_scope = _run_request_field(run, "research_scope", "global")
    new_findings_only = _run_request_field(run, "new_findings_only", False)
    scope_label = "USA + Mexico" if research_scope == "us-mexico" else "Global"
    findings_mode = "New findings only" if new_findings_only else "Current-period findings"
    frontmatter = "\n".join(
        [
            "---",
            f"title: {json.dumps(brief.title)}",
            "type: research-run",
            f"status: {report_status}",
            "owner: research-agents",
            f"updated: {brief.covered_until.date().isoformat()}",
            f"research_scope: {json.dumps(scope_label)}",
            f"findings_mode: {json.dumps(findings_mode)}",
            f"evidence_status: {brief.evidence_status.value}",
            "confidentiality: internal",
            "tags:",
            "  - sheperd/research",
            "  - sheperd/agent-run",
            f"run_id: {json.dumps(brief.run_id)}",
            f"content_hash: {json.dumps(report_hash)}",
            "---",
        ]
    )
    body = f"""# {brief.title}

## Report status

| Gate | State |
| --- | --- |
| Run | {_table_value((run or {}).get('status'))} |
| Validation | {projection.validation_status} |
| Review | {projection.report_status} |
| Readiness | {projection.readiness_status} |
| Scope | {scope_label} |
| Findings | {findings_mode} |
| New findings | {len(current_articles)} |

- Reporting period: {_date(brief.covered_from)} to {_date(brief.covered_until)}
- As of: {_date((run or {}).get('as_of'))}

## Three things to know

{_reader_three_things(projection)}

## Top action

{projection.top_action}

## Executive summary

{summary}

## All new findings

{_reader_article_cards(current_articles)}

<!-- pdf-page-break -->

## Watchlist

{_reader_compact_table(projection.watchlist)}

## Background context

These articles remain useful context but do not count as current-week evidence.

{_reader_compact_table(projection.background_articles)}

## Limitations

{_lines(brief.limitations)}

<!-- pdf-page-break -->

## Source index and validation

{_reader_source_index(projection)}
"""
    return f"{frontmatter}\n\n{body.strip()}\n"


def export_reviewed_brief(
    brief: WeeklyBrief,
    destination: Path,
    *,
    validation: ValidationReport | None = None,
    sources: list[SourceCandidate] | None = None,
    distillations: list[ArticleDistillation] | None = None,
    claims: list[ClaimDraft] | None = None,
    source_hashes: dict[str, str] | None = None,
    signals: Sequence[SignalEvent] | None = None,
    steps: list[dict[str, object]] | None = None,
    tool_calls: list[dict[str, object]] | None = None,
    run: dict[str, object] | None = None,
) -> Path:
    if brief.review_state is not ReviewState.APPROVED:
        raise PermissionError("only reviewed briefs may be exported")
    if validation is None or validation.run_id != brief.run_id:
        raise PermissionError("a matching validation report is required")
    if validation.status is not ValidationStatus.PASS:
        raise PermissionError("only briefs with passing validation may be exported")

    body = render_weekly_markdown(
        brief,
        validation=validation,
        sources=sources,
        distillations=distillations,
        claims=claims,
        source_hashes=source_hashes,
        signals=signals,
        steps=steps,
        tool_calls=tool_calls,
        run=run,
        status="approved",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8")
    return destination
