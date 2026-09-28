from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime

from .costs import COST_RATE_CARD, estimate_run_cost

# Report prose is intentionally kept readable instead of wrapped into code-like fragments.
# ruff: noqa: E501

TABLE_CATALOG: tuple[tuple[str, str, str, str], ...] = (
    ("research_runs", "one immutable execution and readiness state", "root", "append-only run record"),
    ("agent_steps", "agent-stage status, model, latency, tokens, errors", "research_runs", "append-only audit"),
    ("agent_tool_calls", "Tavily Search/Extract receipts", "agent_steps", "append-only audit"),
    ("run_sources", "run-scoped source participation and period state", "research_runs + sources", "append-only participation"),
    ("sources", "canonical source metadata", "canonical_url", "upsert metadata; facts preserved"),
    ("source_snapshots", "retrieval hashes and collection timestamps", "research_runs + sources", "append-only snapshots"),
    ("article_distillations", "structured article summaries and insights", "research_runs + sources", "one run-scoped packet"),
    ("claims", "cited factual claims and evidence state", "research_runs", "corrections supersede"),
    ("signal_events", "structured industry signals", "research_runs", "append-only events"),
    ("weekly_briefs", "synthesized report sections", "research_runs", "draft until review"),
    ("validation_checks", "durable validation-gate result", "research_runs", "latest run gate"),
    ("review_decisions", "human approval or rejection", "research_runs", "append-only decisions"),
    ("checkpoints", "LangGraph resumable state", "thread/run", "managed by checkpoint saver"),
    ("checkpoint_blobs", "serialized checkpoint values", "checkpoint", "managed by checkpoint saver"),
    ("checkpoint_writes", "checkpoint write history", "checkpoint", "managed by checkpoint saver"),
)


def _iso(value: object) -> str:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return str(value)


def _status(value: object) -> str:
    if isinstance(value, Mapping):
        return str(value.get("status", "not recorded"))
    return "not recorded"


def _count(mapping: object, key: str) -> int:
    if isinstance(mapping, Mapping):
        value = mapping.get(key, 0)
        return int(value) if isinstance(value, (int, float)) else 0
    return 0


def _ratio(mapping: object, key: str) -> str:
    if isinstance(mapping, Mapping):
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return f"{value:.1%}"
    return "not recorded"


def _step_rows(snapshot: Mapping[str, object]) -> str:
    rows = snapshot.get("agent_steps")
    if not isinstance(rows, list):
        by_agent = snapshot.get("agent_steps_by_agent")
        if isinstance(by_agent, Mapping):
            rows = [
                {
                    "agent_name": name,
                    "steps": count,
                    "succeeded": "—",
                    "failed": "—",
                    "latency_ms": "—",
                }
                for name, count in by_agent.items()
            ]
    if not isinstance(rows, list) or not rows:
        return "| No persisted agent steps | — | — | — | — |\n"
    output = ""
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        output += (
            f"| {item.get('agent_name', 'unknown')} | {item.get('steps', 0)} | "
            f"{item.get('succeeded', 0)} | {item.get('failed', 0)} | "
            f"{item.get('latency_ms', 0)} ms |\n"
        )
    return output or "| No persisted agent steps | — | — | — | — |\n"


def _tool_rows(snapshot: Mapping[str, object]) -> str:
    rows = snapshot.get("tool_calls")
    if not isinstance(rows, list):
        by_tool = snapshot.get("tool_calls_by_tool")
        if isinstance(by_tool, Mapping):
            rows = [
                {"tool_name": name, "status": "aggregate", "calls": count, "results": "—", "latency_ms": "—"}
                for name, count in by_tool.items()
            ]
    if not isinstance(rows, list) or not rows:
        return "| No persisted tool calls | — | — | — |\n"
    output = ""
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        output += (
            f"| {item.get('tool_name', 'unknown')} | {item.get('status', 'unknown')} | "
            f"{item.get('calls', 0)} | {item.get('results', 0)} | "
            f"{item.get('latency_ms', 0)} ms |\n"
        )
    return output or "| No persisted tool calls | — | — | — |\n"


