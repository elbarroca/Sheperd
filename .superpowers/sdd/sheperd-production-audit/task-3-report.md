# Task 3 report: Integration verification and deployment readiness

## Status

Blocked for production readiness. The scoped integration defects are fixed and covered by regression tests. Static backend/frontend gates pass. Runtime readiness is blocked by live provider capacity, missing database migration `0013_run_sources`, unavailable in-process MCP connectors, an invalid canary E2E command in the brief, and protected API preview access.

No shared branch push, production promotion, report approval, or report export was performed.

## Checkout

- Repository: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD`
- Branch: `feat/evidence-grade-insights`
- Starting state: clean branch, ahead of `origin/feat/evidence-grade-insights`
- External writes performed: Vercel Preview deployments only
- Production writes skipped: database migration, production deployment, production promotion, report approval/export

## Integration fixes

1. Postgres brief summaries
   - `PostgresRepository.list_brief_summaries()` now returns canonical `report_section_count` with `report_sections_complete` and `report_section_completeness`.
   - Added a production-shaped ready-row regression test requiring `report_section_count=5`, `report_sections_complete=5`, `report_section_completeness=1.0`, and `decision_ready=true`.
   - Summary parsing now maps fields by name before deriving `blocking_reasons` and `quality_ready`, avoiding stale row-index promotion.

2. Frontend readiness
   - `isDecisionReadySummary()` now requires canonical denominators for article and report-section completeness.
   - Ready/status flags no longer promote summaries when completeness ratios are present without `article_count` or `report_section_count`.
   - Added regression coverage for missing canonical denominators.

3. SQL report-section readiness
   - Verified the summary SQL uses all-item semantics through `NOT EXISTS` over every report-section bullet.
   - Kept validator-aligned rules: non-empty section, valid bullet text, known citations, and required `why_it_matters`/`next_step` for actionable or v6 sections.
   - Added/updated summary tests to assert completeness count and canonical denominator.

4. Tavily malformed nested results
   - Search and extract now fail closed with stable `malformed_output` classification for malformed nested `results` entries.
   - Added regression coverage for missing search URL and malformed extract result payloads.

## Red tests confirmed

- `uv run pytest tests/test_db.py::test_postgres_brief_summaries_return_production_ready_section_metrics tests/test_provider_failures.py::test_tavily_malformed_nested_result_entries_are_explicit -q` failed before implementation:
  - Postgres summary mapped `decision_ready` incorrectly because the canonical denominator was absent from field mapping.
  - Tavily nested malformed entry had no stable `malformed_output` code.
- `pnpm test -- src/components/report-accordion.test.tsx` failed before implementation:
  - Missing denominator summary still rendered `Decision-ready`.
  - Ready fixture without full canonical summary fields no longer passed under the stricter contract.

## Focused verification

- `uv run pytest tests/test_db.py::test_postgres_brief_summaries_recompute_readiness_from_persisted_evidence tests/test_db.py::test_postgres_brief_summaries_validate_report_section_text_and_counts tests/test_db.py::test_postgres_brief_summaries_return_production_ready_section_metrics tests/test_provider_failures.py::test_tavily_malformed_nested_result_entries_are_explicit -q` -> pass, 4 tests.
- `uv run pytest tests/test_db.py tests/test_provider_failures.py -q` -> pass, 47 tests.
- `uv run ruff check src/sheperd_research/db.py src/sheperd_research/providers/tavily.py tests/test_db.py tests/test_provider_failures.py` -> pass.
- `pnpm test -- src/components/report-accordion.test.tsx` -> pass, 14 tests.
- `pnpm test` -> pass, 3 files / 36 tests.

## Static gates from task brief

Backend, from `research-agents/`:

- `uv run ruff check .` -> pass.
- `uv run mypy src` -> pass, no issues in 23 source files.
- `uv run pytest` -> pass, 207 tests.
- `uv lock --check` -> pass, 67 packages resolved.

Frontend, from `founder-intelligence/`:

- `pnpm lint` -> pass.
- `pnpm typecheck` -> pass.
- `pnpm test` -> pass, 3 files / 36 tests.
- `pnpm build` -> pass, Next 16.2.10 production build.

Local frontend caveat: pnpm printed `Unsupported engine: wanted {"node":"24.x"} (current: {"node":"v26.0.0","pnpm":"9.15.4"})` for all frontend commands. Commands exited 0. Vercel remote install used pnpm 10.33.2.

## Runtime diagnostics from task brief

Backend, from `research-agents/`:

- `uv run sheperd-research doctor --json` -> blocked.
  - Database pooled/direct checks passed.
  - Environment loaded from repository `.env.local`.
  - OpenRouter health blocked with HTTP 429 `rate_limit` on `google/gemma-4-26b-a4b-it:free`.
  - Tavily Search and Extract passed through secondary key slot.
  - Database migration reported `0012_article_insight_quality`.

- `uv run sheperd-research audit --json` -> blocked.
  - Same OpenRouter 429 provider blocker.
  - Database counts observed: sources 46, distillations 59, claims 335, signals 70.
  - Report state observed: active 0, archived 50, failed 25, partial 21, succeeded 3.
  - Validation observed: pass 0, blocked 21, failed 29.
  - Quality observed: article insight completeness 0.033898, report section completeness 0.214286.

- `uv run sheperd-research model-check --allow-free-fallbacks --strict --json` -> pass.
  - Primary and first fallback attempts hit 429 rate limits.
  - Resolved through free fallback `nvidia/nemotron-3-super-120b-a12b:free`.
  - One configured candidate, `openai/gpt-oss-20b:free`, was skipped because it was not present in the live manifest.

- `uv run sheperd-research mcp-check --json` -> blocked.
  - Process reported MCP connectors are host-controlled and unavailable inside the service process.
  - Requires host-level read-only Neon/Tavily MCP smoke checks.

- `uv run sheperd-research agent-check --allow-free-fallbacks --verbose --json` -> pass.
  - Primary and first two fallbacks hit OpenRouter 429.
  - `nvidia/nemotron-3-super-120b-a12b:free` failed with `agent_loop` after repeated Tavily calls.
  - `dots-studio/dots-3-note-preview:free` failed with `model_unavailable`.
  - Final success resolved to `nvidia/nemotron-nano-9b-v2:free`.
  - Tavily search/extract succeeded through secondary key slot.

- `uv run sheperd-research e2e --profile canary --allow-free-fallbacks --verbose --json` -> failed before execution.
  - CLI requires `--run-id`; the exact task-brief command is incomplete.
  - No canary E2E was run because choosing a run ID would expand beyond the exact command and the live database is missing migration `0013_run_sources`.

## Local API and UI contract checks

- `uv run pytest tests/test_web.py tests/test_archive.py tests/test_vercel_app.py -q` -> pass, 14 tests.
  - Covers local FastAPI routes, archive scope behavior, markdown raw-body redaction, and Vercel app fail-closed behavior.

- Live read-only TestClient check against configured `DATABASE_URL`:
  - `/api/health` returned HTTP 200 JSON with health keys.
  - `/api/reports/weekly?limit=1` failed with `psycopg.errors.UndefinedTable: relation "run_sources" does not exist`.
  - Cause: configured database migration is still `0012_article_insight_quality`; this branch requires `0013_run_sources`.
  - No migration was run because Task 3 requested read-only contract checks and did not authorize production database mutation.

- Frontend unavailable, empty, partial, failed, malformed, and no-decision-ready UI states are covered by the passing Vitest suite:
  - `src/lib/research-api.test.ts`
  - `src/app/routes.test.tsx`
  - `src/components/report-accordion.test.tsx`

## Secret scan

- Broad scan found only docs, tests, placeholders, and code references.
- Narrow credential-shaped scan outside generated/test/docs areas returned no matches.
- No secrets were printed in this report.

## Preview deployment

API preview:

- Command: `vercel deploy --yes` from `research-agents/`.
- Result: READY.
- Preview URL: `https://sheperd-research-dvj60wuj6-elbarrocas-projects.vercel.app`
- Deployment ID: `dpl_8ytx5VMmwYpQzqAeQXWYPnJ9HpeQ`
- Smoke:
  - Browser-like requests to API paths returned Vercel HTML instead of API JSON.
  - `Accept: application/json` request to `/api/health` returned HTTP 401 JSON.
  - Classification: preview access/protection blocks API contract smoke.

