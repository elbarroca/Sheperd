from __future__ import annotations

import json
from datetime import datetime

from .contracts import (
    ClaimDraft,
    SourceCandidate,
    ValidationCheck,
    ValidationReport,
    ValidationStatus,
    is_free_model,
)
from .settings import STRICT_OPENROUTER_MODEL
from .validators import content_hash, normalize_url

MIN_SOURCE_COUNT = 10
MIN_CLAIM_COUNT = 5
REQUIRED_LANES = frozenset({"regulatory", "us-ports", "mexico"})
REQUIRED_GEOGRAPHIES = frozenset(
    {"Regulatory", "West Coast", "East Coast", "Gulf", "Mexico", "Europe"}
)


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
) -> ValidationReport:
    quality_sources = source_quality_sources(sources)
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
    missing_geographies = sorted(REQUIRED_GEOGRAPHIES - geography_coverage)
    future_sources = [
        source
        for source in quality_sources
        if source.published_at is not None and source.published_at > as_of
    ]
    uncited_verified = [
        claim
        for claim in claims
        if claim.evidence_status.value == "verified"
        and not claim.source_urls
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
            REQUIRED_LANES.issubset(lane_coverage),
            ",".join(lane_coverage),
            ",".join(sorted(REQUIRED_LANES)),
            "all research lanes must complete",
        ),
        _check(
            "geography_coverage",
            not missing_geographies,
            ",".join(sorted(geography_coverage)),
            ",".join(sorted(REQUIRED_GEOGRAPHIES)),
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
            not uncited_verified,
            len(uncited_verified),
            0,
            "verified claims require citations",
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
            STRICT_OPENROUTER_MODEL,
            "only the strict Gemma model is permitted",
        ),
    ]
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
    lane_partial = any(status in {"partial", "blocked"} for status in lane_statuses.values())
    hard_fail = any(
        check.status is ValidationStatus.FAILED
        and not (check.name == "lane_coverage" and lane_partial)
        for check in checks
    )
    if not lane_partial and not REQUIRED_LANES.issubset(lane_coverage):
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
    payload = report.model_dump(mode="json", exclude={"content_hash"})
    return report.model_copy(
        update={"content_hash": content_hash(json.dumps(payload, sort_keys=True))}
    )
