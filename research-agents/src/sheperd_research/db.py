from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Protocol, cast

from psycopg import Connection, OperationalError

from .contracts import (
    ArticleDistillation,
    ClaimDraft,
    EvidenceStatus,
    ReportBullet,
    ResearchRunRequest,
    ReviewState,
    RunStatus,
    SignalEvent,
    SourceCandidate,
    ValidationReport,
    WeeklyBrief,
)
from .validators import content_hash, normalize_url

MIGRATION_VERSION = "0008_audit_surfaces"


def _sanitized_tool_args(receipt: dict[str, object]) -> dict[str, object]:
    """Keep the small allow-list of tool arguments needed for audit display."""
    raw_args = receipt.get("sanitized_args")
    args = raw_args if isinstance(raw_args, dict) else receipt
    sanitized: dict[str, object] = {}
    query = args.get("query")
    if isinstance(query, str):
        sanitized["query"] = query[:400]
    url_count = args.get("url_count")
    if isinstance(url_count, int) and not isinstance(url_count, bool):
        sanitized["url_count"] = max(0, url_count)
    urls = args.get("urls")
    if isinstance(urls, list) and "url_count" not in sanitized:
        sanitized["url_count"] = len(urls)
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
        limit: int = 100,
        offset: int = 0,
    ) -> list[ArticleDistillation]: ...

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
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
        limit: int = 100,
        offset: int = 0,
    ) -> list[SignalEvent]: ...

    def record_source(self, source: SourceCandidate) -> SourceCandidate: ...

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

    def get_run_lane_statuses(self, run_id: str) -> dict[str, str]: ...

    def get_run_steps(self, run_id: str) -> list[dict[str, object]]: ...

    def get_run_distillations(self, run_id: str) -> list[ArticleDistillation]: ...

    def get_run_signal_events(self, run_id: str) -> list[SignalEvent]: ...

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
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SourceCandidate]: ...

    def list_briefs(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WeeklyBrief]: ...

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]: ...

    def health(self) -> dict[str, object]: ...


