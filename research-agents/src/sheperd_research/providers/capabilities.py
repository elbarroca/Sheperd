from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .errors import ProviderError

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


@dataclass(frozen=True)
class ModelCapability:
    model: str
    free: bool
    supports_tools: bool
    supports_structured_outputs: bool
    reason: str | None = None


@dataclass(frozen=True)
class CapabilityReport:
    requested_models: tuple[str, ...]
    eligible_models: tuple[str, ...]
    capabilities: tuple[ModelCapability, ...]
    skipped_models: tuple[dict[str, str], ...]
    require_tools: bool
    manifest_hash: str
    source: str
    checked_at: datetime

    def evidence_for(self, model: str) -> ModelCapability | None:
        return next((item for item in self.capabilities if item.model == model), None)

    def as_dict(self) -> dict[str, object]:
        return {
            "requested_models": list(self.requested_models),
            "eligible_models": list(self.eligible_models),
            "capabilities": [
                {
                    "model": item.model,
                    "free": item.free,
                    "supports_tools": item.supports_tools,
                    "supports_structured_outputs": item.supports_structured_outputs,
                    "reason": item.reason,
                }
                for item in self.capabilities
            ],
            "skipped_models": [dict(item) for item in self.skipped_models],
            "require_tools": self.require_tools,
            "manifest_hash": self.manifest_hash,
            "source": self.source,
            "checked_at": self.checked_at.isoformat(),
        }


def _free_pricing(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return all(
        str(value.get(key, "")) in {"0", "0.0", "0.000000"}
        for key in ("prompt", "completion")
    )


def _capability_from_record(record: object, model: str) -> ModelCapability | None:
    if not isinstance(record, dict):
        return None
    record_id = record.get("id")
    if not isinstance(record_id, str):
        return None
    if record_id != model:
        return None
    supported = record.get("supported_parameters")
    supported_parameters = (
        {item for item in supported if isinstance(item, str)}
        if isinstance(supported, list)
        else set()
    )
    pricing = record.get("pricing")
    free = _free_pricing(pricing)
    return ModelCapability(
        model=model,
        free=free,
        supports_tools="tools" in supported_parameters,
        supports_structured_outputs=(
            "structured_outputs" in supported_parameters
            or "response_format" in supported_parameters
        ),
    )


def _manifest_hash(capabilities: list[ModelCapability]) -> str:
    payload = [
        {
            "model": item.model,
            "free": item.free,
            "supports_tools": item.supports_tools,
            "supports_structured_outputs": item.supports_structured_outputs,
            "reason": item.reason,
        }
        for item in capabilities
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _build_report(
    requested_models: tuple[str, ...],
    records: Sequence[object],
    *,
    require_tools: bool,
    source: str,
) -> CapabilityReport:
    capabilities: list[ModelCapability] = []
    eligible: list[str] = []
    skipped: list[dict[str, str]] = []
    for model in requested_models:
        capability = next(
            (
                item
                for record in records
                if (item := _capability_from_record(record, model)) is not None
            ),
            None,
        )
        if capability is None:
            skipped.append({"model": model, "reason": "not_present_in_manifest"})
            capabilities.append(
                ModelCapability(model, False, False, False, "not_present_in_manifest")
            )
            continue
        reason = None
        if not capability.free:
            reason = "not_free"
        elif require_tools and not capability.supports_tools:
            reason = "tool_calling_not_supported"
        elif not capability.supports_structured_outputs:
            reason = "structured_outputs_not_supported"
        if reason:
            skipped.append({"model": model, "reason": reason})
            capabilities.append(
                ModelCapability(
                    model,
                    capability.free,
                    capability.supports_tools,
                    capability.supports_structured_outputs,
                    reason,
                )
            )
            continue
        capabilities.append(capability)
        eligible.append(model)
    return CapabilityReport(
        requested_models=requested_models,
        eligible_models=tuple(eligible),
        capabilities=tuple(capabilities),
        skipped_models=tuple(skipped),
        require_tools=require_tools,
        manifest_hash=_manifest_hash(capabilities),
        source=source,
        checked_at=datetime.now(UTC),
    )


def _cache_payload(report: CapabilityReport) -> dict[str, object]:
    return {
        "version": 1,
        "checked_at": report.checked_at.isoformat(),
        "require_tools": report.require_tools,
        "models": [
            {
                "model": model,
                "eligible": model in report.eligible_models,
                "free": next(
                    (
                        item.free
                        for item in report.capabilities
                        if item.model == model
                    ),
                    False,
                ),
                "supports_tools": next(
                    (
                        item.supports_tools
                        for item in report.capabilities
                        if item.model == model
                    ),
                    False,
                ),
                "supports_structured_outputs": next(
                    (
                        item.supports_structured_outputs
                        for item in report.capabilities
                        if item.model == model
                    ),
                    False,
                ),
                "reason": next(
                    (item["reason"] for item in report.skipped_models if item["model"] == model),
                    None,
                ),
            }
            for model in report.requested_models
        ],
    }


def _write_cache(path: Path, report: CapabilityReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_cache_payload(report), indent=2) + "\n", encoding="utf-8")


def _load_cache(
    path: Path,
    requested_models: tuple[str, ...],
    *,
    require_tools: bool,
) -> CapabilityReport | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    cached_models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(cached_models, list):
        return None
    records: list[dict[str, object]] = []
    for item in cached_models:
        if not isinstance(item, dict) or not isinstance(item.get("model"), str):
            continue
        records.append(
            {
                "id": item["model"],
                "pricing": (
                    {"prompt": "0", "completion": "0"}
                    if item.get("free") is True
                    else {"prompt": "1", "completion": "1"}
                ),
                "supported_parameters": (
                    [
                        *(
                            ["tools"]
                            if item.get("supports_tools") is True
                            else []
                        ),
                        *(
                            ["structured_outputs"]
                            if item.get("supports_structured_outputs") is True
                            else []
                        ),
                    ]
                ),
            }
        )
    if not records:
        return None
    report = _build_report(
        requested_models,
        records,
        require_tools=require_tools,
        source="cache",
    )
    if report.require_tools != bool(payload.get("require_tools")):
        return None
    return report


async def resolve_capabilities(
    api_key: str,
    requested_models: tuple[str, ...],
    cache_path: Path,
    *,
    require_tools: bool,
    allow_cached: bool = True,
    timeout_seconds: float = 15,
) -> CapabilityReport:
    if not api_key.strip():
        raise ProviderError("OpenRouter capability check requires an API key")
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(OPENROUTER_MODELS_URL, headers=headers)
            response.raise_for_status()
            payload: Any = response.json()
        records = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise ValueError("models manifest is malformed")
        report = _build_report(
            requested_models,
            records,
            require_tools=require_tools,
            source="live",
        )
        _write_cache(cache_path, report)
        return report
    except (httpx.HTTPError, ValueError, OSError):
        if not allow_cached:
            raise ProviderError("OpenRouter live capability manifest unavailable") from None
        cached = _load_cache(
            cache_path,
            requested_models,
            require_tools=require_tools,
        )
        if cached is not None:
            return cached
        raise ProviderError("OpenRouter capability manifest unavailable") from None
