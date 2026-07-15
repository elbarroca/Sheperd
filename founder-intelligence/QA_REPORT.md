# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Automated gates

| Gate | Result | Evidence |
|---|---|---|
| Generated-data contract | Pass | 88 file manifests, 767 chunks, 1,200 terms, 42 sources, 12 blockers, 8 experiments |
| Complete catalog contract | Pass | 88/88 files visible; two short templates preserved with explicit zero-section states |
| ESLint | Pass | `pnpm lint` |
| Strict TypeScript | Pass | `pnpm typecheck` |
| Unit/data tests | Pass | 7 files, 15 tests via `pnpm test` |
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
- The founder Brief now exposes five traceable research questions with separate founder and Michael consequences.
- The operating plan reconciles all 45 workflows and exposes the five-step `Admit → Route → Prepare → Execute after GO → Decide` loop.
- The new comprehension surfaces passed at 390px with one H1, semantic ordered/definition-list structure, and zero document-level horizontal overflow.

## Live brand sync

- The public identity was checked against `https://www.sheperd.io/` on 2026-07-15.
- The exact 1039x801 white dog-head source asset is stored locally with its original aspect ratio and SHA-256 provenance in `BRAND_SOURCE.md`.
- The dashboard lockup renders the mark at 47x36 on desktop and 36x28 on mobile; both inspected widths had zero document-level horizontal overflow.
- The Evidence library exposes the live identity, capture date, public source, and explicit company-claim boundary without promoting landing-page performance statements.
- Page metadata now uses the synchronized mark for icon and Apple touch icon; the obsolete placeholder icon files were removed.
- The visible public contact label (`info@sheperd.io`) does not match its live `mailto:` target (`avi@sheperd.io`); the conflict remains unresolved and neither address is promoted as canonical.

## Comprehension audit

- Baseline and revised screenshots were captured for the Brief, Evidence library, Operating plan, and Ricardo notes.
- The revised founder synthesis and Michael operating loop were inspected independently at desktop and mobile widths.
- The P1 gaps were the absence of a business-level research narrative and the absence of a repeatable Michael workflow; both are now resolved.
- Accessibility claims remain bounded to the inspected semantics, responsive reflow, visible text states, and native disclosures. Full WCAG conformance is not claimed.

See [COMPREHENSION_AUDIT.md](./COMPREHENSION_AUDIT.md) for the step-by-step audit record.

## Production boundary checks

- `/` remains private, uncached, noindex, frame-denied, and governed by the existing production CSP.
- `/api/files` accepts only exact admitted source paths and fails closed for missing or unknown paths.
- `/api/search` retains bounded local lexical retrieval and makes no external call.
- No customer data, CRM, analytics, email, publishing, or embedding provider was connected.

## Not verified externally

- No Vercel project was created or deployed.
- Vercel Deployment Protection and future authenticated production access must be verified after deployment.
