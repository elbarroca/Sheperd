# SheperD Recovery Corridor QA Report

Status: Production build passes; public deployment authorized
Verified: 2026-07-15
Runtime: Node `v24.18.0`, pnpm `10.33.2`, Next.js `16.2.10`

## Decision

The selected Recovery Corridor redesign is approved for public Vercel deployment. The first viewport explicitly explains shipping-container demurrage and detention recovery, the footer provides clear section/contact/legal paths, the exact SheperD mark and Recovery Summary dashboard remain present, and no open P0/P1/P2 design finding remains.

## Required gates

| Gate | Command | Final result |
| --- | --- | --- |
| Lint | `pnpm lint` | pass; zero warnings |
| Strict typecheck | `pnpm typecheck` | pass |
| Unit/content | `pnpm test` | pass; 2 files, 11 tests |
| Aggregate code gate | `pnpm check` | pass |
| Optimized Production build | `VERCEL_ENV=production pnpm build` | pass; `/`, `/privacy`, `/terms`, and `/404` statically prerendered |
| Browser E2E | `pnpm test:e2e` | pass; 41 passed, 13 intentionally skipped, 0 failed |

The 13 E2E skips are deliberate: visual snapshots are Chromium-owned and are skipped in Firefox and WebKit (12), while the WebKit skip-link keyboard assertion is skipped for the macOS links-only Tab preference (1).

## Design and browser verification

- Side-by-side design QA: pass. See `design-qa.md` and `qa/recovery-corridor/comparison-full-pass4.png`.
- Final focused comparisons: `qa/recovery-corridor/comparison-copy-hero-pass4.png` and `qa/recovery-corridor/comparison-footer-pass4.png`.
- Browser-rendered optimized Preview at 1280 × 720: two-line hero, exact logo, exact dashboard, correct corridor lines, and zero horizontal overflow.
- Audit form: all seven fields accept input; submit produces `Interaction verified. No details were sent.`
- Form boundary: no request, transmission, or storage occurs.
- Fresh optimized-browser console: no application errors, hydration warnings, or runtime logs.
- Footer paths: home sections, free audit, privacy, use notice, email, and LinkedIn all resolve correctly.
- Plain-language copy: shipping-container purpose, demurrage/detention definition, eligible recovery sequence, dashboard, and audit proposition remain consistent across the page and metadata.

## Accessibility and responsive coverage

- Axe WCAG A/AA scan: zero serious violations on `/`, `/privacy`, and `/terms` in Chromium, Firefox, and WebKit.
- No-JavaScript reading path: pass in all three engines.
- Reduced motion, forced colors, 200% zoom reflow, touch CTA, and 320-pixel overflow: pass in all three engines.
- Keyboard skip link: pass in Chromium and Firefox; bounded WebKit/macOS preference skip above.
- Deterministic visual snapshots: pass at 320, 375, 768, 1024, 1440, and 1920 CSS pixels.

## Metadata, assets, and response policy

- `/`, `/privacy`, `/terms`, `/favicon.ico`, and `/og/recovery-corridor.png`: HTTP 200.
- Open Graph card: exact 1200 × 630 image, title, description, and alt text present.
- Twitter large-image metadata, multi-size favicon, Apple touch icon, and web manifest: present.
- `X-Robots-Tag: noindex, nofollow, noarchive`: present.
- CSP, referrer policy, MIME-sniff protection, and permissions policy: present.
- Brand source: `public/brand/sheperd-logo.png`.
- Product source: `public/media/recovery-dashboard.png`.

## Publication boundary

Public Vercel deployment was explicitly authorized on 2026-07-15. Noindex
headers and disabled form delivery remain in place. Approved claims, legal
notice, production form/CRM ownership, privacy controls, canonical origin, and
custom-domain decisions remain unresolved and are not implied by deployment.

## Non-blocking observation

Playwright prints a `NO_COLOR` / `FORCE_COLOR` environment warning. It does not affect execution or assertions.
