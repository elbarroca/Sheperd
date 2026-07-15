# Direction A: Evidence Tide

## Metadata

- Artifact: `index.html`
- Plugin id: `example-web-prototype`
- Design system: `default`
- Public label: `SheperD`

## Direction rationale

Evidence Tide treats record reconstruction as a charted passage. A single oxidized-orange line changes role as it moves from invoice edge to event timeline to source underline. The records sit directly on that route instead of inside repeated cards. Large navigational type provides orientation, while off-white paper and deep-water neutrals keep the page calm and procedural.

The `default` design system supplies the semantic token structure, restrained component behavior, and accessibility baseline. Direction A rebinds the six core color roles to the user-specified deep-water, oxidized-orange, and paper territory.

## Type

- Display: `Inter`, system sans fallback, weight 650-750.
- Body: `Inter`, system sans fallback, weight 400-700.
- Mono: system monospace for route annotations, sequence numbers, and compact labels.
- Hero: fluid 48-115px with a 0.94 line height and tight tracking.
- Section headings: fluid 32-72px with restrained line length.
- Sentence case throughout. Exactly one `h1`.

## Palette

| Token | Value | Role |
| --- | --- | --- |
| `--bg` | `oklch(96% 0.014 90)` | Off-white paper canvas |
| `--surface` | `oklch(21% 0.03 236)` | Deep-water human-review stop |
| `--fg` | `oklch(23% 0.027 235)` | Primary deep-water ink |
| `--muted` | `oklch(43% 0.025 231)` | Secondary text and captions |
| `--border` | `oklch(75% 0.025 225)` | Cool route dividers |
| `--accent` | `oklch(43% 0.12 42)` | Oxidized signal orange |

The accent is reserved for the route, its stops, keyboard focus, and the single primary CTA. No gradients, glow, glass, or decorative color changes.

## Spacing

- Base unit: 8px.
- Inline gutter: fluid 16-32px.
- Content width: 1200px maximum.
- Section rhythm: fluid 64-136px.
- Major route gaps: 32-144px according to viewport.
- Touch targets: 44px minimum, with the primary CTA at 48px.

## Layout

- Mobile first, one column from 320px.
- Desktop uses an editorial 12-column sensibility without exposing grid chrome.
- Hero: large left-aligned thesis, support copy and one CTA, then the charted route.
- Evidence layers: one ordered route with exactly three stops: Billing record, Operational record, Governing record.
- Checklist: sticky orientation copy on desktop and a vertical sequential line; strict single-column flow on mobile.
- Review: one deep-water inset that visibly terminates the route at qualified human review.
- Boundary: preview statement beside the two official source links.
- Records are not cards. Whitespace, route geometry, and sparse hairlines create hierarchy.

## Motion

- One calm route-line draw on initial load: 1.8 seconds, one iteration, ease-out.
- Only stroke offset and opacity animate.
- Hover and active feedback is limited to links and the CTA.
- `prefers-reduced-motion: reduce` disables the draw and smooth scrolling; the complete route remains visible.
- Motion explains sequence. It does not loop or decorate unrelated elements.

## Accessibility

- Semantic landmarks, ordered lists, one `h1`, and labelled navigation.
- Skip link provided.
- Visible keyboard focus uses the accent ring.
- Text and CTA combinations are designed for WCAG AA contrast.
- All interactive targets are at least 44px.
- No horizontal scrolling at 320px; multi-column structures collapse explicitly.
- The route figure has a concise accessible description and does not carry unique factual content.
- Meaning does not depend on color or motion.

## Factual boundaries

- Public-facing label is only `SheperD`.
- Audience is importer finance and logistics teams.
- Thesis is: "Before you assess the charge, reconstruct the record."
- CTA is: "See what to gather."
- Evidence is limited to three generic layers: Billing record, Operational record, Governing record.
- The sequence stops visibly at qualified human review.
- The page is an informational preview and collects nothing.
- No capability, customer, legal conclusion, pricing, security, outcome, upload, form, dashboard, testimonial, analytics, tracking, or fabricated data claim appears.
- External links are limited to `https://www.fmc.gov/` and `https://www.ecfr.gov/current/title-46/chapter-IV/subchapter-B/part-541`.
- No external images, fonts, scripts, or third-party runtime dependencies are used.

Post-generation factual correction: the Open Design prompt supplied `part-545` in error. The product-owned copy was corrected to the controlling workspace source, 46 CFR Part 541, before scoring. No visual or copy-direction change was made.
