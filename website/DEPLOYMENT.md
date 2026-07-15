# SheperD Website Deployment Record

Status: Not deployed; external authentication blocker
Recorded: 2026-07-15 02:30 WEST
Build root: `website/`

## Decision

The app is mechanically ready for a Vercel Preview but no live URL is authorized or verified. It must not be shared until the intended project/team identity and Vercel Deployment Protection are confirmed. `noindex` is crawler guidance, not access control.

Production deployment, promotion, domain attachment, DNS changes, paid resources, and mutation of any existing live site are prohibited until all publication gates resolve and explicit promotion authority is recorded.

## Local release identity

| Field | Value |
|---|---|
| Framework | Next.js 16.2.10 App Router |
| Runtime | Node.js 22.23.1 |
| Package manager | pnpm 10.30.0 through Corepack |
| CLI inspected | Vercel CLI 56.1.0 |
| Source-tree SHA-256 | `de227c7f3504ffb0863dffd8e5b52b14946dbfdc2d801e1e4dcb1d8f631ce582` |
| Preview build | Passed |
| Production build | Intentionally blocked |
| Application secret required | No |

The source hash covers the sorted contents of `package.json`, `pnpm-lock.yaml`, the Next/TypeScript/ESLint/Playwright/Vitest configuration files, and every file under `src/`, `scripts/`, `public/`, and `tests/`:

```bash
find package.json pnpm-lock.yaml next.config.ts tsconfig.json eslint.config.mjs playwright.config.ts vitest.config.ts src scripts public tests -type f \
  | LC_ALL=C sort \
  | xargs shasum -a 256 \
  | shasum -a 256
```

## Authentication evidence

Three bounded, read-only authentication checks were made on 2026-07-15:

| Attempt | Command | Result |
|---:|---|---|
| 1 | `vercel whoami` | `Error: Not authorized` |
| 2 | `vercel whoami` | `Error: Not authorized` |
| 3 | `vercel project ls` | `Error: Not authorized` |

No further login or deployment attempt was made. No token was requested or printed.

Exact blocker: the workstation is not authenticated to the intended Vercel account/team, so project selection and protection cannot be verified safely.

One required user action: run `vercel login` locally and authenticate the intended account/team. Do not share a token in chat.

## Environment contract

Only names and scopes are recorded.

| Name | Scope | Preview rule |
|---|---|---|
| `SITE_PUBLICATION_TARGET` | Build | Leave unset or set to `preview`; never set to `production` while gates remain. |
| `VERCEL_ENV` | Vercel build | Platform context fallback only. |
| `VERCEL_URL` | Vercel build | Mechanical Preview metadata image base only; not canonical approval. |
| `PLAYWRIGHT_BASE_URL` | QA | Optional externally managed test origin. |

There are no application secrets, database credentials, analytics keys, CRM keys, upload credentials, or mail provider settings.

## Remote evidence unavailable

| Required record | State |
|---|---|
| Vercel organization/team ID | Unavailable |
| Vercel project ID and name | Unavailable |
| Preview URL and deployment ID | Unavailable |
| Deployment Protection proof | Unavailable |
| Preview environment-scope inventory | Unavailable |
| Deployed security headers and CSP | Unavailable |
| Platform HSTS behavior | Unavailable |
| Vercel cold-cache transfer and Lighthouse | Unavailable |
| Rollback target and successful rollback record | Unavailable |

No placeholder value is used for any missing field.

## Post-authentication Preview sequence

Run this only after the intended account/team is visible and the project owner authorizes Preview creation:

1. From the parent `SheperD/` directory, inspect account/team identity with `vercel whoami` and project access with `vercel project ls`.
2. Confirm the deployment target is a new or explicitly approved Preview project with Root Directory `website/`.
3. Confirm Deployment Protection is enabled for the Preview before distributing its URL.
4. Run `vercel --cwd website` without `--prod`.
5. Record the returned project, team, Preview URL, deployment ID, source hash, and timestamp in this file.
6. Inspect the deployment with `vercel inspect <preview-url>` and verify protection plus deployed response headers.
7. Run the browser suite against the protected Preview using an owner-approved test session; never weaken protection for automation.
8. Capture cold-cache Lighthouse evidence and reconcile it with `QA-REPORT.md`.
9. Record the rollback target. The inspected CLI command shape is `vercel rollback <deployment-id-or-url>`; do not execute it without explicit rollback authorization.

Do not use `--prod`. A successful Preview is not publication approval.

## Rollback record

Rollback status: Not testable because no deployment ID or URL exists.
Rollback command inspected: `vercel rollback <deployment-id-or-url>`.
Last known safe deployment: None created by this task.

## Production gates

The validator currently blocks `EXT-01` through `EXT-12` and five unapproved educational claim records. The complete traceability matrix is in `CONTENT-MATRIX.md`. `corepack pnpm build:production` must continue to exit nonzero until every gate has evidence and explicit publication authority.
