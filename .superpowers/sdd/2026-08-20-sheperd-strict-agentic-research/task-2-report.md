# Task 2 Report: Explicit LangChain Agents

## Status

Completed. The provider now uses named `create_agent` workers backed by the exact
Gemma `ChatOpenRouter` model, without a legacy structured-output or model-chain path.
Workflow discovery fails closed unless it receives model-issued lane discovery.

## Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/src/sheperd_research/workflow.py`
- `research-agents/tests/test_openrouter_agents.py`
- `research-agents/tests/test_provider_failures.py`
- `research-agents/tests/test_workflow.py`

## Commits

- `9db223c feat: enforce agent-only research workflow`

## Verification

- `uv run pytest tests/test_openrouter_agents.py tests/test_provider_failures.py tests/test_workflow.py tests/test_validators.py` — 37 passed.
- `uv run pytest` — 61 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).

## Concerns

- No live Tavily or OpenRouter request was made; tests use bounded provider fixtures and validate receipts, scopes, schemas, citation gates, and failure paths.

## Fix Round 1

### Status

Completed. Discovery now fails closed on unverifiable returned source metadata,
tool failures, incomplete extraction, and out-of-budget discovery operations.
The workflow no longer performs a direct Tavily extraction fallback.

### Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/src/sheperd_research/workflow.py`
- `research-agents/tests/test_openrouter_agents.py`
- `research-agents/tests/test_workflow.py`

### Commit

- `d845164 fix: fail closed on invalid research evidence`

### Fixes

- Validates returned Tavily host/domain, publisher, geography, and inclusive
  date-window metadata in the provider and repeats lane scope validation in the
  workflow boundary. Lane geography is preserved from returned evidence only.
- Enforces a combined Search+Extract call budget and bounded discovery tool-input
  size; discovery also consumes the workflow LLM call/input budget.
- Treats only succeeded `ToolMessage` receipts as tool success and rejects failed
  or incomplete requested extraction output.
- Removes workflow-owned extraction; every selected source must arrive with
  nonempty agent-extracted content.
- Limits distillation citations to the distilled source and limits critic and
  synthesis URL sets to validated claim citations.

### Verification

- `uv run pytest` — 65 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).

### Concerns

- No live Tavily or OpenRouter request was made. Strict scope metadata validation
  requires Tavily adapters to provide a verifiable publisher, publication date,
  and geography for every returned source; otherwise the lane correctly fails.

## Fix Round 2

### Status

Completed. Live Tavily results now receive lane geography only from returned
metadata or explicit domain/query geography catalogs before strict scope gates.
Failed, unknown, malformed, and unpaired tool receipts are terminal.

### Commit

- `85fda9b fix: validate Tavily research receipts`

### Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/src/sheperd_research/cli.py`
- `research-agents/tests/test_openrouter_agents.py`
- `research-agents/tests/test_settings_and_policy.py`

### Fixes

- Adds explicit domain and query geography catalogs, restricted to the current
  lane's allowed geographies, before source validation.
- Records validation failures from every Search and Extract boundary path; rejects
  failed, unknown, unpaired, malformed, and unsucceeded receipts, then checks
  combined discovery budgets after agent execution.
- Makes CLI validation count only succeeded receipts and require succeeded Search
  and Extract calls in every lane.

### Verification

- `uv run pytest -q` — 68 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).

### Concerns

- No live Tavily or OpenRouter request was made. New domains or query families
  without a catalog or returned geography deliberately fail scope validation.

## Fix Round 3

### Status

Completed. Geography enrichment now uses only configured query and domain evidence
plus the explicit port catalog. Receipt parsing rejects every malformed, unpaired,
unsucceeded, or operation-invalid tool result.

### Commit

- `2ec0441 fix: harden research geography receipts`

### Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/tests/test_openrouter_agents.py`

### Fixes

- Extends configured US-port domain and city-query evidence for Oakland, PANYNJ,
  Georgia Ports, and all configured query families without assigning geography
  outside the active lane scope.
- Emits failed receipts for malformed calls, non-list call collections, unpaired
  tool messages, missing statuses, invalid JSON, and payloads that do not match
  Search or Extract success schemas.

