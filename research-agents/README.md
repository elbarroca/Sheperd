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
4. Put the pooled `main` connection in `DATABASE_URL`; put the direct `main` migration connection in `DIRECT_DATABASE_URL`. `NEON_PG_API_KEY` is optional management access only; set `NEON_BRANCH_ID` to the main branch ID. The service rejects a direct URL in the pooled slot and a pooled URL in the migration slot.
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

The numbered migrations enforce the exact free Gemma model in database defaults
and existing run rows; paid or router model identifiers are not permitted.

## Commands

```bash
uv run sheperd-research doctor --json
uv run sheperd-research model-check --json
uv run sheperd-research mcp-check --json
uv run sheperd-research source-map --check --strict --json
uv run sheperd-research migrate
uv run sheperd-research agent-check --allow-free-fallbacks --json
uv run sheperd-research run --topic-set dnd-port
uv run sheperd-research e2e --profile canary --run-id e2e-<timestamp> --as-of "<timestamp>" --json
uv run sheperd-research validate --run-id <run-id>
uv run sheperd-research index --region all --run-id <run-id> --json
uv run sheperd-research dashboard
uv run sheperd-research review --run-id <run-id> --decision approve --reviewer Mikey
uv run sheperd-research export --run-id <run-id>
```

The dashboard listens on `http://127.0.0.1:8787`. It is read-only; use the CLI for review and export decisions. HTML and JSON routes expose runs, step latency and hashes, sources, claims, distillations, signals, validations, and weekly briefs. Search supports full-text queries plus geography, region, language, freshness, authority, lane, evidence, status, and date filters. Regional Markdown indexes under `../obsidian/06_Research/Research Index/` are generated from Neon and contain structured summaries, claims, citations, evidence locators, and hashes only.

### Public read-only API

`src/app.py` is the ASGI entrypoint for the separate Vercel project
`sheperd-research-api`. Set that project to the FastAPI framework and configure
only the pooled runtime `DATABASE_URL` plus `NEON_BRANCH_ID` in its server-side
environment. Never upload `DIRECT_DATABASE_URL`, provider keys, or management
tokens to the API project. The dashboard's `RESEARCH_API_BASE_URL` must point to
the API's public HTTPS alias.

`mcp-check` is intentionally host-controlled: run the Tavily and Neon MCP smoke
checks from the development host. The service itself uses direct Tavily, OpenRouter,
and PostgreSQL clients. Gemma (`google/gemma-4-26b-a4b-it:free`) is always the
primary model. The default production-safe mode is strict Gemma-only; use
`--allow-free-fallbacks` only when an audited, app-controlled free chain is
required. That mode still requires live capability metadata, disables OpenRouter
provider fallback, records every attempt, and never permits a paid model.

## Research state

User-supplied links are seed references, not verified claims. Primary government, court, port-authority, carrier, and terminal sources outrank trade media and social posts. Unsupported assertions remain `unverified` or `mixed`.
