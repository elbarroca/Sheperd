from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DistillationQualityStatus,
    InsightStatus,
    SourceCandidate,
    WeeklyBrief,
)
from sheperd_research.validators import (
    article_fulfillment,
    can_extract_url,
    deduplicate_sources,
    normalize_url,
    validate_article_distillation_quality,
    validate_claim_citations,
    validate_report_sections,
    validate_source_dates,
)


def test_can_extract_url_blocks_linkedin_and_paywall_markers() -> None:
    assert can_extract_url("https://example.com/article") is True
    assert can_extract_url("https://www.linkedin.com/posts/example") is False
    assert can_extract_url("https://m.linkedin.com/posts/example") is False
    assert can_extract_url("https://linkedin.com./posts/example") is False
    assert can_extract_url("https://example.com/article?subscriber=true") is False
    assert can_extract_url("https://example.com/article?subscription=true") is False
    assert can_extract_url("ftp://example.com/article") is False


def test_normalize_url_removes_tracking_values_and_fragment() -> None:
    url = "https://example.com/article?utm_source=chat&goal=abc&id=42#comments"

    assert normalize_url(url) == "https://example.com/article"


def test_normalize_url_sorts_surviving_query_pairs() -> None:
    url = "https://example.com/article?z=last&a=first&a=second"

    assert normalize_url(url) == "https://example.com/article"


def test_normalize_url_removes_credential_bearing_query_values() -> None:
    url = "https://example.com/article?api_key=KEY_SECRET&token=TOKEN_SECRET"

    assert normalize_url(url) == "https://example.com/article"


def test_deduplicate_sources_keeps_first_record() -> None:
    first = SourceCandidate(url="https://example.com/a", title="First")
    duplicate = SourceCandidate(
        url="https://example.com/a?utm_medium=social",
        title="Duplicate",
    )

    result = deduplicate_sources([first, duplicate])

    assert len(result) == 1
    assert result[0].title == "First"


def test_deduplicate_sources_collapses_query_order_variants() -> None:
    first = SourceCandidate(url="https://example.com/a?z=last&a=first", title="First")
    duplicate = SourceCandidate(url="https://example.com/a?a=first&z=last", title="Duplicate")

    result = deduplicate_sources([first, duplicate])

    assert len(result) == 1
    assert result[0].title == "First"


def test_validate_claim_citations_rejects_unknown_source() -> None:
    claim = ClaimDraft(
        claim="The port experienced congestion.",
        source_urls=["https://unknown.example/article"],
    )

    with pytest.raises(ValueError, match="unknown source"):
        validate_claim_citations(
            [claim],
            {"https://example.com/article"},
            datetime(2026, 8, 19, tzinfo=UTC),
        )


def test_validate_source_dates_rejects_future_publication() -> None:
    source = SourceCandidate(
        url="https://example.com/future",
        published_at=datetime(2026, 8, 20, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="after as_of"):
        validate_source_dates([source], datetime(2026, 8, 19, tzinfo=UTC))


def test_article_quality_rejects_missing_required_insights() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/incomplete",
        summary="Summary",
        key_points=["Only one point"],
    )

    issues = validate_article_distillation_quality(distillation)

    assert {
        "key_points_incomplete",
        "claims_incomplete",
        "missing_what_happened",
        "missing_why_it_matters",
        "uncertainties_incomplete",
        "next_steps_incomplete",
        "missing_risk_assessment",
        "missing_opportunity_assessment",
    }.issubset(issues)


def test_supported_article_insight_requires_evidence() -> None:
    with pytest.raises(ValueError, match="requires an evidence excerpt or locator"):
        ArticleInsight(
            status=InsightStatus.SUPPORTED,
            statement="A supported development occurred.",
            why_it_matters="It changes the operating picture.",
            next_step="Monitor the primary source.",
        )


