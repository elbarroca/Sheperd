# Recovery Corridor Design QA

final result: passed

## Comparison Target

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
