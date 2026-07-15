# SheperD Recovery Corridor Autonomous Goal

Status: active
Created: 2026-07-15
Workspace: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD/website`
Selected reference: `docs/references/recovery-corridor-selected.png`

## Copy-ready `/goal`

```text
/goal

Faithfully rebuild the local SheperD website as the selected Recovery Corridor
design in docs/references/recovery-corridor-selected.png. Treat that image as the
controlling visual target, not loose inspiration.

Preserve and reuse:
- the existing Next.js Pages Router project, strict TypeScript, pnpm, tests,
  security headers, noindex Preview posture, and production fail-closed gate;
- the exact live shepherd logo at public/brand/sheperd-logo.png;
- the exact live Recovery Summary image at
  public/media/recovery-dashboard.png;
- the current live-site headline, problem framing, $2.1B / $6.2B / 3 years,
  160+ checks, benefits, three-step workflow, form fields, LinkedIn,
  Privacy Policy, info@sheperd.io, and footer identity.

Build the selected visual system in depth:
- deep navy hero, enlarged exact shepherd mark, strong left-aligned headline;
- one connected cobalt recovery corridor through the figures and process;
- cool white problem/process surface with precise operational spacing;
- full-width dark dashboard theater using the exact dashboard image;
- integrated audit form with a working local success state and no network or
  persistence side effects;
- responsive desktop, tablet, and mobile layouts;
- purposeful Motion entrance, viewport, dashboard, and form transitions;
- reduced-motion, forced-colors, keyboard, 200% zoom, and 320px support;
- exact favicon/brand icon, Open Graph image, canonical preview metadata, and
  optimized image delivery.

Use website/DESIGN.md as the controlling design schema. Do not introduce a new
brand, logo, dashboard, customer proof, certification, case result, or extra
metric. Do not deploy, publish, change DNS, enable indexing, or remove the
production build block.

Ordered phases:
1. Bind the reference, assets, exact live-source content, and design tokens.
2. Implement the page structure and functional conversion path.
3. Add responsive visual fidelity and reduced-motion-safe Motion behavior.
4. Add favicon, Open Graph, metadata, security, and delivery optimizations.
5. Run lint, strict typecheck, unit tests, build, production negative build, and
   browser E2E.
6. Capture the implementation at the reference viewport, compare it directly
   with the selected image, write design-qa.md, and fix every P0/P1/P2 finding.
7. Stop only when design-qa.md says `final result: passed` and all engineering
   gates pass.

Success criteria:
- The selected layout and hierarchy are immediately recognizable at desktop.
- The exact logo and dashboard are used, not approximated.
- The complete page has no clipped text, broken spacing, hydration errors,
  console errors, failed first-party requests, or horizontal overflow.
- The audit interaction works locally without transmitting or storing data.
- Lint, typecheck, unit tests, build, E2E, accessibility, and design QA pass.
- The live site and production publication state remain untouched.

Stop rules:
- Stop and report blocked if the selected reference, logo, or dashboard cannot
  be read or rendered.
- Do not silently substitute assets, fabricate proof, or weaken production
  publication gates.
- Do not claim production readiness from local technical success.
- Preserve unrelated working-tree changes and do not commit, push, deploy, or
  mutate the public domain without explicit authorization.
```

## Current frontier

- Selected reference resolved and copied into the project.
- Live logo and Recovery Summary image resolved and copied into public assets.
- Existing app is a strict Next.js Pages Router Preview.
- Existing production build intentionally fails with
  `PRODUCTION_PUBLICATION_BLOCKED`.
- The current implementation still uses the superseded Margin Notes design and
  must be replaced by the Recovery Corridor implementation.

## Allowed work

- Local source, styles, components, content, tests, documentation, and assets
  inside `website/`.
- Local dependency installation and local browser verification.
- Local screenshots and Open Graph artifacts derived from the implementation.

## Blocked work

- Public deployment, live-site mutation, domain or DNS changes, indexing,
  analytics, CRM, email delivery, backend intake, persistence, commit, and push.
- Production claim approval or legal/commercial approval by inference.

## Required evidence

- `DESIGN.md`
- `design-qa.md`
- `QA-REPORT.md`
- passing `pnpm lint`, `pnpm typecheck`, and `pnpm test`
- passing optimized Preview build and expected production negative build
- browser capture and interaction checks at desktop and mobile widths
