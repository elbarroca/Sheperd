# SheperD Design QA

final result: passed

## Latest pass — selected section-01 direction

- Source visual truth: `/var/folders/41/_dw_pjd939j0k29gkmp2rlbw0000gn/T/codex-clipboard-27199d5b-27f8-4647-b515-64b01c593cb7.png`
- Browser-rendered implementation: `http://127.0.0.1:3000/`
- Focused evidence: `qa/cfo-editorial-1440.png` and `qa/cfo-editorial-375.png`
- Full-page evidence: `tests/e2e/visual.spec.ts-snapshots/home-1440x1000-chromium-darwin.png` and `tests/e2e/visual.spec.ts-snapshots/home-375x900-chromium-darwin.png`
- Viewports: 1440 × 900 and 375 × 900 focused captures; visual baselines at 320, 375, 768, 1024, 1440, and 1920 CSS pixels; reduced-motion state.
- State: homepage, no authentication, no user data, static hero, selected section editorial layout.
- Normalization note: the source is a fixed mockup raster; comparison preserves the source composition while the implementation keeps live semantic text, responsive flow, and a generated local illustration.
- Findings: the selected direction’s serif headline, ship-and-crane artwork, invoice handoff, and SheperD responsibility rail are present without overflow. The homepage uses the new visual; `/for-importers` retains its existing shared-section layout.
- Result: no actionable P0, P1, or P2 mismatch remains.

## Comparison Target

- Source visual truth: `/var/folders/41/_dw_pjd939j0k29gkmp2rlbw0000gn/T/codex-clipboard-278eedd6-fd67-4479-96a6-fb92ec72301b.png`
- Browser-rendered implementation: `http://127.0.0.1:3100/` (production build)
- Hero evidence: static terminal composition at desktop and mobile widths.
- Viewports checked: 1440 × 900, 768 × 1024, and 375 × 900, plus visual baselines at 320, 375, 768, 1024, 1440 and 1920px.
- Focus: static hero, responsive opportunity rail, transparent PNG artwork, no horizontal overflow, and source-scoped `$13B` claim.

- Source visual truth: `docs/references/recovery-corridor-selected.png` (864 × 1821) and the user-supplied 1128 × 501 corridor-junction crop
- Browser-rendered implementation: `http://127.0.0.1:3000/`
- Primary implementation capture: `qa/review-desktop-top-1440.png`
- Current responsive captures: `qa/review-mobile-320.png`, `qa/review-mission-375.png`, `qa/review-tablet-768.png`, and `qa/review-footer-375.png`
- Responsive evidence: `tests/e2e/visual.spec.ts-snapshots/home-320x900-chromium-darwin.png` and `tests/e2e/visual.spec.ts-snapshots/home-1440x1000-chromium-darwin.png`
- Viewport and state: 1440 × 1000, DPR 1, desktop, initial page state, no authentication; current browser review also covers 320 × 900, 375 × 900, and 768 × 1024 CSS pixels.
- Normalization note: the selected visual is a fixed 864-pixel-wide full-page raster rather than a browser source. Comparisons preserve each artifact's aspect ratio and align equivalent page regions; browser chrome is excluded.

## Evidence

- Full-view comparison: `qa/recovery-corridor/comparison-full-pass4.png`
- Focused hero comparison: `qa/recovery-corridor/comparison-copy-hero-pass4.png`
- Focused footer comparison: `qa/recovery-corridor/comparison-footer-pass4.png`
- Current normalized hero comparison: `qa/design-qa-comparison-hero.png` (the supplied reference hero and the current 1440-pixel implementation hero placed together in one image)
- Current focused mission evidence: `qa/review-desktop-mission-1440.png` and `qa/review-mission-375.png`
- Current container-operations evidence: `qa/container-journey-section-1440.png`, `qa/container-journey-section-768.png`, `qa/container-journey-section-375.png`, and `qa/container-journey-section-320.png`
- Matched corridor-junction comparison: `qa/corridor-junction-comparison.png` (source and implementation in one 2256 × 501 comparison image)
- Continuous-rail evidence: `qa/corridor-junction-1128-pass2.png`, `qa/corridor-handoff-1128-pass2.png`, and `qa/corridor-dashboard-handoff-1128.png`
- Focused regions were required because the full-page board is too small to assess copy hierarchy, logo sharpness, footer paths, and legal-link spacing accurately.

