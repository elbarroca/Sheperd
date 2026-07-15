# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Automated gates

| Gate | Result | Evidence |
|---|---|---|
| Generated-data contract | Pass | 88 file manifests, 767 chunks, 1,200 terms, 42 sources, 12 blockers, 8 experiments |
| Complete catalog contract | Pass | 88/88 files visible; two short templates preserved with explicit zero-section states |
| ESLint | Pass | `pnpm lint` |
| Strict TypeScript | Pass | `pnpm typecheck` |
| Unit/data tests | Pass | 5 files, 10 tests via `pnpm test` |
| Impeccable anti-pattern scan | Pass | `npx --yes impeccable detect src/`; zero findings |
| Production build | Pass | Next.js 16.2.10; 5 product views and 2 dynamic local APIs |

## Visual QA

- The supplied 407x869 reference and a 407x869 implementation capture were compared side by side.
- The implementation preserves the reference's navy-to-light rhythm, electric-blue signal, compact control bar, framed metrics, and embedded analytical surfaces.
- The composition deliberately replaces the public acquisition form and wolf illustration with the private dashboard's hold posture, source navigation, and founder decision content.
- Desktop chart and source-library views were inspected at 1440px; mobile hero, knowledge map, filters, file index, and file reader were inspected at 407px.
- A fresh browser tab produced zero console warnings or errors.

## Browser verification

Verified with the Codex in-app browser against the local Next.js development server.

- All five product routes passed at 407, 768, 1024, and 1440 pixel widths: one H1, visible hold state, visible active navigation, and zero page-level horizontal overflow.
- The Evidence library exposed 88 of 88 admitted files.
- Filtering for `Ricardo` returned one file and lazy-loaded all eight indexed sections.
- The zero-section Decision Record template returned an explicit, traceable empty state.
- Source-path copy changed to a confirmed `Path copied` state.
- Query `What blocks external activation?` returned 12 ranked source sections.
- All three new charts expose exact-data disclosures and disable animation for reduced-motion users.

## Production boundary checks

- `/` remains private, uncached, noindex, frame-denied, and governed by the existing production CSP.
- `/api/files` accepts only exact admitted source paths and fails closed for missing or unknown paths.
- `/api/search` retains bounded local lexical retrieval and makes no external call.
- No customer data, CRM, analytics, email, publishing, or embedding provider was connected.

## Not verified externally

- No Vercel project was created or deployed.
- Vercel Deployment Protection and future authenticated production access must be verified after deployment.
