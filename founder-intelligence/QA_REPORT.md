# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Current product contract

The public, read-only dashboard exposes four content routes:

1. `/competitors` - positioning, 14 observed alternatives, public URLs, pricing signals, and evidence boundaries.
2. `/market` - materiality signals, market friction, timing, sizing limits, reports, papers, and public problem language.
3. `/michael` - immediate action, eight workstreams, AI support, and human approval boundaries.
4. `/knowledge` - interactive 92-page React knowledge map, safe document deep links, full indexed sections, and accessible folder index.

Legacy routes redirect without dropping query parameters:

- `/` to `/competitors`
- `/research` to `/knowledge`
- `/mikey` and `/improvements` to `/michael`
- `/ricardo` to `/market`

## Automated gates

| Gate | Result | Evidence |
|---|---|---|
| Generated-data contract | Pass | 92 file manifests, 828 chunks, 1,200 terms, 53 sources, 12 blockers, 8 experiments |
| Complete catalog contract | Pass | 92/92 files visible, including zero-section templates |
| ESLint | Pass | `corepack pnpm lint` |
| Strict TypeScript | Pass | `corepack pnpm typecheck` |
| Unit and data tests | Pass | 11 files, 29 tests via `corepack pnpm test` |
| Impeccable anti-pattern scan | Pass | `npx --yes impeccable detect src`; zero findings |
| Production build | Pass | Next.js 16.2.10; four product views and two dynamic local APIs |

## Browser verification

Verified with a production-mode local server and `agent-browser`.

| Width | Route or flow | Result |
|---|---|---|
| 1440 | Competitors and knowledge map | Pass |
| 1024 | Market situation | Pass |
| 768 | Knowledge map | Pass |
| 390 | Michael operating plan | Pass |
| 320 | Competitor first viewport and mobile navigation | Pass |

Checks passed:

- Exactly four primary navigation items and one active item.
- Meaningful page content, one H1 per route, and no Next.js error overlay.
- No document-level horizontal overflow at any inspected width.
- Zero captured browser page errors.
- Reduced-motion media preference is honored.
- Keyboard focus begins at the visible-on-focus skip link.
- The competitor chart has an accessible data table and a non-performance boundary.
- The market page links to official reports, research papers, and bounded public problem-language sources.
- The knowledge map initially shows every folder, expands `06_Research` to 14 pages, and renders all 92 file nodes on request.
- Clicking the AI Opportunity Register node updates the shareable URL and opens the correct document.
- `/research?file=<path>` redirects to `/knowledge?file=<path>` and preserves the requested source.
- A traversal-shaped invalid file parameter returns `Document not found in the admitted corpus`, reveals no requested path, and renders no arbitrary document.

## Evidence boundaries

- Competitor coordinates describe public offer shape only. They are not performance, traction, or superiority scores.
- Vendor pricing and outcomes remain company-controlled unless separately promoted by the claims register.
- The `$15.4B` charge pool, `239,231` importer universe, complaint relief, and provider count are never combined into TAM.
- `TAM`, `SAM`, `SOM`, product-market fit, repeatable outcomes, and unit economics remain `unknown`.
- The 16-week source remains labeled `Internal proposal - not an executed agreement`.
- External activation remains on hold until the required truth, authority, product, claims, security, capacity, and evidence gates pass.

## Production boundary

- All pages are public, read-only, uncached, and `noindex`.
- `/api/files` and `/knowledge?file=` accept only exact paths from the admitted generated catalog.
- `/api/search` remains local lexical retrieval and makes no external model call.
- No customer data, CRM, database, analytics, email, publishing, or embedding provider is connected.
- The Vercel Root Directory remains `founder-intelligence`; no deployment was performed in this change.
