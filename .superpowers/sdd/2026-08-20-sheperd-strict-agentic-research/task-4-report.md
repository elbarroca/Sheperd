# Task 4 report: persistence and read-only surfaces

## Status

PASS. Task 4 is implemented on `feat/research-agents-neon`.

The implementation persists and serves the existing structured audit contract: lane, agent, attempt, requested/resolved model, prompt version, sanitized tool arguments, hashes, latency, token counts, errors, source snapshot hashes, distillations, claims/citations, signals, critic/synthesis/validation state, Neon branch and migration metadata, and `as_of`. API projections exclude raw step metadata and legacy unsanitized tool fields from browser responses.

Reviewer fix round 1 is complete: step metadata now passes through an explicit structured-audit allowlist/redaction boundary, including nested call and tool-receipt fields, and failed or missing validation renders as non-decision-ready.

## Changed files

- `research-agents/migrations/0008_audit_surfaces.sql`
- `research-agents/src/sheperd_research/db.py`
- `research-agents/src/sheperd_research/web.py`
- `research-agents/tests/test_db.py`
- `research-agents/tests/test_web.py`
- `founder-intelligence/src/lib/research-api.ts`
- `founder-intelligence/src/components/report-accordion.tsx`
- `founder-intelligence/src/components/report-accordion.test.tsx`
- `founder-intelligence/src/app/sources/page.tsx`

The pre-existing staged founder stylesheet migration, generated files, website, recovery, and unrelated migration files were preserved and excluded from the Task 4 commit.

## API and persistence coverage

- Added the single next migration, `0008_audit_surfaces`, with `sanitized_args` and audit-oriented indexes only.
- Completed read-only health, source catalog, source, distillation, claim, signal, run, run-audit, weekly, and monthly routes.
- Added parameterized filters and bounded pagination across repository queries and API routes.
- Added browser-safe allow-listed audit projections, server-only research API access, no stale fallback, and explicit blocked/failed UI states.

## Exact verification commands and results

- `uv run pytest tests/test_db.py tests/test_web.py` — **12 passed**.
- `uv run pytest` — **109 passed**.
- `uv run ruff check src tests` — **All checks passed**.
- `uv run mypy src` — **Success: no issues found in 20 source files**.
- `pnpm exec vitest run src/components/report-accordion.test.tsx` — **1 test passed**.
- `pnpm lint` — **passed**.
- `pnpm typecheck` — **passed**.
- `pnpm test` — **17 test files, 48 tests passed**.
- `pnpm build` — **passed**; Next.js 16.2.10 compiled, typechecked, generated all 6 pages, and completed route optimization.
- `git diff --cached --check` — **passed with no output** before the implementation commit.

The frontend commands emitted the environment warning that the package requests Node 24.x while the runner is Node 26.0.0; it did not affect results.

## Commits

- Implementation: `eeceb3728bd9d16ab0db835974720412df4d1a19` (`feat: complete Task 4 research audit surfaces`)
- Verification report: follow-up documentation commit containing this file.

## Concerns

- The migration was not applied to a live Neon branch in this run; no Neon credential or connection was available or used.
- The existing dirty migration/rename set remains staged or untracked by the user and was not included.

## Task 4 fix round 1

### Changed behavior

- `record_step` now persists only allow-listed scalar audit fields and safe nested call/attempt/receipt fields. Raw prompts, bodies, reasoning, arbitrary metadata, and credential-bearing values are dropped or redacted before both in-memory and Postgres persistence.
- Report validation with status `failed` or no validation record now shows the existing explicit blocked/failed alert and remains non-decision-ready.
- Added focused regression coverage for both repository implementations and both UI states.

### Exact verification commands and results

- `uv run pytest tests/test_db.py::test_repositories_redact_raw_step_metadata_before_persistence tests/test_db.py::test_in_memory_repository_exposes_structured_step_audit_and_source_hashes tests/test_workflow.py::test_record_step_preserves_provider_attempt_and_input_correlation tests/test_workflow.py::test_workflow_persists_quarantined_seed_leads_without_processing_them` — **4 passed**.
- `uv run pytest tests/test_db.py tests/test_web.py tests/test_workflow.py` — **27 passed**.
- `uv run ruff check src tests` — **All checks passed**.
- `uv run mypy src` — **Success: no issues found in 20 source files**.
- `pnpm exec vitest run src/components/report-accordion.test.tsx` — **1 test file, 3 tests passed**.
- `pnpm lint` — **passed**.
- `pnpm typecheck` — **passed**.
- `pnpm test` — **17 test files, 50 tests passed**.
- `git diff --cached --check` — **passed with no output** before the fix commit.

The frontend commands emitted the existing Node 24.x package-engine warning under Node 26.0.0; it did not affect results. No migration, website, recovery, Neon branch, or credential state was changed.

### Fix-round commits

- Implementation: `0f0fca5869ce06d10578f1c396b02f4d7cc5705c` (`fix: redact audit metadata and block invalid reports`)
- Fix-round report: follow-up documentation commit containing this section.