## Findings

- No actionable P0, P1, or P2 differences remain.
- Typography: the two-line hero lockup, weight, tight tracking, line height, section hierarchy, and small uppercase labels now match the source's visual role. The system sans stack is a close clean-room match; wrapping remains stable at every tested breakpoint.
- Spacing and layout: the hero split, three-stat corridor, two-column explainer, framed dashboard, and audit split retain the source's hierarchy and rhythm. The expanded footer is an intentional user-requested improvement; it remains restrained, aligned to the page grid, and stacks without horizontal overflow.
- Corridor geometry: the metric rail, right bracket, recovery-column rail, lower handoff, left journey/mission rail, and dashboard rail use one 4-pixel stroke, shared turn positions, and matching 28-pixel radii at desktop widths. The matched 1128-pixel comparison shows no gaps, doubled strokes, or corner tails; the mobile rail uses a simplified 3-pixel bracket with no horizontal overflow.
- Colors and tokens: deep navy surfaces, cobalt corridor lines, ice-blue explainer, white text, restrained glow, and semantic focus/success states map to the selected palette in `DESIGN.md`.
- Image quality: the implementation uses the real SheperD logo and exact live Recovery Summary dashboard. Neither is redrawn or substituted; both remain sharp and correctly scaled. Interface icons use the Phosphor library.
- Copy and content: the headline remains intact while the first viewport now explicitly names shipping-container demurrage and detention recovery. The explainer defines both charges in plain language; steps use eligible-outcome wording; metadata and footer repeat the same proposition without adding a second offer. The local-only form disclosure remains an intentional safety addition.
- Interaction and accessibility: primary navigation, anchor CTAs, all form fields, validation, local success feedback, keyboard focus, reduced motion, no-JavaScript reading, and 200% zoom reflow are covered. The form performs no request and stores no personal data.
- Responsive header and footer: the compact header exposes a 42-pixel menu control at 320 and 375 pixels, adds a direct audit link at tablet width, and retains the complete desktop navigation. The mobile footer uses a short overview followed by two compact navigation columns. Browser measurements show `scrollWidth` equals `clientWidth` at 320, 375, 768, and 1440 pixels.
- New mission section: the intentional user-requested extension uses the source palette, typography hierarchy, rule rhythm, and Phosphor icon family. It explains the company objective and three outcomes without introducing a second offer or an unrelated visual motif.

## Comparison History

### Pass 1 — blocked

- [P2] The desktop hero title wrapped to three lines instead of the source's two-line lockup.
- [P2] Hiding summary line breaks on mobile concatenated two sentences without a space.
- [P2] The lower blue corridor line crossed the local-preview helper text in the audit form.

Fixes made:

- Split the title into two controlled block lines and preserved `What’s Yours` as a single line.
- Added explicit whitespace around responsive line breaks and reduced the narrow-screen title scale.
- Lowered the audit corridor line beneath the helper text.

### Pass 2 — visual fixes verified; DOM copy check blocked completion

- Post-fix hero evidence: `qa/recovery-corridor/comparison-hero-pass2.png`
- Post-fix full-page evidence: `qa/recovery-corridor/comparison-full-pass2.png`
- Post-fix form evidence: `qa/recovery-corridor/comparison-form-pass2.png`
- Result: the prior visual P2 findings were resolved. A subsequent browser DOM check found that the two block title spans exposed `RecoverWhat’s Yours` without a separating text node, a P2 copy/accessibility mismatch.

Fix made:

- Added an explicit whitespace text node between the visual title lines without changing the two-line layout.

### Pass 3 — passed

- Post-fix hero evidence: `qa/recovery-corridor/comparison-hero-pass3.png`
- Post-fix form/success-state evidence: `qa/recovery-corridor/comparison-form-pass3.png`
- Browser DOM evidence: the heading now exposes `Recover What’s Yours`; the visible title remains two lines and the page has no horizontal overflow at 1280 pixels.
- Result: no actionable P0/P1/P2 mismatch remains.

### Pass 4 — copy and footer improvement passed

