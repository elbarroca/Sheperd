DONE_WITH_CONCERNS

Changed files
- research-agents/.env.example
- research-agents/README.md
- research-agents/src/sheperd_research/cli.py
- research-agents/src/sheperd_research/diagnostics.py
- research-agents/src/sheperd_research/providers/capabilities.py
- research-agents/src/sheperd_research/providers/openrouter.py
- research-agents/src/sheperd_research/settings.py
- research-agents/tests/test_capabilities.py
- research-agents/tests/test_openrouter_agents.py
- research-agents/tests/test_provider_failures.py
- research-agents/tests/test_settings_and_policy.py

Commit hashes
- base: 100ff85d49c28bc6210c748c85a741291cb4ba98
- implementation: bc2104d1570c65fb1342f746769bd2b778b2739f

Exact tests and outputs
- `cd research-agents && uv run pytest tests/test_settings_and_policy.py tests/test_capabilities.py tests/test_openrouter_agents.py tests/test_provider_failures.py`
  - `23 passed in 0.55s`
- `cd research-agents && uv run ruff check src tests/test_settings_and_policy.py tests/test_capabilities.py tests/test_openrouter_agents.py tests/test_provider_failures.py`
  - `All checks passed!`
- `cd research-agents && uv run mypy src`
  - `Success: no issues found in 19 source files`
- `cd research-agents && uv run pytest`
  - `45 passed in 0.41s`

Concerns
- The repository already contains unrelated staged and untracked work outside this task, including the rest of the `research-agents` tree. Per scope, that work was preserved and not committed here, so this commit contains only the strict OpenRouter policy surface and its Task 1 tests.

---

Fix round 1

Status
- DONE_WITH_CONCERNS

Addressed reviewer findings
- Enforced exact `google/gemma-4-26b-a4b-it:free` in request defaults, model validation, resolved-model validation, CLI checks, and final validation.
- Removed permissive resolved-model substitution when OpenRouter metadata is absent; missing or non-exact resolved models now fail closed.
- Made discovery, extraction, distillation, critique, synthesis, and validation fail closed on provider/schema/validation errors instead of continuing partial runs.
- Required a live capability report at the OpenRouter provider boundary and rejected raw fallback configuration before any effective fallback chain could exist.
- Removed Tavily retry behavior and kept retry scope on the model transport path only.
- Switched workflow/provider audit reads to per-call task-local metadata instead of shared attribution state.
- Updated the report language and verification scope so this fix does not claim standalone reproducible ancestry beyond the current checkout.
- Recorded failed legacy timeout attempts before the strict Gemma retry path.

Changed files
- research-agents/src/sheperd_research/cli.py
- research-agents/src/sheperd_research/contracts.py
- research-agents/src/sheperd_research/diagnostics.py
- research-agents/src/sheperd_research/providers/openrouter.py
- research-agents/src/sheperd_research/providers/tavily.py
- research-agents/src/sheperd_research/validation.py
- research-agents/src/sheperd_research/workflow.py
- research-agents/tests/test_openrouter_agents.py
- research-agents/tests/test_provider_failures.py
- research-agents/tests/test_settings_and_policy.py
- research-agents/tests/test_validation.py
- research-agents/tests/test_workflow.py

Commit hashes
- prior Task 1 commit: bc2104d1570c65fb1342f746769bd2b778b2739f
- fix round 1 commit: 0f2531fa699b3c6a28f24d376d515189fe88e0df

Covering tests
- `cd research-agents && uv run pytest tests/test_contracts.py tests/test_capabilities.py tests/test_settings_and_policy.py tests/test_validation.py tests/test_openrouter_agents.py tests/test_provider_failures.py tests/test_workflow.py`
  - `35 passed in 0.42s`
- `cd research-agents && uv run ruff check src/sheperd_research tests/test_contracts.py tests/test_capabilities.py tests/test_settings_and_policy.py tests/test_validation.py tests/test_openrouter_agents.py tests/test_provider_failures.py tests/test_workflow.py`
  - `All checks passed!`
- `cd research-agents && uv run mypy src/sheperd_research`
  - `Success: no issues found in 19 source files`

Concerns
- The repository still contains unrelated staged and untracked work outside this fix, including broader `research-agents` service files that were preserved by request. This fix commit is intentionally scoped to the strict OpenRouter Task 1 surface and its direct tests, so the verification above is checkout-scoped and is not presented as standalone service ancestry.

---

Fix round 2

Status
- DONE_WITH_CONCERNS

Addressed reviewer findings
- Removed the last `source.snippet` fallbacks from extraction and distillation; every retained source now requires extracted body content or the run fails.
- Restricted retry classification to explicit transport timeout exception types and cause/context chains; message text alone no longer triggers retry.
- Preserved provider attempt numbers in step metadata and added per-source input correlation for concurrent distillation attempts, while keeping persisted step keys unique.
- Removed raw model-issued query text and URL lists from persisted tool receipts; receipts now retain only hashes, counts, identifiers, status, and result hashes/counts.
- Rejected any nonempty raw fallback configuration before normalization in both settings policy evaluation and direct provider construction.
- Extended capability reports to carry explicit free/tool/structured capability evidence plus `require_tools=True`, and enforced that live evidence at the provider boundary.

Changed files
- research-agents/src/sheperd_research/settings.py
- research-agents/src/sheperd_research/providers/capabilities.py
- research-agents/src/sheperd_research/providers/openrouter.py
- research-agents/src/sheperd_research/workflow.py
- research-agents/tests/test_settings_and_policy.py
- research-agents/tests/test_capabilities.py
- research-agents/tests/test_openrouter_agents.py
- research-agents/tests/test_workflow.py

Commit hashes
- prior fix round 1 commit: 0f2531fa699b3c6a28f24d376d515189fe88e0df

Covering tests
- `cd research-agents && uv run pytest tests/test_contracts.py tests/test_settings_and_policy.py tests/test_capabilities.py tests/test_validation.py tests/test_openrouter_agents.py tests/test_provider_failures.py tests/test_workflow.py`
  - `40 passed in 0.89s`
- `cd research-agents && uv run ruff check src/sheperd_research tests/test_contracts.py tests/test_settings_and_policy.py tests/test_capabilities.py tests/test_validation.py tests/test_openrouter_agents.py tests/test_provider_failures.py tests/test_workflow.py`
  - `All checks passed!`
- `cd research-agents && uv run mypy src/sheperd_research`
  - `Success: no issues found in 19 source files`

Concerns
- The repository still contains unrelated staged and untracked work outside this fix. This round was committed by explicit pathspec so the strict Task 1 surface and the report update land without pulling in the broader dirty checkout.