### Verification

- `uv run pytest -q` — 70 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).

### Concerns

- No live Tavily or OpenRouter request was made. Results without configured
  domain/query evidence or returned geography remain fail-closed by design.

## Fix Round 4

### Status

Completed. Malformed, unknown, and unpaired tool activity is retained as failed,
redacted audit evidence; Search and Extract success payloads now require exact
schemas. Geography configuration contains only scoped domains and query families.

### Commits

- `27d6d16 fix: close Task 2 receipt review`
- `572c739 chore: track research provider dependencies`

### Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/tests/test_openrouter_agents.py`
- `research-agents/config/topics.yml`
- `research-agents/src/sheperd_research/topics.py`
- `research-agents/src/sheperd_research/__init__.py`
- `research-agents/src/sheperd_research/providers/__init__.py`
- `research-agents/src/sheperd_research/providers/errors.py`
- `research-agents/src/sheperd_research/validators.py`

### Fixes

- Preserves every parsed receipt in failed-attempt metadata, marks unknown tools
  failed, and emits one redacted failed receipt for malformed top-level results.
- Requires exact Search and Extract payload keys, typed source fields and URLs,
  a non-boolean integer extraction count, and count equality.
- Removes `apmterminals.com`, `maersk.com`, `hapag-lloyd.com`, and `gcaptain.com`
  from geography-scoped discovery domains; removes the unscoped fifth query and
  recognizes Houston as Gulf evidence. Tests cover every remaining domain and query.
- Tracks the minimal topic/package/provider files required for the Task 2 tests to
  import from a clean checkout without relying on unrelated untracked files.

### Verification

- `uv run pytest tests/test_openrouter_agents.py -q` — passed.
- Clean detached worktree focused run — 34 passed; package import resolved inside
  the detached worktree.
- `uv run pytest` — 82 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).

### Concerns

- No live Tavily or OpenRouter request was made. Exact Gemma, no fallback, Search +
  Extract, redaction, budgets, and citation gates remain unchanged.

## Fix Round 5 (Final)

### Status

Completed. Seed-only leads no longer enter extraction or distillation, discovery
defaults remain allowlisted, authoritative domains prevent ambiguous geography
union, and unmatched tool requests persist as failed receipts.

### Files

- `research-agents/src/sheperd_research/providers/openrouter.py`
- `research-agents/src/sheperd_research/topics.py`
- `research-agents/src/sheperd_research/workflow.py`
- `research-agents/src/sheperd_research/db.py`
- `research-agents/tests/test_openrouter_agents.py`
- `research-agents/tests/test_validators.py`
- `research-agents/tests/test_workflow.py`
- `research-agents/pyproject.toml`
- `research-agents/uv.lock`

### Fixes

- Retains configured gCaptain, LinkedIn, and other supplied leads as `seed-only`
  source metadata while excluding every seed-only record from snapshot extraction
  and source distillation. LinkedIn and paywall-marked URLs remain non-extractable.
- Makes configured authoritative domain geography override ambiguous query evidence;
  Port Houston now resolves to Gulf only, without an inferred East Coast label.
- Gives missing topic configuration the exact configured discovery allowlist and
  LinkedIn exclusion instead of unrestricted discovery.
- Converts requested tool calls without a matched result to failed receipts before
  attempt metadata can be persisted.
- Tracks the service manifests and remaining import/test dependencies required for
  Task 2 tests to collect from a clean scoped head.

### Verification

- Red/green regressions for all four behavior findings — 4 passed after failing for
  the reported reasons.
- `uv run pytest` — 84 passed.
- `uv run ruff check src tests` — passed.
- `uv run mypy src` — passed (19 source files).
- `uv lock --check` — passed (67 packages resolved).
- Temporary clean scoped-head run of Task 2 tests — 59 passed; `pyproject.toml`,
  `uv.lock`, `db.py`, and `test_validators.py` were present and collection succeeded.

### Concerns

- No live Tavily or OpenRouter request was made. Exact Gemma, no fallback, strict
  Search + Extract, operation-specific payload schemas, budgets, redaction, and
  citation gates remain unchanged.
