from __future__ import annotations

import json
from datetime import datetime

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    ExtractionStatus,
    SourceCandidate,
    ValidationCheck,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
    is_free_model,
)
from .validators import (
    claim_verification_allowed,
    content_hash,
    normalize_url,
    validate_article_distillation_quality,
    validate_evidence_quality,
    validate_report_sections,
)

MIN_SOURCE_COUNT = 10
MIN_CLAIM_COUNT = 5
REQUIRED_LANES = frozenset({"regulatory", "us-ports", "mexico"})
REQUIRED_GEOGRAPHIES = frozenset(
    {"Regulatory", "West Coast", "East Coast", "Gulf", "Mexico", "Europe"}
)
REQUIRED_REGIONS = frozenset(
    {"us", "canada", "mexico", "europe", "south-america", "middle-east", "global"}
)

_CHECK_REASON_MAP = {
    "article_insight_completeness": "incomplete_article_insights",
    "source_distillation_completeness": "incomplete_source_distillation",
    "citation_coverage": "missing_citation",
    "report_sections": "empty_report_section",
    "evidence_quality": "missing_evidence_locator",
}


def validation_blocking_reasons(report: ValidationReport) -> list[str]:
    """Map failed deterministic checks to stable operator-facing reasons."""
    reasons: set[str] = set()
    checks = getattr(report, "checks", [])
    for check in checks:
        if check.status is not ValidationStatus.FAILED:
            continue
        reason = _CHECK_REASON_MAP.get(check.name)
        if reason is not None:
            reasons.add(reason)
        if "citation" in check.message.lower() and check.name != "citation_coverage":
            reasons.add("missing_citation")
        if "evidence" in check.message.lower() and check.name != "evidence_quality":
            reasons.add("missing_evidence_locator")
    if (
        getattr(report, "status", ValidationStatus.BLOCKED) is not ValidationStatus.PASS
        and not reasons
    ):
        reasons.add("stale_validation")
    return sorted(reasons)


def source_quality_sources(sources: list[SourceCandidate]) -> list[SourceCandidate]:
    return [source for source in sources if not source.is_seed]


def _check(
    name: str,
    passed: bool,
    observed: str | int | float | bool | None,
    expected: str | int | float | bool | None,
    message: str,
) -> ValidationCheck:
    return ValidationCheck(
        name=name,
        status=ValidationStatus.PASS if passed else ValidationStatus.FAILED,
        observed=observed,
        expected=expected,
        message=message,
    )


