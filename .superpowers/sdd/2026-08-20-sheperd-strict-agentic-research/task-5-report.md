# Task 5 report

Status: PASS

Fix round 1: normalized monthly rollup calendar buckets to UTC while retaining
the original instant-based date-range filters.

## Implemented

- Added typed daily and weekly cadence inputs to the existing three-lane strict graph.
- Daily runs retain the existing discovery, extraction, distillation, claim/signal persistence, validation, and draft-brief path.
- Weekly runs load bounded trailing seven-day non-seed evidence, run fresh discovery, reconcile retained and fresh claims through the existing critic, and synthesize a cited draft brief.
- Added deterministic InMemory and Postgres monthly rollups grouped by month/date, lane, geography, persisted publisher authority, signal, evidence status, and distinct signal/run counts.
- Fixed monthly rollup month/date bucketing to use UTC consistently in both repositories.
- Added strict JSON CLI commands:
  - `run --cadence daily|weekly --strict --json`
  - `rollup --month YYYY-MM --json`
- Preserved Gemma-only/no-fallback policy, approval/export gates, no-synthesis-without-retained-or-fresh-evidence, seed exclusion from quality coverage, retained-evidence coverage, and cited brief validation.

## Files

- `research-agents/src/sheperd_research/cli.py`
- `research-agents/src/sheperd_research/contracts.py`
- `research-agents/src/sheperd_research/db.py`
- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/src/sheperd_research/workflow.py`
- `research-agents/tests/test_db.py`
- `research-agents/tests/test_task5_reporting.py`

## Verification

- `uv run pytest -q` — PASS; 116 tests collected and passed; exit 0.
- `uv run pytest -q tests/test_task5_reporting.py tests/test_workflow.py tests/test_db.py tests/test_contracts.py tests/test_settings_and_policy.py` — PASS; exit 0.
- `uv run ruff check .` — PASS; exit 0.
- `uv run mypy src` — PASS; 20 source files checked; exit 0.
- Scoped `git diff --check` — PASS.
- `uv run pytest -q tests/test_task5_reporting.py::test_monthly_rollup_buckets_aware_events_in_utc_without_changing_range_filters` — PASS; 1 test passed; exit 0.
- `uv run pytest -q tests/test_task5_reporting.py tests/test_db.py` — PASS; 18 tests passed; exit 0.
- `uv run ruff check src/sheperd_research/db.py tests/test_task5_reporting.py` — PASS; exit 0.

## Commit

- `59afe23d23212e0e2679a3689f3afd172568f997` — `feat: add strict research reporting cadences`
- `d2c9ee6adaa05ac608254b256cc8304a0a7a025a` — `fix: normalize monthly rollups to UTC`

## Concerns

- Live strict daily/weekly and Neon rollup commands were not executed because they require external provider/database credentials and would write external run/report state; tests use the existing in-memory fixtures.
- The existing source contract has no separate authority column, so rollups use the persisted `sources.publisher` value as authority and add no migration.
- PostgreSQL date-range predicates remain against the raw `timestamptz`; only month/date projection is converted to UTC.
- Existing unrelated staged migration/user work remains untouched in the worktree.
