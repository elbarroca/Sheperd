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