- User-requested change: make the landing page explicitly about shipping-container loss recovery, simplify the explanation, improve the footer, and correct its paths.
- Full-view evidence: `qa/recovery-corridor/comparison-full-pass4.png`.
- Focused copy evidence: `qa/recovery-corridor/comparison-copy-hero-pass4.png`.
- Focused footer evidence: `qa/recovery-corridor/comparison-footer-pass4.png`.
- Responsive evidence: refreshed 320, 375, 768, 1024, 1440, and 1920 Chromium snapshots show no clipping or horizontal overflow. The 320-pixel footer stacks its proposition, navigation, contact, and legal links in a clear reading order.
- Result: the selected visual hierarchy remains recognizable, the longer copy wraps cleanly, footer links resolve to the correct home sections and notice routes, and no actionable P0/P1/P2 mismatch remains.

### Pass 5 — mission, mobile navigation, and delivery states passed

- User-requested change: explain SheperD's company objective, improve the mobile experience, refine header/footer behavior, and prepare the audit form for Resend.
- Initial interaction finding: the animated mobile menu closed before the browser completed its native anchor scroll, leaving the URL hash updated at the top of the page. This was a P1 navigation defect.
- Fix made: the mobile link now closes the menu, waits for its 260-millisecond exit, and then scrolls the named section with a reduced-motion equivalent.
- Initial mobile polish finding: mission outcome icons stacked above their copy at 375 pixels, making the section unnecessarily long. This was a P2 responsive-density issue.
- Fix made: outcomes retain a 44-pixel icon column beside the copy on narrow screens.
- Post-fix evidence: `qa/review-mission-375.png` shows the compact outcome rows; browser state measured the mission section 72 pixels below the sticky header after the menu interaction, with no horizontal overflow.
- Normalized source comparison: `qa/design-qa-comparison-hero.png` shows that the exact SheperD mark, navy/cobalt palette, two-line headline, corridor line, and three-stat hierarchy remain faithful after the additions.
- Result: no actionable P0/P1/P2 finding remains.

### Pass 6 — container-operations content and imagery passed

- User-requested change: add credible container imagery, industry language, and stronger section spacing.
- Fix made: added an original blue-hour terminal-operations image and a focused event record covering last free day, terminal availability, gate-out, empty return, and invoice line items. Section spacing uses the shared responsive section token and preserves the source's light-panel hierarchy.
- Responsive evidence: 1440, 768, 375, and 320-pixel browser captures show a correct image crop, readable hierarchy, five complete event rows, and no horizontal overflow. Console errors remained at zero.
- Result: no actionable P0/P1/P2 finding remains.

### Pass 7 — corridor continuity passed

- Initial P2 finding: the metric rail stopped before its right bracket, the metric bracket and recovery-column rail were drawn from different x-positions, and independent section borders created visible gaps and doubled lines.
- Fix made: replaced independent borders with a shared corridor geometry using one stroke token, one radius token, and a breakpoint-specific turn position. Rail segments now overlap at the exact same pixel boundary; corner endpoints are inset by the radius to prevent square tails.
- Post-fix evidence: `qa/corridor-junction-comparison.png` compares the supplied 1128-pixel crop and implementation together. `qa/corridor-handoff-1128-pass2.png` verifies the lower curve and left rail; `qa/corridor-dashboard-handoff-1128.png` verifies the same 4-pixel rail reaches the dashboard. Browser measurements show `scrollWidth` equals viewport width at 1128 and 375 pixels, and console errors are zero.
- Result: no actionable P0/P1/P2 finding remains.

## Primary Interactions Tested

- Both “Get a Free Invoice Audit” CTAs reach the audit form.
- “See how it works” reaches the process section.
- Completing and submitting the audit form shows: “Interaction verified. No details were sent.”
- Mobile navigation opens, animates out, closes, and scrolls to the selected section; Escape also closes the open menu.
- Browser console and runtime logs were checked after a fresh load; no application errors or hydration warnings were present.
- Footer “What we recover” resolves to `/#why-sheperd`; Privacy Policy resolves to `/privacy`; email and LinkedIn use their correct external destinations.

## Open Questions

- Resend delivery is implemented but intentionally disabled. Sender-domain verification, destination approval, privacy/retention ownership, durable abuse controls, one bounded live delivery test, and deployment authority still block enabling it and production publication.

## Implementation Checklist