Dashboard preview:

- First command from `founder-intelligence/` failed because Vercel project root is configured as `founder-intelligence`, causing the CLI to look for `founder-intelligence/founder-intelligence`.
- Retried from repository root with `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID` selectors.
- Result: READY.
- Preview URL: `https://sheperd-founder-intelligence-o49y09nb5-elbarrocas-projects.vercel.app`
- Deployment ID: `dpl_28yzWV5sH6JFuj1bzuaZ1x22mWDE`
- Smoke:
  - `/` returned HTTP 200 HTML and showed `No decision-ready report yet`.
  - `/sources` returned HTTP 200 HTML.
  - `/monthly` returned HTTP 200 HTML.
  - The dashboard did not show the unavailable state in this preview smoke, but the API preview itself is protected and the local live API route contract is blocked by missing migration.

## Blockers

1. Apply migration `0013_run_sources` to the target database before live API/report routes can pass. Current database reports `0012_article_insight_quality`.
2. OpenRouter primary health is rate-limited with HTTP 429, blocking `doctor` and `audit`.
3. `mcp-check` cannot run in-process because MCP connectors are host-controlled and unavailable to the service process.
4. The task-brief E2E command is invalid without `--run-id`; a valid canary run ID is needed after the schema/provider gates are clear.
5. API preview smoke is blocked by Vercel protection/auth behavior, returning 401 JSON or Vercel HTML instead of public API JSON.
6. Local frontend shell uses Node v26.0.0 while the project declares Node 24.x. Static gates still passed.

## Deployment readiness decision

Not ready for production promotion.

Code-level integration findings are fixed and statically verified. Runtime readiness remains blocked until the database migration, provider capacity, host MCP checks, valid canary E2E run, and preview API access checks pass.