def _model_rows(snapshot: Mapping[str, object]) -> str:
    rows = snapshot.get("models")
    if isinstance(rows, Mapping):
        rows = [
            {"model": name, "steps": count, "input_tokens": "—", "output_tokens": "—"}
            for name, count in rows.items()
        ]
    if not isinstance(rows, list) or not rows:
        return "| No model usage recorded | — | — | — |\n"
    output = ""
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        output += (
            f"| {item.get('model', 'not recorded')} | {item.get('steps', 0)} | "
            f"{item.get('input_tokens', 0)} | {item.get('output_tokens', 0)} |\n"
        )
    return output or "| No model usage recorded | — | — | — |\n"


def _cost_snapshot(snapshot: Mapping[str, object]) -> dict[str, object]:
    steps = snapshot.get("agent_steps")
    tool_rows = snapshot.get("tool_calls")
    normalized_steps: list[Mapping[str, object]] = []
    if isinstance(steps, list):
        normalized_steps = [item for item in steps if isinstance(item, Mapping)]
    normalized_tools: list[Mapping[str, object]] = []
    if isinstance(tool_rows, list):
        normalized_tools = [
            {
                "tool_name": item.get("tool_name"),
                "status": item.get("status"),
                "calls": item.get("calls", 1),
                "result_count": item.get("results", 0),
            }
            for item in tool_rows
            if isinstance(item, Mapping)
        ]
    elif isinstance(tool_rows, Mapping):
        normalized_tools = [
            {"tool_name": name, "status": "succeeded", "result_count": 0}
            for name, count in tool_rows.items()
            for _ in range(int(count) if isinstance(count, (int, float)) else 0)
        ]
    return estimate_run_cost(normalized_steps, normalized_tools)


def _period_rows(snapshot: Mapping[str, object]) -> str:
    counts = snapshot.get("period_counts")
    if not isinstance(counts, Mapping) or not counts:
        return "| No run-source period classifications recorded | — |\n"
    return "".join(
        f"| `{name}` | {value} |\n"
        for name, value in sorted(counts.items())
    )


def _cost_forecast() -> dict[str, object]:
    latest_weekly_input = 77_749
    latest_weekly_output = 45_351
    latest_weekly_llm = estimate_run_cost(
        [{"input_tokens": latest_weekly_input, "output_tokens": latest_weekly_output}],
        [],
        model="gpt-5.6-luna",
    )["llm_estimated_usd"]
    weekly_value = (
        float(latest_weekly_llm)
        if isinstance(latest_weekly_llm, (int, float))
        else 0.0
    )
    return {
        "latest_weekly_llm_proxy_usd": weekly_value,
        "daily_llm_proxy_usd": round(weekly_value / 7, 6),
        "weekly_llm_proxy_usd": weekly_value,
        "monthly_llm_proxy_usd": round(weekly_value * 52 / 12, 6),
        "basis": "latest recorded weekly token volume divided across seven days; excludes Tavily and hosting",
    }


