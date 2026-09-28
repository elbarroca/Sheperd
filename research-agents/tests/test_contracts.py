from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sheperd_research.contracts import (
    DecisionScore,
    EvidenceStatus,
    PageType,
    PublicationDateBasis,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    RunKind,
    SourceCandidate,
)


def test_research_request_defaults_to_draft_only() -> None:
    request = ResearchRunRequest(topic_set="dnd-port")

    assert request.review_state is ReviewState.DRAFT
    assert request.allow_external_actions is False
    assert request.as_of.tzinfo is not None
    assert request.run_kind is RunKind.RESEARCH
    assert request.parent_run_id is None
    assert request.repair_round is None
    assert request.context_version == "legacy-unknown"
    assert request.research_timezone == "Europe/Lisbon"


def test_repair_request_requires_parent_lineage_and_bounded_round() -> None:
    request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="repair",
        run_kind=RunKind.REPAIR,
        parent_run_id="parent-run",
        repair_round=1,
    )

    assert request.run_kind is RunKind.REPAIR
    assert request.parent_run_id == "parent-run"
    assert request.repair_round == 1

    with pytest.raises(ValueError, match="repair runs require parent_run_id"):
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind=RunKind.REPAIR,
            repair_round=1,
        )

    with pytest.raises(ValueError, match="research runs cannot declare repair lineage"):
        ResearchRunRequest(topic_set="dnd-port", parent_run_id="parent-run")


def test_source_candidate_preserves_seed_provenance() -> None:
    published_at = datetime(2026, 8, 19, 10, 0, tzinfo=UTC)
    source = SourceCandidate(
        url="https://example.com/article",
        title="Port update",
        publisher="Example",
        published_at=published_at,
        source_kind="trade-media",
        topics=["port-congestion"],
        geographies=["West Coast"],
        is_seed=True,
        evidence_status=EvidenceStatus.UNVERIFIED,
    )

    assert source.is_seed is True
    assert source.evidence_status is EvidenceStatus.UNVERIFIED


def test_source_candidate_keeps_run_scoped_article_and_date_provenance() -> None:
    published_at = datetime(2026, 8, 25, tzinfo=UTC)
    source = SourceCandidate(
        url="https://example.com/news/direct-article",
        published_at=published_at,
        search_published_at=published_at,
        page_published_at=published_at,
        publication_date_basis=PublicationDateBasis.MATCHED,
        publication_date_locator="Published: 2026-08-25",
        page_type=PageType.ARTICLE,
        direct_content=True,
        parent_navigation_url="https://example.com/news",
    )

    payload = source.model_dump(mode="json")

    assert payload["page_type"] == "article"
    assert payload["publication_date_basis"] == "matched"
    assert payload["parent_navigation_url"] == "https://example.com/news"


def test_decision_score_rejects_a_total_that_does_not_match_components() -> None:
    with pytest.raises(ValueError, match="sum of its components"):
        DecisionScore(
            sheperd_relevance=30,
            operational_impact=25,
            actionability=20,
            recency=15,
            source_authority=10,
            total=99,
            rationale={"sheperd_relevance": "Directly relevant."},
        )


def test_report_bullet_keeps_new_context_fields_optional_for_legacy_records() -> None:
    bullet = ReportBullet.model_validate(
        {
            "text": "A legacy report signal.",
            "source_urls": ["https://example.com/article"],
        }
    )

    assert bullet.why_it_matters is None
    assert bullet.next_step is None
