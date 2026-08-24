from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from ..settings import is_free_openrouter_model, is_openai_model
from .errors import ProviderError

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


@dataclass(frozen=True)
class ModelCapability:
    model: str
    free: bool
    supports_tools: bool
    supports_structured_outputs: bool
    reason: str | None = None
    name: str | None = None
    context_length: int | None = None
    agentic_index: float | None = None
    intelligence_index: float | None = None
    coding_index: float | None = None


@dataclass(frozen=True)
class FreeModelCatalog:
    models: tuple[ModelCapability, ...]
    eligible_models: tuple[str, ...]
    recommended_cascade: tuple[str, ...]
    skipped_models: tuple[dict[str, str], ...]
    manifest_hash: str
    source: str
    checked_at: datetime

    def as_dict(self) -> dict[str, object]:
        eligible_ranks = {
            model: index + 1
            for index, model in enumerate(self.recommended_cascade)
        }
        return {
            "total_free_models": len(self.models),
            "eligible_agentic_models": len(self.eligible_models),
            "eligible_models": list(self.eligible_models),
            "recommended_cascade": list(self.recommended_cascade),
            "models": [
                {
                    "model": item.model,
                    "name": item.name,
                    "free": item.free,
                    "supports_tools": item.supports_tools,
                    "supports_structured_outputs": item.supports_structured_outputs,
                    "context_length": item.context_length,
                    "agentic_index": item.agentic_index,
                    "intelligence_index": item.intelligence_index,
                    "coding_index": item.coding_index,
                    "selection_rank": eligible_ranks.get(item.model),
                    "status": "eligible" if item.model in self.eligible_models else "skipped",
                    "reason": item.reason,
                }
                for item in self.models
            ],
            "skipped_models": [dict(item) for item in self.skipped_models],
            "manifest_hash": self.manifest_hash,
            "source": self.source,
            "checked_at": self.checked_at.isoformat(),
            "policy": {
                "explicit_free_variant_required": True,
                "require_tools": True,
                "require_structured_outputs": True,
                "provider_fallbacks": False,
                "ranking_note": (
                    "The cascade is a capability and benchmark heuristic; every model "
                    "still requires a live agent-check before production use."
                ),
            },
        }


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
        name=record.get("name") if isinstance(record.get("name"), str) else None,
        context_length=(
            int(record["context_length"])
            if isinstance(record.get("context_length"), int)
            else None
        ),
        agentic_index=_benchmark_metric(record, "agentic_index"),
        intelligence_index=_benchmark_metric(record, "intelligence_index"),
        coding_index=_benchmark_metric(record, "coding_index"),
    )


def _benchmark_metric(record: dict[object, object], metric: str) -> float | None:
    benchmarks = record.get("benchmarks")
    if not isinstance(benchmarks, dict):
        return None
    artificial_analysis = benchmarks.get("artificial_analysis")
    if not isinstance(artificial_analysis, dict):
        return None
    value = artificial_analysis.get(metric)
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return None
    return float(value)


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


def _catalog_order_key(item: ModelCapability) -> tuple[float, float, float, int, str]:
    return (
        item.agentic_index if item.agentic_index is not None else -1.0,
        item.intelligence_index if item.intelligence_index is not None else -1.0,
        item.coding_index if item.coding_index is not None else -1.0,
        item.context_length or 0,
        item.model,
    )


def _build_free_model_catalog(
    records: Sequence[object],
    *,
    primary_model: str | None = None,
    source: str,
) -> FreeModelCatalog:
    free_ids = sorted(
        {
            record["id"]
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("id"), str)
            and _free_pricing(record.get("pricing"))
        }
    )
    report = _build_report(
        tuple(free_ids),
        records,
        require_tools=True,
        source=source,
    )
    models = tuple(
        sorted(
            [
                replace(item, reason="not_explicit_free_variant")
                if not is_free_openrouter_model(item.model)
                else item
                for item in report.capabilities
            ],
            key=lambda item: item.model,
        )
    )
    eligible = tuple(
        sorted(
            (item.model for item in models if item.reason is None),
            key=lambda model: _catalog_order_key(
                next(item for item in models if item.model == model)
            ),
            reverse=True,
        )
    )
    if primary_model in eligible:
        recommended = (primary_model, *(model for model in eligible if model != primary_model))
    else:
        recommended = eligible
    manifest_hash = hashlib.sha256(
        json.dumps(
            [
                {
                    "model": item.model,
                    "free": item.free,
                    "tools": item.supports_tools,
                    "structured": item.supports_structured_outputs,
                    "context_length": item.context_length,
                    "agentic_index": item.agentic_index,
                    "intelligence_index": item.intelligence_index,
                    "coding_index": item.coding_index,
                }
                for item in models
            ],
            sort_keys=True,
        ).encode()
    ).hexdigest()
    skipped_by_model = {
        item["model"]: item["reason"] for item in report.skipped_models
    }
    skipped_by_model.update(
        {
            item.model: item.reason
            for item in models
            if item.reason is not None
        }
    )
    return FreeModelCatalog(
        models=models,
        eligible_models=eligible,
        recommended_cascade=recommended,
        skipped_models=tuple(
            {"model": model, "reason": reason}
            for model, reason in sorted(skipped_by_model.items())
        ),
        manifest_hash=manifest_hash,
        source=source,
        checked_at=report.checked_at,
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
        raise ProviderError("LLM capability check requires an API key")
    if requested_models and all(is_openai_model(model) for model in requested_models):
        capabilities = tuple(
            ModelCapability(
                model=model,
                free=False,
                supports_tools=True,
                supports_structured_outputs=True,
                name=model,
            )
            for model in requested_models
        )
        manifest_hash = hashlib.sha256(
            json.dumps(
                {
                    "provider": "openai",
                    "models": list(requested_models),
                    "tools": require_tools,
                    "structured_outputs": True,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        return CapabilityReport(
            requested_models=requested_models,
            eligible_models=requested_models,
            capabilities=capabilities,
            skipped_models=(),
            require_tools=require_tools,
            manifest_hash=manifest_hash,
            source="configured",
            checked_at=datetime.now(UTC),
        )
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


async def resolve_free_model_catalog(
    api_key: str,
    *,
    primary_model: str | None = None,
    timeout_seconds: float = 15,
) -> FreeModelCatalog:
    """Fetch the live explicit-free catalog; never authorize from cache."""
    if not api_key.strip():
        raise ProviderError("OpenRouter model map requires an API key")
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(OPENROUTER_MODELS_URL, headers=headers)
            response.raise_for_status()
            payload: Any = response.json()
        records = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise ValueError("models manifest is malformed")
        return _build_free_model_catalog(
            records,
            primary_model=primary_model,
            source="live",
        )
    except (httpx.HTTPError, ValueError, OSError):
        raise ProviderError("OpenRouter live model catalog unavailable") from None
