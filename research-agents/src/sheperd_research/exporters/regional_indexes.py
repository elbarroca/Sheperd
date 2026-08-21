from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from ..contracts import ArticleDistillation, ClaimDraft, SourceCandidate
from ..db import RepositoryProtocol
from ..validators import content_hash, normalize_url

REGION_LABELS = {
    "us": "US",
    "canada": "Canada",
    "mexico": "Mexico",
    "europe": "Europe",
    "south-america": "South America",
    "middle-east": "Middle East",
    "global": "Global",
}


def _date(value: datetime | None) -> str:
    return value.astimezone(UTC).isoformat() if value is not None else "undated"


def _bullet(value: str) -> str:
    return " ".join(value.strip().split())


def _source_section(
    source: SourceCandidate,
    distillation: ArticleDistillation | None,
    claims: Iterable[ClaimDraft],
    run_id: str,
    source_hash: str | None,
) -> str:
    source_claims = list(claims)
    lines = [
        f"## {source.title or source.url}",
        "",
        f"- **Canonical URL:** [{source.url}]({source.url})",
        f"- **Publisher:** {source.publisher or 'unknown'}",
        f"- **Authority:** {source.authority_tier}",
        f"- **Source type:** {source.source_type}",
        f"- **Region:** {REGION_LABELS.get(source.region, source.region)}",
        f"- **Lane:** {source.lane or 'unknown'}",
        f"- **Topics:** {', '.join(source.topics) or 'none recorded'}",
        f"- **Signal geographies:** {', '.join(source.geographies) or 'none recorded'}",
        f"- **Language:** {source.language_code} ({source.language_confidence:.2f} confidence)",
        f"- **Published:** {_date(source.published_at)}",
        f"- **Retrieved:** {_date(source.retrieved_at)}",
        f"- **Freshness:** {source.freshness_status.value}"
        + (
            f" ({source.freshness_days} days)"
            if source.freshness_days is not None
            else ""
        ),
        f"- **Extraction:** {source.extraction_status.value}"
        + (
            f" ({source.extraction_error_code})"
            if source.extraction_error_code
            else ""
        ),
        f"- **Evidence:** {source.evidence_status.value}",
        f"- **Content hash:** `{source_hash or 'not recorded'}`",
        f"- **Run:** `{run_id}`",
        "",
        f"**Original title:** {source.title or 'not recorded'}",
        "",
        f"**Original snippet:** {source.snippet or 'not recorded'}",
        "",
        "**Normalized English title:** "
        f"{source.normalized_title_en or source.title or 'not recorded'}",
        "",
        "**Normalized English snippet:** "
        f"{source.normalized_snippet_en or source.snippet or 'not recorded'}",
        "",
    ]
    if distillation is None:
        lines.extend([
            "> [!warning] Distillation is missing for this source.",
            "",
        ])
        return "\n".join(lines)

    lines.extend([
        "### English distillation",
        "",
        _bullet(distillation.summary) or "Not recorded.",
        "",
        "### Original-language distillation",
        "",
        _bullet(distillation.summary_original) or "Not recorded.",
        "",
        f"- **Translation:** {distillation.translation_status.value}",
        f"- **Model:** {distillation.model_id}",
        f"- **Prompt version:** {distillation.prompt_version}",
        f"- **Distillation evidence:** {distillation.evidence_status.value}",
        f"- **Distillation hash:** `{distillation.content_hash or 'not recorded'}`",
        "",
        "### Key points",
        "",
    ])
    english_points = distillation.key_points or ["No English key points recorded."]
    lines.extend(f"- {_bullet(point)}" for point in english_points)
    lines.extend(["", "### Original-language key points", ""])
    original_points = distillation.key_points_original or [
        "No original-language key points recorded."
    ]
    lines.extend(f"- {_bullet(point)}" for point in original_points)
    lines.extend(["", "### Claims and evidence", ""])
    if not source_claims:
        lines.append("- No claims recorded.")
    for claim in source_claims:
        citations = ", ".join(
            f"[{url}]({url})" for url in claim.source_urls if url.startswith("http")
        )
        lines.extend(
            [
                f"- **{_bullet(claim.claim)}** — {claim.evidence_status.value}; "
                f"citation: {claim.citation_status}; "
                f"independent sources: {claim.independent_source_count}",
                f"  - Original claim: {_bullet(claim.original_claim or claim.claim)}",
                f"  - Evidence excerpt: {_bullet(claim.evidence_excerpt or 'not recorded')}",
                f"  - Evidence locator: {_bullet(claim.support_locator or 'not recorded')}",
                f"  - Verification basis: {_bullet(claim.verification_basis or 'not recorded')}",
                f"  - Citations: {citations or 'none recorded'}",
            ]
        )
    lines.extend(["", "### Limitations", ""])
    lines.extend(
        f"- {_bullet(item)}" for item in (distillation.limitations or ["None recorded."])
    )
    lines.append("")
    return "\n".join(lines)


