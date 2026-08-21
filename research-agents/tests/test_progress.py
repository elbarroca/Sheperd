from __future__ import annotations

import re
from io import StringIO

from sheperd_research.progress import ProgressReporter


def test_progress_reporter_emits_timestamp_emoji_and_safe_details() -> None:
    stream = StringIO()
    reporter = ProgressReporter(stream=stream)

    reporter.emit(
        "route",
        "Tavily key reroute",
        key_slot=2,
        key_count=2,
        api_key="do-not-print",
    )

    line = stream.getvalue()
    assert re.match(r"^20\d\d-\d\d-\d\dT.*Z 🔁 Tavily key reroute", line)
    assert "key_slot=2" in line
    assert "key_count=2" in line
    assert "do-not-print" not in line
    assert "api_key=<redacted>" in line


def test_progress_reporter_can_be_disabled() -> None:
    stream = StringIO()
    reporter = ProgressReporter(stream=stream, enabled=False)

    reporter.emit("run", "Run started", run_id="run-1")

    assert stream.getvalue() == ""
