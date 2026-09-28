from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DistillationQualityStatus,
    ExtractionStatus,
    InsightStatus,
    PageType,
    PeriodBasis,
    PeriodStatus,
    PublicationDateBasis,
    ReportBullet,
    SignalEvent,
    SourceCandidate,
    WeeklyBrief,
)
from sheperd_research.validators import (
    article_fulfillment,
    can_extract_url,
    classify_page_type,
    deduplicate_sources,
    extract_publication_date,
    normalize_url,
    pack_article_content,
    quality_metrics,
    reader_source_contract_issues,
    reconcile_publication_dates,
    score_article,
    validate_article_distillation_quality,
    validate_claim_citations,
    validate_report_sections,
    validate_signal_event_quality,
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


def test_validate_source_dates_rejects_impossible_historical_year() -> None:
    source = SourceCandidate(
        url="https://example.com/impossible",
        published_at=datetime(202, 1, 1, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="implausible"):
        validate_source_dates([source], datetime(2026, 8, 19, tzinfo=UTC))


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("Published: 2026-08-26", datetime(2026, 8, 26, tzinfo=UTC)),
        (
            "Publication date: Wed, 26 Aug 2026 18:30:00 GMT",
            datetime(2026, 8, 26, 18, 30, tzinfo=UTC),
        ),
        (
            "Updated 2026-08-26T19:30:00+01:00",
            datetime(2026, 8, 26, 18, 30, tzinfo=UTC),
        ),
    ],
)
def test_extract_publication_date_returns_utc_value_and_locator(
    line: str,
    expected: datetime,
) -> None:
    observed, locator = extract_publication_date(f"# Port update\n{line}\nBody")

    assert observed == expected
    assert locator == line


def test_reconcile_publication_dates_fails_closed_on_conflict() -> None:
    source = SourceCandidate(
        url="https://example.com/article",
        published_at=datetime(2026, 8, 25, tzinfo=UTC),
        search_published_at=datetime(2026, 8, 25, tzinfo=UTC),
    )

    matched = reconcile_publication_dates(
        source,
        datetime(2026, 8, 25, 12, tzinfo=UTC),
        "Published: 2026-08-25",
    )
    conflict = reconcile_publication_dates(
        source,
        datetime(2026, 8, 24, tzinfo=UTC),
        "Published: 2026-08-24",
    )

    assert matched.publication_date_basis is PublicationDateBasis.MATCHED
    assert matched.published_at == datetime(2026, 8, 25, 12, tzinfo=UTC)
    assert conflict.publication_date_basis is PublicationDateBasis.CONFLICT
    assert conflict.published_at is None


def test_pack_article_content_spans_opening_date_evidence_and_closing() -> None:
    body = "\n".join(
        [
            "OPENING_SENTINEL",
            *(f"ordinary filler line {index} " + "x" * 80 for index in range(160)),
            "Published: 2026-08-25",
            *(f"more filler line {index} " + "y" * 80 for index in range(160)),
            "CLOSING_SENTINEL",
        ]
    )

    packed = pack_article_content(body, max_chars=8_000)

    assert len(packed) <= 8_000
    assert "OPENING_SENTINEL" in packed
    assert "Published: 2026-08-25" in packed
    assert "CLOSING_SENTINEL" in packed


@pytest.mark.parametrize(
    ("url", "title", "expected"),
    [
        ("https://example.com/news", "News archive", PageType.ARCHIVE),
        ("https://example.com/category/ports", "Ports", PageType.CATEGORY),
        ("https://example.com/search", "Search results", PageType.INDEX),
        ("https://example.com/comments/feed", "Comments feed", PageType.INDEX),
        (
            "https://example.com/news/2026/08/direct-port-update",
            "Direct port update",
            PageType.ARTICLE,
        ),
        ("https://example.com/notices/order-17.pdf", "Order 17", PageType.OFFICIAL_DOCUMENT),
    ],
)
def test_classify_page_type_separates_navigation_from_direct_content(
    url: str,
    title: str,
    expected: PageType,
) -> None:
    source = SourceCandidate(url=url, title=title)

    assert classify_page_type(source, "# Heading\nPublished: 2026-08-25\nArticle body") is expected


