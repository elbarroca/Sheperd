from __future__ import annotations

import asyncio
import json
from types import TracebackType

import httpx
import pytest

from sheperd_research.providers.capabilities import (
    _build_free_model_catalog,
    _build_report,
    resolve_capabilities,
)
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
    assert report.require_tools is True
    evidence = report.evidence_for(STRICT_OPENROUTER_MODEL)
    assert evidence is not None
    assert evidence.free is True
    assert evidence.supports_tools is True
    assert evidence.supports_structured_outputs is True
    assert {
        item["model"]: item["reason"] for item in report.skipped_models
    } == {
        "poolside/laguna-s-2.1:free": "structured_outputs_not_supported",
        "openai/gpt-4o": "not_present_in_manifest",
    }


def test_capability_report_requires_exact_model_identifier() -> None:
    report = _build_report(
        (STRICT_OPENROUTER_MODEL,),
        [
            {
                "id": "google/gemma-4-26b-a4b-it",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools", "structured_outputs"],
            }
        ],
        require_tools=True,
        source="test",
    )

    assert report.eligible_models == ()
    evidence = report.evidence_for(STRICT_OPENROUTER_MODEL)
    assert evidence is not None
    assert evidence.reason == "not_present_in_manifest"
    assert report.skipped_models == (
        {"model": STRICT_OPENROUTER_MODEL, "reason": "not_present_in_manifest"},
    )


def test_free_model_catalog_excludes_paid_and_non_explicit_free_records() -> None:
    catalog = _build_free_model_catalog(
        [
            {
                "id": "google/gemini-3.7-flash",
                "name": "Paid Gemini",
                "pricing": {"prompt": "0.000001", "completion": "0.000002"},
                "supported_parameters": ["tools", "structured_outputs"],
            },
            {
                "id": "provider/zero-priced-without-variant",
                "name": "Unversioned zero-priced model",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools", "structured_outputs"],
            },
            {
                "id": "google/gemma-4-26b-a4b-it:free",
                "name": "Gemma",
                "pricing": {"prompt": "0", "completion": "0"},
                "context_length": 262144,
                "supported_parameters": ["tools", "response_format"],
                "benchmarks": {
                    "artificial_analysis": {
                        "agentic_index": 11,
                        "intelligence_index": 26.1,
                    }
                },
            },
            {
                "id": "z-ai/glm-5.2:free",
                "name": "GLM",
                "pricing": {"prompt": "0", "completion": "0"},
                "context_length": 256000,
                "supported_parameters": ["tools", "structured_outputs"],
                "benchmarks": {
                    "artificial_analysis": {
                        "agentic_index": 45.7,
                        "intelligence_index": 52.6,
                    }
                },
            },
            {
                "id": "poolside/laguna-s-2.1:free",
                "name": "Poolside",
                "pricing": {"prompt": "0", "completion": "0"},
                "supported_parameters": ["tools"],
            },
        ],
        primary_model=STRICT_OPENROUTER_MODEL,
        source="test",
    )

    assert [item.model for item in catalog.models] == [
        STRICT_OPENROUTER_MODEL,
        "poolside/laguna-s-2.1:free",
        "provider/zero-priced-without-variant",
        "z-ai/glm-5.2:free",
    ]
    assert catalog.eligible_models == (
        "z-ai/glm-5.2:free",
        STRICT_OPENROUTER_MODEL,
    )
    assert catalog.recommended_cascade == (
        STRICT_OPENROUTER_MODEL,
        "z-ai/glm-5.2:free",
    )
    assert catalog.skipped_models == (
        {
            "model": "poolside/laguna-s-2.1:free",
            "reason": "structured_outputs_not_supported",
        },
        {
            "model": "provider/zero-priced-without-variant",
            "reason": "not_explicit_free_variant",
        },
    )
    payload = catalog.as_dict()
    assert payload["total_free_models"] == 4
    assert payload["policy"] == {
        "explicit_free_variant_required": True,
        "require_tools": True,
        "require_structured_outputs": True,
        "provider_fallbacks": False,
        "ranking_note": (
            "The cascade is a capability and benchmark heuristic; every model "
            "still requires a live agent-check before production use."
        ),
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
                        "free": True,
                        "supports_tools": True,
                        "supports_structured_outputs": True,
                        "reason": None,
                    }
                ],
                "require_tools": True,
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
