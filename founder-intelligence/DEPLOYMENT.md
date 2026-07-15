# Vercel Deployment

## Project separation

Create a separate Vercel project for this dashboard. Set its Root Directory to `founder-intelligence`. Do not attach the public `website/` project to this directory.

## Required settings

- Framework preset: Next.js.
- Install command: `pnpm install --frozen-lockfile`.
- Build command: `pnpm build`.
- Node.js: 24.x.
- Production branch: `production` (reserved; do not create yet).
- Enable Standard Protection with Vercel Authentication before deploying.
- Keep Production private until an approved authentication and authorization layer exists.
- Do not add customer-data, CRM, analytics, email, or publishing environment variables.

The repository-level two-project setup is documented in `../VERCEL.md`. Pushes
to `main` should be classified as protected Preview deployments. A Vercel
Production build is also rejected in `next.config.ts` until the sharing and
authentication gate is explicitly replaced.

The committed `src/generated/` data allows the app to build when Vercel excludes repository files outside the Root Directory. Local maintainers regenerate those artifacts before committing research changes.

## Founder sharing gate

1. Run all verification commands from `README.md`.
2. Review the generated-data diff for unintended sensitive material.
3. Deploy a protected Preview.
4. Verify access protection, browser console, routes, search, responsive layout, and noindex headers.
5. Share only the protected Preview URL.

Deployment does not authorize external outreach, publishing, customer-data intake, or AI execution.