def test_reader_contract_rejects_a_historically_misclassified_feed_url() -> None:
    source = SourceCandidate(
        url="https://example.com/comments/feed",
        page_type=PageType.ARTICLE,
        direct_content=True,
        extraction_status=ExtractionStatus.SUCCEEDED,
    )

    issues = reader_source_contract_issues(source, None)

    assert "navigation_url" in issues


def test_classify_page_type_accepts_single_slug_articles_with_a_byline() -> None:
    source = SourceCandidate(
        url=(
            "https://gcaptain.com/"
            "container-dwell-times-return-to-pre-pandemic-levels-at-major-ports"
        ),
        title="Container Dwell Times Return to Pre-Pandemic Levels",
    )
    content = "# Container Dwell Times\nBy Staff Writer\n" + ("Article body. " * 150)

    assert classify_page_type(source, content) is PageType.ARTICLE


def test_classify_page_type_accepts_a_substantive_dated_statistics_report() -> None:
    source = SourceCandidate(
        url="https://the-dwell.com/stats",
        title="US port congestion & dwell time (August 2026)",
    )
    content = (
        "# US port congestion & dwell time (August 2026)\n"
        "Key numbers with citations and methodology.\n"
        "Data through Aug 18, 2026\n"
        + ("Evidence and operating context. " * 60)
        + "\nData through Aug 25, 2026\n"
    )

    assert classify_page_type(source, content) is PageType.ARTICLE


def test_score_article_uses_the_published_formula() -> None:
    source = SourceCandidate(
        url="https://example.com/article",
        published_at=datetime(2026, 8, 25, tzinfo=UTC),
        page_type=PageType.ARTICLE,
        direct_content=True,
        lane="us-ports",
        region="us",
        authority_tier="primary",
    )
    insight = ArticleInsight(
        status=InsightStatus.SUPPORTED,
        statement="The change has a supported operational effect.",
        why_it_matters="It changes the operating picture.",
        next_step="Act on the supported change.",
        evidence_locator="paragraph 3",
    )
    distillation = ArticleDistillation(
        source_url=source.url,
        headline="Port announces operating change",
        event_type="port",
        summary="The port announced an operating change.",
        key_points=["One.", "Two.", "Three."],
        what_happened="The port changed its operating schedule.",
        why_it_matters="The change affects cargo planning.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["Duration is not yet known."],
        next_steps=["Update the operating plan."],
        claims=[ClaimDraft(claim="The schedule changed.", source_urls=[source.url])],
        limitations=["One source."],
    )

    score = score_article(source, distillation, datetime(2026, 8, 28, tzinfo=UTC))

    assert score.model_dump(exclude={"rationale"}) == {
        "sheperd_relevance": 30,
        "operational_impact": 25,
        "actionability": 20,
        "recency": 15,
        "source_authority": 10,
        "total": 100,
        "priority": "high",
    }


