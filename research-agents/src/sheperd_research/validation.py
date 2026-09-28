from __future__ import annotations

import json
from datetime import datetime

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    ExtractionStatus,
    SignalEvent,
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
    reader_source_contract_issues,
    validate_article_distillation_quality,
    validate_evidence_quality,
    validate_report_sections,
    validate_signal_event_quality,
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
    "agent_tool_calls": "missing_tool_receipts",
    "citation_coverage": "missing_citation",
    "content_hashes": "duplicate_source_hash",
    "evidence_quality": "missing_evidence_locator",
    "extract_receipts": "missing_extract_receipts",
    "extraction_status": "extraction_failed",
    "model_policy": "model_policy_failed",
    "geography_coverage": "incomplete_geography_coverage",
    "lane_coverage": "incomplete_lane_coverage",
    "minimum_claims": "insufficient_claims",
    "minimum_sources": "insufficient_sources",
    "eligible_weekly_sources": "insufficient_in_period_sources",
    "publication_dates": "invalid_publication_dates",
    "reader_source_contract": "incomplete_reader_source_contract",
    "regional_coverage": "incomplete_regional_coverage",
    "report_sections": "empty_report_section",
    "required_tool_calls": "missing_required_tool_calls",
    "seed_verified_claims": "seed_only_verified_claim",
    "signal_event_completeness": "incomplete_signal_events",
    "source_distillation_completeness": "incomplete_source_distillation",
    "verified_claims": "unsupported_verified_claim",
}
_PROVIDER_ERROR_REASON_MAP = {
    "authentication": "provider_authentication_failed",
    "extraction_failed": "extraction_failed",
    "malformed_output": "provider_malformed_output",
    "missing_tool_call": "missing_required_tool_calls",
    "model_unavailable": "provider_model_unavailable",
    "payg_limit": "provider_usage_limited",
    "plan_usage_limit": "provider_usage_limited",
    "provider_error": "provider_failed",
    "provider": "provider_failed",
    "provider_unavailable": "provider_unavailable",
    "rate_limit": "provider_rate_limit",
    "source_access": "source_access_failed",
    "timeout": "provider_timeout",
    "tool_failure": "provider_tool_failure",
}
_PROVIDER_ERROR_CODES = frozenset(_PROVIDER_ERROR_REASON_MAP)


