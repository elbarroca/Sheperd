from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sheperd_research.contracts import ClaimDraft, SourceCandidate
from sheperd_research.validators import (
    can_extract_url,
    deduplicate_sources,
    normalize_url,
    validate_claim_citations,
    validate_source_dates,
)


def test_can_extract_url_blocks_linkedin_and_paywall_markers() -> None:
    assert can_extract_url("https://example.com/article") is True
    assert can_extract_url("https://www.linkedin.com/posts/example") is False
    assert can_extract_url("https://m.linkedin.com/posts/example") is False
    assert can_extract_url("https://example.com/article?subscriber=true") is False


def test_normalize_url_removes_tracking_values_and_fragment() -> None:
    url = "https://example.com/article?utm_source=chat&goal=abc&id=42#comments"

    assert normalize_url(url) == "https://example.com/article?id=42"


def test_deduplicate_sources_keeps_first_record() -> None:
    first = SourceCandidate(url="https://example.com/a", title="First")
    duplicate = SourceCandidate(
        url="https://example.com/a?utm_medium=social",
        title="Duplicate",
    )

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
