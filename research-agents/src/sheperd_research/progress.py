from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, TextIO


class ProgressSink(Protocol):
    def emit(self, event: str, message: str, **details: object) -> None: ...


EVENT_EMOJI = {
    "run": "🚦",
    "agent": "🤖",
    "discovery": "🔎",
    "query": "🌐",
    "route": "🔁",
    "extract": "📥",
    "persist": "💾",
    "distill": "📝",
    "critic": "⚖️",
    "synthesis": "🧩",
    "validate": "✅",
    "checkpoint": "⏱️",
    "output": "📄",
    "finish": "🏁",
    "error": "⛔",
}

_SECRET_DETAIL_KEYS = frozenset(
    {
        "api-key",
        "api_key",
        "apikey",
        "article_body",
        "authorization",
        "database_url",
        "direct_database_url",
        "password",
        "prompt",
        "raw_body",
        "reasoning",
        "secret",
        "token",
    }
)
_SECRET_VALUE_MARKERS = (
    "api_key",
    "apikey",
    "authorization:",
    "bearer ",
    "password",
    "private key",
    "prompt:",
    "raw body",
    "reasoning:",
    "secret",
    "token=",
)


def _safe_value(key: str, value: object) -> str:
    if key.lower() in _SECRET_DETAIL_KEYS:
        return "<redacted>"
    if value is None:
        return "none"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        compact = " ".join(value.split())
        if any(marker in compact.casefold() for marker in _SECRET_VALUE_MARKERS):
            return "<redacted>"
        return compact[:160] + ("..." if len(compact) > 160 else "")
    if isinstance(value, Mapping):
        return "<mapping>"
    if isinstance(value, (list, tuple, set, frozenset)):
        return "[" + ",".join(_safe_value(key, item) for item in list(value)[:8]) + "]"
    return f"<{type(value).__name__}>"


def format_progress_line(
    event: str,
    message: str,
    details: Mapping[str, object],
    *,
    timestamp: datetime | None = None,
) -> str:
    observed_at = (timestamp or datetime.now(UTC)).astimezone(UTC)
    timestamp_text = observed_at.isoformat(timespec="seconds").replace("+00:00", "Z")
    emoji = EVENT_EMOJI.get(event, "•")
    detail_text = " ".join(
        f"{key}={_safe_value(key, value)}" for key, value in details.items()
    )
    suffix = f" {detail_text}" if detail_text else ""
    return f"{timestamp_text} {emoji} {message}{suffix}"


@dataclass(slots=True)
class ProgressReporter:
    """Write a redacted operator stream without mixing it into JSON stdout."""

    stream: TextIO = field(default_factory=lambda: sys.stderr)
    enabled: bool = True

    def emit(self, event: str, message: str, **details: object) -> None:
        if not self.enabled:
            return
        print(format_progress_line(event, message, details), file=self.stream, flush=True)
