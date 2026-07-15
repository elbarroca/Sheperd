# Open Design Setup Status

Status: integration verified on 2026-07-15; localhost only

## Pinned toolchain

- Open Design release: `open-design-v0.15.0`
- Release commit: `79e257d62c0e6a8d9084f2a6464f08a251a5c0bb`
- Checkout: `/Users/barroca888/Downloads/Dev/Partners/Mikey/open-design-tooling-0.15.0`
- Release/package drift: the release tag is `v0.15.0`; the checked-out package metadata and daemon health endpoint report `0.14.2`. This is recorded, not hidden.
- Node: `v24.18.0`
- pnpm: `10.33.2`
- Codex CLI: `0.144.4`
- Codex authentication: ChatGPT login present; no credential value was read or recorded.
- Runtime namespace: `sheperd`
- Open Design UI: `http://127.0.0.1:7456/`
- Open Design daemon: `http://127.0.0.1:7457/`
- Runtime data: `/Users/barroca888/Downloads/Dev/Partners/Mikey/open-design-tooling-0.15.0/.tmp/sheperd-runtime`

## Primary lane: Open Design to Codex

Observed pass:

- Open Design detected Codex CLI `0.144.4`.
- Its built-in adapter test returned `Codex CLI replied in 7551 ms — 'ok'`.
- The Web Prototype plugin and Neutral Modern design system produced a complete HTML artifact through the Open Design UI.
- Project: `23bd1301-b948-4a28-bbd1-6de5203d48f2`
- Plugin: `example-web-prototype` `0.1.1` (shown in the UI as Web Prototype)
- Design system: `default` (shown in the UI as Neutral Modern)
- Model: Open Design's Codex adapter default. The UI and run metadata did not emit a model identifier, so no model name is inferred.
- Artifact: `website/design-experiments/open-design-smoke/index.html`
- Open Design critique: `website/design-experiments/open-design-smoke/critique.json`
- The smoke prompt was deliberately bounded and made no SheperD capability, customer, legal, outcome, pricing, or security claim.

Exact smoke prompt:

> Create a bounded, single-page mobile-first prototype titled Record Review. Audience: importer finance and logistics teams. Hero message: Start with the record. Show exactly three evidence categories: Billing facts, Operational facts, Governing terms and current rules. Use one on-page CTA labeled Review requirements. No company capability claims, forms, pricing, testimonials, customer logos, fake dashboard, legal conclusions, outcomes, external images, or third-party scripts. Make it distinctive, calm, and responsive at 375px and 1440px. This is an integration smoke, not the final SheperD website.

Open Design asked which record should anchor the page; its prefilled answer `General import record` was accepted. The final output was `record-review-2.html`, copied without modification to the product-owned artifact path above. The recorded critique panel score was 4/5 with clarity 5/5 and hierarchy, typography, motion, and brand each 4/5.

## Secondary lane: Codex to Open Design MCP

Observed pass:

- The exact daemon-derived install proposal was reviewed before installation.
- The global Codex MCP entry uses an absolute Node 24 executable and the pinned checkout's daemon CLI; it does not depend on `/usr/bin/od` or a floating package alias.
- A read-only `codex exec --ephemeral --sandbox read-only` smoke called Open Design `list_skills` and observed 162 skills.
- A second read-only smoke read `od://skills/frontend-design/SKILL.md` from server `open-design` and returned `OPEN_DESIGN_MCP_OK skill=frontend-design mode=mcp surface=resource`.
- No Open Design project was created or modified in the MCP smoke.

The first resource-inspection attempt used the non-existent skill id `web-prototype` and correctly failed closed with a daemon 404. The retry used the exact catalog id `frontend-design` and passed. Unrelated disabled or expired MCP services emitted authentication warnings during Codex startup; they did not affect the observed Open Design calls.

## Direction runs

Three materially different mobile-first directions completed through the primary Open Design-to-Codex lane. The product-owned exact prompts, project IDs, run IDs, plugin IDs, design systems, model non-disclosure, outputs, and source correction are recorded in `website/design-experiments/OPEN-DESIGN-RUN-LOG.md`.

Direction B — Margin Notes won the controlling scorecard at 95/100 before refinement and 97/100 after the observed Open Design critique plus two focused in-place passes. It had no trust/evidence-safety failure.

## Reproduction

Start Open Design from the pinned checkout:

```sh
export PATH=/Users/barroca888/.nvm/versions/node/v24.18.0/bin:/Users/barroca888/.bun/bin:$PATH
export OD_DATA_DIR=/Users/barroca888/Downloads/Dev/Partners/Mikey/open-design-tooling-0.15.0/.tmp/sheperd-runtime
export OD_CODEX_DISABLE_PLUGINS=1
pnpm --dir /Users/barroca888/Downloads/Dev/Partners/Mikey/open-design-tooling-0.15.0 tools-dev run web --namespace sheperd --daemon-port 7457 --web-port 7456
```

Confirm the Codex MCP registration:

```sh
/Users/barroca888/.bun/bin/codex mcp get open-design
```

## Boundary

This setup is local design tooling. It is not a production dependency, runtime service, public deployment, customer integration, or evidence for any company/product capability claim.