def render_system_report(
    *,
    snapshot: Mapping[str, object],
    audit: Mapping[str, object],
    diagnostics: Mapping[str, object],
    as_of: datetime | None = None,
    repository_commit: str = "not recorded",
    branch_id: str | None = None,
    migration_version: str | None = None,
    repository_dirty: bool = False,
) -> str:
    observed_at = as_of or datetime.now(UTC)
    tables = snapshot.get("table_counts", {})
    report_counts = audit.get("reports", {})
    quality = audit.get("quality", {})
    cost = _cost_snapshot(snapshot)
    table_lines = "".join(
        f"| `{name}` | {purpose} | {relationships} | {retention} | "
        f"{_count(tables, name)} |\n"
        for name, purpose, relationships, retention in TABLE_CATALOG
    )
    provider_checks = diagnostics.get("checks", {})
    provider_lines = []
    if isinstance(provider_checks, Mapping):
        for name, value in provider_checks.items():
            if name == "providers" and isinstance(value, Mapping):
                for provider, check in value.items():
                    provider_lines.append(f"- {provider}: {_status(check)}")
            elif isinstance(value, Mapping):
                provider_lines.append(f"- {name}: {_status(value)}")
    provider_status = "\n".join(provider_lines) or "- Diagnostics not recorded"
    persistence_status = (
        "pass" if isinstance(tables, Mapping) and bool(tables) else "not_recorded"
    )
    blockers = audit.get("blockers", [])
    blocker_lines = "\n".join(
        f"- {item.get('check', 'unknown')}: {item.get('message', 'blocked')}"
        for item in blockers
        if isinstance(item, Mapping)
    ) if isinstance(blockers, list) else ""
    period_counts = snapshot.get("period_counts", {})
    table_counts = snapshot.get("table_counts", {})
    if (
        _count(table_counts, "run_sources") > 0
        and _count(period_counts, "in_period") == 0
    ):
        temporal_blocker = (
            "- period:eligible_weekly_sources: no persisted source has a "
            "publication date inside its weekly window"
        )
        blocker_lines = (
            f"{blocker_lines}\n{temporal_blocker}"
            if blocker_lines
            else temporal_blocker
        )
    if _count(quality, "distillations_incomplete") > 0:
        quality_blocker = (
            f"- quality:incomplete_article_insights: "
            f"{_count(quality, 'distillations_incomplete')} historical distillations "
            "remain incomplete"
        )
        blocker_lines = f"{blocker_lines}\n{quality_blocker}" if blocker_lines else quality_blocker
    if (
        _count(quality, "briefs_total") > 0
        and _count(quality, "briefs_with_complete_sections")
        < _count(quality, "briefs_total")
    ):
        section_blocker = (
            f"- quality:empty_report_section: "
            f"{_count(quality, 'briefs_total') - _count(quality, 'briefs_with_complete_sections')} "
            "historical briefs have incomplete sections"
        )
        blocker_lines = f"{blocker_lines}\n{section_blocker}" if blocker_lines else section_blocker
    if not blocker_lines:
        blocker_lines = "- No audit blockers returned; quality gates can still fail independently."
    return f"""---
title: SheperD Technical and Operations Report
type: system-report
status: internal
as_of: {_iso(observed_at)}
repository_commit: {json.dumps(repository_commit)}
repository_dirty: {str(repository_dirty).lower()}
neon_branch: {json.dumps(branch_id or "not recorded")}
migration_version: {json.dumps(migration_version or "not recorded")}
---

# SheperD Technical and Operations Report

Generated from a read-only Neon snapshot at **{_iso(observed_at)}**. Repository commit `{repository_commit}`; working tree dirty: **{str(repository_dirty).lower()}**. This is an operational truth report, not a claim that the research output is production-ready.

## Executive production-readiness status

**Current status: NOT PRODUCTION-READY until the corrected weekly date gate, article/report completeness, human review, and Markdown/PDF delivery gates pass.**

Neon connectivity, provider health, persistence, agent execution, research quality, report readiness, and deployment readiness are separate gates. A healthy database connection proves only infrastructure reachability.

| Dimension | Status | Evidence |
|---|---|---|
| Neon infrastructure | {_status(audit.get('database'))} | branch `{branch_id or 'not recorded'}`, migration `{migration_version or 'not recorded'}` |
| Provider diagnostics | {_status(diagnostics)} | redacted checks listed below |
| Data persistence | {persistence_status} | {len(tables) if isinstance(tables, Mapping) else 0} tracked table counts |
| Agent execution | {'pass' if _count(tables, 'agent_steps') > 0 else 'not recorded'} | {_count(tables, 'agent_steps')} steps, {_count(tables, 'agent_tool_calls')} tool receipts |
| Research quality | {_ratio(quality, 'article_insight_completeness')} | historical completeness must be recomputed |
| Report readiness | {_count(report_counts, 'succeeded')} succeeded runs; review is separate | validation and sections remain gates |
| Deployment | configured separately | API/UI route checks required |

## Architecture and data flow

```mermaid
flowchart LR
    A[Scheduled or on-demand worker] --> B[LangGraph checkpoint coordinator]
    B --> C[Regulatory discovery lane]
    B --> D[Port operations discovery lane]
    B --> E[Global market discovery lane]
    C --> F[Tavily Search and Extract]
    D --> F
    E --> F
    F --> G[Per-source LangChain distillation]
    G --> H[Critic and reconciler]
    H --> I[Weekly or daily brief]
    I --> J[Deterministic validation]
    J --> K[(Neon PostgreSQL)]
    K --> L[FastAPI read-only API]
    L --> M[Next.js Vercel dashboard]
    J --> N[Reviewed Markdown and private PDF]
```

Runtime currently uses **OpenAI `ChatOpenAI` with `gpt-5.6-luna`**. It is not currently OpenRouter-powered. Tavily Search and Extract provide discovery and extraction. Neon uses pooled runtime access and direct migration/admin access. Vercel Blob PDF storage is optional infrastructure until its token and artifact flow are configured.

## Infrastructure

- Python/uv service in `research-agents/`.
- LangGraph provides bounded workflow coordination and resumable checkpoints.
- LangChain workers perform discovery, per-source distillation, critique, and synthesis.
- OpenAI is the current LLM provider; model identity is persisted from agent-step metadata.
- Tavily Search/Extract is the source discovery and extraction provider; key slots route requests and do not create a second quota.
- Neon PostgreSQL is canonical. `DATABASE_URL` is pooled runtime access; `DIRECT_DATABASE_URL` is for migrations/admin.
- FastAPI serves read-only data and report endpoints.
- Next.js/Vercel serves the private research dashboard. Database and Blob credentials remain server-side.
- Vercel Blob is intended for approved private PDFs with expiring signed access.

## Agent inventory

1. `regulatory_research_agent` — D&D, FMC, courts, OSRA, and enforcement.
2. `port_operations_research_agent` — U.S., Canada, Mexico, Europe, and port operations.
3. `global_market_research_agent` — South America, Middle East, and global market signals.
4. Bounded per-source distillation workers — one structured packet per successfully extracted source.
5. `critic_agent` — contradictions, unsupported claims, freshness, and citation gaps.
6. `weekly_synthesis_agent` — cited report sections and follow-up questions.
7. LangGraph coordinator — state, budgets, checkpoints, persistence, and validation.

No prompts, raw article bodies, or hidden chain-of-thought are retained. Agent rationale is represented by structured evidence, limitations, verification basis, impact, and next steps.

## Agent metrics

### Steps by agent

| Agent | Steps | Succeeded | Failed | Total latency |
|---|---:|---:|---:|---:|
{_step_rows(snapshot)}

### Tool receipts

| Tool | Status | Calls | Results | Total latency |
|---|---|---:|---:|---:|
{_tool_rows(snapshot)}

### Model usage

| Model ID | Steps | Input tokens | Output tokens |
|---|---:|---:|---:|
{_model_rows(snapshot)}

Prompt versions are stored as identifiers only. Current workflow identifiers include `discovery-v3-multilingual`, `distill-v6-insight`, `critic-v5-evidence`, and `weekly-brief-v6-decision`; prompt text is intentionally excluded.

## Neon table catalog

| Table | Grain and purpose | Relationships | Retention | Live rows |
|---|---|---|---|---:|
{table_lines}

Facts are append-oriented. Corrections create superseding claims or new run-scoped records. Failed and archived runs retain their evidence. GIN indexes support full-text search where configured; B-tree indexes support run status, dates, evidence, lanes, models, and period state. Orphan checks: `{json.dumps(snapshot.get('orphaned_records', {}), sort_keys=True)}`.

Live row counts are the current growth baseline; historical growth requires periodic snapshots and is not inferred here. API and UI count reconciliation remains a separate deployment gate—the database count alone is not presented as browser parity.

## API and UI data flow

The API reads Neon summaries and detail payloads. The UI never receives database credentials and must show explicit unavailable, empty, partial, failed, undated, background, and incomplete states. Weekly list responses should use database-side aggregates; detail pages hydrate source evidence and audit records.

Primary routes: `/api/health`, `/api/reports/weekly`, `/api/reports/weekly/{{run_id}}`, `/api/reports/weekly/{{run_id}}/markdown`, `/api/reports/weekly/{{run_id}}/pdf`, `/api/reports/monthly`, `/api/sources/explorer`, `/api/runs/{{run_id}}/audit`. The PDF route is available only after a private artifact and signing configuration exist.

## Validation gates and blockers

Historical run status: `{json.dumps(report_counts, sort_keys=True, default=str)}`. Historical article quality: `{json.dumps(quality, sort_keys=True, default=str)}`.

Provider and environment diagnostics (redacted):

{provider_status}

Audit blockers:

{blocker_lines}

The corrected weekly gate counts only sources with `period_status=in_period` and `eligible_for_weekly=true`. Sources without publication dates, or published outside the half-open window, remain visible as background context and do not count as current-week findings. Future-dated sources fail validation.

### Persisted period classification

| Period status | Run-source rows |
|---|---:|
{_period_rows(snapshot)}

## Cost model

This is an estimate, not an invoice. Confirm the configured model’s current account rate before billing decisions.

| Component | Basis |
|---|---|
| OpenAI | approximately $0.50 / 1M input tokens and $3.00 / 1M output tokens for the captured short-context proxy rate card |
| Tavily Search | 1 credit per basic Search call |
| Tavily Extract | approximately 1 credit per five successful URLs |
| Tavily allowance | 1,000 credits/month; routed key slots do not double the quota |
| Vercel Hobby dashboard | $0 within plan limits |
| Vercel Pro dashboard | approximately $20/month plus usage |
| Vercel Blob | Hobby included limits; beyond them, usage-based storage/operations/transfer |
| Neon | $0 under the currently configured plan; verify plan limits |
| Separate ingestion worker | TBD until a host is selected |

Rate-card references (retrieved {COST_RATE_CARD.get('retrieved_at', 'not recorded')}): OpenAI [pricing](https://platform.openai.com/pricing), Tavily [credits](https://docs.tavily.com/documentation/api-credits) and [pricing](https://www.tavily.com/pricing), Vercel [pricing](https://vercel.com/pricing), and Blob [pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing). The configured Luna rate is a proxy and must be confirmed against the account.

Forecast from the latest recorded weekly token volume:

```json
{json.dumps(_cost_forecast(), indent=2, sort_keys=True)}
```

Observed usage-derived estimate:

```json
{json.dumps(cost, indent=2, sort_keys=True, default=str)}
```

Historical proxy from the captured database baseline was about $3.23 for 1,418,168 input and 840,180 output tokens. The latest recorded weekly proxy was about $0.18 for 77,749 input and 45,351 output tokens. These values are rate-card estimates, not provider invoices.

## Weekly date-window policy

`as_of` is normalized to UTC. Business boundaries are calculated in `RESEARCH_TIMEZONE` and stored in UTC. Weekly eligibility uses the half-open interval `[covered_from, covered_until)`: only a publication date inside the interval counts as current-week evidence. `retrieved_at` records collection time and never silently replaces a missing publication date. Undated and out-of-period material is retained as labeled background context.

## Markdown and PDF delivery

Markdown and PDF are generated from the same structured Neon snapshot. Reports contain article summaries, original/English fields, key points, claims, excerpts/locators, citations, period and freshness statuses, hashes, validation, audit metrics, limitations, and a background appendix. Raw bodies, prompts, credentials, and hidden reasoning are excluded.

PDF generation is worker-side static HTML plus print CSS and headless Chrome/Chromium. The renderer must verify file existence, page count, selectable text, source links, and absence of application chrome. Approved PDFs are private Vercel Blob artifacts accessed with expiring signed URLs; drafts can be previewed as Markdown but are not uploaded.

## Recommended next steps

1. Reconcile the `0014_run_source_periods` backfill and revalidated run statuses on Neon `main`.
2. Run a new weekly collection with at least 10 eligible in-period published sources, targeting 20–30.
3. Require 100% article insight and report-section completeness, citation coverage, and evidence-locator coverage.
4. Configure a worker-side Chrome binary and the three server-side PDF/Blob variables.
5. Human-review the passing brief, export Markdown/PDF, and verify the signed URL.
6. Deploy the API and UI only after Neon/API/UI counts and statuses reconcile.
"""
