from __future__ import annotations

import hashlib
from collections.abc import Sequence
from datetime import datetime
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    DistillationQualityStatus,
    FreshnessStatus,
    InsightStatus,
    SourceCandidate,
    WeeklyBrief,
)

REQUIRED_DRAFT_PREFIX = "DRAFT - HUMAN REVIEW REQUIRED"
MANDATORY_EXCLUDED_DOMAINS = ("linkedin.com",)
PAYWALL_QUERY_MARKERS = {
    "member-only",
    "members-only",
    "paywall",
    "premium",
    "subscriber",
    "subscription",
}
ALLOWED_URL_SCHEMES = {"http", "https"}
REPORT_BULLET_SECTIONS = (
    "executive_bullets",
    "developments",
    "risks",
    "opportunities",
    "uncertainties",
)
ACTIONABLE_REPORT_SECTIONS = {"risks", "opportunities", "uncertainties"}
_PLACEHOLDER_TEXT = frozenset(
    {"", "null", "none", "n/a", "na", "not recorded", "not available"}
)


def _is_placeholder(value: str) -> bool:
    normalized = " ".join(value.strip().casefold().rstrip(".").split())
    return normalized in _PLACEHOLDER_TEXT or normalized.startswith(
        ("not recorded ", "not available ")
    )


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    hostname = parsed.hostname.lower() if parsed.hostname else ""
    port = parsed.port
    netloc = hostname
    is_default_port = (parsed.scheme == "https" and port == 443) or (
        parsed.scheme == "http" and port == 80
    )
    if port is not None and not is_default_port:
        netloc = f"{hostname}:{port}"
    path = parsed.path.rstrip("/") or "/"
    # ponytail: strip every query from persisted URLs; add an explicit safe
    # allowlist only if a source identity requires it.
    return urlunsplit((parsed.scheme.lower(), netloc, path, "", ""))


def content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def matches_domain(host: str, domain: str) -> bool:
    canonical_host = host.strip().lower().removesuffix(".")
    canonical_domain = domain.strip().lower().removesuffix(".").removeprefix("www.")
    return canonical_host == canonical_domain or canonical_host.endswith(f".{canonical_domain}")


def matches_any_domain(host: str, domains: tuple[str, ...] | list[str]) -> bool:
    return any(matches_domain(host, domain) for domain in domains)


def url_policy_error(
    url: str,
    *,
    excluded_domains: Sequence[str] = (),
) -> str | None:
    try:
        parsed = urlsplit(url.strip())
    except ValueError:
        return "malformed_url"
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_URL_SCHEMES:
        return "unsupported_scheme"
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return "missing_host"
    if parsed.username or parsed.password:
        return "credential_bearing_url"
    if matches_any_domain(hostname, tuple(MANDATORY_EXCLUDED_DOMAINS) + tuple(excluded_domains)):
        return "excluded_domain"
    query_markers = {
        item.strip().lower()
        for pair in parse_qsl(parsed.query, keep_blank_values=True)
        for item in pair
        if item.strip()
    }
    if query_markers.intersection(PAYWALL_QUERY_MARKERS):
        return "inaccessible_paywall"
    return None


def can_extract_url(url: str) -> bool:
    return url_policy_error(url) is None


def validate_source_dates(sources: list[SourceCandidate], as_of: datetime) -> None:
    for source in sources:
        if source.published_at is not None and source.published_at > as_of:
            raise ValueError(f"source publication date is after as_of: {source.url}")


def classify_freshness(
    source: SourceCandidate,
    as_of: datetime,
    *,
    current_window_days: int = 30,
) -> SourceCandidate:
    """Attach deterministic freshness metadata without changing source identity."""
    published_at = source.published_at
    if published_at is None:
        return source.model_copy(
            update={"freshness_status": FreshnessStatus.UNDATED, "freshness_days": None}
        )
    if published_at > as_of:
        return source.model_copy(
            update={"freshness_status": FreshnessStatus.FUTURE, "freshness_days": None}
        )
    freshness_days = max(0, (as_of - published_at).days)
    status = (
        FreshnessStatus.CURRENT
        if freshness_days <= current_window_days
        else FreshnessStatus.STALE
    )
    return source.model_copy(
        update={"freshness_status": status, "freshness_days": freshness_days}
    )


def independent_source_count(claim: ClaimDraft) -> int:
    """Count distinct publisher domains; URL count is not independent evidence."""
    return len(
        {
            (urlsplit(normalize_url(url)).hostname or "").lower().removeprefix("www.")
            for url in claim.source_urls
        }
    )


def claim_verification_allowed(
    claim: ClaimDraft,
    sources: Sequence[SourceCandidate],
    *,
    critic_approved: bool = False,
) -> bool:
    source_by_url = {normalize_url(source.url): source for source in sources}
    linked = [source_by_url.get(normalize_url(url)) for url in claim.source_urls]
    linked_sources = [source for source in linked if source is not None]
    independent = independent_source_count(claim)
    primary_with_evidence = (
        any(source.authority_tier == "primary" for source in linked_sources)
        and bool(claim.evidence_excerpt or claim.support_locator)
        and critic_approved
    )
    return independent >= 2 or primary_with_evidence


