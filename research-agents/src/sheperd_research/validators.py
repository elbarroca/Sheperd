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
    {
        "",
        "null",
        "none",
        "n/a",
        "na",
        "not recorded",
        "not available",
        "tbd",
        "to be determined",
        "unknown",
        "unsupported",
    }
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


def _is_valid_evidence_excerpt(value: str) -> bool:
    return len(value) <= 320 and len(value.split()) <= 40


def _is_valid_evidence_locator(value: str) -> bool:
    return len(value) <= 300


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
    if not distillation.claims:
        issues.append("claims_incomplete")
    else:
        for index, claim in enumerate(distillation.claims, start=1):
            _required_insight_text(claim.claim, f"claim_{index}", issues)
            if claim.evidence_excerpt is not None:
                if _is_placeholder(claim.evidence_excerpt):
                    issues.append(f"claim_{index}_placeholder_evidence_excerpt")
                if not _is_valid_evidence_excerpt(claim.evidence_excerpt):
                    issues.append(f"claim_{index}_evidence_excerpt_too_long")
            if claim.support_locator is not None and _is_placeholder(claim.support_locator):
                issues.append(f"claim_{index}_placeholder_support_locator")
            if not claim.source_urls:
                issues.append(f"claim_{index}_missing_citation")
            if (
                claim.evidence_status.value == "verified"
                and not (
                    claim.evidence_excerpt
                    and not _is_placeholder(claim.evidence_excerpt)
                    or claim.support_locator
                    and not _is_placeholder(claim.support_locator)
                )
            ):
                issues.append(f"claim_{index}_missing_evidence")
    if not any(
        item.strip() and not _is_placeholder(item)
        for item in [*distillation.evidence_excerpts, *distillation.evidence_locators]
    ):
        issues.append("missing_evidence_locator")
    if any(_is_placeholder(item) for item in distillation.evidence_excerpts):
        issues.append("placeholder_evidence_excerpt")
    if any(not _is_valid_evidence_excerpt(item) for item in distillation.evidence_excerpts):
        issues.append("evidence_excerpt_too_long")
    if any(_is_placeholder(item) for item in distillation.evidence_locators):
        issues.append("placeholder_evidence_locator")
    if any(not _is_valid_evidence_locator(item) for item in distillation.evidence_locators):
        issues.append("evidence_locator_too_long")
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
        if insight.status not in {InsightStatus.SUPPORTED, InsightStatus.NOT_OBSERVED}:
            issues.append(f"invalid_{name}_status")
        _required_insight_text(insight.statement, f"{name}_statement", issues)
        _required_insight_text(
            insight.why_it_matters, f"{name}_why_it_matters", issues
        )
        _required_insight_text(insight.next_step, f"{name}_next_step", issues)
        if insight.evidence_excerpt is not None:
            if _is_placeholder(insight.evidence_excerpt):
                issues.append(f"{name}_placeholder_evidence_excerpt")
            if not _is_valid_evidence_excerpt(insight.evidence_excerpt):
                issues.append(f"{name}_evidence_excerpt_too_long")
        if insight.evidence_locator is not None and _is_placeholder(
            insight.evidence_locator
        ):
            issues.append(f"{name}_placeholder_evidence_locator")
        if (
            insight.status is InsightStatus.SUPPORTED
            and not (
                insight.evidence_excerpt
                and not _is_placeholder(insight.evidence_excerpt)
                or insight.evidence_locator
                and not _is_placeholder(insight.evidence_locator)
            )
        ):
            issues.append(f"{name}_missing_evidence")
    return issues


def article_fulfillment(
    source_url: str,
    *,
    source_persisted: bool,
    extracted: bool,
    distillation: ArticleDistillation | None,
    claims: Sequence[ClaimDraft] | None = None,
) -> dict[str, object]:
    """Project the source-to-UI fulfillment state from canonical records."""
    missing_fields: list[str] = []
    if not source_persisted:
        missing_fields.append("source")
    if not extracted:
        missing_fields.append("extraction")
    if distillation is None:
        missing_fields.append("distillation")
        quality_issues: list[str] = []
    else:
        quality_issues = validate_article_distillation_quality(distillation)
        missing_fields.extend(quality_issues)

    linked_claims = list(claims) if claims is not None else (
        distillation.claims if distillation is not None else []
    )
    citation_count = sum(1 for claim in linked_claims if claim.source_urls)
    complete = not missing_fields
    if not source_persisted:
        status = "orphaned"
    elif not extracted:
        status = "not_extracted"
    elif distillation is None:
        status = "extracted_only"
    elif complete:
        status = "complete"
    else:
        status = "incomplete"
    return {
        "source_url": normalize_url(source_url),
        "status": status,
        "complete": complete,
        "source_persisted": source_persisted,
        "extracted": extracted,
        "distillation_persisted": distillation is not None,
        "claims_persisted": bool(linked_claims),
        "claim_count": len(linked_claims),
        "citation_count": citation_count,
        "citation_complete": bool(linked_claims) and citation_count == len(linked_claims),
        "ui_displayable": source_persisted,
        "missing_fields": sorted(set(missing_fields)),
        "quality_issues": sorted(set(quality_issues)),
    }


