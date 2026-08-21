from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape

from fastapi import FastAPI, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from .contracts import WeeklyBrief
from .db import RepositoryProtocol
from .source_catalog import load_source_catalog


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
)


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
    return public_run


def create_app(repository: RepositoryProtocol) -> FastAPI:
    app = FastAPI(title="SheperD Research", docs_url=None, redoc_url=None)

    def report_payload(
        run_id: str, *, brief: WeeklyBrief | None = None
    ) -> dict[str, object]:
        selected_brief = brief if brief is not None else repository.get_brief(run_id)
        run = repository.get_run(run_id)
        validation = repository.get_validation(run_id)
        steps = _public_steps(repository.get_run_steps(run_id))
        sources = repository.get_run_sources(run_id)
        distillations = repository.get_run_distillations(run_id)
        claims = repository.get_run_claims(run_id)
        signals = repository.get_run_signal_events(run_id)
        if selected_brief is None:
            raise KeyError(run_id)
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
        return {
            "brief": selected_brief,
            "run": public_run,
            "validation": validation,
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
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        reports = repository.list_brief_summaries(
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )
        return JSONResponse(jsonable_encoder({"reports": reports, "count": len(reports)}))

    @app.get("/api/reports/daily", response_class=JSONResponse)
    def api_daily_reports(
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=10000),
    ) -> JSONResponse:
        reports = repository.list_brief_summaries(
            cadence="daily",
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )
        return JSONResponse(jsonable_encoder({"reports": reports, "count": len(reports)}))

    @app.get("/api/regions", response_class=JSONResponse)
    def api_regions() -> JSONResponse:
        return JSONResponse(
            jsonable_encoder(
                {"regions": repository.list_regions(), "counts": repository.region_counts()}
            )
        )

    @app.get("/api/reports/weekly/{run_id}", response_class=JSONResponse)
    def api_weekly_report(run_id: str) -> JSONResponse:
        try:
            payload = report_payload(run_id)
        except KeyError:
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
        return JSONResponse(
            jsonable_encoder(
                {
                    "rollups": repository.monthly_rollup(
                        since=since,
                        until=until,
                        limit=limit,
                        offset=offset,
                        region=region,
                        language=language,
                        evidence=evidence,
                    ),
                    "limit": limit,
                    "offset": offset,
                }
            )
        )

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
        return JSONResponse(
            jsonable_encoder(
                {
                    "run": _public_run(run),
                    "steps": _public_steps(repository.get_run_steps(run_id)),
                    "sources": repository.get_run_sources(run_id),
                    "claims": repository.get_run_claims(run_id),
                    "distillations": repository.get_run_distillations(run_id),
                    "signals": repository.get_run_signal_events(run_id),
                    "tool_calls": _public_tool_calls(repository.get_run_tool_calls(run_id)),
                    "source_hashes": repository.get_run_snapshot_hashes(run_id),
                    "brief": repository.get_brief(run_id),
                    "validation": repository.get_validation(run_id),
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
                    "validation": repository.get_validation(run_id),
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
