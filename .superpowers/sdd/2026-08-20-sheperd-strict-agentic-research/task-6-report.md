# Task 6 report: strict end-to-end gates

## Status

PARTIAL / BLOCKED. Local code, schema, persistence, API/UI, source-map, and
project checks pass. The strict runtime cannot reach PASS because the live
Gemma request is rate-limited. No alternate model, provider, fallback, review,
export, or deployment was used.

## Scope and preservation

- Checkout: `feat/research-agents-neon`, starting `HEAD`
  `a0d7fc2ca36bf8126a13ff15516747466fff7db6`.
- Existing staged/unstaged migration and user work was preserved; no reset,
  revert, subagent, website edit, recovery edit, or public deployment occurred.
- The ignored repository-root `.env.local` was changed only to set
  `OPENROUTER_FALLBACK_MODELS=`. No credential value was printed or committed.

## Research-agent gates

| Command | Result | Evidence |
|---|---|---|
| `uv run ruff check .` | PASS | `All checks passed!` |
| `uv run mypy src` | PASS | 20 source files; no issues |
| `uv run pytest` | PASS | 117 passed in 1.00s |
| `uv lock --check` | PASS | 67 packages resolved; exit 0 |
| `uv run sheperd-research source-map --check --strict --json` | PASS | 43 sources, 43 enabled, 33 required, no required failures; weights US 60%, Mexico 20%, Europe 15%, global 5% |
| `uv run sheperd-research doctor --json` | BLOCKED | Neon pooled/direct DB checks PASS, migration `0008_audit_surfaces`, Tavily Search+Extract PASS; OpenRouter health failed with typed `rate_limit` evidence |
| `uv run sheperd-research model-check --json` | BLOCKED | Live capability manifest proves Gemma is free and supports tools/structured output; health request failed `TooManyRequestsResponseError`, one attempt, no retry/fallback |
| `uv run sheperd-research mcp-check --json` | BLOCKED | Service reports host-controlled Tavily/Neon MCP checks unavailable; no MCP connector was installed or available |
| `uv run sheperd-research migrate` | PASS | First serialized run applied `0008_audit_surfaces.sql`; second run returned `No migrations applied; database is current.` |
| `uv run sheperd-research rollup --month 2026-08 --json` | PASS | Neon-backed monthly rollups returned with `status=pass` |

The connected pooled/direct URLs and configured project/branch identity were
read-only checked as Neon targets; identifiers are intentionally redacted.
The direct SQL identity check matched the configured Neon project and branch.

## Live strict runtime gates

| Command | Result | Redacted evidence |
|---|---|---|
| `uv run sheperd-research agent-check --as-of 2026-08-20T18:00:00Z --json` | PARTIAL / exit 2 | Live Gemma capability PASS; discovery attempt failed with `error_code=rate_limit`, `tool_calls=0`, no resolved model, no fallback |
| `uv run sheperd-research e2e --profile canary --run-id task6-canary-20260820T180000Z --as-of 2026-08-20T18:00:00Z --json` | FAILED / exit 2 | Environment/capability PASS; all three lanes failed at Gemma discovery; 0 sources, 0 distillations, 0 claims, 0 Search calls, 0 Extract calls, no brief, no validation PASS |
| `uv run sheperd-research run --topic-set dnd-port --cadence weekly --strict --run-id task6-weekly-20260820T200000Z --as-of 2026-08-20T20:00:00Z --max-sources 30 --json` | FAILED / exit 2 | `status=failed`, `validation_status=blocked`, 0 sources/claims/distillations, no brief; regulatory, us-ports, and mexico discovery all failed on the same provider condition |
| `uv run sheperd-research validate --run-id task6-canary-20260820T180000Z` | FAILED / exit 2 | 0 sources/claims, 0% citation coverage, empty lane coverage, free-model check PASS, required Search/Extract checks fail closed |

The provider’s direct recorded health evidence was:

```text
requested_model=google/gemma-4-26b-a4b-it:free
capability_source=live
free=true supports_tools=true supports_structured_outputs=true
attempt=1 error_type=TooManyRequestsResponseError error_code=rate_limit
retry_count=0 fallback_models=[]
```

The failed-run records remain in Neon as audit evidence and were not reviewed
or exported. Only a strict `PASS` may enter those actions.

## Persistence, API/UI, and contract checks

- `uv run pytest` includes idempotence, checkpoint allow-list, provider
  failure, validation, DB redaction, tool receipt, and web contract coverage;
  the focused Task 6 subset also passed: **11 passed**.
- Read-only Neon `PostgresRepository.health()` returned `status=pass` and
  migration `0008_audit_surfaces`.
- A live `TestClient` probe returned 200 for health, source catalog, runs,
  sources, distillations, claims, signals, briefs, monthly reports, and the
  corresponding HTML list/detail surfaces. The failed weekly report correctly
  returned 404 because no brief was written.
- The probe found no credential-key markers in API or HTML responses.
- Path/catalog check passed: `dnd-port` loaded, topics/source-catalog paths
  resolved, all 43 catalog sources were enabled, and the Obsidian output
  parent existed.
- Local Markdown link check passed for the README, plan, and task brief:
  zero missing local links.
- Scoped working-tree/index `git diff --check` passed.
- Tracked-content secret scan passed: no credential-shaped private key, bearer
  token, database URL credential, or non-empty API-key assignment was found.

## Founder-intelligence

- `corepack pnpm lint` — PASS.
- `corepack pnpm typecheck` — PASS.
- `corepack pnpm test` — PASS; 19 files, 59 tests.
- `corepack pnpm validate:data` — PASS; 95 files, 971 chunks, 53 sources,
  12 blockers, 8 experiments.
- `corepack pnpm build` — PASS; Next.js compiled and generated all routes.
- Existing warning: package requests Node 24.x; runner is Node 26.0.0.

## Website checks

- `corepack pnpm lint` — PASS.
- `corepack pnpm typecheck` — PASS.
- `corepack pnpm test` — PASS; 3 files, 14 tests.
- `corepack pnpm build` — PASS; preview build completed.
- `corepack pnpm test:e2e` — PARTIAL / exit 1; 54 tests, 6 passed, 36 failed,
  12 skipped. Firefox and WebKit executables are not installed. Chromium also
  reports existing visual-baseline mismatches, stale content selectors, and a
  serious list/listitem accessibility violation. Website and recovery were
  explicitly outside this task and were not modified.

## Concerns and blockers

1. OpenRouter is rate-limiting the configured free Gemma model. Strict policy
   correctly stops without retrying a 429 or selecting any fallback.
2. MCP checks remain host-controlled and unavailable in this service process.
3. The initial migration invocation overlapped the first canary invocation;
   that canary observed the pre-0008 schema while migration was in flight. A
   serialized migration rerun then returned current, and the final doctor/API
   checks confirmed `0008_audit_surfaces`.
4. Website browser installation, visual baselines, content selectors, and
   accessibility findings remain existing project work and were not changed.

No strict PASS, approval, export, CRM/customer operation, alternate provider,
paid model, or public deployment is claimed.
