# Invoice-only website verification

Date: 2026-09-16
Branch: `feat/invoice-only-recovery-site`
Local production-build preview: http://127.0.0.1:3100

## Delivered

- Homepage with the invoice-only CFO promise, managed recovery, $0 upfront,
  and payment tied to recovered value.
- Approved AI positioning across the hero and supporting copy: AI-assisted D&D
  recovery with human review; human reviewers decide what the evidence supports.
- How it works, For importers and About pages; updated enquiry and notice pages.
- Generated maritime terminal artwork, four process glass-green transparent PNGs,
  eight importer glass-green transparent PNGs, responsive delivery and shared
  social imagery.
- The hero uses the approved static terminal composition with the existing
  static maritime terminal composition with no decorative story or replay
  control. The process section remains a single semantic timeline.
  Static reduced-motion, mobile and no-JavaScript equivalents remain complete.
- Homepage opportunity visual renders a sourced `$13B` annual port-delay-cost
  highlight; it does not claim that SheperD recovers the whole figure.
- Disabled intake shows a notice before rendering fields. No upload, analytics,
  CRM or delivery activation. API contracts and flags unchanged.

## Checks

| Check | Result |
| --- | --- |
| Final `corepack pnpm@10.33.2 --dir website lint` | PASS |
| Final `corepack pnpm@10.33.2 --dir website typecheck` | PASS |
| Final `corepack pnpm@10.33.2 --dir website test` | PASS, 12 tests across 4 files |
| `corepack pnpm@10.33.2 --dir website build` | PASS |
| Playwright | PASS, 81 tests, Chromium / Firefox / WebKit |
| Homepage screenshots | Updated at 320, 375, 768, 1024, 1440 and 1920px |
| Accessibility | No axe violations on the public routes in all three browsers |
| Alternate states | Keyboard, reduced motion, no JavaScript, image failure, forced colors, 200% zoom |
| Diff whitespace | PASS |

Tests replace the outdated audit/dashboard assertions rather than preserving
checks for removed content. WebKit tests focus the skip link explicitly because
macOS's default WebKit Tab preference skips links; Enter activation is verified.
Chromium and Firefox verify Tab discovery as well.

## Historical mobile Lighthouse sample

The previous local sample reported performance 96; accessibility 100; best practices 100; SEO 66.
LCP 2.69 s; CLS 0; total blocking time 30 ms.
SEO's failed audit is crawlability: existing noindex controls were intentionally
preserved. An earlier sample scored 99 performance; local lab results vary.
These scores do not establish conversion lift or field performance.

This sample predates the current glass asset pass and is not a current
performance claim. Re-run the local capture/audit scripts before using it for
release decisions.

## Boundaries

No deployment, invoice upload or intake activation was performed. Repository
publication is limited to the feature branch; direct `main` publication is
not performed. Existing unrelated research-platform work was preserved.
Activating enquiry delivery and search indexing remains separate work. All
generated graphics are illustrations, not customer proof or actual recovery
results.