def validate_evidence_quality(
    claims: Sequence[ClaimDraft],
    sources: Sequence[SourceCandidate],
    *,
    critic_approved: bool = False,
) -> list[str]:
    issues: list[str] = []
    for claim in claims:
        if claim.evidence_excerpt is not None and (
            len(claim.evidence_excerpt) > 320
            or len(claim.evidence_excerpt.split()) > 40
        ):
            issues.append("evidence_excerpt_limit")
        if claim.evidence_status.value == "verified" and not claim_verification_allowed(
            claim, sources, critic_approved=critic_approved
        ):
            issues.append("verified_claim_without_independent_basis")
    return sorted(set(issues))


def deduplicate_sources(sources: list[SourceCandidate]) -> list[SourceCandidate]:
    unique: dict[str, SourceCandidate] = {}
    for source in sources:
        normalized = normalize_url(source.url)
        if normalized not in unique:
            unique[normalized] = source.model_copy(update={"url": normalized})
    return list(unique.values())


def validate_claim_citations(
    claims: list[ClaimDraft], source_urls: set[str], as_of: datetime
) -> None:
    del as_of
    known = {normalize_url(url) for url in source_urls}
    for claim in claims:
        if not claim.source_urls:
            raise ValueError("claim has no source URLs")
        if any(not url.startswith(("https://", "http://")) for url in claim.source_urls):
            raise ValueError("claim cites a non-http source URL")
        unknown = {
            normalize_url(url) for url in claim.source_urls if normalize_url(url) not in known
        }
        if unknown:
            raise ValueError(f"claim cites unknown source: {sorted(unknown)[0]}")


def _required_insight_text(value: str, field: str, issues: list[str]) -> None:
    if _is_placeholder(value):
        issues.append(f"missing_{field}")


def validate_article_distillation_quality(
    distillation: ArticleDistillation,
) -> list[str]:
    """Return deterministic completeness issues for one extracted article."""
    issues: list[str] = []
    if distillation.quality_status is not DistillationQualityStatus.COMPLETE:
        issues.append("quality_status_incomplete")
    _required_insight_text(distillation.summary, "summary", issues)
    if len(
        [
            point
            for point in distillation.key_points
            if point.strip() and not _is_placeholder(point)
        ]
    ) < 2:
        issues.append("key_points_incomplete")
    _required_insight_text(distillation.what_happened, "what_happened", issues)
    _required_insight_text(distillation.why_it_matters, "why_it_matters", issues)
    if not distillation.uncertainties or not all(
        item.strip() and not _is_placeholder(item)
        for item in distillation.uncertainties
    ):
        issues.append("uncertainties_incomplete")
    if not distillation.next_steps or not all(
        item.strip() and not _is_placeholder(item)
        for item in distillation.next_steps
    ):
        issues.append("next_steps_incomplete")

    for name, insight in (
        ("risk_assessment", distillation.risk_assessment),
        ("opportunity_assessment", distillation.opportunity_assessment),
    ):
        if insight is None:
            issues.append(f"missing_{name}")
            continue
        if insight.status not in {
            InsightStatus.SUPPORTED,
            InsightStatus.NOT_OBSERVED,
            InsightStatus.UNCERTAIN,
        }:
            issues.append(f"invalid_{name}_status")
        _required_insight_text(insight.statement, f"{name}_statement", issues)
        _required_insight_text(
            insight.why_it_matters, f"{name}_why_it_matters", issues
        )
        _required_insight_text(insight.next_step, f"{name}_next_step", issues)
        if (
            insight.status is InsightStatus.SUPPORTED
            and not insight.evidence_excerpt
            and not insight.evidence_locator
        ):
            issues.append(f"{name}_missing_evidence")
    return issues


def validate_report_sections(
    brief: WeeklyBrief,
    known_urls: set[str],
) -> list[str]:
    """Return deterministic completeness issues for a newly synthesized brief."""
    normalized_known = {normalize_url(url) for url in known_urls}
    issues: list[str] = []
    for section in REPORT_BULLET_SECTIONS:
        bullets = list(getattr(brief, section))
        if not bullets:
            issues.append(f"{section}_empty")
            continue
        for index, bullet in enumerate(bullets, start=1):
            normalized_urls = {normalize_url(url) for url in bullet.source_urls}
            if not normalized_urls or not normalized_urls.issubset(normalized_known):
                issues.append(f"{section}_{index}_unknown_citation")
            if (
                brief.prompt_version.startswith("weekly-brief-v6")
                or section in ACTIONABLE_REPORT_SECTIONS
            ):
                if not bullet.why_it_matters or (
                    _is_placeholder(bullet.why_it_matters)
                ):
                    issues.append(f"{section}_{index}_missing_why_it_matters")
                if not bullet.next_step or (
                    _is_placeholder(bullet.next_step)
                ):
                    issues.append(f"{section}_{index}_missing_next_step")
    if not any(question.strip() for question in brief.follow_up_questions):
        issues.append("follow_up_questions_empty")
    return issues


def with_draft_prefix(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith(REQUIRED_DRAFT_PREFIX):
        return stripped
    return f"{REQUIRED_DRAFT_PREFIX}\n\n{stripped}"
