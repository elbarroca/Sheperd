# Task 6 report: final-review release fix pass

## Status

PARTIAL / BLOCKED. The committed research-agent tree passes local release
gates and the clean-archive receipt. Strict live execution remains blocked by
the recorded OpenRouter Gemma rate limit. No live Gemma or Neon PASS is claimed.

## Scope and preservation

- Base review target: `6b8c362a00a96132b942c102f1b7ae91f956f957`.
- Branch: `feat/research-agents-neon`.
- Code commit: `122e88b9fb2f8e05357f1562876c39ca4dd29055`
  (`fix: close final research-agent release findings`).
- Existing unrelated staged/unstaged migration, Obsidian, website, recovery,
  and founder-intelligence work was preserved. This pass did not edit website
  or recovery files, deploy, push, reset, revert, or dispatch subagents.

## Implemented findings

- Added the required tracked migrations `0001`-`0007`, `0009`, Neon provider,
  Obsidian exporter, and their required tests/configured runtime dependencies.
- Guarded `0007` against absent checkpoint tables and redacted checkpoint
  metadata, channel content, blobs, and writes. The exact Gemma-only default is
  historical-safe in `0002` and enforced/idempotently normalized by `0009`.
- Kept exactly three lanes; the Mexico lane now covers Mexico and Europe with
  Europe queries, authoritative domains, and strict geography acceptance.
- Quarantined malformed/unsupported seed URLs; centralized normalization now
  strips query strings and credential-bearing URL material before persistence.
- Made audit-step and validation inserts immutable no-ops on conflicts while
  retaining the separate run projection update.

## Redacted verification receipts

| Command | Result |
|---|---|
| `uv run pytest` | PASS — 126 passed in 1.04s |
| Focused touched-area pytest | PASS — 93 passed |
| `uv run ruff check .` | PASS — `All checks passed!` |
| `uv run mypy src` | PASS — no issues in 20 source files |
| `uv lock --check` | PASS — 67 packages resolved |
| `git diff --check -- research-agents` | PASS |
| `uv run sheperd-research source-map --check --strict --json` | PASS — 43 sources, 43 enabled, 33 required, no required failures; weights US 60%, Mexico 20%, Europe 15%, global 5% |
| Clean `git archive HEAD` import/migration receipt | PASS — CLI, Neon, and exporter imports; ordered `0001` through `0009` present |

Focused regressions cover fresh migration ordering without credentials,
checkpoint prompts/raw bodies/keys/arbitrary content absence, Europe gating,
seed quarantine, URL persistence sanitization, Gemma migration policy, and
append-only audit/validation reruns.

## Live blockers

The latest recorded live provider evidence remains:

```text
requested_model=google/gemma-4-26b-a4b-it:free
capability_source=live
free=true supports_tools=true supports_structured_outputs=true
attempt=1 error_type=TooManyRequestsResponseError error_code=rate_limit
retry_count=0 fallback_models=[]
```

The live strict run therefore remains blocked; no paid model, router/free
model, retry, fallback, review, export, or deployment was used. Neon migration
application and live persistence were not re-run in this code-only fix pass;
the committed migration set still requires the authorized Neon application and
a fresh live rerun after provider capacity recovers. Host-controlled MCP checks
remain unavailable.
