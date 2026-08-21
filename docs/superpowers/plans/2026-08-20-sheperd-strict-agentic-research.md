# SheperD Strict Agentic Research and Global Source Map

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Build a fail-closed, Gemma-only LangGraph/LangChain research system that discovers, distills, validates, stores, and displays maritime/D&D intelligence from U.S., Mexico, Europe, and global sources.

**Global constraints:** Use only `google/gemma-4-26b-a4b-it:free`; remove configured model fallbacks; do not use `openrouter/free`; set OpenRouter `allow_fallbacks=false`; retry only the same model once for transport timeout; rate limits, unavailable Gemma, malformed output, or failed extraction fail required runs; preserve structured packets/citations/hashes/metrics only; never store prompts, raw bodies, API keys, or hidden reasoning; Neon remains `main`; no publishing, CRM, customer data, or paywall bypass.

## Tasks

### Task 1: Strict OpenRouter policy

Update settings, capabilities, provider, diagnostics, CLI, `.env.example`, README, and tests. Require live Gemma capability metadata for free pricing, tool calling, and structured output. Reject fallback configuration, router models, paid models, and malformed IDs. Configure `require_parameters=true` and `allow_fallbacks=false`. Record model/attempt/request/latency/token/hash/error metadata. Fail 429 immediately; retry only the same Gemma request once on transport timeout.

### Task 2: Explicit LangChain agents

Use `create_agent` with `ChatOpenRouter` for regulatory, U.S. ports, Mexico/Europe, distillation, critic, and weekly synthesis workers. Discovery must have model-issued Tavily Search and Extract calls; no deterministic prefetch. Require at least one Search and Extract call per lane, enforce source/geography/date/query scope, bounded budgets, strict schemas, and no hidden reasoning. Add tests for tool loops, zero-tool failure, invalid URLs, failed extraction, citations, and one distillation per extracted source.

### Task 3: Worldwide source catalog

Create `research-agents/config/source_catalog.yml` with source ID, region, jurisdiction, authority tier, domain, URL, source type, signal types, access, enabled/required flags, and cadence. Cover U.S. regulatory/courts, U.S. West Coast, U.S. East/Gulf, Mexico, Europe, global multilaterals, and public trade sources. Weight coverage U.S. 60%, Mexico 20%, Europe 15%, global 5%. Exclude LinkedIn, paywalls, and inaccessible scraping. Add `source-map --json` and `source-map --check --strict --json` with redacted status output and tests.

### Task 4: Persistence and read-only surfaces

Add the next migration only for missing audit/index fields. Persist run/lane/agent/attempt/model/prompt-version/tool/hash/result/latency/token/error/source/distillation/claim/signal/critic/synthesis/validation/branch/migration/as-of data append-safely. Keep GIN/B-tree indexes and no vector search. Add or complete source-catalog, source, distillation, claim, signal, run-audit, weekly, and monthly read-only API routes. Update the founder dashboard to display sources, distillations, citations, signals, models, tool receipts, validation, and blocked/failed states.

### Task 5: Reporting cadence

Add daily and weekly strict runs. Daily runs collect, extract, distill, persist, and create draft briefs. Weekly runs combine seven days of evidence with fresh discovery, critic reconciliation, and cited synthesis. Add deterministic monthly SQL rollups by lane, geography, authority, signal, evidence, and date. No automatic approval or publishing.

### Task 6: Gates

Run Ruff, mypy, pytest, lock validation, strict doctor/model/source checks, migration, strict agent-check, and strict canary. Then run a full weekly gate with exactly Gemma, three lanes, Search+Extract per lane, at least 10 unique sources with 20–30 target, U.S. regulatory/West/East-Gulf/Mexico/Europe coverage, source distillation completeness, five cited claims, 100% citation coverage, no future dates or duplicate hashes, critic/synthesis completion, Neon persistence, API/UI rendering, and secret scans. Only strict `PASS` can be reviewed/exported.
