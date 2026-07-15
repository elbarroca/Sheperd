# Canonical Goal: Clean-Room SheperD Website Rebuild with Open Design + Codex

Copy this entire file into Codex as one `/goal`.

```text
/goal

Rebuild the SheperD website completely from zero. Use Open Design as the design studio and Codex CLI as the engineering agent. The result must have high-conviction positioning, clear conversion copy, memorable visual identity, original imagery, purposeful motion, excellent mobile UX, accessibility, and verified performance.

This is a clean-room rebuild, not another refinement pass.

## 1. Objective

Replace the current website with a new, evidence-safe marketing experience that answers, within five seconds:

1. Who is this for?
2. What problem does it help frame?
3. Why is the approach credible and distinct?
4. What should the visitor do next?

Use the loop:

brief -> copy strategy -> visual directions -> Open Design artifacts -> scored selection -> Codex implementation -> browser critique -> measured optimization -> verified handoff

Do not preserve the current layout, JSX, CSS, visual system, generated images, component architecture, motion treatment, or visual snapshots. Preserve only verified facts, publication restrictions, official-source links, and legal/evidence constraints.

## 2. Current environment facts

- Workspace: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD`
- Current app target: `/Users/barroca888/Downloads/Dev/Partners/Mikey/SheperD/website`
- The workspace and `website/` are not currently Git repositories.
- Codex is installed at `/Users/barroca888/.bun/bin/codex`.
- On this Mac, `od` currently resolves to `/usr/bin/od`, Apple's octal-dump utility. It is not Open Design. Never run bare `od` until the Open Design executable has been resolved and verified by absolute path.
- Open Design's normal local preview uses `http://localhost:7456`.
- The rebuilt website should use `http://localhost:3000` unless that port is occupied by an unrelated process.
- The current website is a noindex, no-collection Preview. Production publication is fail-closed because product/company/legal/claim authority remains incomplete. Do not weaken that boundary.

Treat these facts as starting evidence, then verify them locally before acting.

## 3. Authorization and destructive boundary

You are authorized to remove and replace the current website implementation inside `website/`, but only after a verified recovery checkpoint.

Before deletion:

1. Inventory the current tree and identify factual/evidence documents separately from UI implementation.
2. Stop the old dev server gracefully if it owns port 3000.
3. Create one timestamped recovery archive outside `website/`.
4. Record the archive path, byte size, SHA-256, and successful list/read check.
5. Extract verified product facts, official sources, publication blockers, and no-collection requirements into a concise new `website/docs/FACTS-AND-CONSTRAINTS.md`.

After the checkpoint:

- Delete the old runtime UI, styling, components, generated visual assets, UI-specific tests, and visual baselines.
- Do not copy old UI code into a `legacy` folder inside the new app.
- Do not use screenshots of the old site as a design direction.
- Do not delete the recovery archive or the factual constraint record.
- Do not delete unrelated research or partner files outside `website/`.

Because there is no Git repository, initialize one only after the recovery checkpoint, using `feat/open-design-rebuild` as the initial branch. Do not create or push a remote without explicit authorization.

## 4. Open Design setup and verification

Use the official `nexu-io/open-design` repository as tooling, never as production application code.

### 4.1 Pin and isolate the tooling

1. Resolve the latest stable Open Design release from its official GitHub repository at execution time.
2. Clone or install that exact release outside the SheperD product directory, for example as a sibling tooling checkout.
3. Record the tag, commit SHA, license, Node requirement, and pnpm version.
4. Read Open Design's root `AGENTS.md`, `QUICKSTART.md`, `docs/agent-adapters.md`, and relevant skill/plugin specifications before running it.
5. Do not document or choose Open Design daemon storage paths until its `AGENTS.md` daemon-data contract has been read.
6. Do not use an unpinned `curl | sh` installation path.

Use the Node and pnpm versions pinned by the checked-out Open Design release. Do not assume versions from this prompt remain current.

### 4.2 Prove Open Design can run Codex

Primary operating mode: Open Design orchestrates the installed Codex CLI.

