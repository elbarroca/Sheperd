from __future__ import annotations

import json

from sheperd_research.cli import (
    _redact_checkpoint,
    _redact_checkpoint_metadata,
    _redact_checkpoint_writes,
)


def test_checkpoint_redaction_drops_metadata_and_arbitrary_transient_writes() -> None:
    checkpoint = {
        "v": 1,
        "id": "checkpoint-1",
        "ts": "2026-08-20T00:00:00+00:00",
        "channel_values": {
            "run_id": "run-1",
            "content": "RAW_BODY_SECRET",
            "messages": ["PROMPT_SECRET"],
            "prompt": "PROMPT_SECRET",
            "api_key": "KEY_SECRET",
            "arbitrary": {"content": "ARBITRARY_SECRET"},
        },
        "channel_versions": {},
        "versions_seen": {},
        "updated_channels": [],
    }
    metadata = {
        "prompt": "PROMPT_SECRET",
        "raw_body": "RAW_BODY_SECRET",
        "api_key": "KEY_SECRET",
        "arbitrary": "ARBITRARY_SECRET",
        "requested_model": "google/gemma-4-26b-a4b-it:free",
    }
    writes = [
        ("content", "RAW_BODY_SECRET"),
        ("messages", ["PROMPT_SECRET"]),
        ("prompt", "PROMPT_SECRET"),
        ("api_key", "KEY_SECRET"),
        ("arbitrary", {"content": "ARBITRARY_SECRET"}),
    ]

    redacted = _redact_checkpoint(checkpoint)
    redacted_metadata = _redact_checkpoint_metadata(metadata)
    redacted_writes = _redact_checkpoint_writes(writes)
    serialized = json.dumps(
        [redacted, redacted_metadata, redacted_writes],
        sort_keys=True,
        default=str,
    )

    for secret in ("PROMPT_SECRET", "RAW_BODY_SECRET", "KEY_SECRET", "ARBITRARY_SECRET"):
        assert secret not in serialized
    assert redacted["channel_values"] == {"run_id": "run-1"}
    assert redacted_metadata == {
        "requested_model": "google/gemma-4-26b-a4b-it:free"
    }
    assert redacted_writes == [("content", {}), ("messages", [])]
