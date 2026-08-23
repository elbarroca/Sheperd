from __future__ import annotations

from collections import Counter
from datetime import datetime
from decimal import Decimal
from html import escape

from fastapi import FastAPI, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, Response

from .contracts import ValidationReport, ValidationStatus, WeeklyBrief
from .db import ArchiveScope, RepositoryProtocol
from .exporters.obsidian import render_weekly_markdown
from .source_catalog import load_source_catalog
from .validation import validation_blocking_reasons
from .validators import quality_metrics


def _value(value: object) -> str:
    return escape(str(value))


def _layout(title: str, body: str) -> str:
    styles = """
body {
  font: 16px/1.5 system-ui, sans-serif;
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1rem;
  color: #172033;
  background: #f7f8fb;
}
a { color: #1558a6; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td {
  padding: .65rem;
  border-bottom: 1px solid #e4e7ec;
  text-align: left;
  vertical-align: top;
}
.muted { color: #667085; }
.card {
  background: white;
  padding: 1rem;
  margin: 1rem 0;
  border: 1px solid #e4e7ec;
  border-radius: .5rem;
}
nav { display: flex; gap: 1rem; margin-bottom: 2rem; }
code { font-size: .9em; }
"""
    return (
        "<!doctype html><html lang='en'><head>"
        "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{_value(title)} · SheperD Research</title>"
        f"<style>{styles}</style></head><body>"
        "<nav><a href='/'>Runs</a><a href='/sources'>Sources</a>"
        f"<a href='/briefs'>Briefs</a></nav>{body}</body></html>"
    )


_PUBLIC_STEP_FIELDS = (
    "agent_name",
    "status",
    "lane",
    "attempt",
    "duration_ms",
    "wall_clock_ms",
    "error_code",
    "input_hash",
    "output_hash",
    "requested_model",
    "resolved_model",
    "prompt_version",
    "request_id",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "model_index",
    "fallback_reason",
    "tool_calls",
    "capability_manifest_hash",
    "required_tools",
    "created_at",
)
_PUBLIC_TOOL_FIELDS = (
    "agent_step_id",
    "agent_name",
    "lane",
    "attempt",
    "call_index",
    "tool_name",
    "sanitized_args",
    "input_hash",
    "result_hash",
    "result_count",
    "latency_ms",
    "status",
    "error_code",
    "created_at",
)
_PUBLIC_RUN_FIELDS = (
    "run_id",
    "topic_set",
    "status",
    "as_of",
    "error",
    "neon_branch_id",
    "migration_version",
    "archived_at",
    "archive_reason",
)


def _archive_visible(
    run: dict[str, object] | None,
    archive_scope: ArchiveScope,
) -> bool:
    if archive_scope not in {"active", "archived", "all"}:
        raise ValueError("archive_scope must be active, archived, or all")
    if run is None:
        return False
    archived = run.get("archived_at") is not None
    return archive_scope == "all" or archived == (archive_scope == "archived")


def _public_steps(steps: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {key: step.get(key) for key in _PUBLIC_STEP_FIELDS if key in step}
        for step in steps
    ]


def _public_tool_calls(calls: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {key: call.get(key) for key in _PUBLIC_TOOL_FIELDS if key in call}
        for call in calls
    ]


def _public_run(run: dict[str, object] | None) -> dict[str, object] | None:
    """Project a run for public responses without exposing its request payload."""
    if run is None:
        return None
    public_run = {
        key: run[key]
        for key in _PUBLIC_RUN_FIELDS
        if key in run and key != "topic_set"
    }
    topic_set = run.get("topic_set")
    if not isinstance(topic_set, str):
        request = run.get("request")
        topic_set = getattr(request, "topic_set", None)
    if isinstance(topic_set, str):
        public_run["topic_set"] = topic_set
    public_run["archived"] = run.get("archived_at") is not None
    return public_run