def test_article_quality_rejects_missing_required_insights() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/incomplete",
        summary="Summary",
        key_points=["Only one point"],
    )

    issues = validate_article_distillation_quality(distillation)

    assert {
        "missing_headline",
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
        headline="A source-bound development",
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


def test_signal_event_quality_rejects_legacy_packet_and_accepts_complete_packet() -> None:
    legacy = SignalEvent(
        event_id="legacy-event",
        run_id="run-1",
        event_type="source-linked-claim",
        summary="Legacy summary",
        source_urls=["https://example.com/source"],
    )
    assert "invalid_event_type" in validate_signal_event_quality(legacy)
    assert "missing_headline" in validate_signal_event_quality(legacy)

    complete = SignalEvent(
        event_id="event-1",
        run_id="run-1",
        event_type="port",
        summary="Terminal dwell changed.",
        headline="Terminal dwell changed",
        what_changed="The terminal published a new dwell-time measure.",
        published_at=datetime(2026, 8, 25, tzinfo=UTC),
        retrieved_at=datetime(2026, 8, 26, tzinfo=UTC),
        period_status=PeriodStatus.IN_PERIOD,
        period_basis=PeriodBasis.PUBLISHED_AT,
        eligible_for_weekly=True,
        region="us",
        lane="us-ports",
        source_urls=["https://example.com/source"],
        evidence_locator="paragraph 2",
        impact="The update changes the operating picture.",
        risk="Not observed: the source does not establish a material risk.",
        opportunity="Not observed: the source does not establish an opportunity.",
        next_step="Monitor the next terminal update.",
        limitations=["One public source."],
    )
    assert validate_signal_event_quality(complete) == []


def test_article_event_date_requires_an_evidence_locator() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/event-date",
        summary="Summary",
        event_at=datetime(2026, 8, 24, tzinfo=UTC),
    )

    assert "event_at_missing_locator" in validate_article_distillation_quality(
        distillation
    )


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
        statement="unknown",
        why_it_matters="tbd",
        next_step="unsupported",
        evidence_excerpt="unknown",
        evidence_locator="tbd",
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
    assert "missing_risk_assessment_statement" in issues
    assert "missing_risk_assessment_why_it_matters" in issues
    assert "missing_risk_assessment_next_step" in issues
    assert "risk_assessment_placeholder_evidence_excerpt" in issues
    assert "risk_assessment_placeholder_evidence_locator" in issues


def test_legacy_article_evidence_entries_load_but_are_incomplete() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/long-excerpt",
        summary="Legacy summary.",
        evidence_excerpts=["word " * 41],
    )

    assert "evidence_excerpt_too_long" in validate_article_distillation_quality(
        distillation
    )


def test_quality_metrics_fail_failed_extraction_and_orphaned_distillation() -> None:
    complete = ArticleDistillation(
        source_url="https://example.com/orphan",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=ArticleInsight(
            status=InsightStatus.NOT_OBSERVED,
            statement="No supported risk was observed in this source.",
            why_it_matters="The source does not establish a risk.",
            next_step="Review an independent source.",
        ),
        opportunity_assessment=ArticleInsight(
            status=InsightStatus.NOT_OBSERVED,
            statement="No supported opportunity was observed in this source.",
            why_it_matters="The source does not establish an opportunity.",
            next_step="Review an independent source.",
        ),
        uncertainties=["The source has limited scope."],
        next_steps=["Compare another source."],
        evidence_excerpts=["The source reports a development."],
        claims=[
            ClaimDraft(
                claim="The source reports a development.",
                source_urls=["https://example.com/orphan"],
            )
        ],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    metrics = quality_metrics(
        [
            SourceCandidate(
                url="https://example.com/failed",
                extraction_status=ExtractionStatus.FAILED,
            )
        ],
        [complete],
    )

    assert metrics["quality_ready"] is False
    assert metrics["article_count"] == 1
    article_issues = metrics["article_quality_issues"]
    assert isinstance(article_issues, dict)
    assert article_issues["https://example.com/failed"] == ["extraction_failed"]
    assert "https://example.com/orphan" not in article_issues
    fulfillment = metrics["article_fulfillment"]
    assert isinstance(fulfillment, list)
    assert any(
        isinstance(item, dict) and item.get("status") == "orphaned"
        for item in fulfillment
    )


def test_quality_metrics_scopes_readiness_to_unique_non_seed_persisted_sources() -> None:
    insight = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="No supported risk was observed in this source.",
        why_it_matters="The source does not establish a risk.",
        next_step="Review an independent source.",
    )
    claim = ClaimDraft(
        claim="The source reports a development.",
        source_urls=["https://example.com/non-seed"],
    )
    complete = ArticleDistillation(
        source_url="https://example.com/non-seed",
        headline="A source-bound development",
        summary="Summary",
        key_points=["Point one", "Point two"],
        what_happened="The source reports a development.",
        why_it_matters="The development may matter operationally.",
        risk_assessment=insight,
        opportunity_assessment=insight,
        uncertainties=["The source has limited scope."],
        next_steps=["Compare another source."],
        evidence_excerpts=["The source reports a development."],
        claims=[claim],
        quality_status=DistillationQualityStatus.COMPLETE,
    )
    seed_distillation = complete.model_copy(
        update={"source_url": "https://example.com/seed"}
    )
    orphan_distillation = complete.model_copy(
        update={"source_url": "https://example.com/orphan"}
    )

    metrics = quality_metrics(
        [
            SourceCandidate(
                url="https://example.com/non-seed",
                extraction_status=ExtractionStatus.SUCCEEDED,
            ),
            SourceCandidate(
                url="https://example.com/non-seed?utm_source=duplicate",
                extraction_status=ExtractionStatus.SUCCEEDED,
            ),
            SourceCandidate(
                url="https://example.com/seed",
                is_seed=True,
                extraction_status=ExtractionStatus.SUCCEEDED,
            ),
        ],
        [complete, seed_distillation, orphan_distillation],
    )

    assert metrics["quality_ready"] is True
    assert metrics["article_count"] == 1
    assert metrics["complete_article_count"] == 1
    assert metrics["article_insight_completeness"] == 1.0
    assert metrics["source_distillation_coverage"] == 1.0
    assert metrics["article_quality_issues"] == {}


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

    assert "invalid_risk_assessment_status" not in issues
    assert "invalid_opportunity_assessment_status" not in issues
    assert "risk_assessment_missing_evidence" not in issues
    assert "opportunity_assessment_missing_evidence" not in issues


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