def build_validation_report(
    run_id: str,
    sources: list[SourceCandidate],
    claims: list[ClaimDraft],
    as_of: datetime,
    model_id: str,
    lane_statuses: dict[str, str],
    source_hashes: list[str] | None = None,
    prompt_version: str = "validation-v1",
    minimum_sources: int = MIN_SOURCE_COUNT,
    minimum_claims: int = MIN_CLAIM_COUNT,
    tool_call_count: int | None = None,
    required_tool_lanes: dict[str, bool] | None = None,
    distillations: list[ArticleDistillation] | None = None,
    required_geographies: set[str] | None = None,
    required_regions: set[str] | None = None,
    required_lanes: set[str] | None = None,
    brief: WeeklyBrief | None = None,
) -> ValidationReport:
    quality_sources = source_quality_sources(sources)
    enriched_sources = [
        source
        for source in quality_sources
        if source.extraction_status is not ExtractionStatus.NOT_ATTEMPTED
        or source.region != "global"
        or source.language_code != "und"
    ]
    enriched_urls = {normalize_url(source.url) for source in enriched_sources}
    normalized_urls = [normalize_url(source.url) for source in quality_sources]
    known_urls = set(normalized_urls)
    cited_claims = [
        claim
        for claim in claims
        if claim.source_urls
        and all(normalize_url(url) in known_urls for url in claim.source_urls)
    ]
    coverage = len(cited_claims) / len(claims) if claims else 0.0
    lane_coverage = sorted(
        lane for lane, status in lane_statuses.items() if status in {"succeeded", "pass"}
    )
    geography_coverage = {
        geography
        for source in quality_sources
        for geography in source.geographies
    }
    expected_geographies = (
        set(REQUIRED_GEOGRAPHIES)
        if required_geographies is None
        else set(required_geographies)
    )
    missing_geographies = sorted(expected_geographies - geography_coverage)
    region_coverage = {source.region for source in quality_sources}
    expected_regions = set() if required_regions is None else set(required_regions)
    missing_regions = sorted(expected_regions - region_coverage)
    expected_lanes = set(REQUIRED_LANES) if required_lanes is None else set(required_lanes)
    future_sources = [
        source
        for source in quality_sources
        if source.published_at is not None and source.published_at > as_of
    ]
    invalid_verified = [
        claim
        for claim in claims
        if claim.evidence_status.value == "verified"
        and any(normalize_url(url) in enriched_urls for url in claim.source_urls)
        and not claim_verification_allowed(claim, quality_sources)
    ]
    seed_urls = {
        normalize_url(source.url) for source in sources if source.is_seed
    }
    seed_only_verified = [
        claim
        for claim in claims
        if claim.evidence_status.value == "verified"
        and claim.source_urls
        and set(normalize_url(url) for url in claim.source_urls).issubset(seed_urls)
    ]
    hashes = source_hashes or []
    duplicate_hashes = len(hashes) != len(set(hashes))
    quality_mode = bool(distillations) or any(
        source.extraction_status is not ExtractionStatus.NOT_ATTEMPTED
        or source.region != "global"
        or source.language_code != "und"
        for source in quality_sources
    )
    extraction_failures = [
        source
        for source in enriched_sources
        if source.extraction_status is not ExtractionStatus.SUCCEEDED
    ]
    distillation_urls = {
        normalize_url(item.source_url) for item in (distillations or [])
    }
    missing_distillations = [
        source
        for source in enriched_sources
        if distillations is not None
        and source.extraction_status is ExtractionStatus.SUCCEEDED
        and normalize_url(source.url) not in distillation_urls
    ]
    distillations_by_url = {
        normalize_url(item.source_url): item for item in (distillations or [])
    }
    article_insight_issues: dict[str, list[str]] = {}
    if distillations is not None:
        for distillation in distillations:
            issues = validate_article_distillation_quality(distillation)
            if issues:
                article_insight_issues[normalize_url(distillation.source_url)] = issues
        for source in enriched_sources:
            if source.extraction_status is not ExtractionStatus.SUCCEEDED:
                continue
            url = normalize_url(source.url)
            matched_distillation = distillations_by_url.get(url)
            issues = (
                ["missing_distillation"]
                if matched_distillation is None
                else validate_article_distillation_quality(matched_distillation)
            )
            if issues:
                article_insight_issues[url] = issues
    evidence_quality_issues = validate_evidence_quality(
        [
            claim
            for claim in claims
            if any(normalize_url(url) in enriched_urls for url in claim.source_urls)
        ],
        quality_sources,
    )
    checks = [
        _check(
            "minimum_sources",
            len(known_urls) >= minimum_sources,
            len(known_urls),
            minimum_sources,
            "unique source threshold",
        ),
        _check(
            "minimum_claims",
            len(claims) >= minimum_claims,
            len(claims),
            minimum_claims,
            "source-linked claim threshold",
        ),
        _check(
            "citation_coverage",
            bool(claims) and coverage == 1.0,
            coverage,
            1.0,
            "every claim must cite known sources",
        ),
        _check(
            "lane_coverage",
            expected_lanes.issubset(lane_coverage),
            ",".join(lane_coverage),
            ",".join(sorted(expected_lanes)) or "none",
            "all research lanes must complete",
        ),
        _check(
            "geography_coverage",
            not missing_geographies,
            ",".join(sorted(geography_coverage)),
            ",".join(sorted(expected_geographies)) or "none",
            "strict acceptance requires regulatory, U.S. ports, Mexico, and Europe coverage",
        ),
        _check(
            "publication_dates",
            not future_sources,
            len(future_sources),
            0,
            "no source may be published after as_of",
        ),
        _check(
            "content_hashes",
            not duplicate_hashes,
            len(hashes),
            "unique",
            "source snapshot hashes must be unique within a run",
        ),
        _check(
            "verified_claims",
            not invalid_verified,
            len(invalid_verified),
            0,
            "verified claims require independent evidence or primary-source critic approval",
        ),
        _check(
            "seed_verified_claims",
            not seed_only_verified,
            len(seed_only_verified),
            0,
            "user-provided seed sources cannot independently verify claims",
        ),
        _check(
            "free_model",
            is_free_model(model_id),
            model_id,
            ":free",
            "only OpenRouter :free models are permitted",
        ),
    ]
    if quality_mode:
        checks.extend(
            [
                _check(
                    "extraction_status",
                    not extraction_failures,
                    len(extraction_failures),
                    0,
                    "all selected non-seed sources must be extracted",
                ),
                _check(
                    "evidence_quality",
                    not evidence_quality_issues,
                    ",".join(evidence_quality_issues),
                    "none",
                    "evidence excerpts and verification bases must be valid",
                ),
            ]
        )
        if distillations is not None:
            checks.append(
                _check(
                    "source_distillation_completeness",
                    not missing_distillations,
                    len(missing_distillations),
                    0,
                    "every successfully extracted source must have one distillation",
                )
            )
            checks.append(
                _check(
                    "article_insight_completeness",
                    not article_insight_issues,
                    len(article_insight_issues),
                    0,
                    "every extracted article must have a complete insight packet",
                )
            )
        if expected_regions:
            checks.append(
                _check(
                    "regional_coverage",
                    not missing_regions,
                    ",".join(sorted(region_coverage)),
                    ",".join(sorted(expected_regions)),
                    "all required regional packs must produce evidence",
                )
            )
    if tool_call_count is not None:
        checks.append(
            _check(
                "agent_tool_calls",
                tool_call_count > 0,
                tool_call_count,
                ">0",
                "discovery must persist model-issued Tavily tool calls",
            )
        )
    if required_tool_lanes is not None:
        checks.append(
            _check(
                "required_tool_calls",
                all(required_tool_lanes.values()),
                sum(1 for passed in required_tool_lanes.values() if passed),
                len(required_tool_lanes),
                "every discovery lane must call Search and Extract",
            )
        )
    if brief is not None:
        report_section_issues = validate_report_sections(
            brief,
            {normalize_url(source.url) for source in sources},
        )
        checks.append(
            _check(
                "report_sections",
                not report_section_issues,
                ";".join(report_section_issues) or "complete",
                "complete",
                "all report sections must be populated, cited, and structured",
            )
        )
    lane_partial = any(status in {"partial", "blocked"} for status in lane_statuses.values())
    hard_fail = any(
        check.status is ValidationStatus.FAILED
        and not (check.name == "lane_coverage" and lane_partial)
        for check in checks
    )
    if not lane_partial and not expected_lanes.issubset(lane_coverage):
        hard_fail = True
    status = (
        ValidationStatus.FAILED
        if hard_fail
        else ValidationStatus.PARTIAL
        if lane_partial
        else ValidationStatus.PASS
    )
    report = ValidationReport(
        run_id=run_id,
        status=status,
        source_count=len(quality_sources),
        unique_source_count=len(known_urls),
        claim_count=len(claims),
        cited_claim_count=len(cited_claims),
        citation_coverage=round(coverage, 6),
        lane_coverage=lane_coverage,
        checks=checks,
        model_id=model_id,
        prompt_version=prompt_version,
        as_of=as_of,
    )
    report = report.model_copy(
        update={"blocking_reasons": validation_blocking_reasons(report)}
    )
    payload = report.model_dump(mode="json", exclude={"content_hash"})
    return report.model_copy(
        update={"content_hash": content_hash(json.dumps(payload, sort_keys=True))}
    )
