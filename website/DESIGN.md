# SheperD Recovery Corridor Design System

Status: controlling implementation schema
Selected reference: `docs/references/recovery-corridor-selected.png`
Reference dimensions: `864 × 1821`
Scope: local Preview; production publication remains blocked

## Design thesis

**Recover shipping-container overcharges through one visible operational corridor.**

The page moves from promise, to market context, to a three-step recovery path,
to the existing recovery dashboard, and finally to the audit form. One cobalt
line connects those stages. It communicates sequence and accountability rather
than acting as decoration.

## Brand invariants

- Brand label: `SheperD`.
- Use the supplied shepherd-head asset without redrawing it:
  `public/brand/sheperd-logo.png`.
- Use the supplied Recovery Summary image without altering its data:
  `public/media/recovery-dashboard.png`.
- Preserve the live-site headline, figures, form fields, contact email,
  LinkedIn destination, privacy destination, and footer identity. Explain the
  three-step workflow in plain shipping-container language.
- Do not invent customer logos, testimonials, certifications, legal seals,
  case studies, or additional outcome data.

## Color tokens

| Token | Value | Role |
| --- | --- | --- |
| `--navy-1000` | `#020912` | page frame and footer |
| `--navy-950` | `#041426` | hero and dashboard field |
| `--navy-900` | `#06223f` | raised dark surfaces |
| `--blue-700` | `#075dcc` | primary action depth |
| `--blue-600` | `#0d6dfd` | primary CTA and corridor |
| `--blue-400` | `#47a3ff` | glow, focus, active state |
| `--ice-100` | `#eaf4ff` | cool section surface |
| `--canvas` | `#f8fbff` | light content surface |
| `--ink` | `#07172a` | light-surface text |
| `--muted` | `#617085` | secondary light text |
| `--white` | `#ffffff` | dark-surface text |
| `--success` | `#16a177` | completed form state only |

No purple. No warm cream. Blue glow is reserved for the corridor, primary
actions, focus, and the hero mark.

## Typography

- Display: `Arial`, `Helvetica Neue`, system sans; 700–800 weight, tight tracking.
- Body and controls: `Inter`-shaped system sans stack; 400–700 weight.
- Utility labels: system monospace, uppercase, tracked, 11–13px.
- One `h1`; sentence case; body copy stays at least 16px on desktop and 15px on
  narrow screens.

## Layout contract

- Content frame: `min(100% - 40px, 1320px)` on desktop; 20px mobile gutters.
- Header: dark, compact, shepherd mark and wordmark left, navigation centered,
  audit CTA right.
- Hero: asymmetric two-column composition. Copy owns the left; the exact mark is
  enlarged on the right.
- Metric corridor: three equal measurements on dark navy, connected by a single
  structural line.
- Problem/process: light split composition. Problem and benefits left; three
  sequential steps right.
- Dashboard/form: dark field. The exact dashboard image is dominant; the form is
  integrated beneath it.
- Footer: a clear three-column endpoint with the brand and recovery proposition,
  section paths, direct contact, and a separated legal bar.

Mobile collapses to one column while preserving this reading order:

```text
brand -> promise -> actions -> mark -> figures -> problem -> benefits
-> process -> dashboard -> audit form -> footer
```

## Motion contract

- Library: `motion` using `LazyMotion`, `m`, and `domAnimation` only.
- Hero: one staggered opacity/translate entrance.
- Section content: restrained once-only viewport reveals.
- Dashboard: masked vertical reveal with no parallax or scroll hijacking.
- Form: focus feedback and a compact success-state transition.
- Animate only opacity and transform in normal flow.
- `prefers-reduced-motion` receives the complete final state without delayed
  reveals or nonessential movement.

## Interaction contract

- Header and hero CTAs scroll to real page targets.
- Audit fields use explicit labels, autocomplete tokens, required constraints,
  visible focus, and a working local success state.
- The Preview sends no request and stores no submitted value.
- Navigation, form, privacy, email, and LinkedIn destinations remain keyboard
  accessible with 44px minimum targets.

## Copy contract

- The first viewport must say that SheperD recovers demurrage and detention
  overcharges from shipping-container invoices.
- Define demurrage and detention before describing exceptions or the recovery
  process; do not assume logistics or legal vocabulary.
- Prefer `eligible`, `estimated`, and `may` where an outcome depends on invoice
  facts or approval. Do not promise that every charge becomes a refund.
- Keep one primary conversion action: a free container-invoice audit.

## Image and delivery contract

- Hero mark: intrinsic `512 × 395`; transparent PNG; responsive `next/image`.
- Dashboard: intrinsic `1892 × 945`; responsive `next/image`; never stretched.
- Selected reference is documentation only and never shipped to the page.
- Open Graph uses a purpose-built `1200 × 630` capture of the implemented hero.
- Avoid runtime third-party image, font, analytics, and tracking requests.

## Accessibility and performance gates

- WCAG AA-oriented contrast, semantic landmarks, one H1, logical headings.
- Skip link, keyboard path, forced-colors resilience, 200% reflow, no 320px
  horizontal overflow.
- No meaning depends on glow, color, motion, crop, hover, or pointer precision.
- Performance targets: Lighthouse Performance at least 95, CLS at most 0.05,
  application-authored script transfer below 150KB where practical, and no
  avoidable third-party runtime.

## Publication boundary

The visual implementation may reproduce content currently visible on
`sheperd.io` for local stakeholder evaluation. It does not independently verify
those claims. `BUILD_TARGET=production` remains fail-closed until exact claim,
legal, intake, commercial, metadata, deployment, and publication approvals are
recorded.