def test_article_fulfillment_marks_duplicate_distillations_incomplete() -> None:
    distillation = ArticleDistillation(
        source_url="https://example.com/article",
        summary="Summary",
        key_points=["Point one", "Point two"],
        claims=[ClaimDraft(claim="A claim.", source_urls=["https://example.com/article"])],
        what_happened="The source reports a development.",
        why_it_matters="It changes the operating picture.",
        risk_assessment=ArticleInsight(
            status=InsightStatus.NOT_OBSERVED,
            statement="No supported risk was observed.",
            why_it_matters="The source does not establish a risk.",
            next_step="Check another source.",
        ),
        opportunity_assessment=ArticleInsight(
            status=InsightStatus.NOT_OBSERVED,
            statement="No supported opportunity was observed.",
            why_it_matters="The source does not establish an opportunity.",
            next_step="Check another source.",
        ),
        uncertainties=["The source has limited scope."],
        next_steps=["Check another source."],
        evidence_locators=["paragraph 2"],
        quality_status=DistillationQualityStatus.COMPLETE,
    )

    fulfillment = article_fulfillment(
        distillation.source_url,
        source_persisted=True,
        extracted=True,
        distillation=distillation,
        distillation_count=2,
    )

    assert fulfillment["status"] == "incomplete"
    assert fulfillment["complete"] is False
    assert "duplicate_distillation" in fulfillment["missing_fields"]
    assert "duplicate_distillation" in fulfillment["quality_issues"]


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


@pytest.mark.parametrize("bullet_text", ["   ", "unknown"])
def test_report_sections_reject_placeholder_bullet_text(bullet_text: str) -> None:
    source_url = "https://example.com/source"
    valid_bullet = ReportBullet(
        text="A cited development.",
        source_urls=[source_url],
        why_it_matters="The source changes the operating picture.",
        next_step="Review an independent source.",
    )
    brief = WeeklyBrief(
        run_id="run-1",
        title="Brief",
        covered_from=datetime(2026, 8, 18, tzinfo=UTC),
        covered_until=datetime(2026, 8, 19, tzinfo=UTC),
        summary="Summary",
        executive_bullets=[valid_bullet],
        developments=[valid_bullet.model_copy(update={"text": bullet_text})],
        risks=[valid_bullet],
        opportunities=[valid_bullet],
        uncertainties=[valid_bullet],
        follow_up_questions=["What independent evidence follows?"],
    )

    issues = validate_report_sections(brief, {source_url})

    assert "developments_1_missing_text" in issues