def test_explicit_not_observed_insights_are_valid() -> None:
    insight = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="No supported risk was observed in this source.",
        why_it_matters="The source does not establish a risk.",
        next_step="Review an independent source.",
    )
    distillation = ArticleDistillation(
        source_url="https://example.com/complete",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source has limited scope."],
        next_steps=["Compare another source."],
        evidence_excerpts=["The source reports a development."],
        claims=[
            ClaimDraft(
                claim="The source reports a development.",
                source_urls=["https://example.com/complete"],
                evidence_excerpt="The source reports a development.",
            )
        ],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    assert validate_article_distillation_quality(distillation) == []


def test_complete_article_packet_requires_evidence_locator_or_excerpt() -> None:
    insight = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="No supported risk was observed in this source.",
        why_it_matters="The source does not establish a risk.",
        next_step="Review an independent source.",
    )
    distillation = ArticleDistillation(
        source_url="https://example.com/no-evidence",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source has limited scope."],
        next_steps=["Compare another source."],
        claims=[
            ClaimDraft(
                claim="The source reports a development.",
                source_urls=["https://example.com/no-evidence"],
            )
        ],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    assert "missing_evidence_locator" in validate_article_distillation_quality(distillation)


def test_placeholder_claim_and_evidence_entries_are_incomplete() -> None:
    insight = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="No supported risk was observed in this source.",
        why_it_matters="The source does not establish a risk.",
        next_step="Review an independent source.",
    )
    distillation = ArticleDistillation(
        source_url="https://example.com/placeholder-evidence",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source has limited scope."],
        next_steps=["Compare another source."],
        evidence_excerpts=["tbd"],
        evidence_locators=["unknown"],
        claims=[
            ClaimDraft(
                claim="unknown",
                source_urls=["https://example.com/placeholder-evidence"],
            )
        ],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    issues = validate_article_distillation_quality(distillation)

    assert "missing_claim_1" in issues
    assert "missing_evidence_locator" in issues
    assert "placeholder_evidence_excerpt" in issues
    assert "placeholder_evidence_locator" in issues


def test_article_evidence_entries_are_bounded_before_persistence() -> None:
    with pytest.raises(ValueError, match="evidence_excerpts entries"):
        ArticleDistillation(
            source_url="https://example.com/long-excerpt",
            evidence_excerpts=["word " * 41],
        )


def test_uncertain_risk_or_opportunity_is_not_an_explicit_evidence_gap() -> None:
    insight = ArticleInsight(
        status=InsightStatus.UNCERTAIN,
        statement="Risk is uncertain.",
        why_it_matters="The source is inconclusive.",
        next_step="Review an independent source.",
    )
    distillation = ArticleDistillation(
        source_url="https://example.com/uncertain",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source is inconclusive."],
        next_steps=["Compare another source."],
        evidence_locators=["paragraph 2"],
        claims=[
            ClaimDraft(
                claim="The source reports a development.",
                source_urls=["https://example.com/uncertain"],
            )
        ],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    issues = validate_article_distillation_quality(distillation)

    assert "invalid_risk_assessment_status" in issues
    assert "invalid_opportunity_assessment_status" in issues


def test_article_fulfillment_reports_persistence_and_missing_quality() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/article",
        summary="Summary",
        key_points=["Point one", "Point two"],
    )

    fulfillment = article_fulfillment(
        distillation.source_url,
        source_persisted=True,
        extracted=True,
        distillation=distillation,
    )

    assert fulfillment["status"] == "incomplete"
    assert fulfillment["source_persisted"] is True
    assert fulfillment["distillation_persisted"] is True
    assert fulfillment["ui_displayable"] is True
    assert "claims_incomplete" in fulfillment["missing_fields"]


def test_article_fulfillment_marks_extracted_only_sources() -> None:
    fulfillment = article_fulfillment(
        "https://example.com/article",
        source_persisted=True,
        extracted=True,
        distillation=None,
    )

    assert fulfillment["status"] == "extracted_only"
    assert fulfillment["missing_fields"] == ["distillation"]


def test_placeholder_article_fields_are_incomplete() -> None:
    insight = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="Not recorded in this run.",
        why_it_matters="Not available yet.",
        next_step="Review another source.",
    )
    distillation = ArticleDistillation(
        source_url="https://example.com/placeholder",
        summary="Not recorded in this run.",
        key_points=["Point one", "Point two"],
        what_happened="A development was reported.",
        why_it_matters="The operating picture may change.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source has limited scope."],
        next_steps=["Review another source."],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    issues = validate_article_distillation_quality(distillation)

    assert "missing_summary" in issues
    assert "missing_risk_assessment_statement" in issues
    assert "missing_risk_assessment_why_it_matters" in issues


def test_v6_report_sections_require_cited_context_and_next_step() -> None:
    brief = WeeklyBrief(
        run_id="run-1",
        title="Brief",
        covered_from=datetime(2026, 8, 18, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Summary",
        prompt_version="weekly-brief-v6-decision",
        executive_bullets=[],
    )

    issues = validate_report_sections(brief, {"https://example.com/source"})

    assert "executive_bullets_empty" in issues
    assert "developments_empty" in issues
    assert "risks_empty" in issues
    assert "opportunities_empty" in issues
    assert "uncertainties_empty" in issues