def _readiness(
    run: dict[str, object] | None,
    validation: ValidationReport | None,
    quality: dict[str, object],
) -> dict[str, object]:
    raw_reasons = quality.get("blocking_reasons", [])
    reasons = (
        {item for item in raw_reasons if isinstance(item, str)}
        if isinstance(raw_reasons, list)
        else set()
    )
    if validation is None:
        reasons.add("missing_validation")
    elif validation.status is not ValidationStatus.PASS:
        reasons.update(validation_blocking_reasons(validation))
    if run is None or run.get("status") != "succeeded":
        reasons.add("run_not_succeeded")
    ready = not reasons and quality.get("quality_ready") is True
    return {
        "ready": ready,
        "readiness_status": "decision_ready" if ready else "review_required",
        "blocking_reasons": sorted(reasons),
    }


def _summary_readiness(summary: dict[str, object]) -> dict[str, object]:
    result = dict(summary)
    raw_reasons = result.get("blocking_reasons", [])
    reasons = {
        item
        for item in raw_reasons
        if isinstance(item, str)
    } if isinstance(raw_reasons, list) else set()
    if result.get("run_status") != "succeeded":
        reasons.add("run_not_succeeded")
    if result.get("validation_status") != "pass":
        reasons.add("validation_not_passed")

    def complete_metric(
        *,
        count_key: str,
        complete_key: str,
        ratio_key: str,
        reason: str,
    ) -> bool:
        count = result.get(count_key)
        complete = result.get(complete_key)
        ratio = result.get(ratio_key)
        normalized_ratio = float(ratio) if isinstance(ratio, Decimal) else ratio
        if not (
            isinstance(count, int)
            and isinstance(complete, int)
            and isinstance(normalized_ratio, (int, float))
        ):
            reasons.add("legacy_quality_evidence_missing")
            return False
        result[ratio_key] = normalized_ratio
        if count <= 0 or complete != count or float(normalized_ratio) != 1.0:
            reasons.add(reason)
            return False
        return True

    article_complete = complete_metric(
        count_key="article_count",
        complete_key="complete_article_count",
        ratio_key="article_insight_completeness",
        reason="incomplete_article_insights",
    )
    report_complete = complete_metric(
        count_key="report_section_count",
        complete_key="report_sections_complete",
        ratio_key="report_section_completeness",
        reason="empty_report_section",
    )
    if result.get("quality_ready") is not True:
        reasons.add("quality_review_required")
    quality_blocking_reasons = sorted(
        reason
        for reason in reasons
        if reason not in {"run_not_succeeded", "validation_not_passed"}
    )
    quality_report_ready = (
        result.get("quality_ready") is True
        and article_complete
        and report_complete
        and not quality_blocking_reasons
    )
    ready = (
        result.get("run_status") == "succeeded"
        and result.get("validation_status") == "pass"
        and result.get("quality_ready") is True
        and article_complete
        and report_complete
        and not reasons
    )
    result["quality_report_ready"] = quality_report_ready
    result["quality_readiness_status"] = (
        "decision_ready" if quality_report_ready else "review_required"
    )
    result["quality_blocking_reasons"] = quality_blocking_reasons
    result["readiness_status"] = "decision_ready" if ready else "review_required"
    result["decision_ready"] = ready
    result["blocking_reasons"] = sorted(reasons)
    return result