def provider_error_codes_from_run(
    *,
    sources: list[SourceCandidate],
    steps: list[dict[str, object]],
    tool_calls: list[dict[str, object]],
) -> list[str]:
    """Collect stable provider/extraction error codes from persisted run evidence."""
    codes: set[str] = set()
    for source in sources:
        if source.extraction_error_code:
            codes.add(source.extraction_error_code)
        if source.extraction_status is ExtractionStatus.FAILED:
            codes.add("extraction_failed")
    for step in steps:
        code = step.get("error_code")
        metadata = step.get("metadata")
        if isinstance(metadata, dict):
            captured_tool_fallback = (
                metadata.get("selection_basis")
                == "captured_tool_evidence_fallback"
            )
            attempts = metadata.get("attempts")
            attempt_records = [
                attempt for attempt in attempts if isinstance(attempt, dict)
            ] if isinstance(attempts, list) else []

            def logical_key(record: dict[str, object]) -> tuple[str, str, str] | None:
                operation = record.get("operation")
                source_url = record.get("source_url")
                input_hash = record.get("input_hash")
                if not isinstance(operation, str):
                    return None
                if not isinstance(source_url, str):
                    source_url = ""
                if not isinstance(input_hash, str):
                    input_hash = ""
                if not source_url and not input_hash:
                    return None
                return operation, source_url, input_hash

            recovered_keys = {
                key
                for attempt in attempt_records
                if not attempt.get("error_code")
                for key in [logical_key(attempt)]
                if key is not None
            }

            def recovered_by_retry(
                attempt: dict[str, object],
                *,
                attempt_records: list[dict[str, object]] = attempt_records,
                recovered_keys: set[tuple[str, str, str]] = recovered_keys,
            ) -> bool:
                key = logical_key(attempt)
                if key is not None and key in recovered_keys:
                    return True
                operation = attempt.get("operation")
                attempt_number = attempt.get("attempt")
                if not isinstance(operation, str) or not isinstance(
                    attempt_number, int
                ):
                    return False
                return any(
                    not later.get("error_code")
                    and later.get("operation") == operation
                    and (
                        (
                            key is not None
                            and logical_key(later) == key
                        )
                        or (
                            key is None
                            and later.get("attempt") == attempt_number + 1
                        )
                    )
                    for later in attempt_records
                )

            call = metadata.get("call")
            step_key = logical_key(call) if isinstance(call, dict) else logical_key(metadata)
            recovered_attempt = any(
                recovered_by_retry(attempt)
                for attempt in attempt_records
                if attempt.get("error_code")
            )
            if (
                isinstance(code, str)
                and code in _PROVIDER_ERROR_CODES
                and not (
                    step_key in recovered_keys
                    or (
                        isinstance(call, dict)
                        and recovered_by_retry(call)
                    )
                    or recovered_attempt
                    or step.get("status") == "succeeded"
                    or (
                        captured_tool_fallback
                        and code == "malformed_output"
                    )
                )
            ):
                codes.add(code)
            if isinstance(call, dict):
                call_code = call.get("error_code")
                if (
                    isinstance(call_code, str)
                    and call_code in _PROVIDER_ERROR_CODES
                    and not recovered_by_retry(call)
                    and not (
                        captured_tool_fallback
                        and call_code == "malformed_output"
                    )
                ):
                    codes.add(call_code)
            for attempt in attempt_records:
                attempt_code = attempt.get("error_code")
                if (
                    isinstance(attempt_code, str)
                    and attempt_code in _PROVIDER_ERROR_CODES
                    and not recovered_by_retry(attempt)
                    and not (
                        captured_tool_fallback
                        and attempt_code == "malformed_output"
                    )
                ):
                    codes.add(attempt_code)
        elif isinstance(code, str) and code in _PROVIDER_ERROR_CODES:
            codes.add(code)
    for call in tool_calls:
        code = call.get("error_code")
        if isinstance(code, str) and code in _PROVIDER_ERROR_CODES:
            codes.add(code)
    return sorted(codes)


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
        if (
            check.name != "provider_error_codes"
            and "citation" in check.message.lower()
            and check.name != "citation_coverage"
        ):
            reasons.add("missing_citation")
        if "provider" in check.message.lower() or "tool" in check.message.lower():
            reasons.add("provider_observability_failed")
        check_text = " ".join(
            str(value)
            for value in (check.name, check.message, check.observed, check.expected)
        )
        for error_code, stable_reason in _PROVIDER_ERROR_REASON_MAP.items():
            if error_code in check_text:
                reasons.add(stable_reason)
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
    required_source_hash_count: int | None = None,
    tool_call_count: int | None = None,
    required_tool_lanes: dict[str, bool] | None = None,
    distillations: list[ArticleDistillation] | None = None,
    signal_events: list[SignalEvent] | None = None,
    required_geographies: set[str] | None = None,
    required_regions: set[str] | None = None,
    required_lanes: set[str] | None = None,
    brief: WeeklyBrief | None = None,
    provider_error_codes: list[str] | None = None,
    eligible_weekly_source_count: int | None = None,
    minimum_eligible_sources: int | None = None,
    require_reader_contract: bool = False,
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
    completed_lanes = {
        lane for lane, status in lane_statuses.items() if status in {"succeeded", "pass"}
    }
    strict_period_mode = (
        eligible_weekly_source_count is not None
        and minimum_eligible_sources is not None
    )
    coverage_sources = (
        [source for source in quality_sources if source.eligible_for_weekly]
        if strict_period_mode
        else quality_sources
    )
    source_lanes = {source.lane for source in coverage_sources}
    lane_coverage = sorted(
        completed_lanes & source_lanes if strict_period_mode else completed_lanes
    )
    geography_coverage = {
        geography
        for source in coverage_sources
        for geography in source.geographies
    }
    expected_geographies = (
        set(REQUIRED_GEOGRAPHIES)
        if required_geographies is None
        else set(required_geographies)
    )
    missing_geographies = sorted(expected_geographies - geography_coverage)
    region_coverage = {source.region for source in coverage_sources}
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
    event_url_counts: dict[str, int] = {}
    event_quality_issues: dict[str, list[str]] = {}
    for event in signal_events or []:
        issues = validate_signal_event_quality(event)
        if issues:
            event_quality_issues[event.event_id] = issues
        if len(event.source_urls) != 1:
            event_quality_issues.setdefault(event.event_id, []).append(
                "event_requires_one_source"
            )
            continue
        url = normalize_url(event.source_urls[0])
        event_url_counts[url] = event_url_counts.get(url, 0) + 1
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
    distillation_url_counts: dict[str, int] = {}
    for item in distillations or []:
        url = normalize_url(item.source_url)
        distillation_url_counts[url] = distillation_url_counts.get(url, 0) + 1
    distillation_urls = set(distillation_url_counts)
    missing_distillations = [
        source
        for source in enriched_sources
        if distillations is not None
        and source.extraction_status is ExtractionStatus.SUCCEEDED
        and normalize_url(source.url) not in distillation_urls
    ]
    duplicate_distillations = [
        url for url, count in distillation_url_counts.items() if count > 1
    ]
    unexpected_distillations = sorted(distillation_urls - known_urls)
    distillations_by_url = {
        normalize_url(item.source_url): item for item in (distillations or [])
    }
    reader_contract_issues = {
        normalize_url(source.url): issues
        for source in enriched_sources
        if (
            issues := reader_source_contract_issues(
                source,
                distillations_by_url.get(normalize_url(source.url)),
                as_of=as_of,
            )
        )
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
            "strict acceptance requires the configured geography scope",
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
            "model_policy",
            is_free_model(model_id),
            model_id,
            "OpenAI model identifier",
            (
                "new runs must use the configured OpenAI model; legacy OpenRouter "
                ":free records remain readable"
            ),
        ),
    ]
    if eligible_weekly_source_count is not None and minimum_eligible_sources is not None:
        checks.append(
            _check(
                "eligible_weekly_sources",
                eligible_weekly_source_count >= minimum_eligible_sources,
                eligible_weekly_source_count,
                minimum_eligible_sources,
                "weekly source threshold uses publication-dated in-period sources",
            )
        )
    if required_source_hash_count is not None:
        checks.append(
            _check(
                "extract_receipts",
                len(hashes) == required_source_hash_count and not duplicate_hashes,
                len(hashes),
                required_source_hash_count,
                "every repaired source requires one unique Extract snapshot receipt",
            )
        )
    if require_reader_contract:
        checks.append(
            _check(
                "reader_source_contract",
                not reader_contract_issues,
                len(enriched_sources) - len(reader_contract_issues),
                len(enriched_sources),
                "every extracted source must be a direct article with honest date "
                "provenance and a scored decision packet",
            )
        )
    if signal_events is not None:
        signal_complete = (
            not event_quality_issues
            and set(event_url_counts) == known_urls
            and all(count == 1 for count in event_url_counts.values())
        )
        checks.append(
            _check(
                "signal_event_completeness",
                signal_complete,
                len(event_url_counts),
                len(known_urls),
                "every source must produce exactly one complete signal event",
            )
        )
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
                    not missing_distillations
                    and not duplicate_distillations
                    and not unexpected_distillations,
                    (
                        len(missing_distillations)
                        + len(duplicate_distillations)
                        + len(unexpected_distillations)
                    ),
                    0,
                    "every successfully extracted source must have exactly one distillation",
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
    if provider_error_codes:
        stable_codes = sorted(set(provider_error_codes))
        checks.append(
            _check(
                "provider_error_codes",
                False,
                ",".join(stable_codes),
                "none",
                "provider/extraction error codes persisted in run evidence",
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