## Task 4 fix round 2

### Changed behavior

- Tool-call persistence now reuses the audit redaction boundary for query text, receipt fields, and URL inputs. Queries are redacted when sensitive, URL lists are limited to validated HTTP(S) metadata with credentials/query strings removed, and hashes, counts, latency, status, and error codes remain available.
- Reports are decision-ready only when `run.status === "succeeded"` and `validation.status === "pass"`. Missing, partial, failed, or unknown states show an explicit blocked/failed/partial alert with both observed statuses.
- `research-api.ts` now validates health, weekly list/detail, monthly, and supporting evidence payloads before returning `ok`; malformed JSON shapes and unavailable HTTP responses return explicit `unavailable` results.
- Added focused DB, UI state-matrix, API runtime-validation, and Vitest `server-only` test-alias coverage. No migration was added.

### Exact verification commands and results

- `uv run pytest tests/test_db.py::test_tool_call_persistence_redacts_sensitive_queries_and_urls tests/test_db.py::test_postgres_repository_persists_sanitized_tool_arguments` — **2 passed**.
- `uv run pytest tests/test_db.py tests/test_web.py tests/test_workflow.py` — **28 passed**.
- `uv run ruff check src tests` — **All checks passed**.
- `uv run mypy src` — **Success: no issues found in 20 source files**.
- `pnpm exec vitest run src/components/report-accordion.test.tsx src/lib/research-api.test.ts` — **2 test files, 8 tests passed**.
- `pnpm lint` — **passed**.
- `pnpm typecheck` — **passed**.
- `pnpm test` — **18 test files, 55 tests passed**.
- `git diff --cached --check` — **passed with no output** before the implementation commit.

The frontend commands emitted the existing Node 24.x package-engine warning under Node 26.0.0; it did not affect results. The Vitest-only `server-only` alias is test infrastructure for the package’s existing server-only boundary; it does not alter production routing or credentials.

### Fix-round 2 commits

- Implementation: `2845ad2f1cb9a1c84d13677ba8ac4f81559063ca` (`fix: harden audit receipts and API readiness`)
- Fix-round 2 report: follow-up documentation commit containing this section.

## Task 4 fix round 3

### Status

PASS. The three requested reviewer findings are implemented with focused regression coverage.

### Changed behavior

- Mounted the read-only report experience in production at `/`, `/reports/[run_id]`, and `/monthly`. The weekly list uses `ReportLink`, the detail route mounts `ReportAccordion`, and all three routes render the explicit unavailable state without fallback data.
- Added a public run projection used by report payloads, `/api/runs/{run_id}`, and `/api/runs/{run_id}/audit`. It preserves `run_id`, `topic_set`, `status`, `as_of`, `error`, Neon branch, and migration fields while excluding the internal request and seed URLs.
- Required report detail payloads to have matching `brief.run_id`, `run.run_id`, and `validation.run_id` for the requested run. Weekly list payloads also reject inconsistent report identities; malformed or cross-run payloads return `unavailable`.

### Changed files

- `research-agents/src/sheperd_research/web.py`
- `research-agents/tests/test_web.py`
- `founder-intelligence/src/lib/research-api.ts`
- `founder-intelligence/src/lib/research-api.test.ts`
- `founder-intelligence/src/components/report-accordion.test.tsx`
- `founder-intelligence/src/app/page.tsx`
- `founder-intelligence/src/app/reports/[run_id]/page.tsx`
- `founder-intelligence/src/app/monthly/page.tsx`
- `founder-intelligence/src/app/routes.test.tsx`

### Exact verification commands and results

- `uv run pytest tests/test_web.py` — **2 passed**.
- `uv run ruff check src/sheperd_research/web.py tests/test_web.py` — **All checks passed**.
- `uv run mypy src/sheperd_research/web.py` — **Success: no issues found in 1 source file**.
- `pnpm exec vitest run src/lib/research-api.test.ts src/app/routes.test.tsx src/components/report-accordion.test.tsx` — **3 test files, 12 tests passed**.
- `pnpm test` — **19 test files, 59 tests passed**.
- `pnpm lint` — **passed**.
- `pnpm typecheck` — **passed**.
- `pnpm exec next build` — **passed**; Next.js 16.2.10 compiled and exposed `/`, `/monthly`, `/reports/[run_id]`, `/sources`, and `/robots.txt`.
- `git diff --check -- research-agents/src/sheperd_research/web.py research-agents/tests/test_web.py founder-intelligence/src/lib/research-api.ts founder-intelligence/src/lib/research-api.test.ts founder-intelligence/src/components/report-accordion.test.tsx` — **passed with no output**.

The frontend commands emitted the existing Node 24.x package-engine warning under Node 26.0.0; it did not affect results.

### Concerns

- The migration was not applied to a live Neon branch in this run; no Neon credential or connection was available or used.
- Existing dirty migration/rename, website, recovery, generated, and stylesheet work remains outside the scoped changes.