def create_app(repository: RepositoryProtocol) -> FastAPI:
    app = FastAPI(title="SheperD Research", docs_url=None, redoc_url=None)

    def report_payload(
        run_id: str,
        *,
        brief: WeeklyBrief | None = None,
        archive_scope: ArchiveScope = "active",
    ) -> dict[str, object]:
        selected_brief = brief if brief is not None else repository.get_brief(run_id)
        run = repository.get_run(run_id)
        if selected_brief is None or not _archive_visible(run, archive_scope):
            raise KeyError(run_id)
        validation = repository.get_validation(run_id)
        steps = _public_steps(repository.get_run_steps(run_id))
        sources = repository.get_run_sources(run_id)
        distillations = repository.get_run_distillations(run_id)
        claims = repository.get_run_claims(run_id)
        signals = repository.get_run_signal_events(run_id)
        resolved_models = sorted(
            {
                str(step["resolved_model"])
                for step in steps
                if step.get("resolved_model")
            }
        )
        requested_models = sorted(
            {
                str(step["requested_model"])
                for step in steps
                if step.get("requested_model")
            }
        )
        brief_model = selected_brief.model_id
        if brief_model and str(brief_model) not in resolved_models:
            resolved_models.append(str(brief_model))
        public_run = _public_run(run)
        quality = quality_metrics(sources, distillations, selected_brief)
        readiness = _readiness(run, validation, quality)
        return {
            "brief": selected_brief,
            "run": public_run,
            "validation": validation,
            "quality": {**quality, **readiness},
            **readiness,
            "lane_coverage": validation.lane_coverage if validation else [],
            "models": resolved_models,
            "requested_models": requested_models,
            "resolved_models": resolved_models,
            "steps": steps,
            "tool_calls": _public_tool_calls(repository.get_run_tool_calls(run_id)),
            "sources": sources,
            "source_hashes": repository.get_run_snapshot_hashes(run_id),
            "distillations": distillations,
            "claims": claims,
            "signals": signals,
            "as_of": public_run.get("as_of") if public_run else selected_brief.covered_until,
            "covered_from": selected_brief.covered_from,
            "covered_until": selected_brief.covered_until,
        }

    @app.get("/api/health", response_class=JSONResponse)
    def api_health() -> JSONResponse:
        try:
            return JSONResponse(jsonable_encoder(repository.health()))
        except Exception as error:
            return JSONResponse(
                {"status": "blocked", "error": error.__class__.__name__},
                status_code=503,
            )

    @app.get("/api/source-catalog", response_class=JSONResponse)
    def api_source_catalog() -> JSONResponse:
        try:
            catalog = load_source_catalog()
        except Exception as error:
            return JSONResponse(
                {"status": "blocked", "error": error.__class__.__name__},
                status_code=503,
            )
        return JSONResponse(
            jsonable_encoder(
                {
                    "status": "pass",
                    "coverage_weights": catalog.coverage_weights.as_dict(),
                    "sources": catalog.redacted_rows(),
                }
            )
        )

    @app.get("/api/reports/weekly", response_class=JSONResponse)
    def api_weekly_reports(
        since: datetime | None = None,
        until: datetime | None = None,
        review: str | None = Query(default=None, max_length=40),
        run_status: str | None = Query(default=None, max_length=40),
        ready: bool = False,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=10000),
        archive_scope: ArchiveScope = Query(default="active", max_length=8),  # noqa: B008
    ) -> JSONResponse:
        reports = repository.list_brief_summaries(
            review_state=review,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
            run_status=run_status,
            ready_only=ready,
            archive_scope=archive_scope,
        )
        total = repository.count_brief_summaries(
            review_state=review,
            since=since,
            until=until,
            run_status=run_status,
            ready_only=ready,
            archive_scope=archive_scope,
        )
        return JSONResponse(
            jsonable_encoder(
                {
                    "reports": [_summary_readiness(report) for report in reports],
                    "count": len(reports),
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(reports) < total,
                }
            )
        )

    @app.get("/api/reports/daily", response_class=JSONResponse)
    def api_daily_reports(
        since: datetime | None = None,
        until: datetime | None = None,
        review: str | None = Query(default=None, max_length=40),
        run_status: str | None = Query(default=None, max_length=40),
        ready: bool = False,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=10000),
        archive_scope: ArchiveScope = Query(default="active", max_length=8),  # noqa: B008
    ) -> JSONResponse:
        reports = repository.list_brief_summaries(
            cadence="daily",
            review_state=review,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
            run_status=run_status,
            ready_only=ready,
            archive_scope=archive_scope,
        )
        total = repository.count_brief_summaries(
            cadence="daily",
            review_state=review,
            since=since,
            until=until,
            run_status=run_status,
            ready_only=ready,
            archive_scope=archive_scope,
        )
        return JSONResponse(
            jsonable_encoder(
                {
                    "reports": [_summary_readiness(report) for report in reports],
                    "count": len(reports),
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(reports) < total,
                }
            )
        )

    @app.get("/api/regions", response_class=JSONResponse)
    def api_regions() -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {"regions": repository.list_regions(), "counts": repository.region_counts()}
            )
        )

    @app.get("/api/audit", response_class=JSONResponse)
    def api_audit() -> JSONResponse:
        try:
            return JSONResponse(
                jsonable_encoder({"status": "pass", **repository.audit_summary()})
            )
        except Exception as error:
            return JSONResponse(
                {"status": "blocked", "error": error.__class__.__name__},
                status_code=503,
            )

    @app.get("/api/reports/weekly/{run_id}/markdown")
    def api_weekly_markdown(
        run_id: str,
        archive_scope: ArchiveScope = Query(default="active", max_length=8),  # noqa: B008
    ) -> Response:
        brief = repository.get_brief(run_id)
        if brief is None or not _archive_visible(repository.get_run(run_id), archive_scope):
            return Response("weekly report not found", status_code=404)
        safe_name = "".join(
            character if character.isalnum() or character in "-_" else "_"
            for character in run_id
        ) or "weekly-report"
        markdown = render_weekly_markdown(
            brief,
            validation=repository.get_validation(run_id),
            sources=repository.get_run_sources(run_id),
            distillations=repository.get_run_distillations(run_id),
            claims=repository.get_run_claims(run_id),
            source_hashes=repository.get_run_source_hashes(run_id),
            signals=repository.get_run_signal_events(run_id),
            steps=_public_steps(repository.get_run_steps(run_id)),
            tool_calls=_public_tool_calls(repository.get_run_tool_calls(run_id)),
            run=_public_run(repository.get_run(run_id)),
        )
        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'inline; filename="{safe_name}.md"',
            },
        )

    @app.get("/api/reports/weekly/{run_id}", response_class=JSONResponse)
    def api_weekly_report(
        run_id: str,
        archive_scope: ArchiveScope = Query(default="active", max_length=8),  # noqa: B008
    ) -> JSONResponse:
        try:
            payload = report_payload(run_id, archive_scope=archive_scope)
        except (KeyError, ValueError):
            return JSONResponse({"error": "weekly report not found"}, status_code=404)
        return JSONResponse(jsonable_encoder(payload))

    @app.get("/api/reports/monthly", response_class=JSONResponse)
    def api_monthly_reports(
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        evidence: str | None = Query(default=None, max_length=40),
    ) -> JSONResponse:
        rollups = repository.monthly_rollup(
            since=since,
            until=until,
            limit=limit,
            offset=offset,
            region=region,
            language=language,
            evidence=evidence,
        )
        normalized_rollups = [
            {
                **rollup,
                "geographies": (
                    [str(rollup["geography"])]
                    if rollup.get("geography")
                    else []
                ),
            }
            for rollup in rollups
        ]
        return JSONResponse(
            jsonable_encoder(
                {
                    "rollups": normalized_rollups,
                    "limit": limit,
                    "offset": offset,
                }
            )
        )

    @app.get("/api/sources/explorer", response_class=JSONResponse)
    def api_source_explorer(
        query: str = Query(default="", max_length=160),
        geography: str | None = Query(default=None, max_length=80),
        lane: str | None = Query(default=None, max_length=80),
        evidence: str | None = Query(default=None, max_length=40),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        freshness: str | None = Query(default=None, max_length=20),
        authority_tier: str | None = Query(default=None, max_length=40),
        source_type: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        page: int = Query(default=1, ge=1, le=10000),
        page_size: int = Query(default=24, ge=1, le=100),
    ) -> JSONResponse:
        payload = repository.list_source_explorer(
            query,
            geography=geography,
            lane=lane,
            evidence_status=evidence,
            region=region,
            language=language,
            freshness=freshness,
            authority_tier=authority_tier,
            source_type=source_type,
            since=since,
            until=until,
            page=page,
            page_size=page_size,
        )
        return JSONResponse(jsonable_encoder(payload))

    @app.get("/api/sources/facets", response_class=JSONResponse)
    def api_source_facets() -> JSONResponse:
        return JSONResponse(jsonable_encoder({"status": "pass", **repository.source_facets()}))

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        rows = "".join(
            f"<tr><td><a href='/runs/{_value(run['run_id'])}'>"
            f"<code>{_value(run['run_id'])}</code></a></td>"
            f"<td>{_value(run.get('topic_set'))}</td><td>{_value(run.get('status'))}</td>"
            f"<td>{_value(run.get('as_of'))}</td></tr>"
            for run in repository.list_runs()
        )
        body = (
            "<h1>SheperD Research</h1>"
            "<p class='muted'>Local read-only view. "
            "Review and export remain explicit CLI actions.</p>"
            "<div class='card'><h2>Runs</h2><table>"
            "<tr><th>Run</th><th>Topic</th><th>Status</th><th>As of</th></tr>"
            f"{rows or '<tr><td colspan=4>No runs recorded.</td></tr>'}</table></div>"
        )
        return HTMLResponse(_layout("Runs", body))

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    def run_detail(run_id: str) -> HTMLResponse:
        run = repository.get_run(run_id)
        if run is None:
            return HTMLResponse(_layout("Not found", "<h1>Run not found</h1>"), status_code=404)
        brief = repository.get_brief(run_id)
        step_rows = "".join(
            "<tr>"
            f"<td>{_value(step.get('agent_name'))}</td>"
            f"<td>{_value(step.get('status'))}</td>"
            f"<td>{_value(step.get('duration_ms', 'unknown'))} ms</td>"
            f"<td><code>{_value(step.get('input_hash', ''))}</code></td>"
            f"<td><code>{_value(step.get('output_hash', ''))}</code></td>"
            f"<td>{_value(step.get('error_code') or 'none')}</td>"
            "</tr>"
            for step in repository.get_run_steps(run_id)
        )
        steps_html = (
            "<div class='card'><h2>Agent steps</h2><table>"
            "<tr><th>Step</th><th>Status</th><th>Latency</th><th>Input hash</th>"
            "<th>Output hash</th><th>Error</th></tr>"
            f"{step_rows or '<tr><td colspan=6>No steps recorded.</td></tr>'}"
            "</table></div>"
        )
        brief_html = (
            f"<h2><a href='/briefs/{_value(run_id)}'>{_value(brief.title)}</a></h2>"
            f"<p>{_value(brief.summary)}</p>"
            if brief
            else "<p>No brief recorded.</p>"
        )
        body = (
            f"<h1>Run <code>{_value(run_id)}</code></h1>"
            f"<div class='card'><p>Status: <strong>{_value(run.get('status'))}</strong></p>"
            f"<p>Topic: {_value(run.get('topic_set'))}</p><p>As of: {_value(run.get('as_of'))}</p>"
            f"<p>Error: {_value(run.get('error') or 'none')}</p></div>"
            f"<div class='card'>{brief_html}</div>"
            f"{steps_html}"
        )
        return HTMLResponse(_layout("Run", body))

    @app.get("/sources", response_class=HTMLResponse)
    def sources(
        query: str = Query(default="", max_length=160),
        geography: str | None = Query(default=None, max_length=80),
        lane: str | None = Query(default=None, max_length=80),
        evidence: str | None = Query(default=None, max_length=40),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        freshness: str | None = Query(default=None, max_length=20),
        authority_tier: str | None = Query(default=None, max_length=40),
        source_type: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> HTMLResponse:
        rows = "".join(
            f"<tr><td><a href='{_value(source.url)}' rel='noreferrer'>"
            f"{_value(source.title)}</a></td>"
            f"<td>{_value(source.publisher)}</td>"
            f"<td>{_value(source.published_at or 'unknown')}</td>"
            f"<td>{_value(', '.join(source.geographies) or 'unknown')}</td></tr>"
            for source in repository.list_sources(
                query,
                geography=geography,
                lane=lane,
                evidence_status=evidence,
                region=region,
                language=language,
                freshness=freshness,
                authority_tier=authority_tier,
                source_type=source_type,
                since=since,
                until=until,
                limit=limit,
            )
        )
        body = (
            "<h1>Sources</h1>"
            f"<form><input name='query' value='{_value(query)}' maxlength='160' "
            "placeholder='Search sources'>"
            " <button>Search</button></form>"
            "<div class='card'><table>"
            "<tr><th>Title</th><th>Publisher</th><th>Published</th><th>Geography</th></tr>"
            f"{rows or '<tr><td colspan=4>No sources recorded.</td></tr>'}</table></div>"
        )
        return HTMLResponse(_layout("Sources", body))

    @app.get("/briefs", response_class=HTMLResponse)
    def briefs(
        query: str = Query(default="", max_length=160),
        review: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=20, ge=1, le=1000),
    ) -> HTMLResponse:
        rows = "".join(
            f"<tr><td><a href='/briefs/{_value(brief.run_id)}'>{_value(brief.title)}</a></td>"
            f"<td>{_value(brief.review_state.value)}</td><td>{_value(brief.covered_until)}</td></tr>"
            for brief in repository.list_briefs(
                query,
                review_state=review,
                since=since,
                until=until,
                limit=limit,
            )
        )
        body = (
            "<h1>Briefs</h1>"
            f"<form><input name='query' value='{_value(query)}' maxlength='160' "
            "placeholder='Search briefs'> <button>Search</button></form>"
            "<div class='card'><table>"
            "<tr><th>Title</th><th>Review</th><th>Covered until</th></tr>"
            f"{rows or '<tr><td colspan=3>No briefs recorded.</td></tr>'}</table></div>"
        )
        return HTMLResponse(_layout("Briefs", body))

    @app.get("/api/runs", response_class=JSONResponse)
    def api_runs(
        topic_set: str | None = Query(default=None, max_length=80),
        status: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "runs": repository.list_runs(
                        topic_set=topic_set,
                        status=status,
                        since=since,
                        until=until,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/sources", response_class=JSONResponse)
    def api_sources(
        query: str = Query(default="", max_length=160),
        geography: str | None = Query(default=None, max_length=80),
        lane: str | None = Query(default=None, max_length=80),
        evidence: str | None = Query(default=None, max_length=40),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        freshness: str | None = Query(default=None, max_length=20),
        authority_tier: str | None = Query(default=None, max_length=40),
        source_type: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "sources": repository.list_sources(
                        query,
                        geography=geography,
                        lane=lane,
                        evidence_status=evidence,
                        region=region,
                        language=language,
                        freshness=freshness,
                        authority_tier=authority_tier,
                        source_type=source_type,
                        since=since,
                        until=until,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/distillations", response_class=JSONResponse)
    def api_distillations(
        run_id: str | None = Query(default=None, max_length=120),
        query: str = Query(default="", max_length=160),
        evidence: str | None = Query(default=None, max_length=40),
        lane: str | None = Query(default=None, max_length=80),
        geography: str | None = Query(default=None, max_length=80),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "distillations": repository.list_distillations(
                        run_id=run_id,
                        query=query,
                        evidence_status=evidence,
                        lane=lane,
                        geography=geography,
                        region=region,
                        language=language,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/claims", response_class=JSONResponse)
    def api_claims(
        run_id: str | None = Query(default=None, max_length=120),
        query: str = Query(default="", max_length=160),
        evidence: str | None = Query(default=None, max_length=40),
        verification_basis: str | None = Query(default=None, max_length=80),
        independent_source_min: int | None = Query(default=None, ge=0, le=100),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "claims": repository.list_claims(
                        run_id=run_id,
                        query=query,
                        evidence_status=evidence,
                        verification_basis=verification_basis,
                        independent_source_min=independent_source_min,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/signals", response_class=JSONResponse)
    def api_signals(
        run_id: str | None = Query(default=None, max_length=120),
        geography: str | None = Query(default=None, max_length=80),
        event_type: str | None = Query(default=None, max_length=80),
        evidence: str | None = Query(default=None, max_length=40),
        region: str | None = Query(default=None, max_length=80),
        language: str | None = Query(default=None, max_length=12),
        limit: int = Query(default=100, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "signals": repository.list_signal_events(
                        run_id=run_id,
                        geography=geography,
                        event_type=event_type,
                        evidence_status=evidence,
                        region=region,
                        language=language,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/briefs", response_class=JSONResponse)
    def api_briefs(
        query: str = Query(default="", max_length=160),
        review: str | None = Query(default=None, max_length=40),
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=20, ge=1, le=1000),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {
                    "briefs": repository.list_briefs(
                        query,
                        review_state=review,
                        since=since,
                        until=until,
                        limit=limit,
                        offset=offset,
                    )
                }
            )
        )

    @app.get("/api/runs/{run_id}", response_class=JSONResponse)
    def api_run(run_id: str) -> JSONResponse:
        run = repository.get_run(run_id)
        if run is None:
            return JSONResponse({"error": "run not found"}, status_code=404)
        brief = repository.get_brief(run_id)
        sources = repository.get_run_sources(run_id)
        distillations = repository.get_run_distillations(run_id)
        validation = repository.get_validation(run_id)
        quality = quality_metrics(sources, distillations, brief)
        readiness = _readiness(run, validation, quality)
        return JSONResponse(
            jsonable_encoder(
                {
                    "run": _public_run(run),
                    "steps": _public_steps(repository.get_run_steps(run_id)),
                    "sources": sources,
                    "claims": repository.get_run_claims(run_id),
                    "distillations": distillations,
                    "signals": repository.get_run_signal_events(run_id),
                    "tool_calls": _public_tool_calls(repository.get_run_tool_calls(run_id)),
                    "source_hashes": repository.get_run_snapshot_hashes(run_id),
                    "brief": brief,
                    "validation": validation,
                    "quality": {**quality, **readiness},
                    **readiness,
                }
            )
        )

    @app.get("/api/runs/{run_id}/audit", response_class=JSONResponse)
    def api_run_audit(run_id: str) -> JSONResponse:
        run = repository.get_run(run_id)
        if run is None:
            return JSONResponse({"error": "run not found"}, status_code=404)
        steps = _public_steps(repository.get_run_steps(run_id))
        tool_calls = _public_tool_calls(repository.get_run_tool_calls(run_id))
        sources = repository.get_run_sources(run_id)
        distillations = repository.get_run_distillations(run_id)
        claims = repository.get_run_claims(run_id)
        signals = repository.get_run_signal_events(run_id)
        source_hashes = repository.get_run_snapshot_hashes(run_id)
        validation_report = repository.get_validation(run_id)
        brief = repository.get_brief(run_id)
        sources_by_region = Counter(source.region for source in sources)
        sources_by_language = Counter(source.language_code for source in sources)
        freshness = Counter(source.freshness_status.value for source in sources)
        extraction = Counter(source.extraction_status.value for source in sources)
        translations = Counter(
            item.translation_status.value for item in distillations
        )
        claims_by_evidence = Counter(item.evidence_status.value for item in claims)
        independent_sources = Counter(
            str(item.independent_source_count) for item in claims
        )
        quality = quality_metrics(sources, distillations, brief)
        readiness = _readiness(run, validation_report, quality)
        article_count = (
            quality["article_count"] if isinstance(quality["article_count"], int) else 0
        )
        complete_article_count = (
            quality["complete_article_count"]
            if isinstance(quality["complete_article_count"], int)
            else 0
        )
        article_quality = Counter(
            {
                "complete": complete_article_count,
                "incomplete": article_count - complete_article_count,
            }
        )
        extraction_success_rate = (
            extraction.get("succeeded", 0) / len(sources) if sources else 0.0
        )
        distillation_success_rate = (
            len(distillations) / len(sources) if sources else 0.0
        )
        translation_success_rate = (
            translations.get("succeeded", 0) / len(distillations)
            if distillations
            else 0.0
        )
        return JSONResponse(
            jsonable_encoder(
                {
                    "run_id": run_id,
                    "run": _public_run(run),
                    "validation": validation_report,
                    "quality": {**quality, **readiness},
                    **readiness,
                    "steps": steps,
                    "tool_calls": tool_calls,
                    "sources": sources,
                    "source_hashes": source_hashes,
                    "distillations": distillations,
                    "claims": claims,
                    "signals": signals,
                        "metrics": {
                        "step_count": len(steps),
                        "tool_call_count": len(tool_calls),
                        "fallback_count": sum(
                            1 for step in steps if step.get("fallback_reason")
                        ),
                        "source_count": len(sources),
                        "source_hash_count": len(source_hashes),
                            "distillation_count": len(distillations),
                            "article_count": article_count,
                            "article_insight_quality": dict(sorted(article_quality.items())),
                            "article_insight_complete_count": article_quality.get("complete", 0),
                            "article_insight_completeness": quality[
                                "article_insight_completeness"
                            ],
                            "report_section_completeness": quality["report_section_completeness"],
                            "source_distillation_coverage": quality["source_distillation_coverage"],
                            "article_quality_issues": quality["article_quality_issues"],
                            "article_fulfillment": quality["article_fulfillment"],
                            "report_quality_issues": quality["report_quality_issues"],
                            "blocking_reasons": readiness["blocking_reasons"],
                        "claim_count": len(claims),
                            "signal_count": len(signals),
                            "sources_by_region": dict(sorted(sources_by_region.items())),
                            "sources_by_language": dict(sorted(sources_by_language.items())),
                            "freshness": dict(sorted(freshness.items())),
                            "extraction": dict(sorted(extraction.items())),
                            "translations": dict(sorted(translations.items())),
                            "claims_by_evidence": dict(sorted(claims_by_evidence.items())),
                            "independent_source_distribution": dict(
                                sorted(independent_sources.items(), key=lambda item: int(item[0]))
                            ),
                            "extraction_success_rate": round(extraction_success_rate, 6),
                            "distillation_success_rate": round(distillation_success_rate, 6),
                            "translation_success_rate": round(translation_success_rate, 6),
                            "citation_coverage": (
                                validation_report.citation_coverage
                                if validation_report is not None
                                else 0.0
                            ),
                            "regions": sorted({source.region for source in sources}),
                            "languages": sorted({source.language_code for source in sources}),
                            "lanes": sorted({source.lane for source in sources}),
                        },
                }
            )
        )

    @app.get("/api/briefs/{brief_id}", response_class=JSONResponse)
    def api_brief(brief_id: str) -> JSONResponse:
        brief = repository.get_brief(brief_id)
        if brief is None:
            return JSONResponse({"error": "brief not found"}, status_code=404)
        return JSONResponse(
            jsonable_encoder(
                {"brief": brief, "validation": repository.get_validation(brief.run_id)}
            )
        )

    @app.get("/briefs/{brief_id}", response_class=HTMLResponse)
    def brief_detail(brief_id: str) -> HTMLResponse:
        brief = repository.get_brief(brief_id)
        if brief is None:
            return HTMLResponse(_layout("Not found", "<h1>Brief not found</h1>"), status_code=404)
        sources = "".join(
            f"<li><a href='{_value(url)}' rel='noreferrer'>{_value(url)}</a></li>"
            for url in brief.source_urls
        )
        limitations = "".join(f"<li>{_value(item)}</li>" for item in brief.limitations)
        body = (
            f"<h1>{_value(brief.title)}</h1>"
            f"<p class='muted'>Review: {_value(brief.review_state.value)} · "
            f"Evidence: {_value(brief.evidence_status.value)}</p>"
            f"<div class='card'><h2>Summary</h2><p>{_value(brief.summary)}</p></div>"
            "<div class='card'><h2>Limitations</h2><ul>"
            f"{limitations or '<li>None recorded.</li>'}</ul></div>"
            "<div class='card'><h2>Sources</h2><ul>"
            f"{sources or '<li>None recorded.</li>'}</ul></div>"
        )
        return HTMLResponse(_layout("Brief", body))

    return app