class InMemoryRepository:
    """Offline repository used by tests and provider-free local development."""

    def __init__(self) -> None:
        self.runs: dict[str, dict[str, object]] = {}
        self.steps: list[dict[str, object]] = []
        self.sources: dict[str, SourceCandidate] = {}
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
            },
        )

    def update_run_status(
        self, run_id: str, status: RunStatus, error: str | None = None
    ) -> None:
        self.runs.setdefault(run_id, {})["status"] = status
        self.runs[run_id]["error"] = error

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
        call_metadata = metadata.get("call")
        if not isinstance(call_metadata, dict):
            call_metadata = metadata
        record: dict[str, object] = {
            "run_id": run_id,
            "agent_name": agent_name,
            "status": status,
            "metadata": metadata,
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
        else:
            existing.update(record)

    def record_source(self, source: SourceCandidate) -> SourceCandidate:
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
        return self.sources[normalized]

    def record_tool_calls(
        self,
        run_id: str,
        agent_name: str,
        attempt: int,
        lane: str,
        receipts: list[dict[str, object]],
    ) -> None:
        for receipt in receipts:
            call_index = receipt.get("call_index", 0)
            record = {
                "run_id": run_id,
                "agent_name": agent_name,
                "attempt": attempt,
                "lane": lane,
                "call_index": call_index,
                "tool_name": receipt.get("tool_name", "unknown"),
                "sanitized_args": _sanitized_tool_args(receipt),
                "input_hash": receipt.get("input_hash"),
                "result_hash": receipt.get("result_hash"),
                "result_count": receipt.get("result_count"),
                "latency_ms": receipt.get("latency_ms"),
                "status": receipt.get("status", "unknown"),
                "error_code": receipt.get("error_code"),
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
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
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
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def record_snapshot(self, run_id: str, source: SourceCandidate, content: str) -> None:
        normalized = normalize_url(source.url)
        self.source_snapshots[(run_id, normalized)] = {
            "run_id": run_id,
            "url": normalized,
            "content_hash": content_hash(content),
            "content_length": len(content),
        }

    def record_distillation(self, run_id: str, distillation: ArticleDistillation) -> None:
        self.distillations[(run_id, normalize_url(distillation.source_url))] = distillation

    def record_claims(self, run_id: str, claims: list[ClaimDraft]) -> None:
        for claim in claims:
            key = (
                run_id,
                claim.claim,
                tuple(sorted(normalize_url(url) for url in claim.source_urls)),
            )
            self.claims.setdefault(key, claim)

    def record_brief(self, brief: WeeklyBrief) -> None:
        self.briefs[brief.run_id] = brief

    def record_validation(self, report: ValidationReport) -> None:
        self.validations[report.run_id] = report

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
        urls = [url for current_run, url in self.source_snapshots if current_run == run_id]
        return [self.sources[url] for url in urls if url in self.sources]

    def get_run_claims(self, run_id: str) -> list[ClaimDraft]:
        return [claim for key, claim in self.claims.items() if key[0] == run_id]

    def get_run_snapshot_hashes(self, run_id: str) -> list[str]:
        return [
            str(snapshot["content_hash"])
            for (current_run, _), snapshot in self.source_snapshots.items()
            if current_run == run_id
        ]

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
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WeeklyBrief]:
        needle = query.lower().strip()
        expected_review = getattr(review_state, "value", review_state)
        values = [
            brief
            for brief in self.briefs.values()
            if (not needle or needle in f"{brief.title} {brief.summary}".lower())
            and (expected_review is None or brief.review_state.value == expected_review)
            and (since is None or brief.covered_until >= since)
            and (until is None or brief.covered_until <= until)
        ]
        bounded_limit = max(1, min(limit, 1000))
        return values[max(0, offset) : max(0, offset) + bounded_limit]

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        buckets: dict[str, dict[str, object]] = {}
        for event in self.signal_events.values():
            event_at = event.event_at or self.runs.get(event.run_id, {}).get("started_at")
            if not isinstance(event_at, datetime):
                continue
            if since is not None and event_at < since:
                continue
            if until is not None and event_at > until:
                continue
            month = event_at.strftime("%Y-%m-01")
            bucket = buckets.setdefault(
                month,
                {"month": month, "signals": 0, "runs": set(), "geographies": set()},
            )
            bucket["signals"] = cast(int, bucket["signals"]) + 1
            cast_runs = bucket["runs"]
            cast_geographies = bucket["geographies"]
            if isinstance(cast_runs, set):
                cast_runs.add(event.run_id)
            if isinstance(cast_geographies, set):
                cast_geographies.update(event.geographies)
        values = [
            {
                "month": month,
                "signals": cast(int, bucket["signals"]),
                "runs": len(bucket["runs"]) if isinstance(bucket["runs"], set) else 0,
                "geographies": sorted(bucket["geographies"])
                if isinstance(bucket["geographies"], set)
                else [],
            }
            for month, bucket in sorted(buckets.items(), reverse=True)
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
                if attempt == 1 or self._connection_url is None:
                    raise
                self.connection.close()
                self._reconnect()
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
            sanitized_args = _sanitized_tool_args(receipt)
            urls = receipt.get("urls")
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
                    receipt.get("call_index", 0),
                    receipt.get("tool_name", "unknown"),
                    sanitized_args.get("query"),
                    json.dumps(urls if isinstance(urls, list) else []),
                    json.dumps(sanitized_args, sort_keys=True),
                    receipt.get("input_hash", content_hash(json.dumps(receipt, sort_keys=True))),
                    receipt.get("result_hash"),
                    receipt.get("result_count"),
                    receipt.get("latency_ms"),
                    receipt.get("status", "unknown"),
                    receipt.get("error_code"),
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
                completed_at = CASE
                    WHEN %s IN ('succeeded', 'partial', 'failed') THEN now()
                    ELSE completed_at
                END
            WHERE run_id = %s
            """,
            (status, error, status, run_id),
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
        call_metadata = metadata.get("call")
        if not isinstance(call_metadata, dict):
            call_metadata = metadata

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
            ON CONFLICT (run_id, agent_name, attempt) DO UPDATE SET
                status = EXCLUDED.status,
                metadata = EXCLUDED.metadata,
                lane = EXCLUDED.lane,
                duration_ms = EXCLUDED.duration_ms,
                input_hash = EXCLUDED.input_hash,
                output_hash = EXCLUDED.output_hash,
                error_code = EXCLUDED.error_code,
                requested_model = EXCLUDED.requested_model,
                resolved_model = EXCLUDED.resolved_model,
                prompt_version = EXCLUDED.prompt_version,
                request_id = EXCLUDED.request_id,
                input_tokens = EXCLUDED.input_tokens,
                output_tokens = EXCLUDED.output_tokens,
                total_tokens = EXCLUDED.total_tokens,
                wall_clock_ms = EXCLUDED.wall_clock_ms,
                model_index = EXCLUDED.model_index,
                fallback_reason = EXCLUDED.fallback_reason,
                tool_calls = EXCLUDED.tool_calls,
                capability_manifest_hash = EXCLUDED.capability_manifest_hash,
                required_tools = EXCLUDED.required_tools
            """,
            (
                run_id,
                agent_name,
                status,
                json.dumps(metadata, default=str),
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

    def record_source(self, source: SourceCandidate) -> SourceCandidate:
        stored = _seed_safe_source(source)
        normalized = normalize_url(stored.url)
        rows = self._execute(
            """
            INSERT INTO sources (
                normalized_url, url, title, publisher, published_at, retrieved_at,
                source_kind, snippet, topics, geographies, lane, is_seed, evidence_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (normalized_url) DO UPDATE SET
                title = EXCLUDED.title,
                publisher = EXCLUDED.publisher,
                published_at = COALESCE(EXCLUDED.published_at, sources.published_at),
                retrieved_at = EXCLUDED.retrieved_at,
                snippet = EXCLUDED.snippet,
                topics = EXCLUDED.topics,
                geographies = EXCLUDED.geographies,
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
                source.url,
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
            ),
        )
        if not rows:
            return stored
        row = rows[0]
        return stored.model_copy(
            update={
                "source_kind": cast(str, row[0]),
                "is_seed": cast(bool, row[1]),
                "evidence_status": EvidenceStatus(cast(str, row[2])),
            }
        )

    def record_snapshot(self, run_id: str, source: SourceCandidate, content: str) -> None:
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
        distillation_hash = distillation.content_hash or content_hash(
            json.dumps(
                {
                    "summary": distillation.summary,
                    "key_points": distillation.key_points,
                    "entities": distillation.entities,
                    "signals": distillation.signals,
                    "limitations": distillation.limitations,
                },
                sort_keys=True,
            )
        )
        self._execute(
            """
            INSERT INTO article_distillations (
                run_id, normalized_url, summary, key_points, entities, signals, limitations,
                model_id, prompt_version, content_hash, evidence_status
            )
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s)
            ON CONFLICT (run_id, normalized_url) DO UPDATE SET
                summary = EXCLUDED.summary,
                key_points = EXCLUDED.key_points,
                entities = EXCLUDED.entities,
                signals = EXCLUDED.signals,
                limitations = EXCLUDED.limitations,
                model_id = EXCLUDED.model_id,
                prompt_version = EXCLUDED.prompt_version,
                content_hash = EXCLUDED.content_hash,
                evidence_status = EXCLUDED.evidence_status
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
                    source_urls, support_locator, conflicts
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)
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
                brief.run_id,
                brief.run_id,
                brief.title,
                brief.covered_from,
                brief.covered_until,
                brief.summary,
                json.dumps(brief.signal_event_ids),
                json.dumps([normalize_url(url) for url in brief.source_urls]),
                json.dumps(brief.limitations),
                brief.review_state,
                brief.evidence_status,
                brief.model_id,
                brief.prompt_version,
                brief.content_hash,
                json.dumps([item.model_dump(mode="json") for item in brief.executive_bullets]),
                json.dumps([item.model_dump(mode="json") for item in brief.developments]),
                json.dumps([item.model_dump(mode="json") for item in brief.risks]),
                json.dumps([item.model_dump(mode="json") for item in brief.opportunities]),
                json.dumps([item.model_dump(mode="json") for item in brief.uncertainties]),
                json.dumps(brief.follow_up_questions),
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
                content_hash = EXCLUDED.content_hash
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
                validation_content_hash = %s
            WHERE run_id = %s
            """,
            (report.citation_coverage, report.status, report.content_hash, report.run_id),
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
        return ValidationReport.model_validate(
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
            source_urls=cast(list[str], row[6]),
            limitations=cast(list[str], row[7]),
            review_state=ReviewState(cast(str, row[8])),
            evidence_status=EvidenceStatus(cast(str, row[9])),
            model_id=cast(str, row[10]),
            prompt_version=cast(str, row[11]),
            content_hash=cast(str | None, row[12]),
            executive_bullets=[
                ReportBullet.model_validate(item)
                for item in cast(list[dict[str, object]], row[13] or [])
            ],
            developments=[
                ReportBullet.model_validate(item)
                for item in cast(list[dict[str, object]], row[14] or [])
            ],
            risks=[
                ReportBullet.model_validate(item)
                for item in cast(list[dict[str, object]], row[15] or [])
            ],
            opportunities=[
                ReportBullet.model_validate(item)
                for item in cast(list[dict[str, object]], row[16] or [])
            ],
            uncertainties=[
                ReportBullet.model_validate(item)
                for item in cast(list[dict[str, object]], row[17] or [])
            ],
            follow_up_questions=cast(list[str], row[18] or []),
        )

    def get_run(self, run_id: str) -> dict[str, object] | None:
        rows = self._execute(
            "SELECT run_id, topic_set, request, status, as_of, started_at, completed_at, error, "
            "model_id, prompt_version, citation_coverage, validation_status, neon_branch_id, "
            "migration_version "
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
        }

    def get_run_sources(self, run_id: str) -> list[SourceCandidate]:
        rows = self._execute(
            """
            SELECT s.url, s.title, s.publisher, s.published_at, s.retrieved_at,
                   s.source_kind, s.snippet, s.topics, s.geographies, s.lane,
                   s.is_seed, s.evidence_status
            FROM sources s
            JOIN source_snapshots ss ON ss.normalized_url = s.normalized_url
            WHERE ss.run_id = %s
            ORDER BY s.retrieved_at DESC
            """,
            (run_id,),
        )
        return [
            SourceCandidate(
                url=cast(str, row[0]),
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
            )
            for row in rows
        ]

    def get_run_claims(self, run_id: str) -> list[ClaimDraft]:
        rows = self._execute(
            """
            SELECT claim_text, evidence_status, confidence, source_urls,
                   support_locator, conflicts
            FROM claims WHERE run_id = %s ORDER BY created_at, claim_id
            """,
            (run_id,),
        )
        return [
            ClaimDraft(
                claim=cast(str, row[0]),
                evidence_status=EvidenceStatus(cast(str, row[1])),
                confidence=cast(str, row[2]),
                source_urls=cast(list[str], row[3] or []),
                support_locator=cast(str | None, row[4]),
                conflicts=cast(list[str], row[5] or []),
            )
            for row in rows
        ]

    def get_run_snapshot_hashes(self, run_id: str) -> list[str]:
        rows = self._execute(
            "SELECT content_hash FROM source_snapshots WHERE run_id = %s ORDER BY snapshot_id",
            (run_id,),
        )
        return [cast(str, row[0]) for row in rows]

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
                   ad.evidence_status, ad.content_hash
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
            ArticleDistillation(
                source_url=cast(str, row[0]),
                summary=cast(str, row[1]),
                key_points=cast(list[str], row[2] or []),
                entities=cast(list[str], row[3] or []),
                signals=cast(list[str], row[4] or []),
                claims=claims_by_url.get(cast(str, row[0]), []),
                limitations=cast(list[str], row[5] or []),
                published_at=cast(datetime | None, row[6]),
                model_id=cast(str, row[7]),
                prompt_version=cast(str, row[8]),
                evidence_status=EvidenceStatus(cast(str, row[9])),
                content_hash=cast(str | None, row[10]),
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
                source_urls=cast(list[str], row[7] or []),
                evidence_status=EvidenceStatus(cast(str, row[8])),
            )
            for row in rows
        ]

    def list_distillations(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
        lane: str | None = None,
        geography: str | None = None,
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
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            """
            SELECT ad.normalized_url, ad.summary, ad.key_points, ad.entities, ad.signals,
                   ad.limitations, s.published_at, ad.model_id, ad.prompt_version,
                   ad.evidence_status, ad.content_hash
            FROM article_distillations ad
            JOIN sources s ON s.normalized_url = ad.normalized_url
            WHERE """
            + " AND ".join(clauses)
            + " ORDER BY ad.created_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            ArticleDistillation(
                source_url=cast(str, row[0]),
                summary=cast(str, row[1]),
                key_points=cast(list[str], row[2] or []),
                entities=cast(list[str], row[3] or []),
                signals=cast(list[str], row[4] or []),
                limitations=cast(list[str], row[5] or []),
                published_at=cast(datetime | None, row[6]),
                model_id=cast(str, row[7]),
                prompt_version=cast(str, row[8]),
                evidence_status=EvidenceStatus(cast(str, row[9])),
                content_hash=cast(str | None, row[10]),
            )
            for row in rows
        ]

    def list_claims(
        self,
        *,
        run_id: str | None = None,
        query: str = "",
        evidence_status: EvidenceStatus | str | None = None,
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
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            "SELECT claim_text, evidence_status, confidence, source_urls, "
            "support_locator, conflicts FROM claims WHERE "
            + " AND ".join(clauses)
            + " ORDER BY created_at, claim_id LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            ClaimDraft(
                claim=cast(str, row[0]),
                evidence_status=EvidenceStatus(cast(str, row[1])),
                confidence=cast(str, row[2]),
                source_urls=cast(list[str], row[3] or []),
                support_locator=cast(str | None, row[4]),
                conflicts=cast(list[str], row[5] or []),
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
                source_urls=cast(list[str], row[8] or []),
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
            "topics, geographies, lane, is_seed, evidence_status FROM sources "
            f"WHERE {' AND '.join(clauses)} ORDER BY retrieved_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            SourceCandidate(
                url=cast(str, row[0]),
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
            )
            for row in rows
        ]

    def list_briefs(
        self,
        query: str = "",
        *,
        review_state: ReviewState | str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[WeeklyBrief]:
        clauses = ["TRUE"]
        params: list[object] = []
        if query.strip():
            clauses.append("search_vector @@ plainto_tsquery('english', %s)")
            params.append(query.strip())
        review_value = getattr(review_state, "value", review_state)
        if review_value is not None:
            clauses.append("review_state = %s")
            params.append(review_value)
        if since is not None:
            clauses.append("covered_until >= %s")
            params.append(since)
        if until is not None:
            clauses.append("covered_until <= %s")
            params.append(until)
        params.append(max(1, min(limit, 1000)))
        params.append(max(0, offset))
        rows = self._execute(
            "SELECT brief_id FROM weekly_briefs "
            f"WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            brief
            for row in rows
            if (brief := self.get_brief(cast(str, row[0]))) is not None
        ]

    def monthly_rollup(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        clauses = ["TRUE"]
        params: list[object] = []
        if since is not None:
            clauses.append("coalesce(se.event_at, se.created_at) >= %s")
            params.append(since)
        if until is not None:
            clauses.append("coalesce(se.event_at, se.created_at) <= %s")
            params.append(until)
        params.extend((max(1, min(limit, 1000)), max(0, offset)))
        rows = self._execute(
            "SELECT date_trunc('month', coalesce(se.event_at, se.created_at))::date, "
            "count(DISTINCT se.event_id), count(DISTINCT se.run_id), "
            "array_agg(DISTINCT geography.value) FILTER (WHERE geography.value IS NOT NULL) "
            "FROM signal_events se "
            "LEFT JOIN LATERAL unnest(se.geographies) AS geography(value) ON TRUE "
            f"WHERE {' AND '.join(clauses)} "
            "GROUP BY 1 ORDER BY 1 DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        return [
            {
                "month": row[0],
                "signals": row[1],
                "runs": row[2],
                "geographies": row[3] or [],
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
