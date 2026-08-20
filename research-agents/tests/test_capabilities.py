from __future__ import annotations

import asyncio
import json
from types import TracebackType

import httpx
import pytest

from sheperd_research.providers.capabilities import _build_report, resolve_capabilities
from sheperd_research.providers.errors import ProviderError
from sheperd_research.settings import STRICT_OPENROUTER_MODEL


class BrokenAsyncClient:
    async def __aenter__(self) -> BrokenAsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def get(self, *_: object, **__: object) -> httpx.Response:
        raise httpx.ReadTimeout("timeout")


def test_capability_report_keeps_only_free_tool_and_structured_models() -> None:
    report = _build_report(
        (
            "google/gemma-4-26b-a4b-it:free",
            "poolside/laguna-s-2.1:free",
            "openai/gpt-4o",
        ),
        [
            {
                "id": "google/gemma-4-26b-a4b-it:free",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools", "structured_outputs"],
            },
            {
                "id": "poolside/laguna-s-2.1:free",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools"],
            },
        ],
        require_tools=True,
        source="test",
    )

    assert report.eligible_models == ("google/gemma-4-26b-a4b-it:free",)
    assert {
        item["model"]: item["reason"] for item in report.skipped_models
    } == {
        "poolside/laguna-s-2.1:free": "structured_outputs_not_supported",
        "openai/gpt-4o": "not_present_in_manifest",
    }


def test_live_capability_requirement_does_not_authorize_from_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pytest.TempPathFactory,
) -> None:
    cache_path = tmp_path / "openrouter-capabilities.json"
    cache_path.write_text(
        json.dumps(
            {
                "version": 1,
                "checked_at": "2026-08-20T00:00:00+00:00",
                "models": [
                    {
                        "model": STRICT_OPENROUTER_MODEL,
                        "eligible": True,
                        "reason": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_: BrokenAsyncClient())

    with pytest.raises(ProviderError, match="live capability manifest unavailable"):
        asyncio.run(
            resolve_capabilities(
                "secret",
                (STRICT_OPENROUTER_MODEL,),
                cache_path,
                require_tools=True,
                allow_cached=False,
            )
        )
