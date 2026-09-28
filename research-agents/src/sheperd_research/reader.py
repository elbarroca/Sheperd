from __future__ import annotations

from .contracts import (
    ArticleDistillation,
    ArticleInsight,
    InsightStatus,
    PeriodStatus,
    ReaderArticle,
    ReaderReport,
    ReaderSourceIndexEntry,
    SourceCandidate,
    ValidationReport,
    WeeklyBrief,
)
from .validators import normalize_url, reader_source_contract_issues

MAX_RANKED_ARTICLES = 8


def _sort_key(article: ReaderArticle) -> tuple[int, float, str]:
    score = article.score.total if article.score is not None else -1
    published = article.published_at.timestamp() if article.published_at else -1.0
    return (-score, -published, article.source_url)


def _supported_statement(
    insight: ArticleInsight | None,
) -> str | None:
    if insight is None or insight.status is not InsightStatus.SUPPORTED:
        return None
    return insight.statement


def build_reader_report(
    brief: WeeklyBrief,
    *,
    validation: ValidationReport | None,
    sources: list[SourceCandidate],
    distillations: list[ArticleDistillation],
    canonical_hash: str,
    readiness_status: str,
) -> ReaderReport:
    """Build the single ranked, reader-facing view used by every presentation."""
    distillations_by_url = {
        normalize_url(item.source_url): item for item in distillations
    }
    articles: list[ReaderArticle] = []
    source_index: list[ReaderSourceIndexEntry] = []
    for source in sources:
        url = normalize_url(source.url)
        distillation = distillations_by_url.get(url)
        issues = reader_source_contract_issues(
            source,
            distillation,
            as_of=brief.covered_until,
        )
        validation_status = "validated" if not issues else "incomplete"
        source_index.append(
            ReaderSourceIndexEntry(
                url=url,
                title=source.title,
                publisher=source.publisher,
                published_at=source.published_at,
                date_basis=source.publication_date_basis,
                page_type=source.page_type,
                eligible_for_weekly=source.eligible_for_weekly,
                validation_status=validation_status,
            )
        )
        if distillation is None:
            continue
        articles.append(
            ReaderArticle(
                source_url=url,
                headline=distillation.headline or source.title,
                publisher=source.publisher,
                published_at=source.published_at,
                event_at=distillation.event_at,
                date_basis=source.publication_date_basis,
                date_locator=source.publication_date_locator,
                retrieved_at=source.retrieved_at,
                page_type=source.page_type,
                score=distillation.decision_score,
                key_points=distillation.key_points[:3],
                what_changed=distillation.what_happened or distillation.summary,
                why_sheperd_cares=distillation.why_it_matters,
                recommended_action=(
                    distillation.next_steps[0]
                    if distillation.next_steps
                    else "No source-supported action recorded."
                ),
                risk=_supported_statement(distillation.risk_assessment),
                opportunity=_supported_statement(distillation.opportunity_assessment),
                limitations=distillation.limitations or distillation.uncertainties,
                lane=source.lane,
                region=source.region,
                eligible_for_weekly=source.eligible_for_weekly,
                validation_status=validation_status,
            )
        )

    current = sorted(
        (
            article
            for article in articles
            if article.eligible_for_weekly
            and article.validation_status == "validated"
            and next(
                source.period_status
                for source in sources
                if normalize_url(source.url) == article.source_url
            )
            is PeriodStatus.IN_PERIOD
        ),
        key=_sort_key,
    )
    background = sorted(
        (article for article in articles if article not in current),
        key=_sort_key,
    )
    ranked = current[:MAX_RANKED_ARTICLES]
    three_things = [
        f"{article.headline}: {article.why_sheperd_cares}" for article in ranked[:3]
    ]
    top_action = next(
        (
            article.recommended_action
            for article in ranked
            if article.recommended_action.strip()
        ),
        "No source-supported action recorded.",
    )
    validation_status = validation.status.value if validation else "blocked"
    if any(item.validation_status != "validated" for item in source_index):
        validation_status = "failed"
    return ReaderReport(
        run_id=brief.run_id,
        title=brief.title,
        covered_from=brief.covered_from,
        covered_until=brief.covered_until,
        report_status=brief.review_state.value,
        validation_status=validation_status,
        readiness_status=readiness_status,
        canonical_hash=canonical_hash,
        three_things=three_things,
        top_action=top_action,
        ranked_articles=ranked,
        watchlist=current[MAX_RANKED_ARTICLES:],
        background_articles=background,
        source_index=sorted(
            source_index,
            key=lambda item: (
                not item.eligible_for_weekly,
                -(item.published_at.timestamp() if item.published_at else -1.0),
                item.url,
            ),
        ),
    )
