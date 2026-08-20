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
uv run sheperd-research migrate
uv run sheperd-research run --topic-set dnd-port
uv run sheperd-research e2e --profile canary --run-id e2e-<timestamp> --as-of "<timestamp>" --json
uv run sheperd-research validate --run-id <run-id>
uv run sheperd-research dashboard
uv run sheperd-research review --run-id <run-id> --decision approve --reviewer Mikey
uv run sheperd-research export --run-id <run-id>
```

The dashboard listens on `http://127.0.0.1:8787`. It is read-only; use the CLI for review and export decisions. HTML and JSON routes expose runs, step latency and hashes, sources, claims, distillations, signals, validations, and weekly briefs. Search supports full-text queries plus geography, lane, evidence, status, and date filters.

`mcp-check` is intentionally host-controlled: run the Tavily and Neon MCP smoke
checks from the development host. The service itself uses direct Tavily, OpenRouter,
and PostgreSQL clients. Production execution accepts only
`google/gemma-4-26b-a4b-it:free`, requires a live OpenRouter capability manifest
showing free pricing plus tool and structured-output support, and does not allow
configured or provider-level fallbacks.

## Research state

User-supplied links are seed references, not verified claims. Primary government, court, port-authority, carrier, and terminal sources outrank trade media and social posts. Unsupported assertions remain `unverified` or `mixed`.
