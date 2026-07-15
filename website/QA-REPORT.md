# SheperD Website QA Report

Status: Local Preview acceptance passed; remote Preview blocked; Production blocked
Evidence timestamp: 2026-07-15 02:30 WEST
Scope: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD/website`

## Release decision

The optimized local Preview passes the implemented content, build, browser, accessibility, visual, motion, performance, and security gates. It is safe only as a noindex, no-collection review artifact.

There is no verified live Preview. Vercel authentication returned `Error: Not authorized`, so deployment identity, access protection, deployed headers, CDN behavior, cold-cache metrics, and rollback remain unverified. Production publication remains hard-blocked by the exact authority and claim registries.

## Verification environment

| Tool | Version |
|---|---:|
| Node.js | 22.23.1 |
| pnpm through Corepack | 10.30.0 |
| Next.js | 16.2.10 |
| React | 19.2.7 |
| Motion | 12.42.2 |
| Playwright | 1.61.1 |
| Lighthouse | 13.4.0 |
| Vercel CLI | 56.1.0 |

All package-manager evidence below uses `corepack pnpm`, not the older global pnpm binary present on the workstation.

## Final local checks

| Check | Result | Evidence |
|---|---|---|
| Frozen install | Pass | Lockfile accepted by pnpm 10.30.0. A forced frozen reinstall repaired one missing local pnpm store index without changing the lockfile. |
| Lint | Pass | ESLint completed with no findings. |
| Typecheck | Pass | `tsc --noEmit` completed with strict TypeScript. |
| Unit and content tests | Pass | 2 files, 8 tests. |
| Preview build | Pass | 12 static routes generated with Next webpack. |
| Content validator | Pass | Preview content gate passed. |
| Link validator | Pass | Internal link gate passed. |
| Motion validator | Pass | Motion is the only animation dependency; initial modern JavaScript is 135,946 gzip bytes against a 150,000-byte ceiling. |
| Impeccable detector | Pass | `node .agents/skills/impeccable/scripts/detect.mjs --json src/` returned `[]`. |
| Browser suite | Pass | 63 passed, 0 failed, 0 skipped across Chromium, Firefox, and WebKit. |
| Production negative build | Pass as a fail-closed gate | Exited 1 before compilation with `EXT-01` through `EXT-12` and all five unapproved `EDU-*` claim IDs. |
| Production license inventory | Pass | License inventory completed after the store repair; licenses are permissive except the expected transitive `libvips` LGPL package used by Sharp. |
| Secret and credential filename scan | Pass | No secret-pattern content or `.env`, key, PEM, or P12 file was found in the project. |
| Native pnpm vulnerability audit | Unavailable | The npm audit endpoint used by pnpm returned HTTP 410. A disposable exact production-dependency npm-lock fallback reported 0 known vulnerabilities. This does not turn the unavailable native audit into a pass. |

`corepack pnpm check` is the combined lint, typecheck, unit-test, validator, and optimized Preview-build gate.

## Browser and accessibility matrix

| Coverage | Chromium | Firefox | WebKit |
|---|---:|---:|---:|
| Functional Preview behavior | Pass | Pass | Pass |
| Axe on `/`, `/privacy`, and `/terms` | 0 automatic violations | 0 automatic violations | 0 automatic violations |
| Keyboard and disclosure behavior | Pass | Pass | Pass |
| Hero evidence hover/focus/press contract | Pass | Pass | Pass |
| No JavaScript reading path | Pass | Pass | Pass |
| Reduced motion final states | Pass | Pass | Pass |
| 200% text zoom and reflow | Pass | Pass | Pass |
| Forced colors and focus | Pass | Pass | Pass |
| Touch path and 44px targets | Pass | Pass | Pass |
| CSP and console errors | Pass | Pass | Pass |

Deterministic Chromium baselines pass at 320, 375, 768, 1024, 1440, and 1920 pixels. They include explicit no-overflow assertions. The hero decorative image is intentionally omitted at 640 pixels and below; the container modules carry the composition on mobile.

## Lighthouse and transfer evidence

Three current local simulated-mobile Lighthouse runs were taken against the optimized build.

| Run | Performance | Accessibility | Best Practices | SEO | FCP | LCP | CLS | TBT | Total transfer | Script transfer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 98 | 100 | 100 | 63 | 0.767s | 2.386s | 0 | 52ms | 239,975 B | 145,028 B |
| 2 | 98 | 100 | 100 | 63 | 0.760s | 2.341s | 0 | 10ms | 239,975 B | 145,028 B |
| 3 | 98 | 100 | 100 | 63 | 0.758s | 2.333s | 0 | 9ms | 239,975 B | 145,028 B |
| Median | 98 | 100 | 100 | 63 | 0.760s | 2.341s | 0 | 10ms | 239,975 B | 145,028 B |

The desktop run scored 100 performance, 100 accessibility, and 100 best practices, with 0.606s LCP, 0 CLS, 0ms TBT, and 286,493 bytes total transfer. Desktop image transfer was 46,518 bytes. Mobile made no image request. Both measured transfer totals are below the 2 MB budget.

SEO is 63 because the Preview deliberately emits `noindex`, `nofollow`, `noarchive`, disallows crawling, omits a canonical, and publishes an empty sitemap. Raising that score would violate the Preview publication contract. INP is unavailable in navigation-only lab Lighthouse; TBT is reported as the lab responsiveness proxy and is not relabeled as INP.

These are local measurements. They do not establish Vercel CDN or field Web Vitals.

## Independent review closure

| Review dimension | Score | Final state |
|---|---:|---|
| Content and storytelling | 12/15 | Coherent safe story; approved capability and conversion wording remain externally blocked. |
| Visual, interaction, and motion | 15/15 | Six baselines pass; inspectable hero modules and monotonic primed reveals satisfy the component contract. |
| Architecture | 15/15 | Static server-first boundary, isolated client leaves, strict publication gate, and minimal runtime dependency set. |
| Responsive UX and accessibility | 15/15 | Three-engine functional and Axe coverage, no-JS, zoom, forced-colors, reduced-motion, touch, and overflow checks pass. |
| Performance, motion resilience, and security review | 9.5/10 | No local P0 or P1; remote platform evidence is unavailable. |

Closed findings:

- P1 hero modules were converted from static labels to semantic inspectable buttons with hover, focus, single-item touch pinning, and `aria-pressed` state.
- P2 post-paint reveal resets were removed by priming the initial section, relationship-line, and container-module states in CSS before hydration.
- P2 design-control documentation was closed by recording `DESIGN_VARIANCE=7`, `MOTION_INTENSITY=6`, and `VISUAL_DENSITY=4` in `DESIGN.md`.
- Earlier no-JavaScript disclosure and ARIA ownership findings were repaired and retested.

Remaining local P0/P1 findings: none.

## Evidence-backed score

| Rubric | Earned | Available |
|---|---:|---:|
| Evidence integrity and publication safety | 20 | 20 |
| Content and storytelling | 12 | 15 |
| Visual, interaction, and motion | 15 | 15 |
| Architecture and implementation | 15 | 15 |
| Responsive UX and accessibility | 15 | 15 |
| Performance and security | 9.5 | 10 |
| SEO, deployment, and handoff | 5 | 10 |
| **Raw local evidence total** | **91.5** | **100** |

Applied score: **8.0/10**. The rubric cap applies because the live protected Preview, deployed headers, rollback record, and remote performance evidence are unresolved. The SEO target also conflicts intentionally with the noindex Preview contract. The authentication exception permits a complete local handoff; it does not justify a 10.0 score.

Production publication readiness: **0/10, blocked**. This is separate from local Preview implementation quality.

## External blockers and next action

- Remote Preview: Vercel account/team authentication is unavailable. See `DEPLOYMENT.md` for the bounded evidence and exact recovery sequence.
- Production: `EXT-01` through `EXT-12` and `EDU-EVIDENCE-001`, `EDU-541-001`, `EDU-41301-001`, `EDU-FMC-001`, and `EDU-CASE-001` remain unresolved.
- User action: run `vercel login` locally and authenticate the intended account/team. Do not send a token in chat.

No Production deployment, domain attachment, DNS change, paid resource, tracking integration, data intake, or existing-site mutation was performed.
