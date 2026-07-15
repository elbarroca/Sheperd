# Founder Intelligence QA Report

Verified locally on **2026-07-15** against the committed D0/D1 research snapshot.

## Current product contract

The public, read-only dashboard exposes five content routes:

1. `/competitors` - positioning, 14 observed alternatives, public URLs, pricing signals, and evidence boundaries.
2. `/market` - materiality signals, market friction, timing, sizing limits, reports, papers, and public problem language.
3. `/decision-room` - ICP, economics, offer, claims, journey, eight bounded experiments, empty account and outcome states, and source traceability.
4. `/michael` - immediate action, eight workstreams, AI support, and human approval boundaries.
5. `/knowledge` - interactive 92-page React knowledge map, safe document deep links, full indexed sections, and accessible folder index.

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
| ESLint | Pass | `pnpm lint` |
| Strict TypeScript | Pass | `pnpm typecheck` |
| Unit and data tests | Pass | 16 files, 45 tests via `pnpm test` |
| Impeccable anti-pattern scan | Prior baseline | Not rerun for this scoped route addition |
| Production build | Pass | Next.js 16.2.10; five product views and two dynamic local APIs |

The automated verification ran with the bundled Node 24.14.0 runtime and the project's existing pnpm 9.15.4 entrypoint.

## Browser verification

Verified with a production-mode local server and the in-app browser.

| Width | Route or flow | Result |
|---|---|---|
| 1440 | Decision room, seven-stage manifest, and five-item navigation | Pass |
| 1024 | Decision room, four-column manifest wrap | Pass |
| 768 | Decision room, two-column manifest wrap | Pass |
| 390 | Decision room and mobile navigation rail | Pass |
| 320 | Decision room first viewport and minimum-width layout | Pass |

Checks passed:

- Exactly five primary navigation items and one active item.
- Meaningful page content, one H1 per route, and no Next.js error overlay.
- No document-level horizontal overflow at any inspected width.
- Zero captured browser page errors.
- A reduced-motion media rule is present and the decision room has zero active animations.
- Keyboard focus is visible with the electric-blue outline, and native disclosure controls toggle without custom scripting.
- The decision room renders one semantic ordered journey, 35 native disclosures, the draft warning, the external hold, and admitted source links.
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
- The target-account queue contains `0 admitted records`; no account or customer record is fabricated.
- All eight experiment results remain `Not run`; only `EXP-001` is prepare-now, `EXP-002` and `EXP-003` are synthetic-only, and the remaining experiments are externally, publication, or security blocked.
- Customer outcomes and win/loss rates have no admitted records. Sensitivity ranges and ROI remain unavailable.
- The 16-week source remains labeled `Internal proposal - not an executed agreement`.
- External activation remains on hold until the required truth, authority, product, claims, security, capacity, and evidence gates pass.

## Production boundary

- All pages are public, read-only, uncached, and `noindex`.
- `/api/files` and `/knowledge?file=` accept only exact paths from the admitted generated catalog.
- `/api/search` remains local lexical retrieval and makes no external model call.
- No customer data, CRM, database, analytics, email, publishing, or embedding provider is connected.
- The Vercel Root Directory remains `founder-intelligence`; no deployment was performed in this change.