def _readiness_source_by_url(
    sources: Sequence[SourceCandidate],
) -> dict[str, SourceCandidate]:
    scoped: dict[str, SourceCandidate] = {}
    for source in sources:
        url = normalize_url(source.url)
        if not source.is_seed and url not in scoped:
            scoped[url] = source
    return scoped


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
            if _is_placeholder(bullet.text):
                issues.append(f"{section}_{index}_missing_text")
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


def quality_metrics(
    sources: Sequence[SourceCandidate],
    distillations: Sequence[ArticleDistillation],
    brief: WeeklyBrief | None = None,
) -> dict[str, object]:
    """Compute current evidence readiness from persisted records, not status flags."""
    readiness_sources = _readiness_source_by_url(sources)
    extracted_sources = [
        source
        for source in readiness_sources.values()
        if source.extraction_status.value == "succeeded"
    ]
    extraction_issue_sources = [
        source
        for source in readiness_sources.values()
        if source.extraction_status.value != "succeeded"
    ]
    required_count = len(readiness_sources)
    all_distillation_counts: dict[str, int] = {}
    distillation_counts: dict[str, int] = {}
    readiness_distillations: dict[str, ArticleDistillation] = {}
    for item in distillations:
        url = normalize_url(item.source_url)
        all_distillation_counts[url] = all_distillation_counts.get(url, 0) + 1
        if url in readiness_sources:
            distillation_counts[url] = distillation_counts.get(url, 0) + 1
            readiness_distillations.setdefault(url, item)

    article_issues: dict[str, list[str]] = {}
    for item in readiness_distillations.values():
        url = normalize_url(item.source_url)
        issues = validate_article_distillation_quality(item)
        if issues:
            article_issues[url] = issues
    for source in extraction_issue_sources:
        article_issues[normalize_url(source.url)] = [
            f"extraction_{source.extraction_status.value}"
        ]
    for source in extracted_sources:
        url = normalize_url(source.url)
        count = distillation_counts.get(url, 0)
        if count == 0:
            article_issues[url] = ["missing_distillation"]
        elif count > 1:
            article_issues[url] = ["duplicate_distillation"]

    complete_count = sum(
        1
        for url, item in readiness_distillations.items()
        if distillation_counts[url] == 1 and not validate_article_distillation_quality(item)
    )
    source_by_url = {normalize_url(source.url): source for source in sources}
    fulfillment_urls = set(source_by_url) | set(all_distillation_counts)
    distillation_by_url = {
        normalize_url(item.source_url): item for item in distillations
    }
    article_fulfillment_records = [
        article_fulfillment(
            url,
            source_persisted=url in source_by_url,
            extracted=(
                source_by_url[url].extraction_status.value == "succeeded"
                if url in source_by_url
                else False
            ),
            distillation=distillation_by_url.get(url),
        )
        for url in sorted(fulfillment_urls)
    ]
    known_urls = set(readiness_sources)
    report_issues = (
        validate_report_sections(brief, known_urls) if brief is not None else []
    )
    report_sections_complete = 0
    if brief is not None:
        for section in REPORT_BULLET_SECTIONS:
            if not any(
                issue == f"{section}_empty" or issue.startswith(f"{section}_")
                for issue in report_issues
            ) and getattr(brief, section):
                report_sections_complete += 1

    blocking_reasons: set[str] = set()
    if article_issues:
        blocking_reasons.add("incomplete_article_insights")
    if any(issue.endswith("_empty") for issue in report_issues):
        blocking_reasons.add("empty_report_section")
    if any("unknown_citation" in issue for issue in report_issues):
        blocking_reasons.add("missing_citation")
    if any("missing_evidence" in issue for issue in report_issues):
        blocking_reasons.add("missing_evidence_locator")

    return {
        "article_count": required_count,
        "complete_article_count": complete_count,
        "article_insight_completeness": (
            round(complete_count / required_count, 6) if required_count else 0.0
        ),
        "article_quality_issues": article_issues,
        "article_fulfillment": article_fulfillment_records,
        "source_distillation_coverage": (
            round(
                sum(
                    1
                    for url in readiness_sources
                    if url in distillation_counts
                )
                / required_count,
                6,
            )
            if required_count
            else 0.0
        ),
        "report_section_count": len(REPORT_BULLET_SECTIONS),
        "report_sections_complete": report_sections_complete,
        "report_section_completeness": round(
            report_sections_complete / len(REPORT_BULLET_SECTIONS), 6
        ) if brief is not None else 0.0,
        "report_quality_issues": report_issues,
        "blocking_reasons": sorted(blocking_reasons),
        "quality_ready": not article_issues and not report_issues,
    }


def with_draft_prefix(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith(REQUIRED_DRAFT_PREFIX):
        return stripped
    return f"{REQUIRED_DRAFT_PREFIX}\n\n{stripped}"
