# SheperD Website

The Recovery Corridor is the public-facing SheperD website. It explains the
shipping-container demurrage and detention recovery workflow while keeping
unapproved publication and data collection fail-closed.

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

Deploy this directory as its own protected Vercel Preview project. Production
builds are intentionally rejected until the legal, claims, privacy, contact,
ownership, and publication gates in `docs/FACTS-AND-CONSTRAINTS.md` resolve.
See `DEPLOYMENT.md` and the repository-level `../VERCEL.md` for exact settings.
