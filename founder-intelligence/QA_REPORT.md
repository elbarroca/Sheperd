# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Automated gates

| Gate | Result | Evidence |
|---|---|---|
| Generated-data contract | Pass | 88 files, 767 chunks, 1,200 terms, 42 sources, 12 blockers, 8 experiments |
| ESLint | Pass | `pnpm lint` |
| Strict TypeScript | Pass | `pnpm typecheck` |
| Unit/data tests | Pass | 3 files, 6 tests via `pnpm test` |
| Production build | Pass | Next.js 16.2.10; 5 static views, one dynamic search route |

## Browser verification

Verified with the Codex in-app browser against the local Next.js development server.

- Desktop founder brief rendered meaningful content with five navigation links, no framework overlay, no horizontal page overflow, and no fresh console warnings or errors.
- Navigation to Research succeeded through the visible application link.
- Query `What blocks external activation?` returned 12 ranked sections with evidence state, knowledge layer, similarity, and original repository path.
- Founder brief, Research, Mikey workflow, Ricardo notes, and Priority lab rendered at a 390 × 844 viewport without page-level horizontal overflow or framework overlays.
- Priority controls exposed unique accessible names for all four range inputs.

## Production boundary checks

- `/` returned `200` with `private, no-store`, `noindex, nofollow, noarchive`, frame denial, restricted permissions, and a production CSP without `unsafe-eval`.
- `/api/search` returned 12 results for the verified query.
- A one-character query failed closed with `400` and a bounded validation message.
- `robots` metadata and response headers both prevent indexing; this is not a substitute for access control.

## Not verified externally

- No Vercel project was created or deployed.
- Vercel Deployment Protection and any future authenticated production access must be verified after deployment.
- No customer data, CRM, analytics, email, publishing, or embedding provider was connected.
