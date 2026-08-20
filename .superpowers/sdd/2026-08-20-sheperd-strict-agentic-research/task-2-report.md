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
