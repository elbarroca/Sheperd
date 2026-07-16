# Founder Intelligence QA Report

Verified locally on **2026-07-16** against the admitted D0/D1 research snapshot.

## Current product contract

The public, read-only dashboard exposes five content routes:

1. `/competitors` - positioning, 14 observed alternatives, public URLs, pricing signals, and evidence boundaries.
2. `/market` - materiality signals, market friction, timing, sizing limits, reports, papers, and public problem language.
3. `/decision-room` - ICP setup counts, five evidence filters, verified public context, research/founder/pilot workstreams, an offer build sequence, claims, journey, eight bounded experiments, empty account and outcome states, and source traceability.
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
| Unit and data tests | Pass | 16 files, 47 tests via `pnpm test` |
| Impeccable anti-pattern scan | Prior baseline | Not rerun for this scoped route addition |
| Production build | Pass | Next.js 16.2.10; five product views and two dynamic local APIs |

The automated verification ran with the bundled Node 24.14.0 runtime and the project's existing pnpm 9.15.4 entrypoint.

## Browser verification

Verified with a production-mode local server and the in-app browser.

| Width | Route or flow | Result |
|---|---|---|
| 1440 | Decision room, seven-stage manifest, and five-item navigation | Pass |
| 1024 | All five routes, responsive manifest, evidence signals, and setup workbench | Pass |
| 768 | All five routes, two-column workbench and offer sequence | Pass |
| 390 | All five routes, ICP controls, and mobile navigation rail | Pass |
| 320 | All five routes, minimum-width layout, and zero document overflow | Pass |

Checks passed:

- Exactly five primary navigation items and one active item.
- The ICP setup strip derives `4` beachheads, `5` buying roles, `5` proof filters, `6` admission gates, `6` disqualifiers, and `0` admitted accounts from the rendered data structures; it displays no synthetic fit score or rate.
- Meaningful page content, one H1 per route, and no Next.js error overlay.
- No document-level horizontal overflow at any inspected width.
- Zero captured browser page errors.
- A reduced-motion media rule is present and the decision room has zero active animations.
- Keyboard focus is visible with the electric-blue outline, and native disclosure controls toggle without custom scripting.
- The decision room renders one semantic ordered journey, 35 native disclosures, the draft warning, the external-action gate, and admitted source links.
- EXP-001 matches the canonical founder truth-and-gates workshop across the Decision Room, Michael route, control note, and structured experiment register.
- The target-account queue distinguishes the proposal's claimed source data from the `0 admitted records` currently connected to the dashboard.
- Missing economics inputs are assigned to `Research now`, `Founder decision`, or `Pilot measurement`, with a method, owner, output, next action, and source path.
- The offer ladder is presented as a progressive setup sequence; red is reserved for prohibited claims rather than ordinary unfinished work.
- The competitor chart has an accessible data table and a non-performance boundary.
- The market page links to official reports, research papers, and bounded public problem-language sources.
- The knowledge map initially shows every folder, expands `06_Research` to 14 pages, and renders all 92 file nodes on request.
- Clicking the AI Opportunity Register node updates the shareable URL and opens the correct document.
- `/research?file=<path>` redirects to `/knowledge?file=<path>` and preserves the requested source.
- A traversal-shaped invalid file parameter returns `Document not found in the admitted corpus`, reveals no requested path, and renders no arbitrary document.

## Evidence boundaries

- Competitor coordinates describe public offer shape only. They are not performance, traction, or superiority scores.
- Vendor pricing and outcomes remain company-controlled unless separately promoted by the claims register.
- The `$15.4B` charge pool, `240,535` importer universe, complaint relief, and provider count are never combined into TAM.
- `TAM`, `SAM`, and `SOM` have explicit calculation methods and owners, but their results remain null until the required inputs and approvals exist. Product-market fit, repeatable outcomes, and unit economics remain unproven.
- The target-account queue contains `0 admitted records`; no account or customer record is fabricated.
- All eight experiment results remain `Not run`; only `EXP-001` is prepare-now, `EXP-002` and `EXP-003` are synthetic-only, and the remaining experiments retain their external, publication, or security execution gates.
- Customer outcomes and win/loss rates have no admitted records. Their measurement fields are staged, but calculated sensitivity ranges and ROI remain unavailable.
- The 16-week source remains labeled `Internal proposal - not an executed agreement`.
- External actions stay gated until the required truth, authority, product, claims, security, capacity, and evidence gates pass; internal research and setup remain active now.

## Production boundary

- All pages are public, read-only, uncached, and `noindex`.
- `/api/files` and `/knowledge?file=` accept only exact paths from the admitted generated catalog.
- `/api/search` remains local lexical retrieval and makes no external model call.
- No customer data, CRM, database, analytics, email, publishing, or embedding provider is connected.
- The production target remains the linked Vercel project with Root Directory `founder-intelligence`; live verification is required after each release.
