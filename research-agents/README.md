# SheperD Research Agents

Small, local-first research service for public maritime, port, carrier, terminal, and D&D intelligence.

## Boundaries

- Neon stores source metadata, hashes, distillations, claims, runs, and review decisions.
- Full article bodies are transient by default; the database keeps metadata, hashes, summaries, and citations.
- Every generated report is `DRAFT - HUMAN REVIEW REQUIRED` until explicitly reviewed.
- Supplied LinkedIn and paywalled URLs are retained as seed leads only; they are not extracted or bypassed.
- No customer data, CRM writes, external publishing, email, LinkedIn automation, or paywall bypass.
- Reviewed reports export to `../obsidian/06_Research/Agent Runs/`.

## Setup

1. Rotate any credential pasted into chat or other public surfaces.
2. Put replacement values in the repository-root `.env.local`; do not copy secrets into this folder.
3. Use the configured Neon project `sheperd-research` and its `main` branch.
4. Put the pooled `main` connection in `DATABASE_URL`; put the direct `main` migration connection in `DIRECT_DATABASE_URL`. Neon management checks use host-controlled MCP OAuth; set `NEON_BRANCH_ID` to the main branch ID. The service rejects a direct URL in the pooled slot and a pooled URL in the migration slot.
5. Install dependencies and run the checks:

```bash
cd research-agents
uv sync
uv run ruff check .
uv run mypy src
uv run pytest
```

Apply the reviewed migration to the configured Neon `main` branch:

```bash
uv run sheperd-research migrate
```

New runs use the configured OpenAI model. Legacy OpenRouter/Gemma run metadata
remains readable for audit, but it cannot authorize new runs.

## Commands

```bash
uv run sheperd-research doctor --json
uv run sheperd-research model-map --json
uv run sheperd-research audit --json
uv run sheperd-research model-check --strict --json
uv run sheperd-research mcp-check --json
uv run sheperd-research source-map --check --strict --json
uv run sheperd-research migrate
uv run sheperd-research agent-check --strict --verbose --json
uv run sheperd-research run --topic-set dnd-port
uv run sheperd-research run --topic-set dnd-port --verbose --json
uv run sheperd-research e2e --profile canary --strict --run-id e2e-<timestamp> --as-of "<timestamp>" --json
uv run sheperd-research e2e --profile canary --strict --run-id e2e-<timestamp> --verbose --json
uv run sheperd-research validate --run-id <run-id>
uv run sheperd-research index --region all --run-id <run-id> --json
uv run sheperd-research dashboard
uv run sheperd-research review --run-id <run-id> --decision approve --reviewer Mikey
uv run sheperd-research export --run-id <run-id>
```

Add `--verbose` to `run`, `e2e`, or `agent-check` for a timestamped operator
stream on stderr. It reports agent starts, Tavily Search/Extract, key routing,
OpenAI attempts, Neon writes, checkpoints, distillation, validation, and
final counts. JSON remains machine-readable on stdout; no prompts, article
bodies, keys, or hidden reasoning are printed.

The dashboard listens on `http://127.0.0.1:8787`. It is read-only; use the CLI for review and export decisions. HTML and JSON routes expose runs, step latency and hashes, sources, claims, distillations, signals, validations, and weekly briefs. Weekly report queries default to active runs; use `archive_scope=archived` or `archive_scope=all` for audit views. Failed runs are archived, never deleted, and their evidence remains recoverable. Search supports full-text queries plus geography, region, language, freshness, authority, lane, evidence, status, and date filters. Regional Markdown indexes under `../obsidian/06_Research/Research Index/` are generated from Neon and contain structured summaries, claims, citations, evidence locators, and hashes only.

### Public read-only API

`src/app.py` is the ASGI entrypoint for the separate Vercel project
`sheperd-research-api`. Set that project to the FastAPI framework and configure
only the pooled runtime `DATABASE_URL` plus `NEON_BRANCH_ID` in its server-side
environment. Never upload `DIRECT_DATABASE_URL`, provider keys, or management
tokens to the API project. The dashboard's `RESEARCH_API_BASE_URL` must point to
the API's public HTTPS alias.

`mcp-check` is intentionally host-controlled: run the Tavily and Neon MCP smoke
checks from the development host. The service itself uses direct Tavily, OpenAI,
and PostgreSQL clients. The default model is `gpt-5.6-luna`, OpenAI's
cost-sensitive GPT-5.6 model for high-volume workloads, with tool-calling and
structured-output support. There is
no model fallback: transport timeouts retry once on the same model, while rate
limits, authentication errors, or malformed output fail the run explicitly.
`--strict` remains the validation gate.

`model-map` reports the configured OpenAI model and its required agent
capabilities. It does not authorize a run; `model-check` performs a live
structured-output health request.

Set `TAVILY_API_KEY` as the primary search key and optionally set
`TAVILY_API_KEY_2` as a secondary. Search and Extract try slot 1 first, then
slot 2 only for rate-limit, quota, authentication, or provider-status failures.
Malformed responses remain failures; key values are never logged or persisted.

## Research state

User-supplied links are seed references, not verified claims. Primary government, court, port-authority, carrier, and terminal sources outrank trade media and social posts. Unsupported assertions remain `unverified` or `mixed`.
