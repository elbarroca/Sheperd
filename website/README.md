# SheperD Website

The Recovery Corridor is the public-facing SheperD website. It explains the
shipping-container demurrage and detention recovery workflow while keeping
form delivery disabled until its separate intake approvals are complete.

## Local setup

Requires Node.js 24.x and pnpm 10.33.2.

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

Open `http://127.0.0.1:3000`.

## Verification

```sh
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
corepack pnpm build
corepack pnpm test:e2e
```

The audit form validates locally but does not transmit or store submissions by
default. Keep the flags in `.env.example` false unless the approvals and
server-only delivery values in `DEPLOYMENT.md` are complete.

## Deployment boundary

Deploy this directory as its own public Vercel project with Root Directory
`website`. Publication was explicitly authorized on 2026-07-15. The unresolved
legal, claims, privacy, contact, and ownership risks remain recorded in
`docs/FACTS-AND-CONSTRAINTS.md`. See `DEPLOYMENT.md` and `../obsidian/VERCEL.md` for the
exact settings.
