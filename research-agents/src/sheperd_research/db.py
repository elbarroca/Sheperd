from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal, Protocol, cast
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from psycopg import Connection, OperationalError

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    DistillationQualityStatus,
    EvidenceStatus,
    ExtractionStatus,
    FreshnessStatus,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    RunStatus,
    SignalEvent,
    SourceCandidate,
    TranslationStatus,
    ValidationReport,
    ValidationStatus,
    WeeklyBrief,
)
from .validation import validation_blocking_reasons
from .validators import (
    ACTIONABLE_REPORT_SECTIONS,
    REPORT_BULLET_SECTIONS,
    article_fulfillment,
    content_hash,
    normalize_url,
    quality_metrics,
)

MIGRATION_VERSION = "0013_run_sources"
ArchiveScope = Literal["active", "archived", "all"]
_ARCHIVE_SCOPES = frozenset({"active", "archived", "all"})
_AUDIT_TEXT_LIMIT = 400
_AUDIT_LIST_LIMIT = 100
_AUDIT_SENSITIVE_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer ",
    "password",
    "private key",
    "-----begin",
    "prompt:",
    "reasoning:",
    "article_body",
    "article body",
    "raw_body",
    "raw body",
    "secret",
)
_AUDIT_SENSITIVE_QUERY_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "apikey",
        "auth",
        "authorization",
        "key",
        "password",
        "secret",
        "token",
    }
)
_AUDIT_METADATA_TEXT_FIELDS = frozenset(
    {
        "brief_id",
        "content_hash",
        "error",
        "fallback_reason",
        "input_hash",
        "lane",
        "mode",
        "operation",
        "output_hash",
        "provider_attempt",
        "prompt_version",
        "request_id",
        "resolved_model",
        "requested_model",
        "source_url",
        "status",
    }
)
_AUDIT_METADATA_INT_FIELDS = frozenset(
    {
        "accepted_seed_count",
        "attempt",
        "claim_count",
        "extracted_count",
        "input_tokens",
        "lane_count",
        "latency_ms",
        "llm_calls",
        "llm_input_chars",
        "missing_agent_extractions",
        "model_index",
        "output_tokens",
        "provider_attempt",
        "quarantined_seed_count",
        "reasoning_tokens",
        "record_attempt",
        "search_calls",
        "seed_only_count",
        "source_count",
        "tool_calls",
        "tool_input_chars",
        "total_tokens",
    }
)
_AUDIT_METADATA_FLOAT_FIELDS = frozenset({"citation_coverage"})
_AUDIT_METADATA_LIST_FIELDS = frozenset(
    {
        "errors",
        "partial_reasons",
        "quarantined_seed_domains",
        "required_tools",
        "source_hashes",
        "tool_errors",
    }
)
_AUDIT_CALL_TEXT_FIELDS = frozenset(
    {
        "capability_manifest_hash",
        "error_code",
        "error_type",
        "fallback_reason",
        "finish_reason",
        "input_hash",
        "operation",
        "output_hash",
        "prompt_version",
        "request_id",
        "resolved_model",
        "requested_model",
        "source_url",
    }
)
_AUDIT_CALL_INT_FIELDS = frozenset(
    {
        "attempt",
        "input_tokens",
        "latency_ms",
        "model_index",
        "output_tokens",
        "record_attempt",
        "reasoning_tokens",
        "status_code",
        "tool_calls",
        "total_tokens",
    }
)
_AUDIT_CALL_FLOAT_FIELDS = frozenset({"retry_after_seconds"})
_AUDIT_CALL_LIST_FIELDS = frozenset({"required_tools"})
_AUDIT_CALL_FIELDS = (
    _AUDIT_CALL_TEXT_FIELDS
    | _AUDIT_CALL_INT_FIELDS
    | _AUDIT_CALL_FLOAT_FIELDS
    | _AUDIT_CALL_LIST_FIELDS
    | {"tool_call_receipts"}
)
_AUDIT_RECEIPT_TEXT_FIELDS = frozenset(
    {"call_id", "error_code", "input_hash", "result_hash", "status", "tool_name"}
)
_AUDIT_RECEIPT_INT_FIELDS = frozenset(
    {
        "call_index",
        "latency_ms",
        "provider_key_count",
        "provider_key_slot",
        "result_count",
        "url_count",
    }
)
_AUDIT_RECEIPT_FIELDS = _AUDIT_RECEIPT_TEXT_FIELDS | _AUDIT_RECEIPT_INT_FIELDS


def _safe_audit_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value[:_AUDIT_TEXT_LIMIT]
    lowered = text.casefold()
    if any(marker in lowered for marker in _AUDIT_SENSITIVE_MARKERS):
        return "[redacted]"
    return text


def _safe_audit_url(value: object) -> str | None:
    text = _safe_audit_text(value)
    if text is None or not text.startswith(("http://", "https://")):
        return None
    try:
        parsed = urlsplit(text)
        query_keys = {
            key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
        }
    except ValueError:
        return None
    if parsed.username or parsed.password or query_keys.intersection(_AUDIT_SENSITIVE_QUERY_KEYS):
        return None
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _safe_audit_urls(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        safe
        for item in value[:_AUDIT_LIST_LIMIT]
        if (safe := _safe_audit_url(item)) is not None
    ]


def _safe_audit_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _safe_audit_float(value: object) -> float | None:
    return value if isinstance(value, float) and not isinstance(value, bool) else None


def _row_float(value: object) -> float:
    return float(value) if isinstance(value, (Decimal, int, float)) else 0.0


def _row_strings(value: object) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, str)]


def _archive_scope_clause(scope: str, column: str) -> str:
    if scope not in _ARCHIVE_SCOPES:
        raise ValueError("archive_scope must be active, archived, or all")
    if scope == "active":
        return f"{column} IS NULL"
    if scope == "archived":
        return f"{column} IS NOT NULL"
    return "TRUE"


def _is_archived(run: dict[str, object]) -> bool:
    return run.get("archived_at") is not None


def _safe_audit_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        safe
        for item in value[:_AUDIT_LIST_LIMIT]
        if (safe := _safe_audit_text(item)) is not None
    ]


def _safe_audit_int_mapping(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {
        key: safe
        for key, item in list(value.items())[:_AUDIT_LIST_LIMIT]
        if isinstance(key, str) and (safe := _safe_audit_int(item)) is not None
    }


def _safe_audit_status_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        key: safe
        for key, item in list(value.items())[:_AUDIT_LIST_LIMIT]
        if isinstance(key, str) and (safe := _safe_audit_text(item)) is not None
    }


