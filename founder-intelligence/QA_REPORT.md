# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Automated gates

| Gate | Result | Evidence |
|---|---|---|
| Generated-data contract | Pass | 88 files, 767 chunks, 1,200 terms, 42 sources, 12 blockers, 8 experiments |
| ESLint | Pass | `pnpm lint` |
| Strict TypeScript | Pass | `pnpm typecheck` |
| Unit/data tests | Pass | 4 files, 8 tests via `pnpm test` |
| Impeccable anti-pattern scan | Pass | `npx impeccable detect src/`; no findings |
| Production build | Pass | Next.js 16.2.10; 5 product views, one dynamic search route |

## Browser verification

Verified with the Codex in-app browser against the local Next.js development server.

- The founder brief led with external hold, 12 open gates, 3 internal tests, 0 external tests, 17/42 verified sources, and the next founder decision.
- The decision map rendered six clusters containing all twelve unique gate IDs.
- Ownership, decision-flow, evidence-mix, gated-timeline, source-analysis, and priority-matrix visualizations retained semantic list, table, meter, or disclosure fallbacks.
- Query `What blocks external activation?` returned 12 ranked sections with evidence state, knowledge layer, lexical similarity, a full-source disclosure, and selectable repository path.
- All five product views rendered at 320, 768, 1024, and 1440 pixel widths without page-level or navigation-level horizontal overflow.
- External hold remained visible at every checked viewport, and all four priority controls exposed unique labels.

## Production boundary checks

- `/` returned `200` with `private, no-store`, `noindex, nofollow, noarchive`, frame denial, restricted permissions, and a production CSP without `unsafe-eval`.
- `/api/search` returned 12 results for the verified query.
- A one-character query failed closed with `400` and a bounded validation message.
- `robots` metadata and response headers both prevent indexing; this is not a substitute for access control.

## Not verified externally

- No Vercel project was created or deployed.
- Vercel Deployment Protection and any future authenticated production access must be verified after deployment.
- No customer data, CRM, analytics, email, publishing, or embedding provider was connected.