1. Confirm the Open Design process PATH includes `/Users/barroca888/.bun/bin`.
2. Start Open Design through its documented lifecycle command, currently `pnpm tools-dev run web` for a source checkout.
3. Confirm the daemon and web UI are healthy and the printed local URL is reachable.
4. In Open Design Settings -> Execution mode, rescan and confirm Codex is detected and authenticated.
5. Run one bounded smoke artifact with `web-prototype` or the current equivalent.
6. Save the artifact, screenshot it, and record the exact skill, design system, model, prompt, and output path.

Do not claim integration success merely because the UI opens. Success requires Codex to complete the bounded artifact run.

### 4.3 Prove Codex can consume Open Design

Secondary operating mode: Codex CLI consumes Open Design through MCP.

1. Obtain the absolute Open Design MCP command from the desktop Settings snippet or the verified installed CLI.
2. Preview the configuration with the official dry-run equivalent of `od mcp install codex --print`.
3. Inspect the proposed change before installing it.
4. Install using the verified absolute Open Design executable, never `/usr/bin/od`.
5. Run `codex mcp list` and inspect the active server in the Codex TUI with `/mcp`.
6. Execute one read-only MCP smoke: list a design skill, retrieve a `DESIGN.md`, or retrieve the bounded smoke artifact.

If the current Codex process must restart before the MCP server appears, write `website/docs/OPEN-DESIGN-SETUP-STATUS.md` with the exact resume command and continue this same goal in the fresh process. Do not pretend the unobserved MCP is active.

## 5. Codex cloud lane

Codex cloud is a separate environment, not an extension of the laptop's local STDIO MCP.

- A local Open Design daemon or local STDIO server is not automatically available inside a cloud task.
- Codex cloud requires a repository branch or commit it can check out. This workspace has no remote yet.
- Cloud setup scripts can install dependencies with internet access, while agent internet access is off by default unless configured.

Use cloud only as a gated reproducibility experiment:

1. Complete the local Open Design + Codex loop first.
2. If a remote repository and push authorization become available, create a Codex cloud environment using the app's pinned runtime and setup commands.
3. Either install and launch a pinned Open Design runtime inside the cloud container, or use a secured remotely reachable MCP endpoint whose transport and authentication are verified.
4. Do not assume the local loopback daemon, local filesystem, MCP config, or secrets exist in cloud.
5. Run one bounded cloud task: critique the selected direction or implement a small isolated section.
6. Compare its output against the local baseline using the same rubric.

If remote authorization or a cloud-compatible Open Design transport is unavailable, record `cloud_not_run_external_authorization_required`. The local Open Design + Codex implementation may still complete the goal. Never label the cloud lane verified without an observed run and diff.

## 6. Strategy before design

Do not generate the final site from a vague landing-page prompt.

Create these artifacts first:

- `website/docs/AUDIENCE-AND-JOB.md`
- `website/docs/POSITIONING.md`
- `website/docs/CLAIM-LEDGER.md`
- `website/docs/COPY-DECK.md`
- `website/docs/OPEN-DESIGN-BRIEF.md`

The strategy must define:

- Primary audience and secondary stakeholders.
- Triggering situation and job-to-be-done.
- Current alternative or failure mode.
- The narrow, verified value proposition.
- One primary visitor action.
- Top objections and evidence that can answer them.
- Claims that are approved, unsupported, or prohibited.
- Voice, memorable idea, and words to avoid.

Use only verified workspace evidence and official sources. Never convert an inference into published fact. Put unresolved facts in the claim ledger and suppress them from rendered copy.

### Copy quality bar

The final copy must:

- Identify the audience and problem immediately.
- Lead with visitor value, not company autobiography.
- Use one clear promise only when evidence supports it.
- Explain the mechanism without jargon.
- Give every section a distinct conversion job.
- Use one dominant CTA and one optional lower-commitment action at most.
- Replace vague words such as revolutionary, seamless, powerful, intelligent, transform, unlock, and optimize unless a concrete sentence earns them.
- Avoid legal conclusions, recovery promises, outcome claims, customer proof, company facts, fees, timelines, security claims, and contact details without publication evidence.
- Be concise enough to scan on a 320px screen.

Do not claim the copy was user-tested unless real users participated. A heuristic five-second review is not user research.

## 7. Open Design exploration