- [x] Match the selected composition and blue design system.
- [x] Use exact brand and dashboard assets.
- [x] Resolve desktop and mobile wrapping drift.
- [x] Verify the conversion path and local-only form behavior.
- [x] Recompare the revised implementation with the source.
- [x] Verify mobile navigation, 320/375/768 reflow, compact mission outcomes, form success state, and console health in the in-app browser.
- [x] Verify the container-operations section at 320, 375, 768, and 1440 pixels.
- [x] Match and verify every corridor handoff at the 1128-pixel reference width.

## Follow-up Polish

- No P3 refinement is required for local stakeholder review.

### Pass 8 — below-hero white split passed

- User-requested scope: preserve the hero; make only the “Your time stays yours” section below it a white split layout, with a soft blue transition and a new port image.
- Generated a blue-hour container-terminal image for the right panel and optimized it to a 1536 × 1024 JPEG (583 KB). Handoff cards remain legible over the photo.
- Desktop review at 1440 pixels and Chromium visual baselines at 1024, 1440, and 1920 pixels show the new white section follows the unchanged hero cleanly. Mobile baseline captures at 320, 375, and 768 pixels show stacked copy and image without horizontal overflow.
- Verification: `pnpm lint`, `pnpm typecheck`, and `pnpm test` passed (12 unit tests). `pnpm exec playwright test` passed all 90 Chromium, Firefox, and WebKit tests, including route-level WCAG 2.1 AA checks, keyboard navigation, reduced-motion behavior, CTA navigation, mobile overflow, and refreshed visual baselines.
- Result: no actionable P0/P1/P2 finding remains for this section.

### Pass 9 — importer section implementation

final result: blocked

### Pass 10 — hero-to-value transition passed

- Reference: `/var/folders/41/_dw_pjd939j0k29gkmp2rlbw0000gn/T/codex-clipboard-25082c50-4447-45f4-b745-a8aa27ae5692.png` (the supplied desktop landing-page view).
- User-requested scope: keep the hero intact; remove the immediate port-photo-to-port-photo transition and make the next section lead with potential bottom-line value from past U.S. invoices.
- Change: the white, pale-blue three-year invoice-history section now follows the hero. The photo-led “Your time stays yours” block is no longer on the homepage; the process section follows the value section. The existing `/pilot` CTA and `pilot-scope`/`evidence` anchors remain available.
- Visual evidence: `qa/transition-1440.png` (1440 × 1000 viewport) and `qa/transition-390.png` (390 × 844 viewport) capture the hero-to-value seam; `qa/landing-desktop.png` and `qa/landing-mobile.png` are full-page captures at those same viewports. Both seam captures show a white financial-value section after the hero, with no second port image.
- Responsive and interaction checks: all 90 Playwright E2E tests passed across Chromium, Firefox, and WebKit. This includes six viewport widths from 320 to 1920px, overflow checks, CTA navigation, keyboard access, reduced motion, and route-level WCAG 2.1 AA checks. Six full-page visual baselines were refreshed for the intentional section reorder.
- `pnpm lint`, `pnpm typecheck`, and `pnpm test` passed; Vitest reported 12 tests across four files. The installed Node version is 26.9.0 while `package.json` specifies 24.x; pnpm emitted an engine warning, but the checks passed.
- Result: no actionable P0/P1/P2 visual or interaction finding remains for this change.

final result: passed

- Source visual truth: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD/website/design-experiments/importers-faq-redesign/directions/03-split-header-faq-panel.png` (1312 × 1199).
- Browser view: `http://127.0.0.1:3000/for-importers`, no authentication; native FAQ disclosures collapsed after keyboard interaction.
- Responsive measurements: 1440 × 896, 765 × 1305, 375 × 846, and 320 × 846 CSS pixels. The importer grid has four columns at desktop and two at narrower widths; FAQ stacks below 820px. Document width matched viewport width at all measured sizes.
- Interaction and runtime: Enter opened and closed a native FAQ disclosure; browser error log was empty. `pnpm check` passed lint, typecheck, and all 12 unit tests.
- Initial P2 finding: two-column tablet cards retained desktop height. Reduced them to 124px at the tablet breakpoint; narrow mobile cards remain 104px.
- Visual review found no remaining visible P0/P1/P2 issue. A persistent implementation screenshot and matched source/prototype comparison could not be saved through the in-app browser API, so the required image archive remains blocked.
