# SheperD Website

A production-engineered, publication-gated Next.js Preview for SheperD. The app is deliberately noindex and non-collecting. Production publication is blocked by unresolved authority, legal, claim, contact, brand, canonical, and deployment gates.

## Requirements

- Node.js 22.12 or newer
- pnpm 10.30.0

## Local use

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:3000`.

No application secret is required. Do not add customer records or credentials to this project.

## Publication targets

Preview is the safe default:

```bash
pnpm build
```

Production is intentionally fail-closed:

```bash
pnpm build:production
```

`build:production` must fail until every entry in `src/content/blockers.ts` is resolved and every required exact claim passes `src/content/publication.ts` for `production-web`.

Environment variable names:

| Name | Scope | Purpose |
|---|---|---|
| `SITE_PUBLICATION_TARGET` | Build | Explicit `preview` or `production` publication contract |
| `VERCEL_ENV` | Vercel build | Fallback target context only |
| `VERCEL_URL` | Vercel build | Mechanical Preview metadata image base; not a canonical approval |
| `PLAYWRIGHT_BASE_URL` | QA | Optional externally managed test server URL |

Never document their values in committed files.

## Required verification

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
pnpm validate:content
pnpm validate:motion
pnpm validate:links
node .agents/skills/impeccable/scripts/detect.mjs --json src/
pnpm test:e2e
```

`pnpm check` runs lint, typecheck, unit tests, validators, and the optimized webpack Preview build. The motion validator also fails when initial modern-browser JavaScript exceeds 150,000 gzip bytes. Playwright builds and tests the optimized app across Chromium, Firefox, and WebKit. Deterministic Chromium visual baselines cover 320, 375, 768, 1024, 1440, and 1920 widths; functional and Axe coverage runs in all three engines.

## Project map

- `PRODUCT.md`: truth, route, state, and publication contract.
- `DESIGN.md`: normative visual tokens and component rules.
- `ARCHITECTURE.md`: rendering, dependency, security, and validation design.
- `CONTENT-MATRIX.md`: rendered/suppressed content traceability.
- `MEDIA-PROVENANCE.md`: selected generated-asset record.
- `QA-REPORT.md`: commands, browser evidence, scores, and unresolved gates.
- `DEPLOYMENT.md`: Preview identity, protection, source hash, rollback, and blocker record.
- `src/content/`: typed UI, source, claim, and blocker registries.
- `scripts/`: fail-closed content, motion, and link gates.
- `tests/`: unit, content, accessibility, browser, and visual coverage.

## Deployment

Set Vercel Root Directory to `website/`. Never promote to Production, attach `sheperd.io`, alter DNS, create paid resources, or change the current live site without explicit approval and every production publication gate resolved.

See `DEPLOYMENT.md` for current authenticated-access status and the exact next action.
