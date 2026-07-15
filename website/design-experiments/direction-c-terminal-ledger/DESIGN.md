# Direction C: Terminal Ledger

## Purpose

Terminal Ledger is a single-page, mobile-first public preview for importer finance and logistics teams. Its thesis is: "Before the claim, align the record." The page presents three generic evidence categories in sequence and stops visibly at qualified human review.

Public label: **SheperD**

Plugin: `example-web-prototype-taste-brutalist`

Design system: `warm-editorial`

## Direction rationale

The direction borrows the rhythm of cargo manifests and port signage without representing a product interface. Condensed type creates urgency, ruled fields keep categories separate, and the vertical sequence makes the stop boundary unmistakable. Registration marks provide the single visual metaphor: category presence can align a review packet, but alignment is not agreement or a conclusion.

The active brutalist plugin's default red accent is replaced by warm safety yellow because the brief explicitly requires it. The Warm Editorial paper and ink tokens remain the base.

## Type

- Display: `Arial Narrow`, `Helvetica Neue Condensed`, `Impact`, sans-serif; black weight; condensed; uppercase; tight tracking; 0.88-0.95 line height.
- Body: `var(--font-body)` from Warm Editorial, with system fallback.
- Micro and numeric text: `var(--font-mono)`; 11-14px; uppercase; 0.08-0.1em tracking; tabular figures.
- One `h1`; semantic `h2` and `h3` hierarchy below it.

## Palette

- Raw paper: `var(--bg)` (`#fbf6ee`).
- Raised paper: `var(--surface)` and `var(--surface-warm)`.
- Ink: `var(--fg)` (`#201914`).
- Secondary ink: `var(--fg-2)` and `var(--muted)`.
- Rules: `var(--border)` and `var(--border-soft)`.
- Warm safety yellow: `color-mix(in oklch, var(--warn) 72%, var(--surface-warm))`, derived only from Warm Editorial tokens.
- No gradients, glow, glass, shadow, or section-level theme inversion.

## Spacing

- Base rhythm: 4, 8, 12, 16, 20, 24, 32, and 48px from the Warm Editorial spacing tokens.
- Section padding: 56px phone, 80px tablet, 112px desktop.
- Page gutters: 16px phone, 24px tablet, 36px desktop.
- Interactive targets: 44px minimum; primary CTA is 52px tall.

## Layout

- Mobile first: one-column register strip, hero, evidence layers, registration plate, checklist, stop block, and sources.
- At 640px: register cells and source links form columns; hero becomes an asymmetric split.
- At 960px: registration plate becomes sticky beside the three evidence layers; checklist becomes a three-column ruled module.
- All ledger modules use one-pixel ink gaps over an ink background for precise dividers.
- Corners remain square throughout. No cards, dashboard chrome, forms, or simulated product UI.
- Layout must remain free of horizontal overflow at 320px.

## Motion

- Motion serves one narrative event only: three offset registration marks align after all three evidence categories have entered the viewport.
- `IntersectionObserver` records category visibility without scroll listeners or user data.
- Animation changes only `transform` and lasts 240ms.
- With `prefers-reduced-motion: reduce`, the same state change occurs instantly. Without JavaScript, the marks remain in the static aligned fallback because all categories are already present in the document.

## Accessibility

- Semantic landmarks: header, main, sections, articles, ordered list, asides, and footer.
- One `h1`, sequential heading levels, descriptive source names, and a skip link.
- Keyboard focus uses a 3px ink outline with a 4px offset.
- Ink on raw paper and raw paper on ink provide strong AA contrast; safety yellow is not used for body text.
- Touch targets are at least 44px.
- Motion has a reduced-motion equivalent.
- Text wraps and modules collapse to one column to prevent overflow at 320px.

## Factual boundaries

- The only public label is **SheperD**.
- The page is explicitly a preview. It does not collect, submit, evaluate, or retain records.
- It shows only three generic evidence categories: Billing record, Operational record, and Governing record.
- The sequence stops at qualified human review.
- Category alignment is not agreement, a legal conclusion, or an outcome.
- No capability, customer, pricing, security, outcome, upload, form, dashboard, testimonial, logo wall, analytics, tracking, external image, or fabricated data appears.
- The only external links are `https://www.fmc.gov/` and `https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541`.

Post-generation factual correction: the Open Design prompt supplied `part-545` in error. The product-owned copy was corrected to the controlling workspace source, 46 CFR Part 541, before scoring. No visual or copy-direction change was made.
