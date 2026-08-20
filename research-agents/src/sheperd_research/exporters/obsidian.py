from __future__ import annotations

import json
from pathlib import Path

from ..contracts import ReviewState, ValidationReport, ValidationStatus, WeeklyBrief
from ..validators import REQUIRED_DRAFT_PREFIX, content_hash


def export_reviewed_brief(
    brief: WeeklyBrief,
    destination: Path,
    *,
    validation: ValidationReport | None = None,
) -> Path:
    if brief.review_state is not ReviewState.APPROVED:
        raise PermissionError("only reviewed briefs may be exported")
    if validation is None or validation.run_id != brief.run_id:
        raise PermissionError("a matching validation report is required")
    if validation.status is not ValidationStatus.PASS:
        raise PermissionError("only briefs with passing validation may be exported")

    summary = brief.summary.strip()
    if summary.startswith(REQUIRED_DRAFT_PREFIX):
        summary = summary[len(REQUIRED_DRAFT_PREFIX) :].lstrip()
    sources = "\n".join(f"- [{url}]({url})" for url in brief.source_urls)
    frontmatter = "\n".join(
        [
            "---",
            f"title: {json.dumps(brief.title)}",
            "type: research-run",
            "status: approved",
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
    limitations = "\n".join(f"- {item}" for item in brief.limitations) or "- None recorded."
    body = (
        f"{frontmatter}\n\n"
        f"# {brief.title}\n\n"
        f"## Summary\n\n{summary}\n\n"
        f"## Limitations\n\n{limitations}\n\n"
        f"## Sources\n\n{sources or '- No sources recorded.'}\n"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(body, encoding="utf-8")
    return destination
