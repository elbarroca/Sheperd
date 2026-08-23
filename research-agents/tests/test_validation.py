from __future__ import annotations

from datetime import UTC, datetime

from sheperd_research.contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    ExtractionStatus,
    ReportBullet,
    SourceCandidate,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.settings import STRICT_OPENROUTER_MODEL
from sheperd_research.validation import build_validation_report, validation_blocking_reasons


def _sources() -> list[SourceCandidate]:
    geographies = (
        "Regulatory",
        "West Coast",
        "East Coast",
        "Gulf",
        "Mexico",
        "Europe",
    )
    return [
        SourceCandidate(
            url=f"https://example.com/source-{index}",
            lane=("regulatory", "us-ports", "mexico")[index % 3],
            geographies=[geographies[index % len(geographies)]],
        )
        for index in range(10)
    ]


def _complete_brief(source_url: str) -> WeeklyBrief:
    def bullet(text: str, *, structured: bool = False) -> ReportBullet:
        fields = (
            {
                "why_it_matters": "This changes the decision context.",
                "next_step": "Monitor the cited source.",
            }
            if structured
            else {}
        )
        return ReportBullet(text=text, source_urls=[source_url], **fields)

    return WeeklyBrief(
        run_id="brief-run",
        title="Complete report",
        covered_from=datetime(2026, 8, 12, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="A complete source-bound report.",
        executive_bullets=[bullet("Executive signal.")],
        developments=[bullet("Development signal.")],
        risks=[bullet("Risk signal.", structured=True)],
        opportunities=[bullet("Opportunity signal.", structured=True)],
        uncertainties=[bullet("Uncertainty signal.", structured=True)],
        follow_up_questions=["What should be monitored next?"],
    )


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
        brief=_complete_brief(sources[0].url),
    )

    assert report.status is ValidationStatus.PASS
    assert report.citation_coverage == 1.0
    assert report.content_hash
    assert report.blocking_reasons == []


def test_validation_rejects_empty_report_sections_when_brief_is_available() -> None:
    sources = _sources()
    brief = _complete_brief(sources[0].url).model_copy(update={"risks": []})
    report = build_validation_report(
        "brief-run",
        sources,
        [
            ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
            for index in range(5)
        ],
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
        brief=brief,
    )

    check = next(check for check in report.checks if check.name == "report_sections")
    assert report.status is ValidationStatus.FAILED
    assert check.status is ValidationStatus.FAILED
    assert "risks" in str(check.observed)
    assert "empty_report_section" in report.blocking_reasons


def test_validation_rejects_uncited_and_unstructured_report_bullets() -> None:
    sources = _sources()
    brief = _complete_brief(sources[0].url).model_copy(
        update={
            "opportunities": [
                ReportBullet(
                    text="Unsupported opportunity.",
                    source_urls=["https://unknown.example/opportunity"],
                )
            ]
        }
    )
    report = build_validation_report(
        "brief-run",
        sources,
        [
            ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
            for index in range(5)
        ],
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
        brief=brief,
    )

    check = next(check for check in report.checks if check.name == "report_sections")
    assert report.status is ValidationStatus.FAILED
    assert check.status is ValidationStatus.FAILED
    assert validation_blocking_reasons(report) == report.blocking_reasons
    assert "opportunities" in str(check.observed)


def test_validation_requires_europe_geography() -> None:
    sources = [
        source.model_copy(update={"geographies": ["Mexico"]})
        for source in _sources()
    ]
    report = build_validation_report(
        "run-europe",
        sources,
        [
            ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
            for index in range(5)
        ],
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
    )

    assert report.status is ValidationStatus.FAILED
    assert (
        next(
            check for check in report.checks if check.name == "geography_coverage"
        ).status
        is ValidationStatus.FAILED
    )


def test_legacy_incomplete_distillation_cannot_remain_pass() -> None:
    sources = _sources()
    claims = [
        ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
        for index in range(5)
    ]
    report = build_validation_report(
        "legacy-incomplete",
        sources,
        claims,
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
        distillations=[
            ArticleDistillation(
                source_url=sources[0].url,
                summary="Legacy summary",
                key_points=["One point"],
            )
        ],
    )

    check = next(
        check for check in report.checks if check.name == "article_insight_completeness"
    )
    assert report.status is ValidationStatus.FAILED
    assert check.status is ValidationStatus.FAILED


def test_validation_requires_exactly_one_distillation_per_extracted_source() -> None:
    sources = [
        source.model_copy(update={"extraction_status": ExtractionStatus.SUCCEEDED})
        for source in _sources()
    ]
    claims = [
        ClaimDraft(claim=f"Claim {index}", source_urls=[sources[index].url])
        for index in range(5)
    ]
    complete_distillation = ArticleDistillation(
        source_url=sources[0].url,
        summary="Complete summary.",
        key_points=["Point one.", "Point two."],
        what_happened="The source reports a development.",
        why_it_matters="It changes the operating picture.",
        risk_assessment={
            "status": "not_observed",
            "statement": "No supported risk was observed.",
            "why_it_matters": "The source does not establish a risk.",
            "next_step": "Check an independent source.",
        },
        opportunity_assessment={
            "status": "not_observed",
            "statement": "No supported opportunity was observed.",
            "why_it_matters": "The source does not establish an opportunity.",
            "next_step": "Check an independent source.",
        },
        uncertainties=["The source has limited scope."],
        next_steps=["Review an independent source."],
        evidence_locators=["paragraph 1"],
        claims=[claims[0]],
        quality_status="complete",
    )

    report = build_validation_report(
        "duplicate-distillation",
        sources,
        claims,
        datetime(2026, 8, 19, tzinfo=UTC),
        STRICT_OPENROUTER_MODEL,
        {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"},
        [f"hash-{index}" for index in range(10)],
        distillations=[complete_distillation, complete_distillation],
    )

    check = next(
        check for check in report.checks if check.name == "source_distillation_completeness"
    )
    assert report.status is ValidationStatus.FAILED
    assert check.status is ValidationStatus.FAILED
    assert check.observed == 10


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