def _redact_audit_receipts(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    receipts: list[dict[str, object]] = []
    for item in value[:_AUDIT_LIST_LIMIT]:
        if not isinstance(item, dict):
            continue
        receipt: dict[str, object] = {}
        for key in _AUDIT_RECEIPT_FIELDS:
            if key not in item:
                continue
            raw = item[key]
            if raw is None:
                receipt[key] = None
            elif key in _AUDIT_RECEIPT_TEXT_FIELDS:
                safe_text = _safe_audit_text(raw)
                if safe_text is not None:
                    receipt[key] = safe_text
            else:
                safe_int = _safe_audit_int(raw)
                if safe_int is not None:
                    receipt[key] = safe_int
        receipts.append(receipt)
    return receipts


def _redact_audit_receipt(value: dict[str, object]) -> dict[str, object]:
    receipts = _redact_audit_receipts([value])
    return receipts[0] if receipts else {}


def _redact_audit_call(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    call: dict[str, object] = {}
    for key in _AUDIT_CALL_FIELDS:
        if key not in value:
            continue
        raw = value[key]
        if raw is None:
            call[key] = None
        elif key == "tool_call_receipts":
            call[key] = _redact_audit_receipts(raw)
        elif key in _AUDIT_CALL_LIST_FIELDS:
            call[key] = _safe_audit_string_list(raw)
        elif key in _AUDIT_CALL_TEXT_FIELDS:
            safe_text = _safe_audit_url(raw) if key == "source_url" else _safe_audit_text(raw)
            if safe_text is not None:
                call[key] = safe_text
        elif key in _AUDIT_CALL_FLOAT_FIELDS:
            safe_float = _safe_audit_float(raw)
            if safe_float is not None:
                call[key] = safe_float
        else:
            safe_int = _safe_audit_int(raw)
            if safe_int is not None:
                call[key] = safe_int
    return call


def _redact_audit_calls(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [
        safe
        for item in value[:_AUDIT_LIST_LIMIT]
        if isinstance(item, dict) and (safe := _redact_audit_call(item))
    ]


def _redact_audit_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Persist only structured audit fields; never store raw workflow payloads."""
    safe_metadata: dict[str, object] = {}
    for key in _AUDIT_METADATA_TEXT_FIELDS:
        if key not in metadata:
            continue
        raw = metadata[key]
        if raw is None:
            safe_metadata[key] = None
        else:
            safe_text = _safe_audit_url(raw) if key == "source_url" else _safe_audit_text(raw)
            if safe_text is not None:
                safe_metadata[key] = safe_text
    for key in _AUDIT_METADATA_INT_FIELDS:
        if key not in metadata:
            continue
        raw = metadata[key]
        if raw is None:
            safe_metadata[key] = None
        else:
            safe_int = _safe_audit_int(raw)
            if safe_int is not None:
                safe_metadata[key] = safe_int
    for key in _AUDIT_METADATA_FLOAT_FIELDS:
        if key not in metadata:
            continue
        raw = metadata[key]
        if raw is None:
            safe_metadata[key] = None
        else:
            safe_float = _safe_audit_float(raw)
            if safe_float is not None:
                safe_metadata[key] = safe_float
    for key in _AUDIT_METADATA_LIST_FIELDS:
        if key in metadata:
            safe_metadata[key] = _safe_audit_string_list(metadata[key])
    if "quarantined_seed_reasons" in metadata:
        safe_metadata["quarantined_seed_reasons"] = _safe_audit_int_mapping(
            metadata["quarantined_seed_reasons"]
        )
    if "lane_statuses" in metadata:
        safe_metadata["lane_statuses"] = _safe_audit_status_mapping(metadata["lane_statuses"])
    for key in ("call", "agent_call"):
        if key in metadata:
            safe_metadata[key] = _redact_audit_call(metadata[key])
    for key in ("attempts", "calls"):
        if key in metadata:
            safe_metadata[key] = _redact_audit_calls(metadata[key])
    if "tool_call_receipts" in metadata:
        safe_metadata["tool_call_receipts"] = _redact_audit_receipts(
            metadata["tool_call_receipts"]
        )
    return safe_metadata


def _sanitized_tool_args(receipt: dict[str, object]) -> dict[str, object]:
    """Keep the small allow-list of tool arguments needed for audit display."""
    raw_args = receipt.get("sanitized_args")
    args = raw_args if isinstance(raw_args, dict) else receipt
    sanitized: dict[str, object] = {}
    query = args.get("query")
    if isinstance(query, str):
        safe_query = _safe_audit_text(query)
        if safe_query is not None:
            sanitized["query"] = safe_query
    url_count = args.get("url_count")
    if isinstance(url_count, int) and not isinstance(url_count, bool):
        sanitized["url_count"] = max(0, url_count)
    urls = args.get("urls")
    if not isinstance(urls, list):
        urls = receipt.get("urls")
    if "url_count" not in sanitized:
        sanitized["url_count"] = len(_safe_audit_urls(urls))
    for key in ("provider_key_slot", "provider_key_count"):
        value = args.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            sanitized[key] = max(0, value)
    return sanitized


def _seed_safe_source(source: SourceCandidate) -> SourceCandidate:
    if not source.is_seed:
        return source
    return source.model_copy(
        update={
            "source_kind": "seed-only",
            "evidence_status": EvidenceStatus.UNVERIFIED,
        }
    )


def _safe_public_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        normalized = normalize_url(value)
    except ValueError:
        return None
    return normalized if normalized.startswith(("http://", "https://")) else None


def _require_public_url(value: object) -> str:
    normalized = _safe_public_url(value)
    if normalized is None:
        raise ValueError("stored source URL is malformed")
    return normalized


def _safe_public_urls(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        normalized
        for item in value
        if (normalized := _safe_public_url(item)) is not None
    ]


def _safe_public_bullets(value: object) -> list[ReportBullet]:
    if not isinstance(value, list):
        return []
    bullets: list[ReportBullet] = []
    for item in value:
        if isinstance(item, ReportBullet):
            bullets.append(
                item.model_copy(update={"source_urls": _safe_public_urls(item.source_urls)})
            )
            continue
        if not isinstance(item, dict):
            continue
        payload = {
            key: item_value
            for key, item_value in item.items()
            if isinstance(key, str)
        }
        payload["source_urls"] = _safe_public_urls(payload.get("source_urls"))
        bullets.append(ReportBullet.model_validate(payload))
    return bullets


def _article_distillation_from_row(
    row: Sequence[object],
    *,
    claims: Sequence[ClaimDraft] = (),
) -> ArticleDistillation:
    """Decode the stable article projection, including legacy defaults."""
    raw_quality = row[18] if len(row) > 18 else None
    try:
        quality_status = DistillationQualityStatus(str(raw_quality or "incomplete"))
    except ValueError:
        quality_status = DistillationQualityStatus.INCOMPLETE
    quality_issues = row[19] if len(row) > 19 and isinstance(row[19], list) else []
    insight_packet = row[17] if len(row) > 17 and isinstance(row[17], dict) else {}
    return ArticleDistillation(
        source_url=_require_public_url(row[0]),
        summary=cast(str, row[1]),
        key_points=cast(list[str], row[2] or []),
        entities=cast(list[str], row[3] or []),
        signals=cast(list[str], row[4] or []),
        claims=list(claims),
        limitations=cast(list[str], row[5] or []),
        published_at=cast(datetime | None, row[6]),
        model_id=cast(str, row[7]),
        prompt_version=cast(str, row[8]),
        evidence_status=EvidenceStatus(cast(str, row[9])),
        content_hash=cast(str | None, row[10]),
        source_language=cast(str, row[11]),
        summary_original=cast(str, row[12]),
        key_points_original=cast(list[str], row[13] or []),
        translation_status=TranslationStatus(cast(str, row[14])),
        evidence_excerpts=cast(list[str], row[15] or []),
        evidence_locators=cast(list[str], row[16] or []),
        insight_packet=insight_packet,
        what_happened=cast(str, insight_packet.get("what_happened") or ""),
        why_it_matters=cast(str, insight_packet.get("why_it_matters") or ""),
        risk_assessment=insight_packet.get("risk_assessment"),
        opportunity_assessment=insight_packet.get("opportunity_assessment"),
        uncertainties=cast(list[str], insight_packet.get("uncertainties", []) or []),
        next_steps=cast(list[str], insight_packet.get("next_steps", []) or []),
        quality_status=quality_status,
        quality_issues=cast(list[str], quality_issues),
    )


def _validate_new_distillation_evidence(distillation: ArticleDistillation) -> None:
    for excerpt in distillation.evidence_excerpts:
        if len(excerpt) > 320 or len(excerpt.split()) > 40:
            raise ValueError(
                "evidence_excerpts entries must be at most 320 characters and 40 words"
            )
    for locator in distillation.evidence_locators:
        if len(locator) > 300:
            raise ValueError("evidence_locators entries must be at most 300 characters")


class RepositoryProtocol(Protocol):
    def create_run(self, run_id: str, request: ResearchRunRequest) -> None: ...

    def update_run_status(
        self, run_id: str, status: RunStatus, error: str | None = None
    ) -> None: ...

    def record_step(
        self,
        run_id: str,
        agent_name: str,
        status: str,
        metadata: dict[str, object],
        *,
        lane: str = "system",
        attempt: int = 1,
        duration_ms: int | None = None,
        input_hash: str | None = None,
        output_hash: str | None = None,
        error_code: str | None = None,
    ) -> None: ...

    def record_tool_calls(
        self,
        run_id: str,
        agent_name: str,
        attempt: int,
        lane: str,
        receipts: list[dict[str, object]],
    ) -> None: ...

    def get_run_tool_calls(self, run_id: str) -> list[dict[str, object]]: ...

    def list_distillations(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        lane: str | None = None,
        geography: str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ArticleDistillation]: ...

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        verification_basis: str | None = None,
        independent_source_min: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ClaimDraft]: ...

    def list_signal_events(
        self,
        *,
        run_id: str | None = None,
        geography: str | None = None,
        event_type: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SignalEvent]: ...

    def record_source(
        self, source: SourceCandidate, *, run_id: str | None = None
    ) -> SourceCandidate: ...

    def record_snapshot(self, run_id: str, source: SourceCandidate, content: str) -> None: ...

    def record_distillation(self, run_id: str, distillation: ArticleDistillation) -> None: ...

    def record_claims(self, run_id: str, claims: list[ClaimDraft]) -> None: ...

    def record_signal_events(self, events: list[SignalEvent]) -> None: ...

    def record_brief(self, brief: WeeklyBrief) -> None: ...

    def record_validation(self, report: ValidationReport) -> None: ...

    def get_validation(self, run_id: str) -> ValidationReport | None: ...

    def review_brief(
        self, run_id: str, decision: ReviewState, reviewer: str, notes: str
    ) -> None: ...

    def get_brief(self, run_id: str) -> WeeklyBrief | None: ...

    def get_run(self, run_id: str) -> dict[str, object] | None: ...

    def get_run_sources(self, run_id: str) -> list[SourceCandidate]: ...

    def get_run_claims(self, run_id: str) -> list[ClaimDraft]: ...

    def get_run_snapshot_hashes(self, run_id: str) -> list[str]: ...

    def get_run_source_hashes(self, run_id: str) -> dict[str, str]: ...

    def get_run_lane_statuses(self, run_id: str) -> dict[str, str]: ...

    def get_run_steps(self, run_id: str) -> list[dict[str, object]]: ...

    def get_run_distillations(self, run_id: str) -> list[ArticleDistillation]: ...

    def get_run_signal_events(self, run_id: str) -> list[SignalEvent]: ...

    def get_trailing_evidence(
        self,
        *,
        topic_set: str,
        since: datetime,
        until: datetime,
        limit: int = 1000,
    ) -> tuple[list[SourceCandidate], list[ArticleDistillation]]: ...

    def list_runs(
        self,
        *,
        topic_set: str | None = None,
        status: RunStatus | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]: ...

    def list_sources(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SourceCandidate]: ...

    def list_source_explorer(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, object]: ...

    def source_facets(self) -> dict[str, list[str]]: ...

    def list_briefs(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        archive_scope: ArchiveScope = "active",
    ) -> list[WeeklyBrief]: ...

    def list_brief_summaries(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> list[dict[str, object]]: ...

    def count_brief_summaries(
        self,
        *,
        cadence: str | None = None,
        review_state: ReviewState | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> int: ...

    def list_regions(self) -> list[str]: ...

    def region_counts(self, run_id: str | None = None) -> list[dict[str, object]]: ...

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        region: str | None = None,
        language: str | None = None,
        evidence: EvidenceStatus | str | None = None,
    ) -> list[dict[str, object]]: ...

    def health(self) -> dict[str, object]: ...

    def audit_summary(self) -> dict[str, object]: ...


class InMemoryRepository:
    """Offline repository used by tests and provider-free local development."""

    def __init__(self) -> None:
        self.runs: dict[str, dict[str, object]] = {}
        self.steps: list[dict[str, object]] = []
        self.sources: dict[str, SourceCandidate] = {}
        self.run_sources: dict[tuple[str, str], SourceCandidate] = {}
        self.source_snapshots: dict[tuple[str, str], dict[str, object]] = {}
        self.distillations: dict[tuple[str, str], ArticleDistillation] = {}
        self.claims: dict[tuple[str, str, tuple[str, ...]], ClaimDraft] = {}
        self.signal_events: dict[str, SignalEvent] = {}
        self.briefs: dict[str, WeeklyBrief] = {}
        self.review_decisions: list[dict[str, object]] = []
        self.validations: dict[str, ValidationReport] = {}
        self.tool_calls: list[dict[str, object]] = []

    def create_run(self, run_id: str, request: ResearchRunRequest) -> None:
        self.runs.setdefault(
            run_id,
            {
                "run_id": run_id,
                "request": request,
                "status": RunStatus.RUNNING,
                "started_at": datetime.now().astimezone(),
                "as_of": request.as_of,
                "model_id": request.model,
                "prompt_version": None,
                "neon_branch_id": None,
                "migration_version": MIGRATION_VERSION,
                "error": None,
                "archived_at": None,
                "archive_reason": None,
            },
        )

    def update_run_status(
        self, run_id: str, status: RunStatus, error: str | None = None
    ) -> None:
        self.runs.setdefault(run_id, {})["status"] = status
        self.runs[run_id]["error"] = error
        if status is RunStatus.FAILED and self.runs[run_id].get("archived_at") is None:
            self.runs[run_id]["archived_at"] = datetime.now(UTC)
            self.runs[run_id]["archive_reason"] = "run_failed"

    def record_step(
        self,
        run_id: str,
        agent_name: str,
        status: str,
        metadata: dict[str, object],
        *,
        lane: str = "system",
        attempt: int = 1,
        duration_ms: int | None = None,
        input_hash: str | None = None,
        output_hash: str | None = None,
        error_code: str | None = None,
    ) -> None:
        existing = next(
            (
                step
                for step in self.steps
                if step["run_id"] == run_id
                and step["agent_name"] == agent_name
                and step["attempt"] == attempt
            ),
            None,
        )
        safe_metadata = _redact_audit_metadata(metadata)
        call_metadata = safe_metadata.get("call")
        if not isinstance(call_metadata, dict):
            call_metadata = safe_metadata
        record: dict[str, object] = {
            "run_id": run_id,
            "agent_name": agent_name,
            "status": status,
            "metadata": safe_metadata,
            "lane": lane,
            "attempt": attempt,
            "duration_ms": duration_ms,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "error_code": error_code,
            "requested_model": call_metadata.get("requested_model"),
            "resolved_model": call_metadata.get("resolved_model"),
            "prompt_version": call_metadata.get("prompt_version"),
            "request_id": call_metadata.get("request_id"),
            "input_tokens": call_metadata.get("input_tokens"),
            "output_tokens": call_metadata.get("output_tokens"),
            "total_tokens": call_metadata.get("total_tokens"),
            "wall_clock_ms": duration_ms,
            "model_index": call_metadata.get("model_index"),
            "fallback_reason": call_metadata.get("fallback_reason"),
            "tool_calls": call_metadata.get("tool_calls", 0),
            "capability_manifest_hash": call_metadata.get("capability_manifest_hash"),
            "required_tools": call_metadata.get("required_tools", []),
        }
        if existing is None:
            self.steps.append(record)

    def record_source(
        self, source: SourceCandidate, *, run_id: str | None = None
    ) -> SourceCandidate:
        normalized = normalize_url(source.url)
        stored = _seed_safe_source(source).model_copy(update={"url": normalized})
        existing = self.sources.get(normalized)
        if existing is None:
            self.sources[normalized] = stored
        elif existing.is_seed or stored.is_seed:
            self.sources[normalized] = existing.model_copy(
                update={
                    "is_seed": True,
                    "source_kind": "seed-only",
                    "evidence_status": EvidenceStatus.UNVERIFIED,
                }
            )
        else:
            self.sources[normalized] = existing.model_copy(
                update={
                    "region": stored.region,
                    "language_code": stored.language_code,
                    "language_confidence": stored.language_confidence,
                    "authority_tier": stored.authority_tier,
                    "catalog_source_id": stored.catalog_source_id,
                    "source_type": stored.source_type,
                    "freshness_status": stored.freshness_status,
                    "freshness_days": stored.freshness_days,
                    "extraction_status": stored.extraction_status,
                    "extraction_error_code": stored.extraction_error_code,
                    "normalized_title_en": stored.normalized_title_en,
                    "normalized_snippet_en": stored.normalized_snippet_en,
                }
            )
        result = self.sources[normalized]
        if run_id is not None:
            self.run_sources[(run_id, normalized)] = result.model_copy(
                update={
                    "extraction_status": stored.extraction_status,
                    "extraction_error_code": stored.extraction_error_code,
                }
            )
        return result

    def record_tool_calls(
        self,
        run_id: str,
        agent_name: str,
        attempt: int,
        lane: str,
        receipts: list[dict[str, object]],
    ) -> None:
        for receipt in receipts:
            safe_receipt = _redact_audit_receipt(receipt)
            call_index = safe_receipt.get("call_index", 0)
            record = {
                "run_id": run_id,
                "agent_name": agent_name,
                "attempt": attempt,
                "lane": lane,
                "call_index": call_index,
                "tool_name": safe_receipt.get("tool_name", "unknown"),
                "sanitized_args": _sanitized_tool_args(receipt),
                "input_hash": safe_receipt.get("input_hash"),
                "result_hash": safe_receipt.get("result_hash"),
                "result_count": safe_receipt.get("result_count"),
                "latency_ms": safe_receipt.get("latency_ms"),
                "status": safe_receipt.get("status", "unknown"),
                "error_code": safe_receipt.get("error_code"),
            }
            key = (run_id, agent_name, attempt, call_index)
            if not any(
                (
                    item.get("run_id"),
                    item.get("agent_name"),
                    item.get("attempt"),
                    item.get("call_index"),
                )
                == key
                for item in self.tool_calls
            ):
                self.tool_calls.append(record)

    def get_run_tool_calls(self, run_id: str) -> list[dict[str, object]]:
        return [item for item in self.tool_calls if item.get("run_id") == run_id]

    def list_distillations(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        lane: str | None = None,
        geography: str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ArticleDistillation]:
        needle = query.lower().strip()
        expected_evidence = getattr(evidence_status, "value", evidence_status)
        values = [
            item
            for (current_run, _), item in self.distillations.items()
            if (run_id is None or current_run == run_id)
            and (
                not needle
                or needle
                in f"{item.source_url} {item.summary} {' '.join(item.key_points)}".lower()
            )
            and (
                expected_evidence is None
                or item.evidence_status.value == expected_evidence
            )
            and (
                lane is None
                or (
                    source := self.sources.get(normalize_url(item.source_url))
                ) is not None
                and source.lane == lane
            )
            and (
                geography is None
                or (
                    source := self.sources.get(normalize_url(item.source_url))
                ) is not None
                and geography in source.geographies
            )
            and (
                region is None
                or (
                    source := self.sources.get(normalize_url(item.source_url))
                ) is not None
                and source.region == region
            )
            and (
                language is None
                or item.source_language == language
            )
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_source_explorer(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, object]:
        all_sources = self.list_sources(
            query,
            geography=geography,
            lane=lane,
            evidence_status=evidence_status,
            region=region,
            language=language,
            freshness=freshness,
            authority_tier=authority_tier,
            source_type=source_type,
            since=since,
            until=until,
            limit=1000,
        )
        ordered = sorted(
            all_sources,
            key=lambda source: (-source.retrieved_at.timestamp(), normalize_url(source.url)),
        )
        bounded_page = max(1, page)
        bounded_size = max(1, min(page_size, 100))
        start = (bounded_page - 1) * bounded_size
        selected = ordered[start : start + bounded_size]
        items: list[dict[str, object]] = []
        for source in selected:
            normalized_url = normalize_url(source.url)
            snapshot = next(
                (
                    value
                    for (run_id, url), value in reversed(list(self.source_snapshots.items()))
                    if url == normalized_url and run_id in self.runs
                ),
                None,
            )
            distillation = next(
                (
                    value
                    for (run_id, url), value in reversed(list(self.distillations.items()))
                    if url == normalized_url and run_id in self.runs
                ),
                None,
            )
            claims = [
                claim
                for (run_id, _, _), claim in self.claims.items()
                if run_id in self.runs
                and normalized_url
                in {normalize_url(url) for url in claim.source_urls}
            ]
            if distillation is not None:
                distillation = distillation.model_copy(update={"claims": claims})
            items.append(
                {
                    "source": source,
                    "distillation": distillation,
                    "claims": claims,
                    "source_hash": snapshot.get("content_hash") if snapshot else None,
                    "fulfillment": article_fulfillment(
                        source.url,
                        source_persisted=True,
                        extracted=source.extraction_status.value == "succeeded",
                        distillation=distillation,
                        claims=claims,
                    ),
                }
            )
        return {
            "items": items,
            "page": bounded_page,
            "page_size": bounded_size,
            "total": len(ordered),
            "has_more": start + len(selected) < len(ordered),
        }

    def source_facets(self) -> dict[str, list[str]]:
        sources = list(self.sources.values())
        return {
            "regions": sorted({source.region for source in sources}),
            "languages": sorted({source.language_code for source in sources}),
            "freshness": sorted({source.freshness_status.value for source in sources}),
            "authority": sorted({source.authority_tier for source in sources}),
            "source_types": sorted({source.source_type for source in sources}),
            "lanes": sorted({source.lane for source in sources}),
            "evidence_states": sorted(
                {source.evidence_status.value for source in sources}
            ),
        }

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        verification_basis: str | None = None,
        independent_source_min: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ClaimDraft]:
        needle = query.lower().strip()
        expected = getattr(evidence_status, "value", evidence_status)
        values = [
            claim
            for (current_run, _, _), claim in self.claims.items()
            if (run_id is None or current_run == run_id)
            and (not needle or needle in claim.claim.lower())
            and (expected is None or claim.evidence_status.value == expected)
            and (
                verification_basis is None
                or claim.verification_basis == verification_basis
            )
            and (
                independent_source_min is None
                or claim.independent_source_count >= independent_source_min
            )
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_signal_events(
        self,
        *,
        run_id: str | None = None,
        geography: str | None = None,
        event_type: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SignalEvent]:
        expected = getattr(evidence_status, "value", evidence_status)
        values = [
            event
            for event in self.signal_events.values()
            if (run_id is None or event.run_id == run_id)
            and (geography is None or geography in event.geographies)
            and (event_type is None or event.event_type == event_type)
            and (expected is None or event.evidence_status.value == expected)
            and (
                region is None
                or any(
                    self.sources.get(normalize_url(url), SourceCandidate(url=url)).region
                    == region
                    for url in event.source_urls
                )
            )
            and (
                language is None
                or any(
                    self.sources.get(normalize_url(url), SourceCandidate(url=url)).language_code
                    == language
                    for url in event.source_urls
                )
            )
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def record_snapshot(self, run_id: str, source: SourceCandidate, content: str) -> None:
        normalized = normalize_url(source.url)
        stored = self.sources.get(normalized)
        if stored is None:
            stored = self.record_source(source)
        self.run_sources.setdefault((run_id, normalized), stored)
        self.source_snapshots[(run_id, normalized)] = {
            "run_id": run_id,
            "url": normalized,
            "content_hash": content_hash(content),
            "content_length": len(content),
        }

    def record_distillation(self, run_id: str, distillation: ArticleDistillation) -> None:
        _validate_new_distillation_evidence(distillation)
        self.distillations[(run_id, normalize_url(distillation.source_url))] = distillation

    def record_claims(self, run_id: str, claims: list[ClaimDraft]) -> None:
        for claim in claims:
            safe_claim = claim.model_copy(
                update={"source_urls": _safe_public_urls(claim.source_urls)}
            )
            key = (
                run_id,
                safe_claim.claim,
                tuple(sorted(safe_claim.source_urls)),
            )
            self.claims.setdefault(key, safe_claim)

    def record_brief(self, brief: WeeklyBrief) -> None:
        self.briefs[brief.run_id] = brief.model_copy(
            update={
                "source_urls": _safe_public_urls(brief.source_urls),
                "executive_bullets": _safe_public_bullets(brief.executive_bullets),
                "developments": _safe_public_bullets(brief.developments),
                "risks": _safe_public_bullets(brief.risks),
                "opportunities": _safe_public_bullets(brief.opportunities),
                "uncertainties": _safe_public_bullets(brief.uncertainties),
            }
        )

    def record_validation(self, report: ValidationReport) -> None:
        self.validations[report.run_id] = report
        run = self.runs.setdefault(report.run_id, {})
        run["validation_status"] = report.status
        run["citation_coverage"] = report.citation_coverage
        if report.status is ValidationStatus.FAILED and run.get("archived_at") is None:
            run["archived_at"] = datetime.now(UTC)
            run["archive_reason"] = "validation_failed"

    def get_validation(self, run_id: str) -> ValidationReport | None:
        return self.validations.get(run_id)

    def record_signal_events(self, events: list[SignalEvent]) -> None:
        for event in events:
            self.signal_events.setdefault(event.event_id, event)

    def review_brief(self, run_id: str, decision: ReviewState, reviewer: str, notes: str) -> None:
        brief = self.briefs.get(run_id)
        if brief is None:
            raise KeyError(f"brief not found: {run_id}")
        self.briefs[run_id] = brief.model_copy(update={"review_state": decision})
        self.review_decisions.append(
            {"run_id": run_id, "decision": decision, "reviewer": reviewer, "notes": notes}
        )

    def get_brief(self, run_id: str) -> WeeklyBrief | None:
        return self.briefs.get(run_id)

    def get_run(self, run_id: str) -> dict[str, object] | None:
        return self.runs.get(run_id)

    def get_run_sources(self, run_id: str) -> list[SourceCandidate]:
        return [
            source
            for (current_run, _), source in self.run_sources.items()
            if current_run == run_id
        ]

    def get_run_claims(self, run_id: str) -> list[ClaimDraft]:
        return [claim for key, claim in self.claims.items() if key[0] == run_id]

    def get_run_snapshot_hashes(self, run_id: str) -> list[str]:
        return [
            str(snapshot["content_hash"])
            for (current_run, _), snapshot in self.source_snapshots.items()
            if current_run == run_id
        ]

    def get_run_source_hashes(self, run_id: str) -> dict[str, str]:
        return {
            url: str(snapshot["content_hash"])
            for (current_run, url), snapshot in self.source_snapshots.items()
            if current_run == run_id
        }

    def get_run_lane_statuses(self, run_id: str) -> dict[str, str]:
        return {
            str(step["agent_name"]).removeprefix("discovery:"): str(step["status"])
            for step in self.steps
            if step["run_id"] == run_id and str(step["agent_name"]).startswith("discovery:")
        }

    def get_run_steps(self, run_id: str) -> list[dict[str, object]]:
        return [step for step in self.steps if step["run_id"] == run_id]

    def get_run_distillations(self, run_id: str) -> list[ArticleDistillation]:
        claims = self.get_run_claims(run_id)
        result: list[ArticleDistillation] = []
        for (current_run, normalized_url), distillation in self.distillations.items():
            if current_run != run_id:
                continue
            linked_claims = [
                claim
                for claim in claims
                if normalized_url in {normalize_url(url) for url in claim.source_urls}
            ]
            result.append(distillation.model_copy(update={"claims": linked_claims}))
        return result

    def get_run_signal_events(self, run_id: str) -> list[SignalEvent]:
        return [event for event in self.signal_events.values() if event.run_id == run_id]

    def get_trailing_evidence(
        self,
        *,
        topic_set: str,
        since: datetime,
        until: datetime,
        limit: int = 1000,
    ) -> tuple[list[SourceCandidate], list[ArticleDistillation]]:
        candidates: dict[
            str, tuple[SourceCandidate, ArticleDistillation, datetime]
        ] = {}
        for (run_id, normalized_url), item in self.distillations.items():
            source = self.sources.get(normalized_url)
            if source is None or source.is_seed:
                continue
            run = self.runs.get(run_id, {})
            request = run.get("request")
            if not (
                topic_set in source.topics
                or isinstance(request, ResearchRunRequest)
                and request.topic_set == topic_set
            ):
                continue
            run_as_of = run.get("as_of")
            observed_at = source.published_at or (
                run_as_of if isinstance(run_as_of, datetime) else source.retrieved_at
            )
            if not since <= observed_at <= until:
                continue
            claims = [
                claim
                for claim in self.get_run_claims(run_id)
                if normalized_url
                in {normalize_url(url) for url in claim.source_urls}
            ]
            retained = item.model_copy(update={"claims": claims or item.claims})
            previous = candidates.get(normalized_url)
            if previous is None or observed_at > previous[2]:
                candidates[normalized_url] = (source, retained, observed_at)

        ordered = sorted(
            candidates.values(),
            key=lambda item: (-item[2].timestamp(), normalize_url(item[0].url)),
        )[: max(1, min(limit, 1000))]
        return [item[0] for item in ordered], [item[1] for item in ordered]

    def list_runs(
        self,
        *,
        topic_set: str | None = None,
        status: RunStatus | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        expected_status = getattr(status, "value", status)
        values = list(self.runs.values())
        filtered_values: list[dict[str, object]] = []
        for run in values:
            request_value = run.get("request")
            run_as_of = run.get("as_of")
            if not isinstance(run_as_of, datetime) and isinstance(
                request_value, ResearchRunRequest
            ):
                run_as_of = request_value.as_of
            if topic_set is not None and not (
                isinstance(request_value, ResearchRunRequest)
                and request_value.topic_set == topic_set
            ):
                continue
            if expected_status is not None and run.get("status") != expected_status:
                continue
            if since is not None and (not isinstance(run_as_of, datetime) or run_as_of < since):
                continue
            if until is not None and (not isinstance(run_as_of, datetime) or run_as_of > until):
                continue
            filtered_values.append(run)
        bounded_limit = max(1, min(limit, 1000))
        return filtered_values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_sources(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SourceCandidate]:
        needle = query.lower().strip()
        values = list(self.sources.values())
        if needle:
            values = [
                source
                for source in values
                if needle
                in f"{source.title} {source.publisher} {source.url} {source.snippet}".lower()
            ]
        expected_evidence = getattr(evidence_status, "value", evidence_status)
        values = [
            source
            for source in values
            if (geography is None or geography in source.geographies)
            and (lane is None or source.lane == lane)
            and (region is None or source.region == region)
            and (language is None or source.language_code == language)
            and (
                freshness is None
                or source.freshness_status.value
                == getattr(freshness, "value", freshness)
            )
            and (authority_tier is None or source.authority_tier == authority_tier)
            and (source_type is None or source.source_type == source_type)
            and (
                expected_evidence is None
                or source.evidence_status.value == expected_evidence
            )
            and (since is None or source.published_at is not None and source.published_at >= since)
            and (until is None or source.published_at is not None and source.published_at <= until)
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_briefs(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> list[WeeklyBrief]:
        if archive_scope not in _ARCHIVE_SCOPES:
            raise ValueError("archive_scope must be active, archived, or all")
        needle = query.lower().strip()
        expected_review = getattr(review_state, "value", review_state)
        expected_run_status = getattr(run_status, "value", run_status)

        def run_value(brief: WeeklyBrief) -> str | None:
            value = self.runs.get(brief.run_id, {}).get("status")
            if isinstance(value, RunStatus):
                return value.value
            return value if isinstance(value, str) else None

        def is_ready(brief: WeeklyBrief) -> bool:
            validation = self.validations.get(brief.run_id)
            validation_value = getattr(
                getattr(validation, "status", ValidationStatus.BLOCKED),
                "value",
                ValidationStatus.BLOCKED.value,
            )
            quality = quality_metrics(
                self.get_run_sources(brief.run_id),
                self.get_run_distillations(brief.run_id),
                brief,
            )
            return (
                run_value(brief) == RunStatus.SUCCEEDED.value
                and validation_value == ValidationStatus.PASS.value
                and quality["quality_ready"] is True
            )

        values = [
            brief
            for brief in self.briefs.values()
            if (not needle or needle in f"{brief.title} {brief.summary}".lower())
            and (expected_review is None or brief.review_state.value == expected_review)
            and (
                cadence is None
                or getattr(self.runs.get(brief.run_id, {}).get("request"), "cadence", None)
                == cadence
            )
            and (since is None or brief.covered_until >= since)
            and (until is None or brief.covered_until <= until)
            and (expected_run_status is None or run_value(brief) == expected_run_status)
            and (not ready_only or is_ready(brief))
            and (
                archive_scope == "all"
                or _is_archived(self.runs.get(brief.run_id, {}))
                == (archive_scope == "archived")
            )
        ]
        values.sort(
            key=lambda brief: (
                not is_ready(brief),
                -brief.covered_until.timestamp(),
                brief.run_id,
            )
        )
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_brief_summaries(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> list[dict[str, object]]:
        briefs = self.list_briefs(
            query,
            review_state=review_state,
            cadence=cadence,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
            run_status=run_status,
            ready_only=ready_only,
            archive_scope=archive_scope,
        )
        return [
            {
                "run_id": brief.run_id,
                "title": brief.title,
                "covered_from": brief.covered_from,
                "covered_until": brief.covered_until,
                "review_state": brief.review_state.value,
                "run_status": self.runs.get(brief.run_id, {}).get("status"),
                "validation_status": getattr(
                    self.validations.get(brief.run_id), "status", ValidationStatus.BLOCKED
                ).value,
                "source_count": len(self.get_run_sources(brief.run_id)),
                "distillation_count": len(self.get_run_distillations(brief.run_id)),
                "claim_count": len(self.get_run_claims(brief.run_id)),
                "signal_count": len(self.get_run_signal_events(brief.run_id)),
                "regions": sorted(
                    {source.region for source in self.get_run_sources(brief.run_id)}
                ),
                "languages": sorted(
                    {source.language_code for source in self.get_run_sources(brief.run_id)}
                ),
                "lane_coverage": sorted(self.get_run_lane_statuses(brief.run_id)),
                "models": sorted(
                    {
                        item.model_id
                        for item in self.get_run_distillations(brief.run_id)
                        if item.model_id
                    }
                    | {brief.model_id},
                ),
                "as_of": self.runs.get(brief.run_id, {}).get("as_of"),
                "archived": _is_archived(self.runs.get(brief.run_id, {})),
                "archived_at": self.runs.get(brief.run_id, {}).get("archived_at"),
                "archive_reason": self.runs.get(brief.run_id, {}).get("archive_reason"),
                **quality_metrics(
                    self.get_run_sources(brief.run_id),
                    self.get_run_distillations(brief.run_id),
                    brief,
                ),
                # Test/local repository compatibility: production uses the SQL
                # summary query and does not hydrate these detail fields.
                "brief": brief,
                "run": {
                    key: value
                    for key, value in self.runs.get(brief.run_id, {}).items()
                    if key != "request"
                },
                "validation": self.validations.get(brief.run_id),
                "steps": self.get_run_steps(brief.run_id),
                "tool_calls": self.get_run_tool_calls(brief.run_id),
                "sources": self.get_run_sources(brief.run_id),
                "source_hashes": self.get_run_snapshot_hashes(brief.run_id),
                "distillations": self.get_run_distillations(brief.run_id),
                "claims": self.get_run_claims(brief.run_id),
                "signals": self.get_run_signal_events(brief.run_id),
            }
            for brief in briefs
        ]

    def count_brief_summaries(
        self,
        *,
        cadence: str | None = None,
        review_state: ReviewState | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> int:
        return len(
            self.list_briefs(
                review_state=review_state,
                cadence=cadence,
                since=since,
                until=until,
                run_status=run_status,
                ready_only=ready_only,
                archive_scope=archive_scope,
                limit=1000,
            )
        )

    def list_regions(self) -> list[str]:
        return sorted({source.region for source in self.sources.values()})

    def region_counts(self, run_id: str | None = None) -> list[dict[str, object]]:
        sources = (
            self.get_run_sources(run_id)
            if run_id is not None
            else list(self.sources.values())
        )
        counts: dict[str, dict[str, int]] = {}
        for source in sources:
            bucket = counts.setdefault(source.region, {"sources": 0, "languages": 0})
            bucket["sources"] += 1
        return [
            {"region": region, **values}
            for region, values in sorted(counts.items())
        ]

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        region: str | None = None,
        language: str | None = None,
        evidence: EvidenceStatus | str | None = None,
    ) -> list[dict[str, object]]:
        buckets: dict[
            tuple[str, str, str, str, str, str, str], dict[str, set[str]]
        ] = {}
        for event in self.signal_events.values():
            event_at = event.event_at or self.runs.get(event.run_id, {}).get("started_at")
            if not isinstance(event_at, datetime):
                continue
            if since is not None and event_at < since:
                continue
            if until is not None and event_at > until:
                continue
            utc_event_at = event_at.astimezone(UTC)
            source_matches: list[SourceCandidate | None] = [
                self.sources[normalize_url(url)]
                for url in event.source_urls
                if normalize_url(url) in self.sources
            ]
            if not source_matches:
                source_matches = [None]
            expected_evidence = getattr(evidence, "value", evidence)
            if region is not None and not any(
                source is not None and source.region == region for source in source_matches
            ):
                continue
            if language is not None and not any(
                source is not None and source.language_code == language
                for source in source_matches
            ):
                continue
            if expected_evidence is not None and event.evidence_status.value != expected_evidence:
                continue
            groups: set[tuple[str, str, str, str, str, str]] = set()
            for source in source_matches:
                lane = source.lane if source is not None else "unknown"
                authority = source.publisher if source is not None else "unknown"
                geographies = (
                    event.geographies
                    or (source.geographies if source is not None else [])
                    or ["unknown"]
                )
                for geography in geographies:
                    groups.add(
                        (
                            utc_event_at.strftime("%Y-%m-01"),
                            utc_event_at.strftime("%Y-%m-%d"),
                            lane,
                            geography,
                            authority,
                            event.event_type,
                        )
                    )
            for month, date, lane, geography, authority, signal in groups:
                key = (
                    month,
                    date,
                    lane,
                    geography,
                    authority,
                    signal,
                    event.evidence_status.value,
                )
                bucket = buckets.setdefault(
                    key,
                    {"signals": set(), "runs": set()},
                )
                bucket["signals"].add(event.event_id)
                bucket["runs"].add(event.run_id)
        values = [
            {
                "month": key[0],
                "date": key[1],
                "lane": key[2],
                "geography": key[3],
                "authority": key[4],
                "signal": key[5],
                "evidence": key[6],
                "signals": len(bucket["signals"]),
                "runs": len(bucket["runs"]),
            }
            for key, bucket in sorted(buckets.items(), reverse=True)
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def health(self) -> dict[str, object]:
        return {
            "status": "pass",
            "migration_version": MIGRATION_VERSION,
            "branch_id": None,
            "database": "in-memory",
        }

    def audit_summary(self) -> dict[str, object]:
        runs = list(self.runs.values())
        validations = list(self.validations.values())
        return {
            "reports": {
                "active": sum(not _is_archived(run) for run in runs),
                "archived": sum(_is_archived(run) for run in runs),
                "succeeded": sum(run.get("status") == RunStatus.SUCCEEDED for run in runs),
                "partial": sum(run.get("status") == RunStatus.PARTIAL for run in runs),
                "failed": sum(run.get("status") == RunStatus.FAILED for run in runs),
            },
            "records": {
                "sources": len(self.sources),
                "distillations": len(self.distillations),
                "claims": len(self.claims),
                "signals": len(self.signal_events),
            },
            "validation": {
                "checks": len(validations),
                "pass": sum(item.status is ValidationStatus.PASS for item in validations),
                "partial": sum(item.status is ValidationStatus.PARTIAL for item in validations),
                "failed": sum(item.status is ValidationStatus.FAILED for item in validations),
                "blocked": sum(item.status is ValidationStatus.BLOCKED for item in validations),
            },
            "quality": {
                "distillations_complete": sum(
                    item.quality_status.value == "complete"
                    for item in self.distillations.values()
                ),
                "distillations_incomplete": sum(
                    item.quality_status.value != "complete"
                    for item in self.distillations.values()
                ),
            },
            "migration_version": MIGRATION_VERSION,
        }


class PostgresRepository:
    def __init__(
        self,
        connection: Connection[tuple[object, ...]],
        neon_branch_id: str | None = None,
        connection_url: str | None = None,
    ) -> None:
        self.connection = connection
        self.neon_branch_id = neon_branch_id
        self._connection_url = connection_url

    @classmethod
    def from_url(
        cls, url: str, neon_branch_id: str | None = None
    ) -> PostgresRepository:
        import psycopg

        return cls(
            psycopg.connect(
                url,
                connect_timeout=15,
                application_name="sheperd-research",
            ),
            neon_branch_id,
            url,
        )

    def close(self) -> None:
        self.connection.close()

    def _reconnect(self) -> None:
        if self._connection_url is None:
            raise OperationalError("database connection is closed and cannot be reopened")
        import psycopg

        self.connection = psycopg.connect(
            self._connection_url,
            connect_timeout=15,
            application_name="sheperd-research",
        )

    def _execute(
        self, query: str, params: tuple[object, ...] = ()
    ) -> list[tuple[object, ...]]:
        for attempt in range(2):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(query, params)
                    rows = cursor.fetchall() if cursor.description else []
                self.connection.commit()
                return rows
            except OperationalError:
                self.connection.rollback()
                if attempt == 1 or self._connection_url is None:
                    raise
                self.connection.close()
                self._reconnect()
            except Exception:
                self.connection.rollback()
                raise
        raise OperationalError("database operation could not be completed")

    def create_run(self, run_id: str, request: ResearchRunRequest) -> None:
        self._execute(
            """
            INSERT INTO research_runs (
                run_id, topic_set, request, status, as_of, started_at,
                neon_branch_id, migration_version, model_id, prompt_version
            )
            VALUES (%s, %s, %s::jsonb, %s, %s, now(), %s, %s, %s, %s)
            ON CONFLICT (run_id) DO NOTHING
            """,
            (
                run_id,
                request.topic_set,
                json.dumps(request.model_dump(mode="json")),
                RunStatus.RUNNING,
                request.as_of,
                self.neon_branch_id,
                MIGRATION_VERSION,
                request.model,
                "workflow-v2",
            ),
        )

    def record_tool_calls(
        self,
        run_id: str,
        agent_name: str,
        attempt: int,
        lane: str,
        receipts: list[dict[str, object]],
    ) -> None:
        step_rows = self._execute(
            "SELECT step_id FROM agent_steps "
            "WHERE run_id = %s AND agent_name = %s AND attempt = %s",
            (run_id, agent_name, attempt),
        )
        step_id = step_rows[0][0] if step_rows else None
        for receipt in receipts:
            safe_receipt = _redact_audit_receipt(receipt)
            sanitized_args = _sanitized_tool_args(receipt)
            raw_args = receipt.get("sanitized_args")
            urls = raw_args.get("urls") if isinstance(raw_args, dict) else None
            if not isinstance(urls, list):
                urls = receipt.get("urls")
            safe_urls = _safe_audit_urls(urls)
            call_index = safe_receipt.get("call_index", 0)
            if not isinstance(call_index, int) or isinstance(call_index, bool):
                call_index = 0
            input_hash = safe_receipt.get("input_hash")
            if not isinstance(input_hash, str):
                input_hash = content_hash(json.dumps(receipt, sort_keys=True, default=str))
            self._execute(
                """
                INSERT INTO agent_tool_calls (
                    run_id, agent_step_id, agent_name, lane, attempt, call_index,
                    tool_name, query, urls, sanitized_args, input_hash, result_hash,
                    result_count, latency_ms, status, error_code
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (run_id, agent_name, attempt, call_index) DO NOTHING
                """,
                (
                    run_id,
                    step_id,
                    agent_name,
                    lane,
                    attempt,
                    call_index,
                    safe_receipt.get("tool_name", "unknown"),
                    sanitized_args.get("query"),
                    json.dumps(safe_urls),
                    json.dumps(sanitized_args, sort_keys=True),
                    input_hash,
                    safe_receipt.get("result_hash"),
                    safe_receipt.get("result_count"),
                    safe_receipt.get("latency_ms"),
                    safe_receipt.get("status", "unknown"),
                    safe_receipt.get("error_code"),
                ),
            )

    def get_run_tool_calls(self, run_id: str) -> list[dict[str, object]]:
        rows = self._execute(
            """
            SELECT agent_step_id, agent_name, lane, attempt, call_index, tool_name,
                   query, urls, sanitized_args, input_hash, result_hash, result_count,
                   latency_ms, status, error_code, created_at
            FROM agent_tool_calls
            WHERE run_id = %s
            ORDER BY created_at, tool_call_id
            """,
            (run_id,),
        )
        fields = (
            "agent_step_id", "agent_name", "lane", "attempt", "call_index",
            "tool_name", "query", "urls", "sanitized_args", "input_hash",
            "result_hash", "result_count", "latency_ms", "status", "error_code",
            "created_at",
        )
        return [dict(zip(fields, row, strict=True)) for row in rows]

    def update_run_status(
        self, run_id: str, status: RunStatus, error: str | None = None
    ) -> None:
        self._execute(
            """
            UPDATE research_runs
            SET status = %s,
                error = %s,
                archived_at = CASE
                    WHEN %s = 'failed' THEN COALESCE(archived_at, now())
                    ELSE archived_at
                END,
                archive_reason = CASE
                    WHEN %s = 'failed' THEN COALESCE(archive_reason, 'run_failed')
                    ELSE archive_reason
                END,
                completed_at = CASE
                    WHEN %s IN ('succeeded', 'partial', 'failed') THEN now()
                    ELSE completed_at
                END
            WHERE run_id = %s
            """,
            (status, error, status, status, status, run_id),
        )

    def record_step(
        self,
        run_id: str,
        agent_name: str,
        status: str,
        metadata: dict[str, object],
        *,
        lane: str = "system",
        attempt: int = 1,
        duration_ms: int | None = None,
        input_hash: str | None = None,
        output_hash: str | None = None,
        error_code: str | None = None,
    ) -> None:
        safe_metadata = _redact_audit_metadata(metadata)
        call_metadata = safe_metadata.get("call")
        if not isinstance(call_metadata, dict):
            call_metadata = safe_metadata

        def optional_int(name: str) -> int | None:
            value = call_metadata.get(name)
            return value if isinstance(value, int) else None

        self._execute(
            """
            INSERT INTO agent_steps (
                run_id, agent_name, status, metadata, lane, attempt, duration_ms,
                input_hash, output_hash, error_code, requested_model, resolved_model,
                prompt_version, request_id, input_tokens, output_tokens, total_tokens,
                wall_clock_ms, model_index, fallback_reason, tool_calls,
                capability_manifest_hash, required_tools
            )
            VALUES (
                %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (run_id, agent_name, attempt) DO NOTHING
            """,
            (
                run_id,
                agent_name,
                status,
                json.dumps(safe_metadata, default=str),
                lane,
                attempt,
                duration_ms,
                input_hash,
                output_hash,
                error_code,
                call_metadata.get("requested_model"),
                call_metadata.get("resolved_model"),
                call_metadata.get("prompt_version"),
                call_metadata.get("request_id"),
                optional_int("input_tokens"),
                optional_int("output_tokens"),
                optional_int("total_tokens"),
                duration_ms,
                optional_int("model_index"),
                call_metadata.get("fallback_reason"),
                optional_int("tool_calls") or 0,
                call_metadata.get("capability_manifest_hash"),
                json.dumps(call_metadata.get("required_tools", [])),
            ),
        )

    def record_source(
        self, source: SourceCandidate, *, run_id: str | None = None
    ) -> SourceCandidate:
        stored = _seed_safe_source(source)
        normalized = normalize_url(stored.url)
        stored = stored.model_copy(update={"url": normalized})
        rows = self._execute(
            """
            INSERT INTO sources (
                normalized_url, url, title, publisher, published_at, retrieved_at,
                source_kind, snippet, topics, geographies, lane, is_seed, evidence_status,
                region, language_code, language_confidence, authority_tier, catalog_source_id,
                source_type, freshness_status, freshness_days, extraction_status,
                extraction_error_code, normalized_title_en, normalized_snippet_en
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (normalized_url) DO UPDATE SET
                title = EXCLUDED.title,
                publisher = EXCLUDED.publisher,
                published_at = COALESCE(EXCLUDED.published_at, sources.published_at),
                retrieved_at = EXCLUDED.retrieved_at,
                snippet = EXCLUDED.snippet,
                topics = EXCLUDED.topics,
                geographies = EXCLUDED.geographies,
                region = EXCLUDED.region,
                language_code = EXCLUDED.language_code,
                language_confidence = EXCLUDED.language_confidence,
                authority_tier = EXCLUDED.authority_tier,
                catalog_source_id = EXCLUDED.catalog_source_id,
                source_type = EXCLUDED.source_type,
                freshness_status = EXCLUDED.freshness_status,
                freshness_days = EXCLUDED.freshness_days,
                extraction_status = EXCLUDED.extraction_status,
                extraction_error_code = EXCLUDED.extraction_error_code,
                normalized_title_en = EXCLUDED.normalized_title_en,
                normalized_snippet_en = EXCLUDED.normalized_snippet_en,
                lane = CASE
                    WHEN sources.lane = 'unassigned' THEN EXCLUDED.lane
                    ELSE sources.lane
                END,
                source_kind = CASE
                    WHEN sources.is_seed OR EXCLUDED.is_seed THEN 'seed-only'
                    ELSE sources.source_kind
                END,
                is_seed = sources.is_seed OR EXCLUDED.is_seed,
                evidence_status = CASE
                    WHEN sources.is_seed OR EXCLUDED.is_seed THEN 'unverified'
                    ELSE sources.evidence_status
                END
            RETURNING source_kind, is_seed, evidence_status
            """,
            (
                normalized,
                stored.url,
                source.title,
                source.publisher,
                source.published_at,
                source.retrieved_at,
                stored.source_kind,
                stored.snippet,
                stored.topics,
                stored.geographies,
                stored.lane,
                stored.is_seed,
                stored.evidence_status,
                stored.region,
                stored.language_code,
                stored.language_confidence,
                stored.authority_tier,
                stored.catalog_source_id,
                stored.source_type,
                stored.freshness_status,
                stored.freshness_days,
                stored.extraction_status,
                stored.extraction_error_code,
                stored.normalized_title_en,
                stored.normalized_snippet_en,
            ),
        )
        result = stored
        if rows:
            row = rows[0]
            result = stored.model_copy(
                update={
                    "source_kind": cast(str, row[0]),
                    "is_seed": cast(bool, row[1]),
                    "evidence_status": EvidenceStatus(cast(str, row[2])),
                }
            )
        if run_id is not None:
            self._execute(
                """
                INSERT INTO run_sources (
                    run_id, normalized_url, extraction_status, extraction_error_code
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (run_id, normalized_url) DO UPDATE SET
                    extraction_status = EXCLUDED.extraction_status,
                    extraction_error_code = EXCLUDED.extraction_error_code,
                    updated_at = now()
                """,
                (
                    run_id,
                    normalized,
                    stored.extraction_status,
                    stored.extraction_error_code,
                ),
            )
        return result

    def record_snapshot(self, run_id: str, source: SourceCandidate, content: str) -> None:
        self._execute(
            """
            INSERT INTO run_sources (run_id, normalized_url)
            VALUES (%s, %s)
            ON CONFLICT (run_id, normalized_url) DO NOTHING
            """,
            (run_id, normalize_url(source.url)),
        )
        self._execute(
            """
            INSERT INTO source_snapshots (
                run_id, normalized_url, content_hash, content_length, retrieved_at
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (run_id, normalized_url) DO NOTHING
            """,
            (
                run_id,
                normalize_url(source.url),
                content_hash(content),
                len(content),
                source.retrieved_at,
            ),
        )

    def record_distillation(self, run_id: str, distillation: ArticleDistillation) -> None:
        _validate_new_distillation_evidence(distillation)
        distillation_hash = distillation.content_hash or content_hash(
            json.dumps(
                {
                    "summary": distillation.summary,
                    "key_points": distillation.key_points,
                    "entities": distillation.entities,
                    "signals": distillation.signals,
                    "limitations": distillation.limitations,
                    "source_language": distillation.source_language,
                    "summary_original": distillation.summary_original,
                    "key_points_original": distillation.key_points_original,
                    "evidence_excerpts": distillation.evidence_excerpts,
                    "evidence_locators": distillation.evidence_locators,
                    "insight_packet": distillation.insight_packet,
                    "quality_status": distillation.quality_status.value,
                    "quality_issues": distillation.quality_issues,
                },
                sort_keys=True,
            )
        )
        self._execute(
            """
            INSERT INTO article_distillations (
                run_id, normalized_url, summary, key_points, entities, signals, limitations,
                model_id, prompt_version, content_hash, evidence_status, source_language,
                summary_original, key_points_original, translation_status, evidence_excerpts,
                evidence_locators, insight_packet, quality_status, quality_issues
            )
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s,
                    %s, %s, %s::jsonb, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s::jsonb)
            ON CONFLICT (run_id, normalized_url) DO UPDATE SET
                summary = EXCLUDED.summary,
                key_points = EXCLUDED.key_points,
                entities = EXCLUDED.entities,
                signals = EXCLUDED.signals,
                limitations = EXCLUDED.limitations,
                model_id = EXCLUDED.model_id,
                prompt_version = EXCLUDED.prompt_version,
                content_hash = EXCLUDED.content_hash,
                evidence_status = EXCLUDED.evidence_status,
                source_language = EXCLUDED.source_language,
                summary_original = EXCLUDED.summary_original,
                key_points_original = EXCLUDED.key_points_original,
                translation_status = EXCLUDED.translation_status,
                evidence_excerpts = EXCLUDED.evidence_excerpts,
                evidence_locators = EXCLUDED.evidence_locators,
                insight_packet = EXCLUDED.insight_packet,
                quality_status = EXCLUDED.quality_status,
                quality_issues = EXCLUDED.quality_issues
            """,
            (
                run_id,
                normalize_url(distillation.source_url),
                distillation.summary,
                json.dumps(distillation.key_points),
                json.dumps(distillation.entities),
                json.dumps(distillation.signals),
                json.dumps(distillation.limitations),
                distillation.model_id,
                distillation.prompt_version,
                distillation_hash,
                distillation.evidence_status,
                distillation.source_language,
                distillation.summary_original,
                json.dumps(distillation.key_points_original),
                distillation.translation_status,
                json.dumps(distillation.evidence_excerpts),
                json.dumps(distillation.evidence_locators),
                json.dumps(distillation.insight_packet),
                distillation.quality_status.value,
                json.dumps(distillation.quality_issues),
            ),
        )

    def record_claims(self, run_id: str, claims: list[ClaimDraft]) -> None:
        for claim in claims:
            claim_hash = content_hash(
                f"{claim.claim}\n"
                f"{','.join(sorted(normalize_url(url) for url in claim.source_urls))}"
            )
            self._execute(
                """
                INSERT INTO claims (
                    run_id, claim_hash, claim_text, evidence_status, confidence,
                    source_urls, support_locator, conflicts, original_claim, evidence_excerpt,
                    independent_source_count, citation_status, verification_basis
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id, claim_hash) DO NOTHING
                """,
                (
                    run_id,
                    claim_hash,
                    claim.claim,
                    claim.evidence_status,
                    claim.confidence,
                    json.dumps([normalize_url(url) for url in claim.source_urls]),
                    claim.support_locator,
                    json.dumps(claim.conflicts),
                    claim.original_claim,
                    claim.evidence_excerpt,
                    claim.independent_source_count
                    or len(
                        {
                            (urlsplit(normalize_url(url)).hostname or "")
                            .lower()
                            .removeprefix("www.")
                            for url in claim.source_urls
                        }
                    ),
                    claim.citation_status
                    if claim.citation_status != "uncited" or not claim.source_urls
                    else "cited",
                    claim.verification_basis,
                ),
            )

    def record_signal_events(self, events: list[SignalEvent]) -> None:
        for event in events:
            self._execute(
                """
                INSERT INTO signal_events (
                    event_id, run_id, event_type, summary, geographies, ports,
                    carriers, event_at, source_urls, evidence_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.event_type,
                    event.summary,
                    event.geographies,
                    event.ports,
                    event.carriers,
                    event.event_at,
                    json.dumps([normalize_url(url) for url in event.source_urls]),
                    event.evidence_status,
                ),
            )

    def record_brief(self, brief: WeeklyBrief) -> None:
        safe_brief = brief.model_copy(
            update={
                "source_urls": _safe_public_urls(brief.source_urls),
                "executive_bullets": _safe_public_bullets(brief.executive_bullets),
                "developments": _safe_public_bullets(brief.developments),
                "risks": _safe_public_bullets(brief.risks),
                "opportunities": _safe_public_bullets(brief.opportunities),
                "uncertainties": _safe_public_bullets(brief.uncertainties),
            }
        )
        self._execute(
            """
            INSERT INTO weekly_briefs (
                brief_id, run_id, title, covered_from, covered_until, summary,
                signal_event_ids, source_urls, limitations, review_state, evidence_status,
                model_id, prompt_version, content_hash, executive_bullets, developments,
                risks, opportunities, uncertainties, follow_up_questions
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
            ON CONFLICT (brief_id) DO UPDATE SET
                title = EXCLUDED.title,
                summary = EXCLUDED.summary,
                signal_event_ids = EXCLUDED.signal_event_ids,
                source_urls = EXCLUDED.source_urls,
                limitations = EXCLUDED.limitations,
                review_state = EXCLUDED.review_state,
                evidence_status = EXCLUDED.evidence_status,
                model_id = EXCLUDED.model_id,
                prompt_version = EXCLUDED.prompt_version,
                content_hash = EXCLUDED.content_hash,
                executive_bullets = EXCLUDED.executive_bullets,
                developments = EXCLUDED.developments,
                risks = EXCLUDED.risks,
                opportunities = EXCLUDED.opportunities,
                uncertainties = EXCLUDED.uncertainties,
                follow_up_questions = EXCLUDED.follow_up_questions
            """,
            (
                safe_brief.run_id,
                safe_brief.run_id,
                safe_brief.title,
                safe_brief.covered_from,
                safe_brief.covered_until,
                safe_brief.summary,
                json.dumps(safe_brief.signal_event_ids),
                json.dumps(safe_brief.source_urls),
                json.dumps(safe_brief.limitations),
                safe_brief.review_state,
                safe_brief.evidence_status,
                safe_brief.model_id,
                safe_brief.prompt_version,
                safe_brief.content_hash,
                json.dumps([item.model_dump(mode="json") for item in safe_brief.executive_bullets]),
                json.dumps([item.model_dump(mode="json") for item in safe_brief.developments]),
                json.dumps([item.model_dump(mode="json") for item in safe_brief.risks]),
                json.dumps([item.model_dump(mode="json") for item in safe_brief.opportunities]),
                json.dumps([item.model_dump(mode="json") for item in safe_brief.uncertainties]),
                json.dumps(safe_brief.follow_up_questions),
            ),
        )

    def record_validation(self, report: ValidationReport) -> None:
        self._execute(
            """
            INSERT INTO validation_checks (
                run_id, status, source_count, unique_source_count, claim_count,
                cited_claim_count, citation_coverage, lane_coverage, checks,
                model_id, prompt_version, as_of, content_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
                status = EXCLUDED.status,
                source_count = EXCLUDED.source_count,
                unique_source_count = EXCLUDED.unique_source_count,
                claim_count = EXCLUDED.claim_count,
                cited_claim_count = EXCLUDED.cited_claim_count,
                citation_coverage = EXCLUDED.citation_coverage,
                lane_coverage = EXCLUDED.lane_coverage,
                checks = EXCLUDED.checks,
                model_id = EXCLUDED.model_id,
                prompt_version = EXCLUDED.prompt_version,
                as_of = EXCLUDED.as_of,
                content_hash = EXCLUDED.content_hash,
                created_at = now()
            """,
            (
                report.run_id,
                report.status,
                report.source_count,
                report.unique_source_count,
                report.claim_count,
                report.cited_claim_count,
                report.citation_coverage,
                report.lane_coverage,
                json.dumps([check.model_dump(mode="json") for check in report.checks]),
                report.model_id,
                report.prompt_version,
                report.as_of,
                report.content_hash,
            ),
        )
        self._execute(
            """
            UPDATE research_runs
            SET citation_coverage = %s,
                validation_status = %s,
                validation_content_hash = %s,
                archived_at = CASE
                    WHEN %s = 'failed' THEN COALESCE(archived_at, now())
                    ELSE archived_at
                END,
                archive_reason = CASE
                    WHEN %s = 'failed' THEN COALESCE(archive_reason, 'validation_failed')
                    ELSE archive_reason
                END
            WHERE run_id = %s
            """,
            (
                report.citation_coverage,
                report.status,
                report.content_hash,
                report.status,
                report.status,
                report.run_id,
            ),
        )

    def get_validation(self, run_id: str) -> ValidationReport | None:
        rows = self._execute(
            """
            SELECT run_id, status, source_count, unique_source_count, claim_count,
                   cited_claim_count, citation_coverage, lane_coverage, checks,
                   model_id, prompt_version, as_of, content_hash
            FROM validation_checks WHERE run_id = %s
            """,
            (run_id,),
        )
        if not rows:
            return None
        row = rows[0]
        report = ValidationReport.model_validate(
            {
                "run_id": row[0],
                "status": row[1],
                "source_count": row[2],
                "unique_source_count": row[3],
                "claim_count": row[4],
                "cited_claim_count": row[5],
                "citation_coverage": row[6],
                "lane_coverage": row[7] or [],
                "checks": row[8] or [],
                "model_id": row[9],
                "prompt_version": row[10],
                "as_of": row[11],
                "content_hash": row[12],
            }
        )
        return report.model_copy(
            update={"blocking_reasons": validation_blocking_reasons(report)}
        )

    def review_brief(
        self, run_id: str, decision: ReviewState, reviewer: str, notes: str
    ) -> None:
        self._execute(
            "INSERT INTO review_decisions "
            "(run_id, decision, reviewer, notes) VALUES (%s, %s, %s, %s)",
            (run_id, decision, reviewer, notes),
        )
        self._execute(
            "UPDATE weekly_briefs SET review_state = %s WHERE brief_id = %s",
            (decision, run_id),
        )

    def get_brief(self, run_id: str) -> WeeklyBrief | None:
        rows = self._execute(
            """
            SELECT run_id, title, covered_from, covered_until, summary, signal_event_ids,
                   source_urls, limitations, review_state, evidence_status, model_id,
                   prompt_version, content_hash, executive_bullets, developments, risks,
                   opportunities, uncertainties, follow_up_questions
            FROM weekly_briefs WHERE brief_id = %s
            """,
            (run_id,),
        )
        if not rows:
            return None
        row = rows[0]
        return WeeklyBrief(
            run_id=cast(str, row[0]),
            title=cast(str, row[1]),
            covered_from=cast(datetime, row[2]),
            covered_until=cast(datetime, row[3]),
            summary=cast(str, row[4]),
            signal_event_ids=cast(list[str], row[5]),
            source_urls=_safe_public_urls(row[6]),
            limitations=cast(list[str], row[7]),
            review_state=ReviewState(cast(str, row[8])),
            evidence_status=EvidenceStatus(cast(str, row[9])),
            model_id=cast(str, row[10]),
            prompt_version=cast(str, row[11]),
            content_hash=cast(str | None, row[12]),
            executive_bullets=_safe_public_bullets(row[13] or []),
            developments=_safe_public_bullets(row[14] or []),
            risks=_safe_public_bullets(row[15] or []),
            opportunities=_safe_public_bullets(row[16] or []),
            uncertainties=_safe_public_bullets(row[17] or []),
            follow_up_questions=cast(list[str], row[18] or []),
        )

    def get_run(self, run_id: str) -> dict[str, object] | None:
        rows = self._execute(
            "SELECT run_id, topic_set, request, status, as_of, started_at, completed_at, error, "
            "model_id, prompt_version, citation_coverage, validation_status, neon_branch_id, "
            "migration_version, archived_at, archive_reason "
            "FROM research_runs WHERE run_id = %s",
            (run_id,),
        )
        if not rows:
            return None
        row = rows[0]
        return {
            "run_id": row[0],
            "topic_set": row[1],
            "request": row[2],
            "status": row[3],
            "as_of": row[4],
            "started_at": row[5],
            "completed_at": row[6],
            "error": row[7],
            "model_id": row[8],
            "prompt_version": row[9],
            "citation_coverage": row[10],
            "validation_status": row[11],
            "neon_branch_id": row[12],
            "migration_version": row[13],
            "archived_at": row[14],
            "archive_reason": row[15],
        }

    def get_run_sources(self, run_id: str) -> list[SourceCandidate]:
        rows = self._execute(
            """
            SELECT s.url, s.title, s.publisher, s.published_at, s.retrieved_at,
                   s.source_kind, s.snippet, s.topics, s.geographies, s.lane,
                   s.is_seed, s.evidence_status, s.region, s.language_code,
                   s.language_confidence, s.authority_tier, s.catalog_source_id,
                   s.source_type, s.freshness_status, s.freshness_days,
                   rs.extraction_status, rs.extraction_error_code,
                   s.normalized_title_en, s.normalized_snippet_en
            FROM sources s
            JOIN run_sources rs ON rs.normalized_url = s.normalized_url
            WHERE rs.run_id = %s
            ORDER BY s.retrieved_at DESC
            """,
            (run_id,),
        )
        sources: list[SourceCandidate] = []
        for row in rows:
            url = _safe_public_url(row[0])
            if url is None:
                continue
            quality = row[12:] if len(row) >= 24 else ()
            sources.append(
                SourceCandidate(
                    url=url,
                    title=cast(str, row[1]),
                    publisher=cast(str, row[2]),
                    published_at=cast(datetime | None, row[3]),
                    retrieved_at=cast(datetime, row[4]),
                    source_kind=cast(str, row[5]),
                    snippet=cast(str, row[6]),
                    topics=cast(list[str], row[7] or []),
                    geographies=cast(list[str], row[8] or []),
                    lane=cast(str, row[9]),
                    is_seed=cast(bool, row[10]),
                    evidence_status=EvidenceStatus(cast(str, row[11])),
                    region=cast(str, quality[0]) if quality else "global",
                    language_code=cast(str, quality[1]) if quality else "und",
                    language_confidence=_row_float(quality[2]) if quality else 0.0,
                    authority_tier=cast(str, quality[3]) if quality else "unknown",
                    catalog_source_id=cast(str | None, quality[4]) if quality else None,
                    source_type=cast(str, quality[5]) if quality else "unknown",
                    freshness_status=(
                        FreshnessStatus(cast(str, quality[6]))
                        if quality
                        else FreshnessStatus.UNKNOWN
                    ),
                    freshness_days=cast(int | None, quality[7]) if quality else None,
                    extraction_status=(
                        ExtractionStatus(cast(str, quality[8]))
                        if quality
                        else ExtractionStatus.NOT_ATTEMPTED
                    ),
                    extraction_error_code=cast(str | None, quality[9]) if quality else None,
                    normalized_title_en=cast(str | None, quality[10]) if quality else None,
                    normalized_snippet_en=cast(str | None, quality[11]) if quality else None,
                )
            )
        return sources

    def get_run_claims(self, run_id: str) -> list[ClaimDraft]:
        rows = self._execute(
            """
            SELECT claim_text, evidence_status, confidence, source_urls,
                   support_locator, conflicts, original_claim, evidence_excerpt,
                   independent_source_count, citation_status, verification_basis
            FROM claims WHERE run_id = %s ORDER BY created_at, claim_id
            """,
            (run_id,),
        )
        return [
            ClaimDraft(
                claim=cast(str, row[0]),
                evidence_status=EvidenceStatus(cast(str, row[1])),
                confidence=cast(str, row[2]),
                source_urls=_safe_public_urls(row[3] or []),
                support_locator=cast(str | None, row[4]),
                conflicts=cast(list[str], row[5] or []),
                original_claim=cast(str | None, row[6]),
                evidence_excerpt=cast(str | None, row[7]),
                independent_source_count=cast(int, row[8] or 0),
                citation_status=cast(str, row[9]),
                verification_basis=cast(str | None, row[10]),
            )
            for row in rows
        ]

    def get_run_snapshot_hashes(self, run_id: str) -> list[str]:
        rows = self._execute(
            "SELECT content_hash FROM source_snapshots WHERE run_id = %s ORDER BY snapshot_id",
            (run_id,),
        )
        return [cast(str, row[0]) for row in rows]

    def get_run_source_hashes(self, run_id: str) -> dict[str, str]:
        rows = self._execute(
            "SELECT normalized_url, content_hash FROM source_snapshots "
            "WHERE run_id = %s ORDER BY snapshot_id",
            (run_id,),
        )
        return {cast(str, row[0]): cast(str, row[1]) for row in rows}

    def get_run_lane_statuses(self, run_id: str) -> dict[str, str]:
        rows = self._execute(
            "SELECT lane, status FROM agent_steps "
            "WHERE run_id = %s AND agent_name LIKE 'discovery:%%'",
            (run_id,),
        )
        return {cast(str, row[0]): cast(str, row[1]) for row in rows}

    def get_run_steps(self, run_id: str) -> list[dict[str, object]]:
        rows = self._execute(
            """
            SELECT agent_name, status, metadata, lane, attempt, duration_ms,
                   input_hash, output_hash, error_code, created_at, requested_model,
                   resolved_model, prompt_version, request_id, input_tokens, output_tokens,
                   total_tokens, wall_clock_ms, model_index, fallback_reason, tool_calls,
                   capability_manifest_hash, required_tools
            FROM agent_steps WHERE run_id = %s ORDER BY step_id
            """,
            (run_id,),
        )
        return [
            {
                "agent_name": row[0],
                "status": row[1],
                "metadata": row[2],
                "lane": row[3],
                "attempt": row[4],
                "duration_ms": row[5],
                "input_hash": row[6],
                "output_hash": row[7],
                "error_code": row[8],
                "created_at": row[9],
                "requested_model": row[10],
                "resolved_model": row[11],
                "prompt_version": row[12],
                "request_id": row[13],
                "input_tokens": row[14],
                "output_tokens": row[15],
                "total_tokens": row[16],
                "wall_clock_ms": row[17],
                "model_index": row[18],
                "fallback_reason": row[19],
                "tool_calls": row[20],
                "capability_manifest_hash": row[21],
                "required_tools": row[22] or [],
            }
            for row in rows
        ]

    def get_run_distillations(self, run_id: str) -> list[ArticleDistillation]:
        rows = self._execute(
            """
            SELECT ad.normalized_url, ad.summary, ad.key_points, ad.entities, ad.signals,
                   ad.limitations, s.published_at, ad.model_id, ad.prompt_version,
                   ad.evidence_status, ad.content_hash, ad.source_language,
                   ad.summary_original, ad.key_points_original, ad.translation_status,
                   ad.evidence_excerpts, ad.evidence_locators, ad.insight_packet,
                   ad.quality_status, ad.quality_issues
            FROM article_distillations ad
            JOIN sources s ON s.normalized_url = ad.normalized_url
            WHERE ad.run_id = %s ORDER BY ad.distillation_id
            """,
            (run_id,),
        )
        claims_by_url: dict[str, list[ClaimDraft]] = defaultdict(list)
        for claim in self.get_run_claims(run_id):
            for url in claim.source_urls:
                claims_by_url[normalize_url(url)].append(claim)
        return [
            _article_distillation_from_row(
                row,
                claims=claims_by_url.get(cast(str, row[0]), []),
            )
            for row in rows
        ]

    def get_run_signal_events(self, run_id: str) -> list[SignalEvent]:
        rows = self._execute(
            """
            SELECT event_id, event_type, summary, geographies, ports, carriers,
                   event_at, source_urls, evidence_status
            FROM signal_events WHERE run_id = %s ORDER BY created_at, event_id
            """,
            (run_id,),
        )
        return [
            SignalEvent(
                event_id=cast(str, row[0]),
                run_id=run_id,
                event_type=cast(str, row[1]),
                summary=cast(str, row[2]),
                geographies=cast(list[str], row[3] or []),
                ports=cast(list[str], row[4] or []),
                carriers=cast(list[str], row[5] or []),
                event_at=cast(datetime | None, row[6]),
                source_urls=_safe_public_urls(row[7] or []),
                evidence_status=EvidenceStatus(cast(str, row[8])),
            )
            for row in rows
        ]

    def get_trailing_evidence(
        self,
        *,
        topic_set: str,
        since: datetime,
        until: datetime,
        limit: int = 1000,
    ) -> tuple[list[SourceCandidate], list[ArticleDistillation]]:
        bounded_limit = max(1, min(limit, 1000))
        rows = self._execute(
            """
            SELECT ad.run_id, s.url, s.title, s.publisher, s.published_at,
                   s.retrieved_at, s.source_kind, s.snippet, s.topics, s.geographies,
                   s.lane, s.is_seed, s.evidence_status, ad.summary, ad.key_points,
                   ad.entities, ad.signals, ad.limitations, ad.model_id,
                   ad.prompt_version, ad.evidence_status, ad.content_hash,
                   s.region, s.language_code, s.language_confidence, s.authority_tier,
                   s.catalog_source_id, s.source_type, s.freshness_status, s.freshness_days,
                   s.extraction_status, s.extraction_error_code, s.normalized_title_en,
                   s.normalized_snippet_en, ad.source_language, ad.summary_original,
                   ad.key_points_original, ad.translation_status, ad.evidence_excerpts,
                   ad.evidence_locators, ad.insight_packet, ad.quality_status,
                   ad.quality_issues
            FROM article_distillations ad
            JOIN sources s ON s.normalized_url = ad.normalized_url
            JOIN research_runs rr ON rr.run_id = ad.run_id
            WHERE rr.topic_set = %s
              AND NOT s.is_seed
              AND coalesce(s.published_at, rr.as_of) >= %s
              AND coalesce(s.published_at, rr.as_of) <= %s
            ORDER BY coalesce(s.published_at, rr.as_of) DESC, ad.distillation_id
            LIMIT %s
            """,
            (topic_set, since, until, bounded_limit),
        )
        claims_by_run_url: dict[tuple[str, str], list[ClaimDraft]] = defaultdict(list)
        for run_id in {cast(str, row[0]) for row in rows}:
            for claim in self.get_run_claims(run_id):
                for url in claim.source_urls:
                    claims_by_run_url[(run_id, normalize_url(url))].append(claim)

        sources: list[SourceCandidate] = []
        distillations: list[ArticleDistillation] = []
        seen_urls: set[str] = set()
        for row in rows:
            normalized_url = normalize_url(cast(str, row[1]))
            if normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)
            run_id = cast(str, row[0])
            source = SourceCandidate(
                url=normalized_url,
                title=cast(str, row[2]),
                publisher=cast(str, row[3]),
                published_at=cast(datetime | None, row[4]),
                retrieved_at=cast(datetime, row[5]),
                source_kind=cast(str, row[6]),
                snippet=cast(str, row[7]),
                topics=cast(list[str], row[8] or []),
                geographies=cast(list[str], row[9] or []),
                lane=cast(str, row[10]),
                is_seed=cast(bool, row[11]),
                evidence_status=EvidenceStatus(cast(str, row[12])),
                region=cast(str, row[22]),
                language_code=cast(str, row[23]),
                language_confidence=_row_float(row[24]),
                authority_tier=cast(str, row[25]),
                catalog_source_id=cast(str | None, row[26]),
                source_type=cast(str, row[27]),
                freshness_status=FreshnessStatus(cast(str, row[28])),
                freshness_days=cast(int | None, row[29]),
                extraction_status=ExtractionStatus(cast(str, row[30])),
                extraction_error_code=cast(str | None, row[31]),
                normalized_title_en=cast(str | None, row[32]),
                normalized_snippet_en=cast(str | None, row[33]),
            )
            sources.append(source)
            distillations.append(
                _article_distillation_from_row(
                    (
                        row[1],
                        row[13],
                        row[14],
                        row[15],
                        row[16],
                        row[17],
                        row[4],
                        row[18],
                        row[19],
                        row[20],
                        row[21],
                        row[34],
                        row[35],
                        row[36],
                        row[37],
                        row[38],
                        row[39],
                        row[40],
                        row[41],
                        row[42],
                    ),
                    claims=claims_by_run_url.get((run_id, normalized_url), []),
                )
            )
        return sources, distillations

    def list_distillations(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        lane: str | None = None,
        geography: str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ArticleDistillation]:
        clauses = ["TRUE"]
        params: list[object] = []
        if run_id is not None:
            clauses.append("ad.run_id = %s")
            params.append(run_id)
        if query.strip():
            clauses.append("(ad.summary ILIKE %s OR ad.normalized_url ILIKE %s)")
            params.append(f"%{query.strip()}%")
            params.append(f"%{query.strip()}%")
        evidence_value = getattr(evidence_status, "value", evidence_status)
        if evidence_value is not None:
            clauses.append("ad.evidence_status = %s")
            params.append(evidence_value)
        if lane is not None:
            clauses.append("s.lane = %s")
            params.append(lane)
        if geography is not None:
            clauses.append("%s = ANY(s.geographies)")
            params.append(geography)
        if region is not None:
            clauses.append("s.region = %s")
            params.append(region)
        if language is not None:
            clauses.append("ad.source_language = %s")
            params.append(language)
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            """
            SELECT ad.normalized_url, ad.summary, ad.key_points, ad.entities, ad.signals,
                   ad.limitations, s.published_at, ad.model_id, ad.prompt_version,
                   ad.evidence_status, ad.content_hash, ad.source_language,
                   ad.summary_original, ad.key_points_original, ad.translation_status,
                   ad.evidence_excerpts, ad.evidence_locators, ad.insight_packet,
                   ad.quality_status, ad.quality_issues, ad.run_id
            FROM article_distillations ad
            JOIN sources s ON s.normalized_url = ad.normalized_url
            WHERE """
            + " AND ".join(clauses)
            + " ORDER BY ad.created_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        run_ids = sorted({cast(str, row[20]) for row in rows if len(row) > 20})
        claims_by_run_url: dict[tuple[str, str], list[ClaimDraft]] = defaultdict(list)
        if run_ids:
            claim_rows = self._execute(
                "SELECT run_id, claim_text, evidence_status, confidence, source_urls, "
                "support_locator, conflicts, original_claim, evidence_excerpt, "
                "independent_source_count, citation_status, verification_basis "
                "FROM claims WHERE run_id = ANY(%s) ORDER BY created_at, claim_id",
                (run_ids,),
            )
            for row in claim_rows:
                claim = ClaimDraft(
                    claim=cast(str, row[1]),
                    evidence_status=EvidenceStatus(cast(str, row[2])),
                    confidence=cast(str, row[3]),
                    source_urls=_safe_public_urls(row[4] or []),
                    support_locator=cast(str | None, row[5]),
                    conflicts=cast(list[str], row[6] or []),
                    original_claim=cast(str | None, row[7]),
                    evidence_excerpt=cast(str | None, row[8]),
                    independent_source_count=cast(int, row[9] or 0),
                    citation_status=cast(str, row[10]),
                    verification_basis=cast(str | None, row[11]),
                )
                for url in claim.source_urls:
                    claims_by_run_url[(cast(str, row[0]), normalize_url(url))].append(claim)
        return [
            _article_distillation_from_row(
                row,
                claims=claims_by_run_url.get(
                    (cast(str, row[20]), cast(str, row[0])), []
                ),
            )
            for row in rows
        ]

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        verification_basis: str | None = None,
        independent_source_min: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ClaimDraft]:
        clauses = ["TRUE"]
        params: list[object] = []
        if run_id is not None:
            clauses.append("run_id = %s")
            params.append(run_id)
        if query.strip():
            clauses.append("claim_text ILIKE %s")
            params.append(f"%{query.strip()}%")
        expected = getattr(evidence_status, "value", evidence_status)
        if expected is not None:
            clauses.append("evidence_status = %s")
            params.append(expected)
        if verification_basis is not None:
            clauses.append("verification_basis = %s")
            params.append(verification_basis)
        if independent_source_min is not None:
            clauses.append("independent_source_count >= %s")
            params.append(independent_source_min)
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            "SELECT claim_text, evidence_status, confidence, source_urls, "
            "support_locator, conflicts, original_claim, evidence_excerpt, "
            "independent_source_count, citation_status, verification_basis FROM claims WHERE "
            + " AND ".join(clauses)
            + " ORDER BY created_at, claim_id LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            ClaimDraft(
                claim=cast(str, row[0]),
                evidence_status=EvidenceStatus(cast(str, row[1])),
                confidence=cast(str, row[2]),
                source_urls=_safe_public_urls(row[3] or []),
                support_locator=cast(str | None, row[4]),
                conflicts=cast(list[str], row[5] or []),
                original_claim=cast(str | None, row[6]),
                evidence_excerpt=cast(str | None, row[7]),
                independent_source_count=cast(int, row[8] or 0),
                citation_status=cast(str, row[9]),
                verification_basis=cast(str | None, row[10]),
            )
            for row in rows
        ]

    def list_signal_events(
        self,
        *,
        run_id: str | None = None,
        geography: str | None = None,
        event_type: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SignalEvent]:
        clauses = ["TRUE"]
        params: list[object] = []
        if run_id is not None:
            clauses.append("run_id = %s")
            params.append(run_id)
        if geography is not None:
            clauses.append("%s = ANY(geographies)")
            params.append(geography)
        if event_type is not None:
            clauses.append("event_type = %s")
            params.append(event_type)
        evidence_value = getattr(evidence_status, "value", evidence_status)
        if evidence_value is not None:
            clauses.append("evidence_status = %s")
            params.append(evidence_value)
        if region is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM jsonb_array_elements_text(source_urls) u "
                "JOIN sources s ON s.normalized_url = u "
                "WHERE s.region = %s)"
            )
            params.append(region)
        if language is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM jsonb_array_elements_text(source_urls) u "
                "JOIN sources s ON s.normalized_url = u "
                "WHERE s.language_code = %s)"
            )
            params.append(language)
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            "SELECT event_id, run_id, event_type, summary, geographies, ports, carriers, "
            "event_at, source_urls, evidence_status FROM signal_events WHERE "
            + " AND ".join(clauses)
            + " ORDER BY created_at, event_id LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            SignalEvent(
                event_id=cast(str, row[0]),
                run_id=cast(str, row[1]),
                event_type=cast(str, row[2]),
                summary=cast(str, row[3]),
                geographies=cast(list[str], row[4] or []),
                ports=cast(list[str], row[5] or []),
                carriers=cast(list[str], row[6] or []),
                event_at=cast(datetime | None, row[7]),
                source_urls=_safe_public_urls(row[8] or []),
                evidence_status=EvidenceStatus(cast(str, row[9])),
            )
            for row in rows
        ]

    def list_runs(
        self,
        *,
        topic_set: str | None = None,
        status: RunStatus | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        clauses = ["TRUE"]
        params: list[object] = []
        status_value = getattr(status, "value", status)
        if topic_set is not None:
            clauses.append("topic_set = %s")
            params.append(topic_set)
        if status_value is not None:
            clauses.append("status = %s")
            params.append(status_value)
        if since is not None:
            clauses.append("as_of >= %s")
            params.append(since)
        if until is not None:
            clauses.append("as_of <= %s")
            params.append(until)
        params.append(max(1, min(limit, 1000)))
        params.append(max(0, offset))
        rows = self._execute(
            "SELECT run_id, topic_set, status, as_of, started_at, completed_at, error "
            f"FROM research_runs WHERE {' AND '.join(clauses)} "
            "ORDER BY started_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            {
                "run_id": row[0],
                "topic_set": row[1],
                "status": row[2],
                "as_of": row[3],
                "started_at": row[4],
                "completed_at": row[5],
                "error": row[6],
            }
            for row in rows
        ]

    def list_sources(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SourceCandidate]:
        clauses = ["TRUE"]
        params: list[object] = []
        if query.strip():
            clauses.append("search_vector @@ plainto_tsquery('english', %s)")
            params.append(query.strip())
        if geography is not None:
            clauses.append("%s = ANY(geographies)")
            params.append(geography)
        if lane is not None:
            clauses.append("lane = %s")
            params.append(lane)
        if region is not None:
            clauses.append("region = %s")
            params.append(region)
        if language is not None:
            clauses.append("language_code = %s")
            params.append(language)
        if freshness is not None:
            clauses.append("freshness_status = %s")
            params.append(getattr(freshness, "value", freshness))
        if authority_tier is not None:
            clauses.append("authority_tier = %s")
            params.append(authority_tier)
        if source_type is not None:
            clauses.append("source_type = %s")
            params.append(source_type)
        evidence_value = getattr(evidence_status, "value", evidence_status)
        if evidence_value is not None:
            clauses.append("evidence_status = %s")
            params.append(evidence_value)
        if since is not None:
            clauses.append("published_at >= %s")
            params.append(since)
        if until is not None:
            clauses.append("published_at <= %s")
            params.append(until)
        params.append(max(1, min(limit, 1000)))
        params.append(max(0, offset))
        rows = self._execute(
            "SELECT url, title, publisher, published_at, retrieved_at, source_kind, snippet, "
            "topics, geographies, lane, is_seed, evidence_status, region, language_code, "
            "language_confidence, authority_tier, catalog_source_id, source_type, "
            "freshness_status, freshness_days, extraction_status, extraction_error_code, "
            "normalized_title_en, normalized_snippet_en FROM sources "
            f"WHERE {' AND '.join(clauses)} "
            "ORDER BY retrieved_at DESC, normalized_url ASC LIMIT %s OFFSET %s",
            tuple(params),
        )
        sources: list[SourceCandidate] = []
        for row in rows:
            url = _safe_public_url(row[0])
            if url is None:
                continue
            quality = row[12:] if len(row) >= 24 else ()
            sources.append(
                SourceCandidate(
                    url=url,
                    title=cast(str, row[1]),
                    publisher=cast(str, row[2]),
                    published_at=cast(datetime | None, row[3]),
                    retrieved_at=cast(datetime, row[4]),
                    source_kind=cast(str, row[5]),
                    snippet=cast(str, row[6]),
                    topics=cast(list[str], row[7] or []),
                    geographies=cast(list[str], row[8] or []),
                    lane=cast(str, row[9]),
                    is_seed=cast(bool, row[10]),
                    evidence_status=EvidenceStatus(cast(str, row[11])),
                    region=cast(str, quality[0]) if quality else "global",
                    language_code=cast(str, quality[1]) if quality else "und",
                    language_confidence=_row_float(quality[2]) if quality else 0.0,
                    authority_tier=cast(str, quality[3]) if quality else "unknown",
                    catalog_source_id=cast(str | None, quality[4]) if quality else None,
                    source_type=cast(str, quality[5]) if quality else "unknown",
                    freshness_status=(
                        FreshnessStatus(cast(str, quality[6]))
                        if quality
                        else FreshnessStatus.UNKNOWN
                    ),
                    freshness_days=cast(int | None, quality[7]) if quality else None,
                    extraction_status=(
                        ExtractionStatus(cast(str, quality[8]))
                        if quality
                        else ExtractionStatus.NOT_ATTEMPTED
                    ),
                    extraction_error_code=cast(str | None, quality[9]) if quality else None,
                    normalized_title_en=cast(str | None, quality[10]) if quality else None,
                    normalized_snippet_en=cast(str | None, quality[11]) if quality else None,
                )
            )
        return sources

    def list_source_explorer(
        self,
        query: str = "",
        *,
        geography: str | None = None,
        lane: str | None = None,
        evidence_status: EvidenceStatus | str | None = None,
        region: str | None = None,
        language: str | None = None,
        freshness: FreshnessStatus | str | None = None,
        authority_tier: str | None = None,
        source_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, object]:
        clauses = ["TRUE"]
        params: list[object] = []
        if query.strip():
            clauses.append("search_vector @@ plainto_tsquery('english', %s)")
            params.append(query.strip())
        if geography is not None:
            clauses.append("%s = ANY(geographies)")
            params.append(geography)
        if lane is not None:
            clauses.append("lane = %s")
            params.append(lane)
        if region is not None:
            clauses.append("region = %s")
            params.append(region)
        if language is not None:
            clauses.append("language_code = %s")
            params.append(language)
        if freshness is not None:
            clauses.append("freshness_status = %s")
            params.append(getattr(freshness, "value", freshness))
        if authority_tier is not None:
            clauses.append("authority_tier = %s")
            params.append(authority_tier)
        if source_type is not None:
            clauses.append("source_type = %s")
            params.append(source_type)
        evidence_value = getattr(evidence_status, "value", evidence_status)
        if evidence_value is not None:
            clauses.append("evidence_status = %s")
            params.append(evidence_value)
        if since is not None:
            clauses.append("published_at >= %s")
            params.append(since)
        if until is not None:
            clauses.append("published_at <= %s")
            params.append(until)
        where = " AND ".join(clauses)
        total_rows = self._execute(
            f"SELECT count(*) FROM sources WHERE {where}", tuple(params)
        )
        total = cast(int, total_rows[0][0]) if total_rows else 0
        bounded_page = max(1, page)
        bounded_size = max(1, min(page_size, 100))
        sources = self.list_sources(
            query,
            geography=geography,
            lane=lane,
            evidence_status=evidence_status,
            region=region,
            language=language,
            freshness=freshness,
            authority_tier=authority_tier,
            source_type=source_type,
            since=since,
            until=until,
            limit=bounded_size,
            offset=(bounded_page - 1) * bounded_size,
        )
        urls = [normalize_url(source.url) for source in sources]
        snapshots: dict[str, str] = {}
        distillations: dict[str, ArticleDistillation] = {}
        claims_by_url: dict[str, list[ClaimDraft]] = defaultdict(list)
        if urls:
            snapshot_rows = self._execute(
                "SELECT DISTINCT ON (normalized_url) normalized_url, content_hash "
                "FROM source_snapshots WHERE normalized_url = ANY(%s) "
                "ORDER BY normalized_url, snapshot_id DESC",
                (urls,),
            )
            snapshots = {
                cast(str, row[0]): cast(str, row[1]) for row in snapshot_rows
            }
            distillation_rows = self._execute(
                "SELECT DISTINCT ON (ad.normalized_url) ad.normalized_url, ad.summary, "
                "ad.key_points, ad.entities, ad.signals, ad.limitations, s.published_at, "
                "ad.model_id, ad.prompt_version, ad.evidence_status, ad.content_hash, "
                "ad.source_language, ad.summary_original, ad.key_points_original, "
                "ad.translation_status, ad.evidence_excerpts, ad.evidence_locators, "
                "ad.insight_packet, ad.quality_status, ad.quality_issues "
                "FROM article_distillations ad JOIN sources s "
                "ON s.normalized_url = ad.normalized_url "
                "WHERE ad.normalized_url = ANY(%s) "
                "ORDER BY ad.normalized_url, ad.distillation_id DESC",
                (urls,),
            )
            for row in distillation_rows:
                normalized_url = cast(str, row[0])
                distillations[normalized_url] = _article_distillation_from_row(row)
            claim_rows = self._execute(
                "SELECT claim_text, evidence_status, confidence, source_urls, "
                "support_locator, conflicts, original_claim, evidence_excerpt, "
                "independent_source_count, citation_status, verification_basis "
                "FROM claims c WHERE EXISTS (SELECT 1 FROM jsonb_array_elements_text "
                "(c.source_urls) AS source_url(value) WHERE source_url.value = ANY(%s)) "
                "ORDER BY c.created_at, c.claim_id",
                (urls,),
            )
            for row in claim_rows:
                claim = ClaimDraft(
                    claim=cast(str, row[0]),
                    evidence_status=EvidenceStatus(cast(str, row[1])),
                    confidence=cast(str, row[2]),
                    source_urls=_safe_public_urls(row[3] or []),
                    support_locator=cast(str | None, row[4]),
                    conflicts=cast(list[str], row[5] or []),
                    original_claim=cast(str | None, row[6]),
                    evidence_excerpt=cast(str | None, row[7]),
                    independent_source_count=cast(int, row[8] or 0),
                    citation_status=cast(str, row[9]),
                    verification_basis=cast(str | None, row[10]),
                )
                for url in claim.source_urls:
                    normalized_url = normalize_url(url)
                    if normalized_url in urls:
                        claims_by_url[normalized_url].append(claim)
        items: list[dict[str, object]] = []
        for source in sources:
            normalized_url = normalize_url(source.url)
            source_claims = claims_by_url.get(normalized_url, [])
            distillation = distillations.get(normalized_url)
            if distillation is not None:
                distillation = distillation.model_copy(update={"claims": source_claims})
            items.append(
                {
                    "source": source,
                    "distillation": distillation,
                    "claims": source_claims,
                    "source_hash": snapshots.get(normalized_url),
                    "fulfillment": article_fulfillment(
                        source.url,
                        source_persisted=True,
                        extracted=source.extraction_status.value == "succeeded",
                        distillation=distillation,
                        claims=source_claims,
                    ),
                }
            )
        start = (bounded_page - 1) * bounded_size
        return {
            "items": items,
            "page": bounded_page,
            "page_size": bounded_size,
            "total": total,
            "has_more": start + len(items) < total,
        }

    def source_facets(self) -> dict[str, list[str]]:
        columns = {
            "regions": "region",
            "languages": "language_code",
            "freshness": "freshness_status",
            "authority": "authority_tier",
            "source_types": "source_type",
            "lanes": "lane",
            "evidence_states": "evidence_status",
        }
        facets: dict[str, list[str]] = {}
        for name, column in columns.items():
            rows = self._execute(
                f"SELECT DISTINCT {column} FROM sources "
                f"WHERE {column} IS NOT NULL ORDER BY {column}"
            )
            facets[name] = [str(row[0]) for row in rows if row[0]]
        return facets

    def list_briefs(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        archive_scope: ArchiveScope = "active",
    ) -> list[WeeklyBrief]:
        clauses = ["TRUE"]
        params: list[object] = []
        if query.strip():
            clauses.append("search_vector @@ plainto_tsquery('english', %s)")
            params.append(query.strip())
        review_value = getattr(review_state, "value", review_state)
        if review_value is not None:
            clauses.append("wb.review_state = %s")
            params.append(review_value)
        if cadence is not None:
            clauses.append(
                "wb.run_id IN (SELECT run_id FROM research_runs WHERE request ->> 'cadence' = %s)"
            )
            params.append(cadence)
        if since is not None:
            clauses.append("wb.covered_until >= %s")
            params.append(since)
        if until is not None:
            clauses.append("wb.covered_until <= %s")
            params.append(until)
        clauses.append(_archive_scope_clause(archive_scope, "rr.archived_at"))
        params.append(max(1, min(limit, 1000)))
        params.append(max(0, offset))
        rows = self._execute(
            "SELECT wb.brief_id FROM weekly_briefs wb "
            "JOIN research_runs rr ON rr.run_id = wb.run_id "
            f"WHERE {' AND '.join(clauses)} ORDER BY wb.created_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            brief
            for row in rows
            if (brief := self.get_brief(cast(str, row[0]))) is not None
        ]

    def list_brief_summaries(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        cadence: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> list[dict[str, object]]:
        placeholder_values = (
            "''",
            "'null'",
            "'none'",
            "'n/a'",
            "'na'",
            "'not recorded'",
            "'not available'",
            "'tbd'",
            "'to be determined'",
            "'unknown'",
            "'unsupported'",
        )
        placeholders_sql = ", ".join(placeholder_values)

        def text_ok(expression: str) -> str:
            normalized = f"lower(trim(both '.' from trim(coalesce({expression}, ''))))"
            return (
                f"({normalized} NOT IN ({placeholders_sql}) "
                f"AND NOT starts_with({normalized}, 'not recorded ') "
                f"AND NOT starts_with({normalized}, 'not available '))"
            )

        def excerpt_ok(expression: str) -> str:
            return (
                f"({text_ok(expression)} AND length({expression}) <= 320 "
                f"AND array_length(regexp_split_to_array(trim({expression}), E'\\\\s+'), 1) <= 40)"
            )

        locator_ok = text_ok
        evidence_ok = (
            "EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.evidence_excerpts, '[]'::jsonb)) AS ex(value) "
            f"WHERE {excerpt_ok('ex.value')}) "
            "OR EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.evidence_locators, '[]'::jsonb)) AS loc(value) "
            f"WHERE {locator_ok('loc.value')} AND length(loc.value) <= 300)"
        )

        def insight_ok(name: str) -> str:
            insight = f"adq.insight_packet -> '{name}'"
            status = f"{insight} ->> 'status'"
            statement = f"{insight} ->> 'statement'"
            why = f"{insight} ->> 'why_it_matters'"
            next_step = f"{insight} ->> 'next_step'"
            excerpt = f"{insight} ->> 'evidence_excerpt'"
            locator = f"{insight} ->> 'evidence_locator'"
            return (
                f"({status} IN ('supported', 'not_observed') "
                f"AND {text_ok(statement)} "
                f"AND {text_ok(why)} "
                f"AND {text_ok(next_step)} "
                f"AND ({excerpt} IS NULL OR {excerpt_ok(excerpt)}) "
                f"AND ({locator} IS NULL OR ({locator_ok(locator)} AND length({locator}) <= 300)) "
                f"AND ({status} <> 'supported' OR {excerpt_ok(excerpt)} "
                f"OR ({locator_ok(locator)} AND length({locator}) <= 300)))"
            )

        claim_ok = (
            "EXISTS (SELECT 1 FROM claims cq "
            "WHERE cq.run_id = wb.run_id AND cq.source_urls ? adq.normalized_url "
            f"AND {text_ok('cq.claim_text')} "
            f"AND (cq.evidence_excerpt IS NULL OR {excerpt_ok('cq.evidence_excerpt')}) "
            f"AND (cq.support_locator IS NULL OR {locator_ok('cq.support_locator')})) "
            "AND NOT EXISTS (SELECT 1 FROM claims cq_bad "
            "WHERE cq_bad.run_id = wb.run_id AND cq_bad.source_urls ? adq.normalized_url "
            f"AND (NOT {text_ok('cq_bad.claim_text')} "
            "OR (cq_bad.evidence_excerpt IS NOT NULL AND NOT "
            f"{excerpt_ok('cq_bad.evidence_excerpt')}) "
            "OR (cq_bad.support_locator IS NOT NULL AND NOT "
            f"{locator_ok('cq_bad.support_locator')})))"
        )
        what_happened_ok = text_ok("adq.insight_packet ->> 'what_happened'")
        why_it_matters_ok = text_ok("adq.insight_packet ->> 'why_it_matters'")
        article_complete_sql = (
            "COALESCE(adq.quality_status, 'incomplete') = 'complete' "
            f"AND {text_ok('adq.summary')} "
            "AND (SELECT count(*) FROM jsonb_array_elements_text("
            "COALESCE(adq.key_points, '[]'::jsonb)) AS kp(value) "
            f"WHERE {text_ok('kp.value')}) >= 2 "
            f"AND ({evidence_ok}) "
            f"AND {what_happened_ok} "
            f"AND {why_it_matters_ok} "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.insight_packet -> 'uncertainties', '[]'::jsonb)) AS un(value) "
            f"WHERE {text_ok('un.value')}) "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.insight_packet -> 'next_steps', '[]'::jsonb)) AS ns(value) "
            f"WHERE {text_ok('ns.value')}) "
            f"AND {insight_ok('risk_assessment')} "
            f"AND {insight_ok('opportunity_assessment')} "
            f"AND {claim_ok}"
        )
        relationship_issue_sql = (
            "EXISTS (SELECT 1 FROM run_sources rsq "
            "JOIN sources sq ON sq.normalized_url = rsq.normalized_url "
            "WHERE rsq.run_id = wb.run_id AND NOT sq.is_seed "
            "AND rsq.extraction_status <> 'succeeded') "
            "OR EXISTS (SELECT 1 FROM run_sources rsq "
            "JOIN sources sq ON sq.normalized_url = rsq.normalized_url "
            "WHERE rsq.run_id = wb.run_id AND NOT sq.is_seed "
            "AND rsq.extraction_status = 'succeeded' "
            "AND NOT EXISTS (SELECT 1 FROM article_distillations adm "
            "WHERE adm.run_id = wb.run_id AND adm.normalized_url = rsq.normalized_url))"
        )
        incomplete_article_sql = (
            f"({relationship_issue_sql}) OR EXISTS (SELECT 1 FROM article_distillations adq "
            "WHERE adq.run_id = wb.run_id "
            "AND EXISTS (SELECT 1 FROM run_sources rsadq "
            "JOIN sources sadq ON sadq.normalized_url = rsadq.normalized_url "
            "WHERE rsadq.run_id = wb.run_id "
            "AND rsadq.normalized_url = adq.normalized_url "
            "AND NOT sadq.is_seed) "
            f"AND NOT ({article_complete_sql}))"
        )

        def report_section_ok(column: str, *, actionable: bool) -> str:
            array_sql = f"COALESCE(wb.{column}, '[]'::jsonb)"
            action_required = (
                "TRUE"
                if actionable
                else "starts_with(coalesce(wb.prompt_version, ''), 'weekly-brief-v6')"
            )
            bullet_why_ok = text_ok("bullet.value ->> 'why_it_matters'")
            bullet_next_ok = text_ok("bullet.value ->> 'next_step'")
            bullet_text_ok = text_ok("bullet.value ->> 'text'")
            return (
                f"jsonb_array_length({array_sql}) > 0 "
                f"AND NOT EXISTS (SELECT 1 FROM jsonb_array_elements({array_sql}) "
                "AS bullet(value) WHERE "
                f"NOT {bullet_text_ok} "
                "OR jsonb_array_length(COALESCE(bullet.value -> 'source_urls', '[]'::jsonb)) = 0 "
                "OR EXISTS (SELECT 1 FROM jsonb_array_elements_text("
                "COALESCE(bullet.value -> 'source_urls', '[]'::jsonb)) AS url(value) "
                "WHERE NOT EXISTS (SELECT 1 FROM run_sources known "
                "JOIN sources known_source "
                "ON known_source.normalized_url = known.normalized_url "
                "WHERE known.run_id = wb.run_id AND NOT known_source.is_seed "
                "AND known.normalized_url = url.value)) "
                f"OR ({action_required} AND (NOT {bullet_why_ok} OR NOT {bullet_next_ok})))"
            )

        report_section_checks = [
            report_section_ok(
                section,
                actionable=section in ACTIONABLE_REPORT_SECTIONS,
            )
            for section in REPORT_BULLET_SECTIONS
        ]
        report_sections_complete_sql = "(" + " + ".join(
            f"CASE WHEN ({check}) THEN 1 ELSE 0 END"
            for check in report_section_checks
        ) + ")"
        report_section_completeness_sql = "(" + " + ".join(
            f"CASE WHEN ({check}) THEN 1 ELSE 0 END"
            for check in report_section_checks
        ) + f")::numeric / {len(REPORT_BULLET_SECTIONS)}"
        report_complete_sql = (
            f"{report_section_ok('executive_bullets', actionable=False)} "
            f"AND {report_section_ok('developments', actionable=False)} "
            f"AND {report_section_ok('risks', actionable=True)} "
            f"AND {report_section_ok('opportunities', actionable=True)} "
            f"AND {report_section_ok('uncertainties', actionable=True)} "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(wb.follow_up_questions, '[]'::jsonb)) AS question(value) "
            f"WHERE {text_ok('question.value')})"
        )
        ready_sql = (
            "rr.status = 'succeeded' "
            "AND COALESCE(vc.status, 'blocked') = 'pass' "
            "AND EXISTS (SELECT 1 FROM run_sources rs_exists "
            "JOIN sources s_exists ON s_exists.normalized_url = rs_exists.normalized_url "
            "WHERE rs_exists.run_id = wb.run_id AND NOT s_exists.is_seed) "
            f"AND NOT ({incomplete_article_sql}) "
            f"AND {report_complete_sql}"
        )
        blocking_reasons_sql = (
            "ARRAY_REMOVE(ARRAY["
            "CASE WHEN rr.status <> 'succeeded' THEN 'run_not_succeeded' END, "
            "CASE WHEN COALESCE(vc.status, 'blocked') <> 'pass' THEN 'validation_not_passed' END, "
            f"CASE WHEN {incomplete_article_sql} THEN 'incomplete_article_insights' END, "
            f"CASE WHEN NOT ({report_complete_sql}) THEN 'empty_report_section' END"
            "], NULL)"
        )
        clauses = ["TRUE"]
        params: list[object] = []
        if query.strip():
            clauses.append("wb.search_vector @@ plainto_tsquery('english', %s)")
            params.append(query.strip())
        review_value = getattr(review_state, "value", review_state)
        if review_value is not None:
            clauses.append("wb.review_state = %s")
            params.append(review_value)
        if cadence is not None:
            clauses.append("rr.request ->> 'cadence' = %s")
            params.append(cadence)
        if since is not None:
            clauses.append("wb.covered_until >= %s")
            params.append(since)
        if until is not None:
            clauses.append("wb.covered_until <= %s")
            params.append(until)
        clauses.append(_archive_scope_clause(archive_scope, "rr.archived_at"))
        run_status_value = getattr(run_status, "value", run_status)
        if run_status_value is not None:
            clauses.append("rr.status = %s")
            params.append(run_status_value)
        if ready_only:
            clauses.append(f"({ready_sql})")
        bounded_limit = max(1, min(limit, 1000))
        bounded_offset = max(0, offset)
        params.extend((bounded_limit, bounded_offset))
        rows = self._execute(
            f"""
            SELECT wb.run_id, wb.title, wb.covered_from, wb.covered_until,
                   wb.review_state, rr.status, COALESCE(vc.status, 'blocked'),
                   count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed),
                   count(DISTINCT ad.distillation_id),
                   count(DISTINCT c.claim_id), count(DISTINCT se.event_id),
                   COALESCE(
                       array_agg(DISTINCT s.region)
                       FILTER (WHERE s.region IS NOT NULL), '{{}}'
                   ),
                   COALESCE(
                       array_agg(DISTINCT s.language_code)
                       FILTER (WHERE s.language_code IS NOT NULL), '{{}}'
                   ),
                   COALESCE(
                       array_agg(DISTINCT s.lane)
                       FILTER (WHERE s.lane IS NOT NULL), '{{}}'
                   ),
                   COALESCE(
                       array_agg(DISTINCT ad.model_id)
                       FILTER (WHERE ad.model_id IS NOT NULL), '{{}}'
                   ) || ARRAY[wb.model_id],
                   rr.as_of, rr.archived_at, rr.archive_reason,
                   count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed),
                   count(DISTINCT ad.normalized_url) FILTER (
                       WHERE EXISTS (
                           SELECT 1 FROM article_distillations adq
                           WHERE adq.distillation_id = ad.distillation_id
                             AND {article_complete_sql}
                       )
                       AND EXISTS (
                           SELECT 1 FROM run_sources rsa
                           JOIN sources sa ON sa.normalized_url = rsa.normalized_url
                           WHERE rsa.run_id = wb.run_id
                             AND rsa.normalized_url = ad.normalized_url
                             AND NOT sa.is_seed
                       )
                   ),
                   CASE WHEN count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed) > 0
                       THEN round(
                           count(DISTINCT ad.normalized_url) FILTER (
                               WHERE EXISTS (
                                   SELECT 1 FROM article_distillations adq
                                   WHERE adq.distillation_id = ad.distillation_id
                                     AND {article_complete_sql}
                               )
                               AND EXISTS (
                                   SELECT 1 FROM run_sources rsa
                                   JOIN sources sa ON sa.normalized_url = rsa.normalized_url
                                   WHERE rsa.run_id = wb.run_id
                                     AND rsa.normalized_url = ad.normalized_url
                                     AND NOT sa.is_seed
                               )
                           )::numeric
                           / count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed),
                           6
                       )
                       ELSE 0
                   END,
                   {report_sections_complete_sql},
                   {len(REPORT_BULLET_SECTIONS)},
                   CASE WHEN {ready_sql} THEN 'decision_ready' ELSE 'review_required' END,
                   {blocking_reasons_sql},
                   ({ready_sql}),
                   CASE WHEN {len(REPORT_BULLET_SECTIONS)} > 0 THEN
                       round(
                           {report_section_completeness_sql}, 6
                       )
                       ELSE 0
                   END,
                   COALESCE(vc.checks, '[]'::jsonb),
                   CASE WHEN count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed) > 0
                       THEN round(
                           count(DISTINCT ad.normalized_url) FILTER (
                               WHERE EXISTS (
                                   SELECT 1 FROM run_sources rsd
                                   JOIN sources sd ON sd.normalized_url = rsd.normalized_url
                                   WHERE rsd.run_id = wb.run_id
                                     AND rsd.normalized_url = ad.normalized_url
                                     AND NOT sd.is_seed
                               )
                           )::numeric
                           / count(DISTINCT rs.normalized_url) FILTER (WHERE NOT s.is_seed),
                           6
                       )
                       ELSE 0
                   END
            FROM weekly_briefs wb
            JOIN research_runs rr ON rr.run_id = wb.run_id
            LEFT JOIN validation_checks vc ON vc.run_id = wb.run_id
            LEFT JOIN run_sources rs ON rs.run_id = wb.run_id
            LEFT JOIN sources s ON s.normalized_url = rs.normalized_url
            LEFT JOIN article_distillations ad ON ad.run_id = wb.run_id
            LEFT JOIN claims c ON c.run_id = wb.run_id
            LEFT JOIN signal_events se ON se.run_id = wb.run_id
            WHERE """
            + " AND ".join(clauses)
            + " GROUP BY wb.run_id, wb.title, wb.covered_from, wb.covered_until, "
            "wb.review_state, rr.status, vc.status, vc.checks, rr.as_of, wb.model_id, "
            "wb.prompt_version, rr.archived_at, rr.archive_reason, "
            "wb.executive_bullets, wb.developments, "
            "wb.risks, wb.opportunities, wb.uncertainties, wb.follow_up_questions "
            f"ORDER BY CASE WHEN {ready_sql} THEN 0 ELSE 1 END, "
            "wb.covered_until DESC, wb.run_id ASC LIMIT %s OFFSET %s",
            tuple(params),
        )
        fields = (
            "run_id", "title", "covered_from", "covered_until", "review_state",
            "run_status", "validation_status", "source_count", "distillation_count",
            "claim_count", "signal_count", "regions", "languages", "lane_coverage",
            "models", "as_of", "archived_at", "archive_reason", "article_count",
            "complete_article_count",
            "article_insight_completeness", "report_sections_complete", "report_section_count",
            "readiness_status", "blocking_reasons", "decision_ready",
            "report_section_completeness",
        )
        summaries: list[dict[str, object]] = []
        for row in rows:
            raw_summary = dict(zip(fields, row[: len(fields)], strict=True))
            summary = {
                **raw_summary,
                "archived": row[16] is not None,
                "regions": sorted(set(_row_strings(row[11]))),
                "languages": sorted(set(_row_strings(row[12]))),
                "lane_coverage": sorted(set(_row_strings(row[13]))),
                "models": sorted(set(_row_strings(row[14]))),
                "blocking_reasons": sorted(
                    set(_row_strings(raw_summary["blocking_reasons"]))
                ),
                "quality_ready": raw_summary["decision_ready"] is True,
            }
            checks = next(
                (
                    row[index]
                    for index in (len(fields), len(fields) - 1)
                    if len(row) > index and isinstance(row[index], list)
                ),
                [],
            )
            if summary["validation_status"] != ValidationStatus.PASS.value:
                persisted_validation = ValidationReport.model_validate(
                    {
                        "run_id": summary["run_id"],
                        "status": summary["validation_status"],
                        "checks": checks,
                    }
                )
                summary["blocking_reasons"] = sorted(
                    set(cast(list[str], summary["blocking_reasons"]))
                    | set(validation_blocking_reasons(persisted_validation))
                )
            summary["source_distillation_coverage"] = (
                _row_float(row[len(fields) + 1])
                if len(row) > len(fields) + 1
                else _row_float(summary["article_insight_completeness"])
            )
            summaries.append(summary)
        return summaries

    def count_brief_summaries(
        self,
        *,
        cadence: str | None = None,
        review_state: ReviewState | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        run_status: RunStatus | str | None = None,
        ready_only: bool = False,
        archive_scope: ArchiveScope = "active",
    ) -> int:
        placeholder_values = (
            "''",
            "'null'",
            "'none'",
            "'n/a'",
            "'na'",
            "'not recorded'",
            "'not available'",
            "'tbd'",
            "'to be determined'",
            "'unknown'",
            "'unsupported'",
        )
        placeholders_sql = ", ".join(placeholder_values)

        def text_ok(expression: str) -> str:
            normalized = f"lower(trim(both '.' from trim(coalesce({expression}, ''))))"
            return (
                f"({normalized} NOT IN ({placeholders_sql}) "
                f"AND NOT starts_with({normalized}, 'not recorded ') "
                f"AND NOT starts_with({normalized}, 'not available '))"
            )

        def excerpt_ok(expression: str) -> str:
            return (
                f"({text_ok(expression)} AND length({expression}) <= 320 "
                f"AND array_length(regexp_split_to_array(trim({expression}), E'\\\\s+'), 1) <= 40)"
            )

        def insight_ok(name: str) -> str:
            insight = f"adq.insight_packet -> '{name}'"
            status = f"{insight} ->> 'status'"
            statement = f"{insight} ->> 'statement'"
            why = f"{insight} ->> 'why_it_matters'"
            next_step = f"{insight} ->> 'next_step'"
            excerpt = f"{insight} ->> 'evidence_excerpt'"
            locator = f"{insight} ->> 'evidence_locator'"
            return (
                f"({status} IN ('supported', 'not_observed') "
                f"AND {text_ok(statement)} "
                f"AND {text_ok(why)} "
                f"AND {text_ok(next_step)} "
                f"AND ({excerpt} IS NULL OR {excerpt_ok(excerpt)}) "
                f"AND ({locator} IS NULL OR ({text_ok(locator)} AND length({locator}) <= 300)) "
                f"AND ({status} <> 'supported' OR {excerpt_ok(excerpt)} "
                f"OR ({text_ok(locator)} AND length({locator}) <= 300)))"
            )

        evidence_ok = (
            "EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.evidence_excerpts, '[]'::jsonb)) AS ex(value) "
            f"WHERE {excerpt_ok('ex.value')}) "
            "OR EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.evidence_locators, '[]'::jsonb)) AS loc(value) "
            f"WHERE {text_ok('loc.value')} AND length(loc.value) <= 300)"
        )
        claim_ok = (
            "EXISTS (SELECT 1 FROM claims cq "
            "WHERE cq.run_id = wb.run_id AND cq.source_urls ? adq.normalized_url "
            f"AND {text_ok('cq.claim_text')} "
            f"AND (cq.evidence_excerpt IS NULL OR {excerpt_ok('cq.evidence_excerpt')}) "
            f"AND (cq.support_locator IS NULL OR {text_ok('cq.support_locator')})) "
            "AND NOT EXISTS (SELECT 1 FROM claims cq_bad "
            "WHERE cq_bad.run_id = wb.run_id AND cq_bad.source_urls ? adq.normalized_url "
            f"AND (NOT {text_ok('cq_bad.claim_text')} "
            "OR (cq_bad.evidence_excerpt IS NOT NULL AND NOT "
            f"{excerpt_ok('cq_bad.evidence_excerpt')}) "
            f"OR (cq_bad.support_locator IS NOT NULL AND NOT {text_ok('cq_bad.support_locator')})))"
        )
        what_happened_ok = text_ok("adq.insight_packet ->> 'what_happened'")
        why_it_matters_ok = text_ok("adq.insight_packet ->> 'why_it_matters'")
        article_complete_sql = (
            "COALESCE(adq.quality_status, 'incomplete') = 'complete' "
            f"AND {text_ok('adq.summary')} "
            "AND (SELECT count(*) FROM jsonb_array_elements_text("
            "COALESCE(adq.key_points, '[]'::jsonb)) AS kp(value) "
            f"WHERE {text_ok('kp.value')}) >= 2 "
            f"AND ({evidence_ok}) "
            f"AND {what_happened_ok} "
            f"AND {why_it_matters_ok} "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.insight_packet -> 'uncertainties', '[]'::jsonb)) AS un(value) "
            f"WHERE {text_ok('un.value')}) "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(adq.insight_packet -> 'next_steps', '[]'::jsonb)) AS ns(value) "
            f"WHERE {text_ok('ns.value')}) "
            f"AND {insight_ok('risk_assessment')} "
            f"AND {insight_ok('opportunity_assessment')} "
            f"AND {claim_ok}"
        )
        relationship_issue_sql = (
            "EXISTS (SELECT 1 FROM run_sources rsq "
            "JOIN sources sq ON sq.normalized_url = rsq.normalized_url "
            "WHERE rsq.run_id = wb.run_id AND NOT sq.is_seed "
            "AND rsq.extraction_status <> 'succeeded') "
            "OR EXISTS (SELECT 1 FROM run_sources rsq "
            "JOIN sources sq ON sq.normalized_url = rsq.normalized_url "
            "WHERE rsq.run_id = wb.run_id AND NOT sq.is_seed "
            "AND rsq.extraction_status = 'succeeded' "
            "AND NOT EXISTS (SELECT 1 FROM article_distillations adm "
            "WHERE adm.run_id = wb.run_id AND adm.normalized_url = rsq.normalized_url))"
        )
        incomplete_article_sql = (
            f"({relationship_issue_sql}) OR EXISTS (SELECT 1 FROM article_distillations adq "
            "WHERE adq.run_id = wb.run_id "
            "AND EXISTS (SELECT 1 FROM run_sources rsadq "
            "JOIN sources sadq ON sadq.normalized_url = rsadq.normalized_url "
            "WHERE rsadq.run_id = wb.run_id "
            "AND rsadq.normalized_url = adq.normalized_url "
            "AND NOT sadq.is_seed) "
            f"AND NOT ({article_complete_sql}))"
        )

        def report_section_ok(column: str, *, actionable: bool) -> str:
            array_sql = f"COALESCE(wb.{column}, '[]'::jsonb)"
            action_required = (
                "TRUE"
                if actionable
                else "starts_with(coalesce(wb.prompt_version, ''), 'weekly-brief-v6')"
            )
            bullet_why_ok = text_ok("bullet.value ->> 'why_it_matters'")
            bullet_next_ok = text_ok("bullet.value ->> 'next_step'")
            bullet_text_ok = text_ok("bullet.value ->> 'text'")
            return (
                f"jsonb_array_length({array_sql}) > 0 "
                f"AND NOT EXISTS (SELECT 1 FROM jsonb_array_elements({array_sql}) "
                "AS bullet(value) WHERE "
                f"NOT {bullet_text_ok} "
                "OR jsonb_array_length(COALESCE(bullet.value -> 'source_urls', '[]'::jsonb)) = 0 "
                "OR EXISTS (SELECT 1 FROM jsonb_array_elements_text("
                "COALESCE(bullet.value -> 'source_urls', '[]'::jsonb)) AS url(value) "
                "WHERE NOT EXISTS (SELECT 1 FROM run_sources known "
                "JOIN sources known_source "
                "ON known_source.normalized_url = known.normalized_url "
                "WHERE known.run_id = wb.run_id AND NOT known_source.is_seed "
                "AND known.normalized_url = url.value)) "
                f"OR ({action_required} AND (NOT {bullet_why_ok} OR NOT {bullet_next_ok})))"
            )

        report_complete_sql = (
            f"{report_section_ok('executive_bullets', actionable=False)} "
            f"AND {report_section_ok('developments', actionable=False)} "
            f"AND {report_section_ok('risks', actionable=True)} "
            f"AND {report_section_ok('opportunities', actionable=True)} "
            f"AND {report_section_ok('uncertainties', actionable=True)} "
            "AND EXISTS (SELECT 1 FROM jsonb_array_elements_text("
            "COALESCE(wb.follow_up_questions, '[]'::jsonb)) AS question(value) "
            f"WHERE {text_ok('question.value')})"
        )
        ready_sql = (
            "rr.status = 'succeeded' "
            "AND COALESCE(vc.status, 'blocked') = 'pass' "
            "AND EXISTS (SELECT 1 FROM run_sources rs_exists "
            "JOIN sources s_exists ON s_exists.normalized_url = rs_exists.normalized_url "
            "WHERE rs_exists.run_id = wb.run_id AND NOT s_exists.is_seed) "
            f"AND NOT ({incomplete_article_sql}) "
            f"AND {report_complete_sql}"
        )
        clauses = ["TRUE"]
        params: list[object] = []
        if review_state is not None:
            clauses.append("wb.review_state = %s")
            params.append(getattr(review_state, "value", review_state))
        if cadence is not None:
            clauses.append("rr.request ->> 'cadence' = %s")
            params.append(cadence)
        if since is not None:
            clauses.append("wb.covered_until >= %s")
            params.append(since)
        if until is not None:
            clauses.append("wb.covered_until <= %s")
            params.append(until)
        clauses.append(_archive_scope_clause(archive_scope, "rr.archived_at"))
        run_status_value = getattr(run_status, "value", run_status)
        if run_status_value is not None:
            clauses.append("rr.status = %s")
            params.append(run_status_value)
        if ready_only:
            clauses.append(f"({ready_sql})")
        rows = self._execute(
            "SELECT count(*) FROM weekly_briefs wb "
            "JOIN research_runs rr ON rr.run_id = wb.run_id "
            "LEFT JOIN validation_checks vc ON vc.run_id = wb.run_id "
            f"WHERE {' AND '.join(clauses)}",
            tuple(params),
        )
        return cast(int, rows[0][0]) if rows else 0

    def list_regions(self) -> list[str]:
        rows = self._execute("SELECT DISTINCT region FROM sources ORDER BY region")
        return [cast(str, row[0]) for row in rows]

    def region_counts(self, run_id: str | None = None) -> list[dict[str, object]]:
        params: tuple[object, ...] = (run_id,) if run_id is not None else ()
        where = "WHERE ss.run_id = %s" if run_id is not None else ""
        rows = self._execute(
            "SELECT s.region, count(DISTINCT s.normalized_url) "
            "FROM sources s "
            "LEFT JOIN source_snapshots ss ON ss.normalized_url = s.normalized_url "
            f"{where} GROUP BY s.region ORDER BY s.region",
            params,
        )
        return [{"region": row[0], "sources": row[1]} for row in rows]

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        region: str | None = None,
        language: str | None = None,
        evidence: EvidenceStatus | str | None = None,
    ) -> list[dict[str, object]]:
        clauses = ["TRUE"]
        params: list[object] = []
        if since is not None:
            clauses.append("event_rows.event_timestamp >= %s")
            params.append(since)
        if until is not None:
            clauses.append("event_rows.event_timestamp <= %s")
            params.append(until)
        if region is not None:
            clauses.append("event_rows.region = %s")
            params.append(region)
        if language is not None:
            clauses.append("event_rows.language = %s")
            params.append(language)
        if evidence is not None:
            clauses.append("event_rows.evidence_status = %s")
            params.append(getattr(evidence, "value", evidence))
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            "WITH event_rows AS ("
            "SELECT se.event_id, se.run_id, se.event_type, se.evidence_status, "
            "coalesce(se.event_at, se.created_at) AS event_timestamp, "
            "coalesce(se.event_at, se.created_at) AT TIME ZONE 'UTC' AS event_date, "
            "coalesce(nullif(s.lane, ''), 'unknown') AS lane, "
            "coalesce(nullif(s.publisher, ''), 'unknown') AS authority, "
            "coalesce(nullif(s.region, ''), 'unknown') AS region, "
            "coalesce(nullif(s.language_code, ''), 'und') AS language, "
            "CASE WHEN cardinality(se.geographies) > 0 THEN se.geographies "
            "WHEN s.geographies IS NOT NULL THEN s.geographies "
            "ELSE ARRAY['unknown']::text[] END AS geographies "
            "FROM signal_events se "
            "LEFT JOIN LATERAL jsonb_array_elements_text(se.source_urls) AS source_url(value) "
            "ON TRUE "
            "LEFT JOIN sources s ON s.normalized_url = source_url.value"
            ") SELECT date_trunc('month', event_rows.event_date)::date, "
            "event_rows.event_date::date, event_rows.lane, geography.value, "
            "event_rows.authority, event_rows.region, event_rows.language, "
            "event_rows.event_type, event_rows.evidence_status, "
            "count(DISTINCT event_rows.event_id), count(DISTINCT event_rows.run_id) "
            "FROM event_rows "
            "LEFT JOIN LATERAL unnest(event_rows.geographies) AS geography(value) ON TRUE "
            f"WHERE {' AND '.join(clauses)} "
            "GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9 "
            "ORDER BY 2 DESC, 3, 4, 5, 6, 7, 8, 9 LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            {
                "month": row[0].isoformat() if hasattr(row[0], "isoformat") else row[0],
                "date": row[1].isoformat() if hasattr(row[1], "isoformat") else row[1],
                "lane": row[2],
                "geography": row[3] or "unknown",
                "authority": row[4],
                "region": row[5],
                "language": row[6],
                "signal": row[7],
                "evidence": row[8],
                "signals": row[9],
                "runs": row[10],
            }
            for row in rows
        ]

    def health(self) -> dict[str, object]:
        rows = self._execute(
            "SELECT current_database(), current_user, "
            "(SELECT max(version) FROM schema_migrations), current_setting('server_version')"
        )
        if not rows:
            raise RuntimeError("database health query returned no row")
        row = rows[0]
        return {
            "status": "pass",
            "database": row[0],
            "user": row[1],
            "migration_version": row[2] or MIGRATION_VERSION,
            "branch_id": self.neon_branch_id,
            "server_version": row[3],
        }

    def audit_summary(self) -> dict[str, object]:
        rows = self._execute(
            """
            SELECT
                count(*) FILTER (WHERE archived_at IS NULL),
                count(*) FILTER (WHERE archived_at IS NOT NULL),
                count(*) FILTER (WHERE status = 'succeeded'),
                count(*) FILTER (WHERE status = 'partial'),
                count(*) FILTER (WHERE status = 'failed'),
                count(*) FILTER (WHERE validation_status = 'pass'),
                count(*) FILTER (WHERE validation_status = 'partial'),
                count(*) FILTER (WHERE validation_status = 'failed'),
                count(*) FILTER (WHERE validation_status = 'blocked'),
                (SELECT count(*) FROM sources),
                (SELECT count(*) FROM article_distillations),
                (SELECT count(*) FROM claims),
                (SELECT count(*) FROM signal_events),
                (SELECT count(*) FROM validation_checks)
            FROM research_runs
            """
        )
        if not rows:
            raise RuntimeError("audit query returned no row")
        row = rows[0]
        health = self.health()
        quality_rows = self._execute(
            """
            SELECT
                count(*),
                count(*) FILTER (WHERE quality_status = 'complete'),
                count(*) FILTER (WHERE quality_status <> 'complete'),
                (SELECT count(*) FROM weekly_briefs),
                (SELECT count(*) FROM weekly_briefs WHERE
                    jsonb_array_length(COALESCE(executive_bullets, '[]'::jsonb)) > 0
                    AND jsonb_array_length(COALESCE(developments, '[]'::jsonb)) > 0
                    AND jsonb_array_length(COALESCE(risks, '[]'::jsonb)) > 0
                    AND jsonb_array_length(COALESCE(opportunities, '[]'::jsonb)) > 0
                    AND jsonb_array_length(COALESCE(uncertainties, '[]'::jsonb)) > 0
                    AND jsonb_array_length(COALESCE(follow_up_questions, '[]'::jsonb)) > 0)
            FROM article_distillations
            """
        )
        quality = quality_rows[0] if quality_rows else (0, 0, 0, 0, 0)
        quality_counts = [
            int(value) if isinstance(value, int) else 0 for value in quality
        ]
        return {
            "database": health,
            "reports": {
                "active": row[0],
                "archived": row[1],
                "succeeded": row[2],
                "partial": row[3],
                "failed": row[4],
            },
            "records": {
                "sources": row[9],
                "distillations": row[10],
                "claims": row[11],
                "signals": row[12],
            },
            "validation": {
                "pass": row[5],
                "partial": row[6],
                "failed": row[7],
                "blocked": row[8],
                "checks": row[13],
            },
            "quality": {
                "distillations_total": quality_counts[0],
                "distillations_complete": quality_counts[1],
                "distillations_incomplete": quality_counts[2],
                "article_insight_completeness": (
                    round(quality_counts[1] / quality_counts[0], 6)
                    if quality_counts[0]
                    else 0.0
                ),
                "briefs_total": quality_counts[3],
                "briefs_with_complete_sections": quality_counts[4],
                "report_section_completeness": (
                    round(quality_counts[4] / quality_counts[3], 6)
                    if quality_counts[3]
                    else 0.0
                ),
            },
            "migration_version": health.get("migration_version"),
        }


def run_migrations(database_url: str, migrations_dir: Path) -> list[str]:
    import psycopg

    migration_paths = sorted(migrations_dir.glob("*.sql"))
    if not migration_paths:
        raise FileNotFoundError(f"no migrations found in {migrations_dir}")
    with psycopg.connect(
        database_url,
        connect_timeout=15,
        application_name="sheperd-research-migrate",
    ) as connection:
        applied_names: list[str] = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            cursor.execute("SELECT version FROM schema_migrations")
            applied = {cast(str, row[0]) for row in cursor.fetchall()}
            for migration_path in migration_paths:
                if migration_path.stem in applied:
                    continue
                cursor.execute(migration_path.read_text(encoding="utf-8"))
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (migration_path.stem,),
                )
                applied_names.append(migration_path.name)
        connection.commit()
    return applied_names


def run_migration(database_url: str, migration_path: Path) -> None:
    """Apply one migration for backwards-compatible local tooling."""
    import psycopg

    with psycopg.connect(
        database_url,
        connect_timeout=15,
        application_name="sheperd-research-migrate",
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(migration_path.read_text(encoding="utf-8"))
        connection.commit()
