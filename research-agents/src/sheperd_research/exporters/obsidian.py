from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from pathlib import Path

from ..contracts import (
    ArticleDistillation,
    ClaimDraft,
    ReportBullet,
    ReviewState,
    SourceCandidate,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from ..validators import REQUIRED_DRAFT_PREFIX, content_hash, normalize_url


def _clean_summary(value: str) -> str:
    summary = value.strip()
    if summary.startswith(REQUIRED_DRAFT_PREFIX):
        return summary[len(REQUIRED_DRAFT_PREFIX) :].lstrip()
    return summary


def _lines(values: Iterable[str], *, empty: str = "- None recorded.") -> str:
    rows = [f"- {value}" for value in values if value.strip()]
    return "\n".join(rows) or empty


def _bullet_lines(values: Iterable[ReportBullet]) -> str:
    rows = []
    for item in values:
        citations = " ".join(f"[{url}]({url})" for url in item.source_urls)
        rows.append(f"- {item.text}  \n  Evidence: {item.evidence_status.value}. {citations}")
    return "\n".join(rows) or "- None recorded."


def _date(value: object) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else str(value or "unknown")


def _article_section(
    sources: list[SourceCandidate],
    distillations: list[ArticleDistillation],
    claims: list[ClaimDraft],
    source_hashes: dict[str, str],
) -> str:
    distillations_by_url = {
        normalize_url(item.source_url): item for item in distillations
    }
    claims_by_url: dict[str, list[ClaimDraft]] = {}
    for claim in claims:
        for url in claim.source_urls:
            claims_by_url.setdefault(normalize_url(url), []).append(claim)

    articles: list[str] = []
    for source in sources:
        normalized_url = normalize_url(source.url)
        distillation = distillations_by_url.get(normalized_url)
        article_claims = claims_by_url.get(normalized_url, [])
        article_lines = [
            f"### {source.title}",
            f"- URL: [{source.url}]({source.url})",
            f"- Publisher: {source.publisher or 'unknown'}",
            f"- Region / lane: {source.region} / {source.lane}",
            f"- Language: {source.language_code}",
            f"- Published: {_date(source.published_at)}",
            f"- Retrieved: {_date(source.retrieved_at)}",
            f"- Freshness: {source.freshness_status.value}",
            f"- Extraction: {source.extraction_status.value}",
            f"- Authority / type: {source.authority_tier} / {source.source_type}",
            f"- Evidence state: {source.evidence_status.value}",
            f"- Content hash: `{source_hashes.get(normalized_url, 'not-recorded')}`",
        ]
        if distillation is None:
            article_lines.extend(["", "No distillation recorded."])
        else:
            article_lines.extend(
                [
                    "",
                    "#### English summary",
                    _clean_summary(distillation.summary),
                    "",
                    "#### Original-language summary",
                    distillation.summary_original or "Not recorded.",
                    "",
                    "#### Key points",
                    _lines(distillation.key_points),
                    "",
                    "#### Original-language key points",
                    _lines(distillation.key_points_original),
                    "",
                    "#### Translation and evidence",
                    f"- Translation: {distillation.translation_status.value}",
                    f"- Evidence: {distillation.evidence_status.value}",
                    "- Limitations:",
                    _lines(distillation.limitations),
                ]
            )
        article_lines.extend(["", "#### Claims and citations"])
        if article_claims:
            for claim in article_claims:
                citations = " ".join(f"[{url}]({url})" for url in claim.source_urls)
                article_lines.extend(
                    [
                        f"- {claim.claim}",
                        "  - Evidence: "
                        f"{claim.evidence_status.value}; citation: {claim.citation_status}",
                        f"  - Independent sources: {claim.independent_source_count}",
                        f"  - Excerpt: {claim.evidence_excerpt or 'not recorded'}",
                        f"  - Locator: {claim.support_locator or 'not recorded'}",
                        f"  - Sources: {citations}",
                    ]
                )
        else:
            article_lines.append("- No claims recorded.")
        articles.append("\n".join(article_lines))
    return "\n\n".join(articles) or "- No sources recorded."


def _audit_section(
    validation: ValidationReport | None,
    run: dict[str, object] | None,
    steps: list[dict[str, object]],
    tool_calls: list[dict[str, object]],
) -> str:
    lines = [
        f"- Run status: {run.get('status', 'unknown') if run else 'unknown'}",
        f"- Validation: {validation.status.value if validation else 'blocked'}",
        "- Sources / claims: "
        f"{validation.source_count if validation else 0} / "
        f"{validation.claim_count if validation else 0}",
        f"- Citation coverage: {validation.citation_coverage if validation else 0.0:.1%}",
        f"- Agent steps: {len(steps)}",
        f"- Tool receipts: {len(tool_calls)}",
    ]
    for step in steps:
        lines.append(
            "- Step `{}#{}`: {} · model={} · latency={}ms · error={}".format(
                step.get("agent_name", "unknown"),
                step.get("attempt", 1),
                step.get("status", "unknown"),
                step.get("resolved_model") or step.get("requested_model") or "unknown",
                step.get("duration_ms") or "unknown",
                step.get("error_code") or "none",
            )
        )
    return "\n".join(lines)


def render_weekly_markdown(
    brief: WeeklyBrief,
    *,
    validation: ValidationReport | None = None,
    sources: list[SourceCandidate] | None = None,
    distillations: list[ArticleDistillation] | None = None,
    claims: list[ClaimDraft] | None = None,
    source_hashes: dict[str, str] | None = None,
    signals: Sequence[object] | None = None,
    steps: list[dict[str, object]] | None = None,
    tool_calls: list[dict[str, object]] | None = None,
    run: dict[str, object] | None = None,
    status: str | None = None,
) -> str:
    """Render structured Neon evidence without exporting article bodies or prompts."""
    resolved_sources = sources or []
    resolved_distillations = distillations or []
    resolved_claims = claims or []
    resolved_hashes = source_hashes or {}
    resolved_steps = steps or []
    resolved_tool_calls = tool_calls or []
    report_status = status or (
        "approved" if brief.review_state is ReviewState.APPROVED else "draft"
    )
    summary = _clean_summary(brief.summary)
    frontmatter = "\n".join(
        [
            "---",
            f"title: {json.dumps(brief.title)}",
            "type: research-run",
            f"status: {report_status}",
            "owner: research-agents",
            f"updated: {brief.covered_until.date().isoformat()}",
            f"evidence_status: {brief.evidence_status.value}",
            "confidentiality: internal",
            "tags:",
            "  - sheperd/research",
            "  - sheperd/agent-run",
            f"run_id: {json.dumps(brief.run_id)}",
            f"content_hash: {json.dumps(content_hash(summary))}",
            "---",
        ]
    )
    executive = _bullet_lines(brief.executive_bullets) if brief.executive_bullets else summary
    signals_text = (
        _lines(
            [
                getattr(signal, "summary", "")
                for signal in (signals or [])
                if getattr(signal, "summary", "")
            ]
        )
        if signals
        else "- None recorded."
    )
    body = f"""# {brief.title}

## Report metadata

- Covered period: {_date(brief.covered_from)} to {_date(brief.covered_until)}
- As of: {_date((run or {}).get('as_of'))}
- Review state: {brief.review_state.value}
- Validation state: {validation.status.value if validation else 'blocked'}

## Executive summary

{executive}

## Developments by lane and region

{_bullet_lines(brief.developments)}

### Recorded signals

{signals_text}

## Risks and threats

{_bullet_lines(brief.risks)}

## Opportunities

{_bullet_lines(brief.opportunities)}

## Uncertainty and follow-up questions

{_bullet_lines(brief.uncertainties)}

### Follow-up questions

{_lines(brief.follow_up_questions)}

## Article findings

{_article_section(resolved_sources, resolved_distillations, resolved_claims, resolved_hashes)}

## Validation and agent audit

{_audit_section(validation, run, resolved_steps, resolved_tool_calls)}

## Limitations

{_lines(brief.limitations)}
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
    signals: Sequence[object] | None = None,
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
