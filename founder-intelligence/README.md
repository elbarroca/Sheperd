# SheperD Research Dashboard

Small, read-only Next.js dashboard for Neon-backed daily and weekly research briefs.

## Local run

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`. The server-side dashboard reads the FastAPI service at
`RESEARCH_API_BASE_URL`, defaulting to `http://127.0.0.1:8787`. Neon credentials
stay in the Python service and never reach the browser.

## Routes

- `/` - daily and weekly brief summaries, system status, and workflow explanation
- `/reports/{run_id}` - cited report detail and agent audit
- `/sources` - searchable source and distillation explorer
- `/monthly` - deterministic signal rollups

The UI has no static research fallback. An unavailable API is shown as an explicit
state. Reports remain drafts until human review and are never approved or published
by the dashboard.

## Verification

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Vercel project root: `founder-intelligence`. Configure `RESEARCH_API_BASE_URL` with
the read-only API's public HTTPS URL before expecting live report data in a public
deployment. A local `127.0.0.1` API cannot be reached by Vercel.
