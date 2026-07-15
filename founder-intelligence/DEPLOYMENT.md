# Vercel Deployment

## Project separation

Create a separate Vercel project for this dashboard. Set its Root Directory to `founder-intelligence`. Do not attach the public `website/` project to this directory.

## Required settings

- Framework preset: Next.js.
- Install command: `pnpm install --frozen-lockfile`.
- Build command: `pnpm build`.
- Node.js: 24.x.
- Production branch: `main`.
- Deployment Protection: disabled; all generated URLs are public.
- Keep the dashboard read-only and do not introduce customer or case data.
- Do not add customer-data, CRM, analytics, email, or publishing environment variables.

The repository-level two-project setup is documented in `../VERCEL.md`. Pushes
to `main` create public Production deployments. Public access was explicitly
authorized on 2026-07-15.

The committed `src/generated/` data allows the app to build when Vercel excludes repository files outside the Root Directory. Local maintainers regenerate those artifacts before committing research changes.

## Founder sharing gate

1. Run all verification commands from `README.md`.
2. Review the generated-data diff for unintended sensitive material.
3. Deploy Production from `main`.
4. Verify anonymous access, browser console, routes, search, responsive layout, and noindex headers.
5. Share the stable Production URL.

Deployment does not authorize external outreach, publishing, customer-data intake, or AI execution.
