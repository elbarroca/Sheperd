from __future__ import annotations

from datetime import UTC, datetime

from sheperd_research.contracts import (
    ClaimDraft,
    EvidenceStatus,
    SourceCandidate,
    ValidationStatus,
)
from sheperd_research.settings import STRICT_OPENROUTER_MODEL
from sheperd_research.validation import build_validation_report


def _sources() -> list[SourceCandidate]:
    return [
        SourceCandidate(
            url=f"https://example.com/source-{index}",
            lane=("regulatory", "us-ports", "mexico")[index % 3],
            geographies=[("Regulatory", "West Coast", "Mexico")[index % 3]],
        )
        for index in range(10)
    ]


def test_validation_passes_with_thresholds_and_full_citations() -> None:
    sources = _sources()
    claims = [
        ClaimDraft(
            claim=f"Claim {index}",
            source_urls=[sources[index].url],
        )
        for index in range(5)
    ]
    report = build_validation_report(
        "run-1",
        sources,
        claims,
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
    )

    assert report.status is ValidationStatus.PASS
    assert report.citation_coverage == 1.0
    assert report.content_hash


def test_provider_partial_is_not_silently_promoted_to_pass() -> None:
    sources = _sources()
    report = build_validation_report(
        "run-2",
        sources,
        [
            ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
            for index in range(5)
        ],
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "partial", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
    )

    assert report.status is ValidationStatus.PARTIAL


def test_seed_only_verified_claim_is_not_promoted() -> None:
    sources = _sources()
    sources[0] = sources[0].model_copy(update={"is_seed": True})
    claims = [
        ClaimDraft(
            claim=f"Claim {index}",
            source_urls=[sources[index].url],
            evidence_status=EvidenceStatus.VERIFIED if index == 0 else EvidenceStatus.UNVERIFIED,
        )
        for index in range(5)
    ]

    report = build_validation_report(
        "run-seed",
        sources,
        claims,
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
    )

    assert report.status is ValidationStatus.FAILED
    assert any(check.name == "seed_verified_claims" for check in report.checks)


def test_validation_excludes_seed_only_sources_from_quality_counts() -> None:
    sources = _sources()
    sources[0] = sources[0].model_copy(
        update={"is_seed": True, "source_kind": "seed-only"}
    )
    claims = [
        ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
        for index in range(1, 6)
    ]

    report = build_validation_report(
        "run-seed-counts",
        sources,
        claims,
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(1, 10)],
        minimum_sources=9,
    )

    assert report.status is ValidationStatus.PASS
    assert report.source_count == 9
    assert report.unique_source_count == 9
