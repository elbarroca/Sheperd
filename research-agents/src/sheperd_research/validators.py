from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    DecisionScore,
    DistillationQualityStatus,
    ExtractionStatus,
    FreshnessStatus,
    InsightStatus,
    PageType,
    PeriodBasis,
    PeriodStatus,
    PublicationDateBasis,
    SignalEvent,
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
ALLOWED_SIGNAL_EVENT_TYPES = frozenset(
    {
        "regulatory",
        "court",
        "port",
        "carrier",
        "terminal",
        "congestion",
        "closure",
        "fee",
        "volume",
        "other",
    }
)
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
_MIN_EVIDENCE_DATE = datetime(2000, 1, 1, tzinfo=UTC)
_ISO_DATE_PATTERN = re.compile(
    r"\b\d{4}-\d{2}-\d{2}(?:[T ][0-2]\d:[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?\b"
)
_RFC_2822_PATTERN = re.compile(
    r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\d{1,2}\s+"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}"
    r"(?:\s+\d{2}:\d{2}(?::\d{2})?\s+(?:GMT|UTC|[+-]\d{4}))?\b",
    re.IGNORECASE,
)
_PUBLICATION_MARKERS = ("published", "publication date", "updated", "posted")
_MIN_SINGLE_SLUG_ARTICLE_CHARS = 1_500
_MIN_SINGLE_SLUG_ARTICLE_WORDS = 5
_MIN_DATED_REPORT_MARKERS = 2
_NAVIGATION_PAGE_TYPES = frozenset(
    {PageType.ARCHIVE, PageType.INDEX, PageType.CATEGORY, PageType.LANDING}
)
_RELEVANCE_MARKERS = (
    "port",
    "terminal",
    "carrier",
    "cargo",
    "shipping",
    "maritime",
    "congestion",
    "dwell",
    "demurrage",
    "detention",
    "regulation",
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


def classify_page_type(source: SourceCandidate, content: str) -> PageType:
    path = urlsplit(normalize_url(source.url)).path.casefold()
    segments = [segment for segment in path.split("/") if segment]
    title = source.title.casefold()
    if path.endswith(".pdf") or any(
        marker in segments for marker in ("orders", "notices", "regulations", "rulings")
    ):
        return PageType.OFFICIAL_DOCUMENT
    if "feed" in segments or path.endswith((".atom", ".rss", ".xml")):
        return PageType.INDEX
    if "category" in segments or "category" in title:
        return PageType.CATEGORY
    if "search" in segments or "search results" in title:
        return PageType.INDEX
    if "archive" in segments or "archive" in title:
        return PageType.ARCHIVE
    navigation_endings = {
        "articles",
        "blog",
        "media",
        "news",
        "news-events",
        "newsroom",
        "press-releases",
        "updates",
    }
    if not segments:
        return PageType.LANDING
    if segments[-1] in navigation_endings:
        return PageType.ARCHIVE
    single_slug_article = (
        len(segments) == 1
        and len(segments[0].split("-")) >= _MIN_SINGLE_SLUG_ARTICLE_WORDS
        and len(content) >= _MIN_SINGLE_SLUG_ARTICLE_CHARS
        and re.search(r"(?im)^(?:by|author)\s+(?:[:-]\s*)?\S+", content) is not None
    )
    dated_report = (
        segments[-1] in {"report", "statistics", "stats"}
        and len(content) >= _MIN_SINGLE_SLUG_ARTICLE_CHARS
        and re.search(r"(?m)^#\s+\S", content) is not None
        and len(re.findall(r"(?im)^\W*data through\b", content))
        >= _MIN_DATED_REPORT_MARKERS
    )
    if (
        len(segments) >= 2
        or extract_publication_date(content)[0] is not None
        or single_slug_article
        or dated_report
    ):
        return PageType.ARTICLE
    return PageType.UNKNOWN


def _parse_evidence_datetime(value: str) -> datetime | None:
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(normalized)
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def extract_publication_date(content: str) -> tuple[datetime | None, str | None]:
    """Extract a declared page publication timestamp and its exact line locator."""
    for raw_line in content.splitlines():
        line = " ".join(raw_line.strip().split())
        if not line or not any(marker in line.casefold() for marker in _PUBLICATION_MARKERS):
            continue
        match = _ISO_DATE_PATTERN.search(line) or _RFC_2822_PATTERN.search(line)
        if match is None:
            continue
        parsed = _parse_evidence_datetime(match.group(0))
        if parsed is not None:
            return parsed, line[:300]
    return None, None


def reconcile_publication_dates(
    source: SourceCandidate,
    page_published_at: datetime | None,
    locator: str | None,
) -> SourceCandidate:
    """Resolve independent search/page evidence without laundering conflicts."""
    search_published_at = source.search_published_at or source.published_at
    search_valid = (
        search_published_at is not None and search_published_at >= _MIN_EVIDENCE_DATE
    )
    page_valid = page_published_at is not None and page_published_at >= _MIN_EVIDENCE_DATE
    if (
        page_published_at is not None
        and not page_valid
        or search_published_at is not None
        and not search_valid
    ):
        basis = PublicationDateBasis.CONFLICT
        published_at = None
    elif search_valid and page_valid:
        assert search_published_at is not None and page_published_at is not None
        if search_published_at.astimezone(UTC).date() == page_published_at.astimezone(UTC).date():
            basis = PublicationDateBasis.MATCHED
            published_at = page_published_at
        else:
            basis = PublicationDateBasis.CONFLICT
            published_at = None
    elif page_valid:
        basis = PublicationDateBasis.PAGE
        published_at = page_published_at
    elif search_valid:
        basis = PublicationDateBasis.SEARCH
        published_at = search_published_at
    else:
        basis = PublicationDateBasis.UNKNOWN
        published_at = None
    return source.model_copy(
        update={
            "published_at": published_at,
            "search_published_at": search_published_at,
            "page_published_at": page_published_at,
            "publication_date_basis": basis,
            "publication_date_locator": (
                locator
                if page_valid
                else source.publication_date_locator
                if search_valid
                else None
            ),
        }
    )


def pack_article_content(content: str, *, max_chars: int = 8_000) -> str:
    """Keep opening, date/relevance evidence, headings, and closing in one bounded packet."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    cleaned = content.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    lines = [line.rstrip() for line in cleaned.splitlines()]
    opening_budget = max_chars // 4
    closing_budget = max_chars // 4
    signal_budget = max_chars - opening_budget - closing_budget - 64
    opening = "\n".join(lines)[:opening_budget]
    closing = "\n".join(lines)[-closing_budget:]
    signal_lines: list[str] = []
    for index, line in enumerate(lines):
        lowered = line.casefold()
        if not (
            line.lstrip().startswith("#")
            or _ISO_DATE_PATTERN.search(line)
            or _RFC_2822_PATTERN.search(line)
            or any(marker in lowered for marker in _RELEVANCE_MARKERS)
        ):
            continue
        for nearby in lines[max(0, index - 1) : min(len(lines), index + 2)]:
            if nearby and nearby not in signal_lines:
                signal_lines.append(nearby)
    signals = "\n".join(signal_lines)[:signal_budget]
    packed = (
        f"[OPENING]\n{opening}\n\n[DATE AND RELEVANCE EVIDENCE]\n{signals}"
        f"\n\n[CLOSING]\n{closing}"
    )
    return packed[:max_chars]


def score_article(
    source: SourceCandidate,
    distillation: ArticleDistillation,
    as_of: datetime,
) -> DecisionScore:
    relevance = 30 if source.lane != "unassigned" and source.region else 15
    impact = 25 if distillation.event_type != "other" and distillation.why_it_matters else 10
    actionability = 20 if distillation.next_steps else 0
    if source.published_at is None or source.published_at > as_of:
        recency = 0
        recency_reason = "No valid publication date at the run snapshot."
    else:
        age_days = (as_of - source.published_at).days
        recency = 15 if age_days <= 7 else 10 if age_days <= 14 else 5 if age_days <= 30 else 0
        recency_reason = f"Published {age_days} day(s) before the run as-of."
    authority = {"primary": 10, "reference": 8, "trade-press": 6}.get(
        source.authority_tier,
        4,
    )
    total = relevance + impact + actionability + recency + authority
    return DecisionScore(
        sheperd_relevance=relevance,
        operational_impact=impact,
        actionability=actionability,
        recency=recency,
        source_authority=authority,
        total=total,
        rationale={
            "sheperd_relevance": f"Mapped to {source.lane} / {source.region}.",
            "operational_impact": f"Classified as {distillation.event_type} with stated impact.",
            "actionability": (
                "Includes a source-bound next step." if actionability else "No next step."
            ),
            "recency": recency_reason,
            "source_authority": f"Authority tier is {source.authority_tier}.",
        },
    )


def source_weekly_evidence_ready(
    source: SourceCandidate,
    distillation: ArticleDistillation | None,
) -> bool:
    return (
        source.direct_content
        and classify_page_type(source, "") not in _NAVIGATION_PAGE_TYPES
        and source.page_type in {PageType.ARTICLE, PageType.OFFICIAL_DOCUMENT}
        and source.publication_date_basis
        in {
            PublicationDateBasis.MATCHED,
            PublicationDateBasis.PAGE,
            PublicationDateBasis.SEARCH,
        }
        and source.extraction_status is ExtractionStatus.SUCCEEDED
        and source.lane in {"regulatory", "us-ports", "mexico"}
        and bool(source.region)
        and distillation is not None
        and distillation.quality_status is DistillationQualityStatus.COMPLETE
        and distillation.decision_score is not None
    )


def reader_source_contract_issues(
    source: SourceCandidate,
    distillation: ArticleDistillation | None,
    *,
    as_of: datetime | None = None,
) -> list[str]:
    """Return fail-closed reader-pipeline defects for one persisted source."""
    issues: list[str] = []
    if classify_page_type(source, "") in _NAVIGATION_PAGE_TYPES:
        issues.append("navigation_url")
    if not source.direct_content:
        issues.append("not_direct_content")
    if source.page_type not in {PageType.ARTICLE, PageType.OFFICIAL_DOCUMENT}:
        issues.append("invalid_page_type")
    if source.extraction_status is not ExtractionStatus.SUCCEEDED:
        issues.append("extraction_incomplete")

    date_values = (
        source.published_at,
        source.search_published_at,
        source.page_published_at,
    )
    if any(value is not None and value < _MIN_EVIDENCE_DATE for value in date_values):
        issues.append("implausible_publication_date")
    if as_of is not None and any(
        value is not None and value > as_of for value in date_values
    ):
        issues.append("future_publication_date")
    if source.published_at is not None:
        if source.publication_date_basis not in {
            PublicationDateBasis.MATCHED,
            PublicationDateBasis.PAGE,
            PublicationDateBasis.SEARCH,
        }:
            issues.append("invalid_publication_date_basis")
        if not source.publication_date_locator or _is_placeholder(
            source.publication_date_locator
        ):
            issues.append("missing_publication_date_locator")
    elif source.publication_date_basis is PublicationDateBasis.CONFLICT:
        issues.append("conflicting_publication_date")

    if distillation is None:
        issues.append("missing_distillation")
        return sorted(set(issues))
    issues.extend(validate_article_distillation_quality(distillation))
    if not distillation.prompt_version.startswith("distill-v7"):
        issues.append("legacy_distillation_contract")
    if len(distillation.key_points) != 3:
        issues.append("key_points_must_equal_three")
    if distillation.decision_score is None:
        issues.append("missing_decision_score")
    return sorted(set(issues))


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
        for value in (
            source.published_at,
            source.search_published_at,
            source.page_published_at,
        ):
            if value is not None and value < _MIN_EVIDENCE_DATE:
                raise ValueError(f"source publication date is implausible: {source.url}")
            if value is not None and value > as_of:
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
    if distillation.event_type not in ALLOWED_SIGNAL_EVENT_TYPES:
        issues.append("invalid_event_type")
    _required_insight_text(distillation.headline, "headline", issues)
    if distillation.event_at is not None and (
        not distillation.event_at_locator
        or _is_placeholder(distillation.event_at_locator)
    ):
        issues.append("event_at_missing_locator")
    if distillation.event_at is not None and distillation.event_at < _MIN_EVIDENCE_DATE:
        issues.append("implausible_event_at")
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
    if distillation.prompt_version.startswith("distill-v7") and len(distillation.key_points) != 3:
        issues.append("key_points_must_equal_three")
    if distillation.prompt_version.startswith("distill-v7") and distillation.decision_score is None:
        issues.append("missing_decision_score")
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


def validate_signal_event_quality(event: SignalEvent) -> list[str]:
    """Reject incomplete new events while keeping legacy rows readable."""
    issues: list[str] = []
    if event.event_type not in ALLOWED_SIGNAL_EVENT_TYPES:
        issues.append("invalid_event_type")
    for field, value in (
        ("headline", event.headline),
        ("what_changed", event.what_changed),
        ("region", event.region),
        ("lane", event.lane),
        ("impact", event.impact),
        ("risk", event.risk),
        ("opportunity", event.opportunity),
        ("next_step", event.next_step),
    ):
        _required_insight_text(value, field, issues)
    if event.retrieved_at is None:
        issues.append("missing_retrieved_at")
    if event.period_status is None:
        issues.append("missing_period_status")
    if event.period_basis is None:
        issues.append("missing_period_basis")
    if not event.evidence_locator or _is_placeholder(event.evidence_locator):
        issues.append("missing_evidence_locator")
    if not event.limitations or any(
        _is_placeholder(item) for item in event.limitations
    ):
        issues.append("limitations_incomplete")
    if event.eligible_for_weekly:
        if event.period_status is not PeriodStatus.IN_PERIOD:
            issues.append("eligible_event_outside_period")
        if event.period_basis not in {
            PeriodBasis.PUBLISHED_AT,
            PeriodBasis.EVENT_AT,
        }:
            issues.append("eligible_event_invalid_period_basis")
        if (
            event.period_basis is PeriodBasis.PUBLISHED_AT
            and event.published_at is None
        ) or (
            event.period_basis is PeriodBasis.EVENT_AT and event.event_at is None
        ):
            issues.append("eligible_event_missing_period_date")
    return issues


def article_fulfillment(
    source_url: str,
    *,
    source_persisted: bool,
    extracted: bool,
    distillation: ArticleDistillation | None,
    claims: Sequence[ClaimDraft] | None = None,
    distillation_count: int | None = None,
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
    persisted_distillations = (
        distillation_count
        if distillation_count is not None
        else (1 if distillation is not None else 0)
    )
    if persisted_distillations > 1:
        quality_issues.append("duplicate_distillation")
        missing_fields.append("duplicate_distillation")

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


def quality_blocking_reasons(
    article_issues: dict[str, list[str]],
    report_issues: Sequence[str],
) -> list[str]:
    reasons: set[str] = set()
    flattened_article_issues = {
        issue for issues in article_issues.values() for issue in issues
    }
    if article_issues:
        reasons.add("incomplete_article_insights")
    if "duplicate_distillation" in flattened_article_issues:
        reasons.add("duplicate_distillation")
    if any(
        "missing_evidence" in issue
        or "missing_evidence_locator" in issue
        or "placeholder_evidence" in issue
        for issue in flattened_article_issues
    ):
        reasons.add("missing_evidence_locator")
    if any(
        "missing_citation" in issue or issue == "claims_incomplete"
        for issue in flattened_article_issues
    ):
        reasons.add("missing_citation")
    if any(issue.endswith("_empty") for issue in report_issues):
        reasons.add("empty_report_section")
    if any("unknown_citation" in issue for issue in report_issues):
        reasons.add("missing_citation")
    if any("missing_evidence" in issue for issue in report_issues):
        reasons.add("missing_evidence_locator")
    return sorted(reasons)


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
    for url, source in readiness_sources.items():
        distillation = readiness_distillations.get(url)
        if (
            distillation is None
            or not distillation.prompt_version.startswith("distill-v7")
        ):
            continue
        contract_issues = reader_source_contract_issues(source, distillation)
        if contract_issues:
            article_issues[url] = sorted(
                set(article_issues.get(url, [])) | set(contract_issues)
            )

    complete_count = sum(
        1
        for url, item in readiness_distillations.items()
        if distillation_counts[url] == 1 and url not in article_issues
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
            distillation_count=all_distillation_counts.get(url, 0),
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
        "blocking_reasons": quality_blocking_reasons(article_issues, report_issues),
        "quality_ready": not article_issues and not report_issues,
    }


def with_draft_prefix(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith(REQUIRED_DRAFT_PREFIX):
        return stripped
    return f"{REQUIRED_DRAFT_PREFIX}\n\n{stripped}"
