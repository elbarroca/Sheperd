---
name: SheperD Preview
description: A port-control-room visual system for careful record review.
designDials:
  DESIGN_VARIANCE: 8
  MOTION_INTENSITY: 7
  VISUAL_DENSITY: 5
colors:
  paper: "#F9FBFA"
  paper-raised: "#EEF4F3"
  ink: "#071D28"
  steel-700: "#39515A"
  steel-600: "#586D73"
  steel-300: "#A9BABC"
  steel-150: "#D7E2E2"
  oxide-800: "#8F2E16"
  oxide-700: "#B5401F"
  oxide-100: "#F4DDD5"
typography:
  display:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "clamp(4rem, 7.4vw, 6rem)"
    fontWeight: 500
    lineHeight: 0.88
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "clamp(2.6rem, 5.2vw, 5.25rem)"
    fontWeight: 500
    lineHeight: 0.94
    letterSpacing: "-0.04em"
  title:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 500
    lineHeight: 1.2
  lead:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  small:
    fontFamily: "Barlow, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Azeret Mono, ui-monospace, monospace"
    fontSize: "0.72rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.04em"
rounded:
  structural: "0px"
  seal: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
  4xl: "96px"
components:
  seal-link:
    backgroundColor: "{colors.oxide-700}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.structural}"
    padding: "13px 19px"
    height: "52px"
  seal-link-hover:
    backgroundColor: "{colors.oxide-800}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.structural}"
    padding: "13px 19px"
    height: "52px"
  container-module:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.structural}"
    padding: "18px"
---

# Design System: SheperD Preview

The controlling design dials are `DESIGN_VARIANCE=8`, `MOTION_INTENSITY=7`, and `VISUAL_DENSITY=5`.

## Creative north star

**The Port Control Room**

SheperD should feel like a calm working surface for separating a charge into records, questions, and a conditional review path. The visual language combines maritime ink, sea-glass neutrals, blank evidence materials, terminal geometry, and one oxide signal. It is more vivid than the earlier sparse ledger while remaining serious, exact, and evidence-safe.

The page keeps the approved narrative order and uses six distinct composition families:

1. An asymmetric hero with a documentary material image and inspectable evidence assembly.
2. A still-life manifest where the three questions overlap the image as one working record.
3. A sea-glass checklist bench with one dark active-detail surface.
4. A panoramic route image and keyboard-accessible horizontal six-step rail.
5. A sticky FAQ, bounded limits field, and direct answers without marketing expansion.
6. A staggered source register instead of repeated source cards.

Fixed light mode remains intentional because the Preview's controlling product contract selected a single document-like theme. Dark ink is reserved for active workbench surfaces and the footer, not arbitrary section inversion.

## Brand register

### Point of view

The invoice is not treated as the whole story. The design separates billing facts, operating records, applicable text, and unresolved questions without claiming that SheperD decides a case.

### Recognition anchors

- Plain `SheperD` wordmark with one square oxide stop.
- Square modules, hard rules, and physical overlap rather than rounded cards.
- Maritime ink plus oxide signal, never a second accent.
- Blank paper, clips, steel, and route geometry used only as illustrative material.
- Azeret Mono reserved for evidence labels, source metadata, indexes, and controls.

### Anti-slop rules

- No generic three-card feature row, bento grid, metrics strip, fake dashboard, or product screenshot.
- No gradients, glass, glow, blur panels, pills, soft shadows, or decorative grids.
- No repeated eyebrow labels. The audience line is the single main-flow kicker.
- No customer records, carrier marks, container IDs, certification symbols, or implied operational proof.
- No alternating dark/light section theme pattern.

## Color

Oxide is the only accent. It marks primary action, focus, active state, indexes, and the thin verification edge. Maritime ink is the structural neutral, while sea-glass tones create section grouping without adding a second accent.

- `paper`: primary canvas and reading surface.
- `paper-raised`: checklist and limits grouping.
- `ink`: headings, structural controls, active-detail surface, and footer.
- `steel-700`: support and body-secondary copy.
- `steel-600`: metadata only.
- `steel-300`: strong boundaries only; never text.
- `steel-150`: quiet rules and dark-surface body text.
- `oxide-700`: primary action and active signal.
- `oxide-800`: hover/pressed state.
- `oxide-100`: selection and dark-surface metadata.

Text contrast must remain valid throughout motion. Semantic text never animates opacity.

## Typography

Barlow carries all reading hierarchy. Azeret Mono is a compact evidence register, not a terminal theme.

- Display: one H1, never above `6rem`, tracking no tighter than `-0.04em`, exactly two lines from 320px upward.
- Headline: fluid to `5.25rem`, short balanced measures, no isolated one-word wrapping where avoidable.
- Title: `1.25rem` or a fluid title clamp only for active record state.
- Lead: `1.125rem`.
- Body: `1rem`, with a 65 to 75 character reading measure.
- Small: `0.875rem`.
- Label: `0.72rem` desktop and `0.875rem` mobile when compact labels need legibility.

## Imagery

The page uses three original generated editorial studies recorded in `MEDIA-PROVENANCE.md`:

- Hero: blank papers, metal clip, corrugated steel, and distant terminal geometry.
- Manifest: three blank record groups arranged around a physical timeline strip.
- Route: unmarked terminal lanes branching around container stacks.

Every image is responsive AVIF with a local JPEG fallback, explicit dimensions, descriptive alt text, and no third-party request. Imagery is illustrative only and must not be described as a SheperD product, customer record, real case, official port, or operating proof.

## Motion

Motion explains entry, relationship, and state:

- Hero copy enters by short transform-only stagger; the hero image settles through a shallow clip and opacity reveal.
- Evidence modules assemble as one spring group.
- Manifest relation lines draw once as rows enter view.
- Section wrappers vary between lift, lateral shift, and settle; semantic text does not fade.
- Checklist detail transitions only after interaction and is lazy-loaded.
- Buttons use a short `0.98` press scale.

All motion reads shared tokens, uses only Motion, avoids raw scroll listeners, and ends immediately under `prefers-reduced-motion`. Content remains complete without JavaScript.

## Components

### Navigation

The header is sticky, solid, and rule-led. Desktop keeps the four approved anchors and one primary action. The native mobile `details` menu preserves keyboard and no-JavaScript behavior. Every target is at least 44px.

### Container assembly

Three dark modules overlap the hero image and form one semantic button list. Hover or focus reveals detail; press pins one detail for touch users. The image remains visible on mobile because the redesign relies on imagery to establish context.

### Manifest

The semantic definition list overlaps the record still life. The image and list stack on mobile without changing DOM order or clipping focus.

### Evidence disclosure

Five numbered buttons control one stable region. The active record renders on a dark ink surface with oxide top edge. Only one animated panel is mounted at a time.

### Route rail

The six ordered steps form a continuous horizontal rail rather than six cards. On narrow screens it uses scroll snap, a visible partial next item, a focusable labeled container, and no page-level overflow.

### FAQ, limits, and sources

FAQ uses native `details`. Limits remain a bounded no-claim field. Sources use staggered register rows with direct official links and safe external-link attributes.

## Non-negotiables

- Preserve one H1, logical headings, visible focus, 200% reflow, forced colors, reduced motion, and no-JavaScript reading order.
- Preserve the Preview publication boundary and all Production blockers.
- Keep official source links direct and visually distinct.
- Keep the initial modern JavaScript under 150,000 gzip bytes.
- Do not add intake, analytics, tracking, contact capture, third-party media, or a second motion runtime.
