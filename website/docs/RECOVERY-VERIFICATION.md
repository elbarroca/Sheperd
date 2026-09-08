# Invoice-only website verification

Date: 2026-09-08
Branch: `feat/invoice-only-recovery-site`
Local production-build preview: http://127.0.0.1:3211

## Delivered

- Seven-section homepage with the invoice-only CFO promise, managed recovery,
  $0 upfront, and payment tied to recovered value.
- How it works, For importers and About pages; updated enquiry and notice pages.
- Custom rendered port artwork, four reusable process objects, eight industry
  thumbnails, responsive WebP delivery and shared social imagery.
- One-shot forward/reverse motion and replay. Static reduced-motion and
  no-JavaScript equivalents. Short phone screens omit the motion overlay so it
  cannot obscure the offer.
- Disabled intake shows a notice before rendering fields. No upload, analytics,
  CRM or delivery activation. API contracts and flags unchanged.

## Checks

| Check | Result |
| --- | --- |
| Baseline lint / typecheck / unit tests | PASS, 14 original tests |
| Final `pnpm lint` | PASS |
| Final `pnpm typecheck` | PASS |
| Final `pnpm test` | PASS, 10 tests across 3 files |
| `pnpm build` | PASS, run by the Playwright web-server setup |
| Playwright | PASS, 72 tests, Chromium / Firefox / WebKit, no skips |
| Homepage screenshots | Reviewed at 320, 375, 768, 1024, 1440 and 1920px |
| Supporting pages | Captured at 375 and 1440px; no horizontal overflow |
| Short mobile | 375 x 667, offer unobscured and next section boundary visible |
| Accessibility | No axe violations on the seven public routes in all three browsers |
| Alternate states | Keyboard, reduced motion, no JavaScript, image failure, forced colors, 200% zoom |
| Diff whitespace | PASS |

Tests replace the outdated audit/dashboard assertions rather than preserving
checks for removed content. WebKit tests focus the skip link explicitly because
macOS's default WebKit Tab preference skips links; Enter activation is verified.
Chromium and Firefox verify Tab discovery as well.

## Final mobile Lighthouse sample

Performance 96; accessibility 100; best practices 100; SEO 66.
LCP 2.69 s; CLS 0; total blocking time 30 ms.
SEO's failed audit is crawlability: existing noindex controls were intentionally
preserved. An earlier sample scored 99 performance; local lab results vary.
These scores do not establish conversion lift or field performance.

Evidence: `qa/invoice-only/`, including `lighthouse-mobile.json`, responsive
homepage screenshots, route screenshots and `hero-short-mobile.png`.
Repeat with `node scripts/capture-recovery.mjs` and
`node scripts/audit-recovery.mjs` against the local server on port 3211.

## Boundaries

No deployment, commit, push, invoice upload or intake activation was performed.
Existing unrelated research-platform work was preserved. Activating enquiry
delivery and search indexing remains separate work. All generated graphics are
illustrations, not customer proof or actual recovery results.
