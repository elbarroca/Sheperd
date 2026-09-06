# SheperD website

The React/Next.js marketing site for SheperD detention and demurrage invoice
review. The design uses a centered Georgia hero, optimized container artwork,
ambient CSS motion, and a shared visual system across the homepage, pilot,
privacy, and use-notice pages.

## Local setup

Requires Node.js 24.x and pnpm 10.33.2.

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

Open http://127.0.0.1:3000.

## Verification

```sh
corepack pnpm check
corepack pnpm build
corepack pnpm test:e2e --workers=3
```

The browser suite covers three engines, responsive layouts, keyboard behavior,
reduced motion, no-JavaScript navigation, accessibility, image containment,
metadata, and the disabled pilot flow. Visual baselines belong to Chromium.

## Deployment

Production: https://sheperd-website.vercel.app

Keep the existing `sheperd-website` Vercel project with Root Directory `website`.
Only production homepage indexing is enabled. Pilot intake remains unavailable:
its fields and submission are disabled, and the interface sends or stores
nothing. Keep delivery flags false in `.env.example` and hosting settings.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the build policy, release checks, and
future intake boundary. Historical claims and research records remain in
`docs/FACTS-AND-CONSTRAINTS.md`.
