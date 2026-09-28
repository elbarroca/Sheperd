from __future__ import annotations

from datetime import UTC, datetime

from sheperd_research.contracts import (
    ArticleDistillation,
    ArticleInsight,
    ClaimDraft,
    DecisionScore,
    DistillationQualityStatus,
    ExtractionStatus,
    InsightStatus,
    PageType,
    PeriodStatus,
    PublicationDateBasis,
    ReviewState,
    SourceCandidate,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from sheperd_research.exporters.obsidian import render_weekly_markdown
from sheperd_research.reader import build_reader_report
from sheperd_research.validators import quality_metrics


def _score(total: int) -> DecisionScore:
    relevance = min(30, total)
    impact = min(25, total - relevance)
    actionability = min(20, total - relevance - impact)
    recency = min(15, total - relevance - impact - actionability)
    authority = total - relevance - impact - actionability - recency
    return DecisionScore(
        sheperd_relevance=relevance,
        operational_impact=impact,
        actionability=actionability,
        recency=recency,
        source_authority=authority,
        total=total,
    )


def _source(index: int, *, eligible: bool = True) -> SourceCandidate:
    published_at = datetime(2026, 8, 25 - index, tzinfo=UTC)
    return SourceCandidate(
        url=f"https://example.com/article-{index}",
        title=f"Article {index}",
        publisher="Example",
        published_at=published_at,
        retrieved_at=datetime(2026, 8, 28, tzinfo=UTC),
        extraction_status=ExtractionStatus.SUCCEEDED,
        page_type=PageType.ARTICLE,
        direct_content=True,
        page_published_at=published_at,
        publication_date_basis=PublicationDateBasis.PAGE,
        publication_date_locator=f"Published: {published_at.date().isoformat()}",
        period_status=(PeriodStatus.IN_PERIOD if eligible else PeriodStatus.BACKGROUND),
        eligible_for_weekly=eligible,
        lane="us-ports",
        region="us",
    )


def _distillation(source: SourceCandidate, total: int) -> ArticleDistillation:
    claim = ClaimDraft(claim="A cited port development.", source_urls=[source.url])
    supported = ArticleInsight(
        status=InsightStatus.SUPPORTED,
        statement="Capacity may tighten.",
        why_it_matters="Operators may need to adjust bookings.",
        next_step="Check affected bookings.",
        evidence_locator="paragraph 4",
    )
    not_observed = ArticleInsight(
        status=InsightStatus.NOT_OBSERVED,
        statement="No supported opportunity was observed.",
        why_it_matters="The article did not establish an opportunity.",
        next_step="Monitor new evidence.",
    )
    return ArticleDistillation(
        source_url=source.url,
        headline=f"Decision headline {total}",
        event_type="port",
        summary="A source-bound decision summary.",
        key_points=["Point one.", "Point two.", "Point three."],
        claims=[claim],
        what_happened="A port operating condition changed.",
        why_it_matters="The change may affect SheperD operations.",
        risk_assessment=supported,
        opportunity_assessment=not_observed,
        uncertainties=["One public article."],
        next_steps=["Check affected bookings."],
        limitations=["One public article."],
        evidence_locators=["paragraph 4"],
        quality_status=DistillationQualityStatus.COMPLETE,
        prompt_version="distill-v7-reader",
        decision_score=_score(total),
    )


def _brief(sources: list[SourceCandidate]) -> WeeklyBrief:
    return WeeklyBrief(
        run_id="reader-run",
        title="Weekly reader report",
        covered_from=datetime(2026, 8, 21, tzinfo=UTC),
        covered_until=datetime(2026, 8, 28, tzinfo=UTC),
        summary="DRAFT - HUMAN REVIEW REQUIRED\n\nReader summary.",
        source_urls=[source.url for source in sources],
        review_state=ReviewState.DRAFT,
    )


def test_reader_report_ranks_current_articles_and_separates_background() -> None:
    low = _source(1)
    high = _source(2)
    background = _source(3, eligible=False)
    sources = [low, background, high]
    report = build_reader_report(
        _brief(sources),
        validation=ValidationReport(
            run_id="reader-run", status=ValidationStatus.PASS
        ),
        sources=sources,
        distillations=[
            _distillation(low, 60),
            _distillation(background, 95),
            _distillation(high, 90),
        ],
        canonical_hash="canonical-secret",
        readiness_status="review_required",
    )

    assert [article.score.total for article in report.ranked_articles] == [90, 60]
    assert [article.score.total for article in report.background_articles] == [95]
    assert report.three_things[0].startswith("Decision headline 90")
    assert report.top_action == "Check affected bookings."
    assert report.ranked_articles[0].risk == "Capacity may tighten."
    assert report.ranked_articles[0].opportunity is None
    assert len(report.source_index) == 3


def test_reader_report_demotes_misclassified_feed_urls_to_background() -> None:
    valid = _source(1)
    feed = _source(2).model_copy(
        update={"url": "https://example.com/comments/feed"}
    )
    report = build_reader_report(
        _brief([valid, feed]),
        validation=ValidationReport(
            run_id="reader-run", status=ValidationStatus.PASS
        ),
        sources=[valid, feed],
        distillations=[_distillation(valid, 70), _distillation(feed, 100)],
        canonical_hash="canonical-secret",
        readiness_status="review_required",
    )

    assert [article.source_url for article in report.ranked_articles] == [valid.url]
    assert [article.source_url for article in report.background_articles] == [feed.url]
    assert report.background_articles[0].validation_status == "incomplete"
    assert report.validation_status == "failed"

    metrics = quality_metrics(
        [valid, feed],
        [_distillation(valid, 70), _distillation(feed, 100)],
    )
    assert metrics["quality_ready"] is False
    assert metrics["complete_article_count"] == 1
    assert metrics["article_quality_issues"] == {
        feed.url: ["navigation_url"]
    }


def test_reader_markdown_is_concise_and_keeps_source_link_parity() -> None:
    sources = [_source(index) for index in range(10)]
    distillations = [
        _distillation(source, 90 - index) for index, source in enumerate(sources)
    ]
    brief = _brief(sources)
    projection = build_reader_report(
        brief,
        validation=ValidationReport(
            run_id="reader-run", status=ValidationStatus.PASS
        ),
        sources=sources,
        distillations=distillations,
        canonical_hash="canonical-secret",
        readiness_status="review_required",
    )

    markdown = render_weekly_markdown(
        brief,
        validation=ValidationReport(
            run_id="reader-run", status=ValidationStatus.PASS
        ),
        sources=sources,
        distillations=distillations,
        source_hashes={source.url: "hash-secret" for source in sources},
        canonical_hash="canonical-secret",
        reader_report=projection,
    )

    assert len(projection.ranked_articles) == 8
    assert len(projection.watchlist) == 2
    assert "## Three things to know" in markdown
    assert "## Top action" in markdown
    assert "## All new findings" in markdown
    assert "Decision headline 81" in markdown
    assert markdown.count("Source: [Example]") >= 10
    assert "Priority: 90/100" in markdown
    assert "Published: 2026-08-23" in markdown
    assert "T00:00:00" not in markdown
    assert "hash-secret" not in markdown
    visible_markdown = markdown.split("---", 2)[-1]
    assert "canonical-secret" not in visible_markdown
    assert "Agent steps" not in markdown
    assert "Locator:" not in markdown
    assert "Not observed:" not in markdown
    assert {source.url for source in sources} == {
        source.url for source in projection.source_index if source.url in markdown
    }
