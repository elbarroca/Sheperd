# Task 4 report: persistence and read-only surfaces

## Status

PASS. Task 4 is implemented on `feat/research-agents-neon`.

The implementation persists and serves the existing structured audit contract: lane, agent, attempt, requested/resolved model, prompt version, sanitized tool arguments, hashes, latency, token counts, errors, source snapshot hashes, distillations, claims/citations, signals, critic/synthesis/validation state, Neon branch and migration metadata, and `as_of`. API projections exclude raw step metadata and legacy unsanitized tool fields from browser responses.

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