Store product-owned experiment outputs under `website/design-experiments/`. Do not rely on undocumented Open Design daemon paths.

Before generating:

1. List the installed marketing/design skills, relevant plugins, and candidate design systems.
2. Inspect their exact manifests and versions.
3. Use only capabilities that are actually installed and healthy.
4. Prefer `web-prototype` or `saas-landing`, the critique utility, and a verified media-generation workflow when available.
5. Treat migration/Next.js export plugins as optional until their current status and output quality are proven.

Generate three materially different mobile-first directions from the same approved strategy and copy objective. They must differ in concept, information rhythm, art direction, type, image behavior, and motion—not just color.

Each direction must include:

- A named creative idea and one-sentence rationale.
- Its own `DESIGN.md` using the active Open Design schema.
- A real single-page HTML/CSS artifact.
- Original or rights-cleared image assets with provenance.
- A mobile screenshot at 375px and desktop screenshot at 1440px.
- A short motion plan with reduced-motion behavior.
- The same approved core message so visual comparisons remain meaningful.

Reject directions that use:

- Generic SaaS hero + three cards + logo wall.
- Fake dashboards or fabricated product UI.
- Gradient text, purple AI glow, glass panels, decorative grids, excess pills, or template-like bento layouts.
- Stock imagery that implies customers, operations, certification, or results.
- Animation without narrative or interaction value.
- Desktop layouts merely stacked on mobile.

## 8. Scored selection and iteration

Score every direction out of 100:

- Message clarity in five seconds: 25
- Audience relevance: 15
- Memorability and visual distinctiveness: 15
- Trust and evidence safety: 15
- CTA clarity and conversion path: 10
- Mobile UX: 10
- Accessibility readiness: 5
- Performance feasibility: 5

Create `website/design-experiments/SCORECARD.md` with evidence for every score.

Selection rules:

- No direction can win with a trust/evidence-safety failure.
- The winner must score at least 80/100.
- If none reaches 80, synthesize one additional direction from the strongest non-conflicting traits and rescore.
- Run the Open Design critique workflow on the winner.
- Make two focused refinement passes. Edit the artifact in place instead of regenerating randomly.
- Record why each accepted change improved the rubric.

## 9. Clean-room implementation

Implement the selected direction as the real website under `website/` with Codex CLI.

- Start from a fresh application scaffold.
- Keep Next.js and strict TypeScript only if they remain the simplest fit; do not preserve the previous component tree merely because it exists.
- Translate the chosen artifact into semantic, maintainable application code. Do not ship the Open Design repo or iframe artifact as the production implementation.
- Use server-rendered/static content by default and isolate client code to actual interaction or motion leaves.
- Use one motion system only.
- Keep semantic content available without JavaScript.
- Use responsive images with explicit dimensions, local optimized formats, meaningful alt text, and provenance.
- Preserve the official-source register and fail-closed content/publication boundary.
- Add no form, upload, analytics, cookies, CRM, contact capture, tracking, or third-party runtime without explicit approval.
- Keep all secrets out of source, prompts, logs, screenshots, and documentation.

Required experience:

- A strong mobile hero with audience, message, and CTA visible without horizontal scrolling.
- Distinct section compositions instead of repeated cards.
- Purposeful sticky behavior only when it improves navigation or comprehension.
- Purposeful motion for entry, sequence, state, or feedback.
- Full `prefers-reduced-motion` support.
- Keyboard navigation, visible focus, 44px minimum targets, 200% reflow, forced-colors resilience, and WCAG AA contrast.
- A finished footer and coherent closing action.

## 10. Browser and optimization loop

Start the new dev server and keep it available for review. Open the local URL in a browser and test the real page, not static files only.

At minimum verify:

- 320x900
- 375x900
- 768x1024
- 1024x900
- 1440x1000
- 1920x1080

For each relevant viewport:

- Check visual hierarchy, wrapping, crop, touch targets, sticky behavior, and page overflow.
- Exercise navigation, CTA, disclosures, menus, keyboard focus, and touch input.
- Inspect console errors, runtime errors, failed network requests, hydration warnings, CSP violations, and layout shifts.
- Capture deterministic screenshots.

