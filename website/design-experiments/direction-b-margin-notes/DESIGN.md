# Direction B: Margin Notes

## Direction

An annotated case file for importer finance and logistics teams. The main column carries a strict three-record checklist. Wide editorial margins carry source-date prompts, boundary notes, gaps, and the final stop. The composition is cropped and asymmetric, but the reading order remains direct.

Plugin: `example-web-prototype-taste-editorial`

Design system: `editorial`

## Type

- Display: Georgia and Times New Roman fallback, serif, weight 500.
- Body and controls: system UI sans stack for compact operational reading.
- Metadata: IBM Plex Mono with system monospace fallbacks.
- Display tracking: `-0.025em`; display line height: `0.98-1.05`; body line height: `1.55`.

The serif headlines establish the case-file voice. Sans body text keeps the checklist literal and scannable. Monospace is reserved for dates, labels, and source metadata.

## Palette

- Paper background: `--bg` at `#fbf7f0`.
- Reading surface: `--surface` at `#fffdf8`.
- Warm case-paper field: `--surface-warm` at `#f1e6d6`.
- Primary ink: `--fg` at `#1f1a16`.
- Secondary ink: `--fg-2` at `#4b4038`.
- Hairlines: `--border` at `#ded3c5`.
- Direction accent: cobalt pencil at `oklch(48% 0.21 264)` with a darker `oklch(39% 0.2 264)` for AA text and controls.

Cobalt is the sole directional accent. It marks checks, source annotations, focus, progress, and the review stop. The cobalt addition is the explicit Direction B override to the Editorial package accent.

## Spacing

- Base rhythm: 8px.
- Inline gaps: 8-24px.
- Record padding: 48px top and 64px bottom.
- Section padding: 88px on small screens and 112px on wide screens.
- Container gutters: 16px mobile, 24px tablet, 36px desktop.
- Interactive targets: 44px minimum; primary CTA: 48px minimum.

## Layout

- Mobile first: one reading column with the progress rail above the evidence sequence and margin notes placed directly after their records.
- Wide screens: three columns. A sticky progress rail occupies the left margin, a 640px reading column carries the checklist, and source-date or gap notes occupy the right margin.
- The hero uses a left-heavy editorial split with a single boundary note.
- The page has one `h1`; each major region uses a semantic section heading.
- The layout has no horizontal scroll at 320px.

## Motion

The cobalt margin marker advances through Billing record, Operational record, and Governing record as each enters the review band. It ends as a square stop marker at unresolved evidence. `IntersectionObserver` provides the state change without a scroll event listener.

Motion is limited to marker translation and CTA feedback. Under `prefers-reduced-motion: reduce`, marker travel is removed, the active label changes instantly, and a visible note explains the equivalent.

## Original imagery

- Asset: `material-study.jpg`, a 529 KB delivery derivative of the generated source recorded in `../../docs/ASSET-PROVENANCE.md`.
- Placement: a narrow hero-margin crop; the mobile crop expands into a tactile case-file plate.
- Meaning: three abstract paper layers connected by one orange thread and cobalt registration marks. It is not a customer document, invoice, port, legal artifact, or product interface.
- Explicit dimensions: 1717 × 916; local file only; no third-party request.

## Accessibility

- Semantic landmarks, headings, articles, asides, ordered progress, and source links.
- One `h1` and a skip link.
- Visible 3px cobalt focus outline with offset.
- AA-oriented foreground, secondary text, CTA, and source-link contrast.
- All links and controls meet a 44px minimum target.
- Progress status is announced through `aria-live`; the active item uses `aria-current="step"`.
- No information depends on motion alone.
- Responsive typography and explicit single-column collapse prevent clipping and horizontal overflow at 320px.

## Factual boundaries

- Public label: SheperD only.
- Thesis: A D&D invoice is one record. The review needs the rest.
- First-screen audience: importer finance and logistics teams preparing demurrage and detention evidence for qualified human review.
- Evidence layers: Billing record, Operational record, Governing record only.
- The sequence stops at qualified human review when evidence is unresolved.
- The prototype is a preview with no collection, fields, submissions, customer documents, or case data.
- It makes no capability, customer, legal conclusion, pricing, security, or outcome claim.
- No fabricated data or customer document appears.
- External sources are limited to `https://www.fmc.gov/` and `https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541`.
- No analytics, tracking, external images, third-party scripts, forms, uploads, testimonials, logo walls, dashboards, or pricing surfaces.

The selected CTA is `Review the checklist`; it links to existing on-page content and does not imply creation, intake, or submission.

## Direction rationale

Margin Notes makes evidence boundaries visible without implying resolution. The central checklist supports sequential review, while the outer notes preserve dates, gaps, and scope beside the record they qualify. Cobalt pencil marks feel provisional and exact: they guide attention, then stop. CSS paper grain gives the case file materiality without imitating or fabricating a customer document.

Post-generation factual correction: the Open Design prompt supplied `part-545` in error. The product-owned copy was corrected to the controlling workspace source, 46 CFR Part 541, before scoring. No visual or copy-direction change was made.