def generate_regional_indexes(
    repository: RepositoryProtocol,
    output_root: Path,
    *,
    run_id: str,
    regions: str | Iterable[str] = "all",
) -> dict[str, object]:
    run = repository.get_run(run_id)
    if run is None:
        raise ValueError(f"run not found: {run_id}")
    selected = list(REGION_LABELS) if regions == "all" else list(regions)
    unknown = sorted(set(selected) - set(REGION_LABELS))
    if unknown:
        raise ValueError(f"unknown region: {unknown[0]}")

    sources = repository.get_run_sources(run_id)
    distillations = {
        normalize_url(item.source_url): item
        for item in repository.get_run_distillations(run_id)
    }
    source_hashes = repository.get_run_source_hashes(run_id)
    claims_by_source: dict[str, list[ClaimDraft]] = {}
    for claim in repository.get_run_claims(run_id):
        for url in claim.source_urls:
            claims_by_source.setdefault(normalize_url(url), []).append(claim)

    destination = output_root.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC)
    file_hashes: dict[str, str] = {}
    region_counts: dict[str, dict[str, int]] = {}
    statuses: dict[str, str] = {}
    for region in selected:
        label = REGION_LABELS[region]
        region_sources = [source for source in sources if source.region == region]
        partial = any(
            source.extraction_status.value != "succeeded"
            or source.freshness_status.value in {"future", "unknown"}
            or (
                distillations.get(normalize_url(source.url)) is not None
                and distillations[normalize_url(source.url)].translation_status.value == "failed"
            )
            for source in region_sources
        )
        body_lines = [
            "---",
            f"title: {json.dumps(f'{label} Research Index')}",
            "type: generated-research-index",
            f"region: {json.dumps(region)}",
            f"run_id: {json.dumps(run_id)}",
            f"generated_at: {json.dumps(generated_at.isoformat())}",
            f"status: {'partial' if partial else 'pass'}",
            "confidentiality: internal",
            "tags:",
            "  - sheperd/research",
            "  - sheperd/generated-index",
            "---",
            "",
            f"# {label} Research Index",
            "",
            "> [!info] Generated from Neon. This index is not the source of truth.",
            "> Raw article bodies, prompts, credentials, and hidden reasoning are not exported.",
            "",
            f"**Run:** `{run_id}`  ",
            f"**Generated:** {generated_at.isoformat()}  ",
            f"**Status:** {'PARTIAL' if partial else 'PASS'}  ",
            f"**Sources:** {len(region_sources)}",
            "",
        ]
        if not region_sources:
            body_lines.extend(["No sources recorded for this region.", ""])
        for source in region_sources:
            body_lines.append(
                _source_section(
                    source,
                    distillations.get(normalize_url(source.url)),
                    claims_by_source.get(normalize_url(source.url), []),
                    run_id,
                    source_hashes.get(normalize_url(source.url)),
                )
            )
        content = "\n".join(body_lines)
        path = destination / label / "index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        relative = path.relative_to(destination).as_posix()
        file_hashes[relative] = content_hash(content)
        region_counts[region] = {
            "sources": len(region_sources),
            "distillations": sum(
                normalize_url(source.url) in distillations for source in region_sources
            ),
            "claims": sum(
                len(claims_by_source.get(normalize_url(source.url), []))
                for source in region_sources
            ),
        }
        statuses[region] = "partial" if partial else "pass"

    health = repository.health()
    manifest = {
        "generated_at": generated_at.isoformat(),
        "run_id": run_id,
        "neon_branch_id": health.get("branch_id"),
        "migration_version": health.get("migration_version"),
        "regions": region_counts,
        "files": file_hashes,
        "statuses": statuses,
        "status": "partial" if any(status == "partial" for status in statuses.values()) else "pass",
    }
    manifest_content = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    manifest_path = destination / "manifest.json"
    manifest_path.write_text(manifest_content, encoding="utf-8")
    return {
        "status": manifest["status"],
        "run_id": run_id,
        "output_root": str(destination),
        "manifest": str(manifest_path),
        "regions": region_counts,
        "file_hashes": file_hashes,
        "manifest_hash": content_hash(manifest_content),
        "source_count": len(sources),
        "distillation_count": len(distillations),
        "claim_count": len(repository.get_run_claims(run_id)),
        "domain_counts": {
            region: sum(
                (urlsplit(source.url).hostname or "").lower().removeprefix("www.")
                != ""
                for source in sources
                if source.region == region
            )
            for region in selected
        },
    }