Run at least one copy A/B comparison on the selected design. Change only the hero message/CTA, not the visual direction, then choose the clearer version against the same rubric.

## 11. Verification gates

Define project-equivalent commands and run all of them before completion:

1. Lint.
2. Strict typecheck.
3. Unit/content tests.
4. Optimized Preview build.
5. Browser E2E in Chromium, Firefox, and WebKit.
6. Axe on the home page and notice routes.
7. Visual regression at all six viewports.
8. No-JavaScript reading path.
9. Reduced motion, forced colors, 200% zoom, keyboard, and touch paths.
10. Link, image, and external-request checks.
11. Secret and credential scan.
12. Dependency/license review.
13. Production negative build proving publication remains blocked.

Performance targets for the local optimized Preview:

- Lighthouse mobile Performance >= 95.
- Lighthouse Accessibility = 100.
- Lighthouse Best Practices = 100.
- CLS <= 0.05.
- No avoidable render-blocking third-party requests.
- Responsive images stay within a 2 MB total-page transfer ceiling.
- Initial modern JavaScript stays below 150,000 gzip bytes unless a measured exception is documented and approved.

Do not optimize the intentional noindex Preview for SEO by weakening crawler restrictions. Keep technical performance separate from publication readiness.

## 12. Required deliverables

- New website source under `website/`.
- `website/docs/FACTS-AND-CONSTRAINTS.md`.
- `website/docs/OPEN-DESIGN-SETUP-STATUS.md`.
- `website/docs/AUDIENCE-AND-JOB.md`.
- `website/docs/POSITIONING.md`.
- `website/docs/CLAIM-LEDGER.md`.
- `website/docs/COPY-DECK.md`.
- `website/docs/OPEN-DESIGN-BRIEF.md`.
- Three direction artifacts and screenshots under `website/design-experiments/`.
- `website/design-experiments/SCORECARD.md`.
- Final project `DESIGN.md`.
- Image/media provenance record.
- Updated automated tests and six visual baselines.
- `website/QA-REPORT.md` with exact current evidence.
- `website/DEPLOYMENT.md` with local source identity, remote state, and production blockers.
- One running local URL for user review.

## 13. Stop rules

- Do not delete the current implementation before the recovery archive passes verification.
- Do not run `/usr/bin/od` as Open Design.
- Do not use unpinned remote install scripts.
- Do not claim Open Design, MCP, or cloud integration without an observed smoke run.
- Do not push, deploy, attach a domain, change DNS, create paid resources, or mutate an existing live site without explicit authorization.
- Do not publish unsupported claims to make the copy sound stronger.
- Do not use a generic template merely because it passes tests.
- Do not mark the goal complete while any local P0/P1 remains.
- If external authentication blocks cloud or deployment, finish all safe local work, record the exact blocker and one required user action, and stop there.

## 14. Completion contract

Complete only when:

- The old website implementation is absent from the active app.
- The recovery checkpoint is verifiable.
- Open Design has completed one real artifact through Codex locally.
- The selected design scored at least 80/100 with no evidence-safety failure.
- The new website implements the selected artifact as real maintainable code.
- All local verification gates pass.
- There are no local P0/P1 findings.
- The local review URL is running and reported.
- Preview quality and Production readiness are reported separately.
- Production remains blocked unless every publication requirement has independently resolved.

Work autonomously through discovery, setup, experimentation, implementation, browser review, and optimization. Make evidence-based choices without asking preference questions that the rubric can answer. Ask for user input only when authority, credentials, remote publication, or missing business truth would materially change the safe result.
```

## Verified basis for this goal

- Open Design officially lists Codex CLI support through `od mcp install codex`, a dry-run `--print` option, local artifacts, skills, plugins, and `DESIGN.md` systems.
- Open Design's source quickstart currently requires the versions pinned in its repository and uses `pnpm tools-dev run web` as the foreground lifecycle command.
- Open Design warns that macOS `/usr/bin/od` can shadow its CLI; this machine currently resolves `od` to that Apple binary.
- Codex clients support local STDIO MCP servers, but Codex cloud tasks run in isolated repository containers with their own setup and network policy.
- This SheperD workspace currently has no Git repository, so cloud execution and remote handoff cannot be assumed.
