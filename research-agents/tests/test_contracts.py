from __future__ import annotations

from datetime import UTC, datetime

from sheperd_research.contracts import (
    EvidenceStatus,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    SourceCandidate,
)


def test_research_request_defaults_to_draft_only() -> None:
    request = ResearchRunRequest(topic_set="dnd-port")

    assert request.review_state is ReviewState.DRAFT
    assert request.allow_external_actions is False
    assert request.as_of.tzinfo is not None


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


def test_report_bullet_keeps_new_context_fields_optional_for_legacy_records() -> None:
    bullet = ReportBullet.model_validate(
        {
            "text": "A legacy report signal.",
            "source_urls": ["https://example.com/article"],
        }
    )

    assert bullet.why_it_matters is None
    assert bullet.next_step is None
