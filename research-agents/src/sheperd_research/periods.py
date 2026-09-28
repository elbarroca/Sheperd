from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .contracts import PeriodBasis, PeriodStatus


@dataclass(frozen=True, slots=True)
class PeriodClassification:
    status: PeriodStatus
    basis: PeriodBasis
    eligible_for_weekly: bool


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("period timestamps must include a timezone")
    return value.astimezone(UTC)


def weekly_window(
    as_of: datetime,
    timezone_name: str,
    *,
    since: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return a UTC half-open weekly window ending at ``as_of``.

    The start is the local midnight seven calendar days before the local
    ``as_of`` date. This keeps DST changes in the configured business zone.
    """
    end = utc_datetime(as_of)
    if since is not None:
        return utc_datetime(since), end
    zone = ZoneInfo(timezone_name)
    local_as_of = end.astimezone(zone)
    start_date = local_as_of.date() - timedelta(days=7)
    start = datetime.combine(start_date, time.min, tzinfo=zone)
    return start.astimezone(UTC), end


def classify_period(
    published_at: datetime | None,
    *,
    covered_from: datetime,
    covered_until: datetime,
    as_of: datetime,
) -> PeriodClassification:
    """Classify one source without substituting retrieval time for publication."""
    start = utc_datetime(covered_from)
    end = utc_datetime(covered_until)
    observed_as_of = utc_datetime(as_of)
    if start >= end:
        raise ValueError("period start must be before period end")
    if published_at is None:
        return PeriodClassification(
            PeriodStatus.UNDATED,
            PeriodBasis.UNKNOWN,
            False,
        )
    published = utc_datetime(published_at)
    if published > observed_as_of:
        return PeriodClassification(PeriodStatus.FUTURE, PeriodBasis.PUBLISHED_AT, False)
    if start <= published < end:
        return PeriodClassification(PeriodStatus.IN_PERIOD, PeriodBasis.PUBLISHED_AT, True)
    return PeriodClassification(PeriodStatus.BACKGROUND, PeriodBasis.PUBLISHED_AT, False)


def date_window_for_month(year: int, month: int) -> tuple[date, date]:
    """Return a simple calendar-month interval for deterministic reporting."""
    first = date(year, month, 1)
    next_first = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return first, next_first
