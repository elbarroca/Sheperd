---
title: Goal 2 - 10 of 10 Next.js Website
type: goal
status: ready
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/goal
  - sheperd/website
  - sheperd/design
---

# Goal 2 - 10/10 Next.js Website

> [!tip] How to use
> Start a new autonomous Codex task in this repository and paste everything from `/goal` onward. This goal creates `website/`, deploys a verified Vercel Preview, and promotes production only after every truth, legal, privacy, security, brand, contact, and domain gate passes.

/goal

Design, engineer, verify, and deploy a production-grade SheperD marketing website as a nested Next.js application at `website/`. Make it exceptional through content, storytelling, typography, layout, personalized logistics components, purposeful Framer Motion, evidence, responsive composition, accessibility, and engineering quality.

This is a **motion-rich but disciplined website**. Use Framer Motion for purposeful enter, exit, hover, focus-adjacent, disclosure, and storytelling mechanics. Build original shipping-container and evidence-led components. Do not use ScrollWorld or Higgsfield/Xfield. Motion must improve comprehension and perceived quality without weakening trust, accessibility, responsiveness, or performance.

Work autonomously through all non-blocked implementation and verification. Do not claim “10/10” through taste or self-assessment. Earn it through the evidence-backed rubric and hard gates below.

## 1. Required outcome

Create:

- a production-grade Next.js App Router application in `website/`;
- publication-safe copy derived from the vault's claim registry;
- a distinctive design and motion system documented in `website/DESIGN.md`;
- a product/content contract in `website/PRODUCT.md`;
- strict content and claim validation that fails closed;
- complete responsive, accessibility, performance, SEO, metadata, privacy, and security implementation;
- browser, visual, content, unit, integration, and end-to-end verification;
- a verified Vercel Preview with a deployment and rollback record;
- production promotion only when all external approval gates are satisfied.

The website must tell a coherent story and create trust without invented statistics, customer logos, testimonials, case studies, product screenshots, regulatory certainty, or recovery promises.

## 2. Motion and interaction contract

Use the current official **Motion for React** package, commonly called Framer Motion: package `motion`, imports from `motion/react`. Verify the current stable release from official documentation, pin its exact version in the project lockfile, and make it the only motion runtime. Keep animation inside small client-leaf components while all semantic content renders on the server.

Required motion purposes:

- establish hierarchy when a section enters;
- show cause and effect in the invoice-to-evidence journey;
- make shipping-container components feel tactile and inspectable;
- clarify hover, press, expand, collapse, filter, or route-state changes only where those real interactions exist;
- provide coherent enter and exit behavior through `AnimatePresence` where content is genuinely mounted or removed;
- guide attention to evidence, requirements, and the primary CTA;
- reinforce the logistics/container visual language without simulating a product capability.

Motion rules:

- Animate `transform` and `opacity` by default. Animate layout only when measured and necessary.
- Typical micro-interactions: 120–220ms. Component transitions: 220–400ms. Major narrative transitions: no more than 600ms.
- Use one spring family and one easing family documented as tokens. No random per-component physics.
- Hover mechanics must also have keyboard-visible and touch-safe equivalents. Content cannot depend on hover.
- Use `useReducedMotion` and CSS media queries. Reduced-motion mode must remove non-essential movement, preserve all content, and use immediate state changes.
- Never hide meaningful content solely to reveal it on scroll. Server-rendered/no-JavaScript content must remain complete.
- Do not SSR meaningful content with `initial={{ opacity: 0 }}` or an off-screen transform. Use `initial={false}` or a progressive-enhancement pattern that leaves text visible before hydration, then animates only after an explicit client-ready state without content flash.
- Prevent layout shift by reserving final geometry before animation.
- Pause or avoid off-screen work. Remove listeners and observers on unmount.
- Respect pointer capability and do not apply desktop hover motion on coarse pointers.
- One coordinated animation grammar must control the whole site.

Prohibited:

- ScrollWorld or any part of `oso95/scroll-world`;
- Higgsfield/Xfield CLI, authentication, credits, images, videos, or generated scenes;
- GSAP, Lottie, Lenis, Three.js, WebGL scenes, a second motion library, or a home-grown animation framework;
- autoplay video, animated GIF/WebP, canvas loops, marquee, ticker, carousel autoplay, cursor follower, particle field, or endless ambient movement;
- raw scroll listeners, manual `requestAnimationFrame` loops, scroll hijacking, or smooth-scroll libraries;
- animation that delays reading, blocks interaction, causes nausea, or turns regulatory content into spectacle;
- fake product screens, fake data flow, or fake container tracking presented as operational proof.

Create `pnpm validate:motion` for static dependency/import/AST/token checks. It must verify:

- `motion` imported only from approved `motion/react` entry points is the sole motion dependency; legacy `framer-motion` and every second runtime fail validation;
- ScrollWorld and Higgsfield/Xfield are absent;
- motion code exists only in approved client-leaf modules;
- every animated component declares a reduced-motion path for browser verification;
- no raw scroll listener, uncontrolled RAF loop, autoplay media, or endless animation exists;
- duration, easing, spring, and viewport behavior use documented tokens.

Create `pnpm test:motion` for runtime performance, visibility, interaction, reduced-motion, cleanup, off-screen work, and Section 13 budgets. Static validation may not claim runtime guarantees.

## 3. Current truth and publication boundary

Vault snapshot date is 2026-07-15. Record the actual execution date and use it for source freshness. Load the vault before writing copy.

Safe provisional positioning:

> SheperD is positioning itself as an evidence-first demurrage and detention invoice audit and recovery service for U.S. importers. Cases and outcomes are assessed individually.

This is not yet a generally approved public sentence. The claim registry and human publication approval still control.

Do not publish these claims until their rows are verified and explicitly approved for the exact wording and channel:

- `$2.1B`, `$6.2B`, `$100B`, `25%`, `85%`, or `$750 per container`;
- “160+ automated checks,” a working portal, AI-driven platform, or production automation maturity;
- “most clients recover,” customer outcomes, recovery totals, error rates, or case results;
- customer names, logos, testimonials, case studies, or screenshots;
- blanket “three years of refunds” or 36-month recovery;
- guaranteed recovery, eligibility, compliance, legality, refund, or outcome;
- 24-hour or 48–72-hour estimates;
- free audit, no-risk, no-upfront-cost, success-fee, or pricing language unless commercial terms are approved;
- founder/entity/team details beyond the exact publication-approved source record.

Use primary regulatory evidence to explain context. Do not imply that FMC data proves unlawful charges or recoverable value. Regulatory language must remain educational, current, case-specific, and non-legal-advice.

If proof is missing, suppress the section or use a truthful conditional explanation. Never fill a proof gap with decorative trust signals.

Build-blocking regulatory safeguards:

- covered invoices have a 30-day issuance rule under current Part 541 in the applicable circumstances;
- the billed party must receive at least 30 calendar days to request mitigation, refund, or waiver;
- the billing party must attempt resolution within 30 days, not guarantee resolution;
- former §541.4 was vacated and the current eCFR section is reserved;
- the FMC Charge Complaint route is for common-carrier charges and has specific MTO scope boundaries;
- Charge Complaints remain separate from formal and small-claims procedures and cannot be silently combined;
- the three-year complaint limitation is not blanket eligibility, refund entitlement, or guaranteed recovery.

Regulatory entries older than 30 days relative to execution date fail public validation until refreshed from current primary sources. Case-specific conclusions remain human/domain-reviewer decisions.

## 4. Mandatory context load

Read fully, in order:

1. `SheperD HQ.md`
2. `00_System/Vault Operating Manual.md`
3. `00_System/Knowledge Retrieval Contract.md`
4. `01_Company/Claims and Evidence Register.md`
5. `01_Company/Company Brief.md`
6. `01_Company/Product and Business Model.md`
7. `01_Company/Open Questions and Diligence.md`
8. `02_Domain/D&D and OSRA Primer.md`
9. `02_Domain/Market and Competitive Landscape.md`
10. `03_GTM/ICP and Stakeholder Personas.md`
11. `03_GTM/Customer Journey and Funnel.md`
12. `03_GTM/Website and Content Audit.md`
13. `04_Operations/Customer Data Intake and Security.md`
14. `05_AI/Human Approval Policy.md`
15. relevant `10_Sources/` notes
16. `06_Research/` outputs if Goal 1 has been completed and passed QA

Then inspect:

- root and nested `AGENTS.md` instructions;
- Git state and user changes;
- Node and pnpm versions;
- existing Vercel configuration and authentication without printing credentials;
- current official Next.js, React, Vercel, Impeccable, DesignMD, and Taste Skill documentation.

Before scaffolding:

- If `website/` exists, inventory it and determine ownership. Never overwrite, delete, reinitialize, or run a force scaffold. Preserve user work and stop for a destructive conflict.
- If Git exists, work on `feat/sheperd-website` or a user-approved feature branch; never commit to `main`/`master`, force push, skip hooks, or discard unrelated changes.
- If Git does not exist, do not initialize it without explicit approval; record a deterministic source hash instead.
- Record a before-state file manifest and protect unrelated root/vault files from formatters, package scripts, and deployment configuration.

Preserve the existing Obsidian vault at the repository root. Create only `website/`. Do not move the vault into a new folder, rename the repository, or create a competing context system.

## 5. Design and engineering skill sequence

Use these tools in this order because later tools must obey the evidence, design, motion, and performance contracts:

1. **Vault evidence synthesis**
   - Convert approved context into `website/PRODUCT.md` and a public-content matrix.

2. **DesignMD research**
   - Review 3–5 relevant systems from [DesignMD](https://getdesign.md/design-md).
   - Record typography, grid, density, color, navigation, proof patterns, conversion patterns, mobile behavior, and take/avoid notes.
   - Select one coherent reference family. Do not assemble a collage of unrelated trends.
   - Use principles only. Do not copy layouts, identity, assets, proprietary copy, or trademarks.

3. **Taste Skill**
   - Read and follow the installed `design-taste-frontend` skill completely before design or code changes.
   - Record the design read and dials in `website/DESIGN.md`.
   - Use its motion guidance only within this goal's single-runtime, tokenized, reduced-motion contract.

4. **Impeccable**
   - Recheck the current official installation instructions at [Impeccable](https://impeccable.style/).
   - Current starting point: Node `>=22.12`, project-local install, `/impeccable init`, `document`, `craft`, `polish`, `critique`, `audit`, and deterministic detection. Recheck at execution time.
   - Pin the chosen Impeccable version in `website/` and run the local executable from that directory with `pnpm exec impeccable detect src/`; do not use an unpinned `npx` fetch in acceptance checks.
   - Do not approve or create global hooks. Project hooks require user approval.
   - Run Impeccable sequentially after `PRODUCT.md` and `DESIGN.md` exist.
   - Reject generic motion, conflicting timing, glassmorphism, generic gradients, or unsafe claims.

5. **Visual and motion production**
   - Use original diagrams, geometric editorial compositions, data-line motifs, port/shipping abstractions, approved local photography, and personalized shipping-container components.
   - Build motion from layout and vector primitives with Framer Motion. Do not depend on generated video.
   - If the installed image-generation skill is used, generate static source imagery, preserve prompt/provenance, review for misleading operational detail, and animate only its presentation layer.
   - Maintain `website/ASSET-MANIFEST.md` with origin, creator/tool, prompt where applicable, license/usage right, source URL, checksum, EXIF/metadata stripping result, optimization, alt/decorative decision, approver, and production status for every non-code asset.
   - Never invent a product interface, customer evidence, container event, regulatory document, or result screenshot.

6. **Next.js and Vercel verification skills**
   - Use installed Next.js, browser-verification, accessibility, and deployment skills when applicable.
   - Read each applicable skill before acting and record its material constraints in the working plan.

Do not install ScrollWorld, inspect its setup, or authenticate Higgsfield/Xfield. Motion for React and original components are the approved implementation path.

## 6. Design contract

Design read:

> Trust-first B2B logistics recovery for finance and supply-chain buyers. Precise industrial-editorial composition, strong information hierarchy, restrained color, visible evidence, tactile shipping-container mechanics, and controlled cinematic depth. Serious without feeling institutional. Distinctive without spectacle.

Initial dials:

```text
DESIGN_VARIANCE=7
MOTION_INTENSITY=6
VISUAL_DENSITY=4
```

The design agent may propose a dial change with a written reason before component implementation. The independent design reviewer must approve it; motion above 7 also requires user approval.

System rules:

- Before implementation, declare exactly one theme strategy in `DESIGN.md`: `light-only`, `dark-only`, or `dual-mode`. Do not alternate themes by section. A dual-mode choice requires full token, visual, accessibility, and screenshot coverage in both modes.
- One approved accent family with accessible shades.
- One radius system, spacing scale, grid, type scale, and shadow policy.
- Use a plain text SheperD wordmark until an approved mark is supplied.
- No invented production logo or iconography presented as the company mark.
- For internal Preview, derive a neutral typographic `S`/`D` utility icon from the approved wordmark styling and label it Preview-only. Approved production brand assets remain a production gate; never imply the neutral icon is an approved logo.
- Hero headline: maximum two lines at the target desktop width.
- Hero support: one concise sentence, ideally 20 words or fewer.
- One visible primary CTA per viewport region.
- No AI-purple gradients, generic blue gradients, glassmorphism, glowing orbs, fake browser chrome, three-equal-card templates, endless rounded cards, oversized empty hero, route-dot navigation, numbered badges, or testimonial/logo placeholders.
- No default center bias. Use asymmetric editorial composition when it improves hierarchy.
- No visible em dash or en dash in website copy.
- No decorative section labels that repeat headings.
- Use cards only for genuinely independent, scannable units.
- Every visual must support trust, comprehension, proof, or conversion.
- Mobile layouts must be intentionally recomposed, not proportionally shrunk.
- Interaction states must be clear, responsive, accessible, and consistent with the motion tokens.

Depth may come from crop, scale, type contrast, grid overlap, texture, borders, controlled shadow, photography, illustration, layered transforms, and deliberate enter/exit choreography. Avoid continuous decorative movement.

### Personalized logistics component system

Design and implement an original component family. Final names may change, but each component needs a documented purpose:

- **Container Hero:** a responsive composition of container modules that establishes audience, problem, and evidence flow. On entry, modules assemble once. Evidence labels remain in the DOM and use real button/disclosure semantics with `aria-expanded`; pointer hover may preview, keyboard focus/activation must work, coarse pointers use tap, and no-JavaScript/reduced-motion modes show the labels by default. No perpetual movement.
- **Invoice Manifest:** a semantic list showing how invoice facts, operational facts, and rules must align. Rows reveal relationships through short staggered transitions, with all text present without JavaScript.
- **Evidence Stack:** layered document/evidence cards that expand and collapse accessibly. It must not resemble an actual customer file or product screenshot.
- **Recovery Route:** an educational process path from intake to reviewed outcome. Animate state changes, not scrolling itself. Every conditional step is visibly conditional.
- **Container Seal CTA:** a distinctive CTA treatment inspired by a shipping seal or inspection mark, with clear button semantics and restrained press/hover mechanics.
- **Port Grid:** a responsive editorial grid for stakeholder, FAQ, or review-requirement content. Reflow on mobile without JavaScript measurement.

For every component document:

`purpose`, semantic structure, content source, visual anatomy, variants, responsive behavior, hover/focus/press behavior, enter/exit behavior, reduced-motion behavior, performance cost, and prohibited misuse. Add loading, failure, or empty-state contracts only when the component genuinely loads or mutates data.

Do not create a component only to display an effect. Reuse the system where it improves comprehension, but avoid repeating the same animation in every section.

## 7. Content and storytelling contract

The main page must answer, in this order:

1. Who SheperD serves.
2. What D&D invoice problem it examines.
3. What SheperD can truthfully do today.
4. What documents and facts a review may require.
5. How the case-specific process works.
6. Why the regulatory and evidence discipline matters.
7. What is conditional, not guaranteed, or outside SheperD's role.
8. What safe next action the visitor can take.

Recommended page architecture:

- Header with wordmark, essential navigation, and one CTA.
- Hero with clear audience/problem/outcome framing.
- Problem anatomy using an evidence-led, motion-enhanced diagram with a complete semantic fallback.
- What SheperD reviews, based only on approved current capability.
- How it works, separating intake, review, evidence, dispute support, and outcome.
- Why evidence matters, using primary regulatory context.
- Who is involved: finance, supply chain, operations, legal/security.
- Data and security expectations, without claiming unverified controls.
- Case-specific limitations and FAQ.
- Final CTA with truthful next-step expectations.
- Footer with approved entity/contact/legal information only.

Rules:

- Write for CFO, finance, supply-chain, and operations stakeholders without pretending they share the same motivation.
- Prefer plain English, short sentences, concrete verbs, and evidence over hype.
- Avoid “revolutionize,” “unlock,” “seamless,” “cutting-edge,” “AI-powered,” “game-changing,” and generic startup language.
- Do not call SheperD a SaaS, platform, fintech, regtech, or AI product unless approved evidence supports it.
- Do not create fake urgency, countdowns, scarcity, risk-free promises, or outcome guarantees.
- Do not present legal or regulatory guidance as legal advice.
- Hide unsupported modules entirely. Do not leave “coming soon” proof sections.

## 8. Content safety architecture

Create a typed public-content registry in `website/src/content/`.

Each factual claim requires:

```text
claimId
exactText
sourceState
evidenceStatus
claimType
claimDisposition
publicationStatus
sourceIds
sourceUrls
checkedDate
expiresOn
approvedFor
approvedBy
approvalDate
notes
```

`evidenceStatus` must use the vault enum exactly: `verified`, `company-claim`, `internal-proposal`, `internal-observation`, `internal-data`, `internal-decision`, `inference`, `unverified`, `mixed`, or `policy`.

`sourceState` preserves the Claims Register row state verbatim. Normalize it through this explicit mapping; fail on any unmapped value:

| Claims Register `sourceState` | `evidenceStatus` | `claimDisposition` |
|---|---|---|
| `Verified` | `verified` | `eligible-after-approval` |
| `Verified context` | `verified` | `context-only` |
| `Company-controlled consistency` | `company-claim` | `attributed-only` |
| `Company claim` | `company-claim` | `attributed-only` |
| `Company-platform claim` | `company-claim` | `attributed-only` |
| `Mixed` or `Mixed/unresolved` | `mixed` | `blocked-mixed` |
| `Unverified` or `Unverified model` | `unverified` | `blocked-unverified` |
| `Misleading` | `mixed` | `blocked-misleading` |
| `Contradicted`, `Contradicted/mixed`, or equivalent explicit conflict | `mixed` | `blocked-contradicted` |

`claimDisposition` must use: `eligible-after-approval`, `context-only`, `attributed-only`, `blocked-unverified`, `blocked-mixed`, `blocked-misleading`, `blocked-contradicted`, or `expired`. A disposition beginning `blocked-` can never be published, even if a publication field is accidentally approved.

`claimType` must use: `verified-fact`, `attributed-company-description`, `educational-primary-source`, `legal-disclaimer`, `ui-label`, or `internal-only`.

`publicationStatus` must use: `draft`, `approved`, `rejected`, `expired`, or `internal-only`.

Public eligibility matrix:

| Claim type | Required evidence | Required publication state | Extra gate |
|---|---|---|---|
| Verified fact | `verified` | `approved` | Current source, exact channel, approver, and unexpired review |
| Attributed company description | `company-claim` | `approved` | Visible attribution such as “SheperD says”; no unsupported number, result, guarantee, or product-maturity implication |
| Educational primary-source statement | `verified` | `approved` | Current primary source, accurate limitations, non-legal-advice context, regulatory freshness <=30 days |
| Legal disclaimer | `policy` or approved legal decision | `approved` | Named legal/privacy approver and exact channel |
| UI label | `policy` or `internal-decision` | `approved` | Non-factual interface wording only |

Every other combination is build-blocking. Approval never upgrades a company claim to verified. Until a baseline positioning sentence is approved, only an access-protected internal Preview may display draft copy; an externally reachable Preview and Production remain blocked.

Create `pnpm validate:content` that:

- parses the entire typed public-content registry and approved UI-label lexicon;
- finds claim references used by public routes;
- fails if a claim is missing, unsafe, expired, outside its approved channel, or lacks a source and approver;
- fails if a Claims Register source state is unmapped, normalized inconsistently, or loses its raw `sourceState`;
- fails on prohibited quantitative and guarantee wording;
- fails on fake testimonials, customer logos, product screenshots, or unapproved team/entity/contact fields;
- fails when privacy/contact/fee/product-state configuration is unresolved for production mode;
- fails if visible strings in JSX/TSX, metadata, Open Graph/Twitter assets, alt text, JSON-LD, manifest fields, legal routes, navigation, forms, or generated output bypass the typed content API or approved UI-label lexicon;
- forbids meaningful CSS `content` strings and scans built HTML/assets plus rendered pages for unregistered public claims;
- produces a route/channel-to-claim-ID manifest and verifies it against rendered text;
- prints file and claim ID without printing sensitive content.

Use an allowlisted typed API such as `getPublicClaim(claimId, channel)` and `getUiText(key)`, not duplicated or inline factual strings. AST checks, built-output checks, and rendered-page checks are all mandatory. Every public claim must be traceable from page/channel to registry to vault source and approval.

## 9. Engineering architecture

Use current stable patched versions verified from official documentation at execution time:

- Next.js App Router;
- React;
- strict TypeScript with no `any`;
- pnpm and one lockfile;
- Server Components by default;
- static generation for marketing and legal routes;
- `next/image`, `next/font`, typed metadata, and Next.js metadata-file conventions.

Choose the smallest styling system that implements `DESIGN.md` well. The pinned `motion` package with `motion/react` imports is the single approved animation dependency. Do not add another component framework, motion library, CMS, database, authentication, API layer, analytics, or form service without demonstrated need and approval.

Recommended structure:

```text
website/
├── PRODUCT.md
├── DESIGN.md
├── ARCHITECTURE.md
├── CONTENT-MATRIX.md
├── README.md
├── QA-REPORT.md
├── DEPLOYMENT.md
├── package.json
├── pnpm-lock.yaml
├── next.config.*
├── tsconfig.json
├── eslint.config.*
├── playwright.config.*
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── privacy/page.tsx
│   │   ├── terms/page.tsx
│   │   ├── not-found.tsx
│   │   ├── robots.ts
│   │   ├── sitemap.ts
│   │   ├── manifest.ts
│   │   ├── opengraph-image.tsx
│   │   └── twitter-image.tsx
│   ├── components/
│   │   ├── sections/
│   │   ├── ui/
│   │   ├── motion/
│   │   ├── logistics/
│   │   └── icons/
│   ├── content/
│   │   ├── claims.ts
│   │   ├── site.ts
│   │   └── legal.ts
│   ├── lib/
│   └── styles/
├── scripts/
│   ├── validate-content.*
│   ├── validate-motion.*
│   └── validate-links.*
├── public/
│   ├── media/
│   └── icons/
└── tests/
    ├── unit/
    ├── content/
    ├── accessibility/
    ├── visual/
    └── e2e/
```

Architecture constraints:

- Semantic content renders server-side without JavaScript.
- Use client components only for necessary interaction and isolated Framer Motion leaves.
- No unsafe HTML, runtime string-to-HTML, hardcoded secrets, mixed package managers, or unnecessary `vercel.json`.
- No sensitive data collection, invoice upload, portal, account system, or recovery estimator.
- No raw personal data in fixtures, snapshots, logs, screenshots, analytics, or deployment documentation.
- Named exports for shared modules.
- Early returns, small single-purpose components, strict types, and no speculative abstraction.
- Keep page composition readable. Do not turn every element into a component.
- Prefer CSS layout over JavaScript layout measurement.
- Do not use viewport-height tricks that break mobile browser chrome.
- Every route has a meaningful no-JavaScript experience.
- Centralize motion tokens and variants; do not duplicate anonymous variants across sections.
- Dynamically load non-critical motion leaves when it reduces initial JavaScript without causing content flashes.
- Keep the first meaningful hero copy server-rendered and immediately visible. Motion may enhance it but may not gate it.

## 10. Responsive and accessibility contract

Support at minimum:

- 320px, 375px, 768px, 1024px, 1440px, and 1920px widths;
- 200% browser zoom;
- keyboard-only operation;
- screen-reader landmarks and labels;
- high-contrast user needs where practical;
- long headings, longer translated strings, and browser text resizing;
- touch targets at least 44px where possible.

Required:

- WCAG 2.2 AA contrast and interaction behavior;
- one H1, logical heading order, landmarks, skip link, descriptive links, meaningful alt text, and decorative-image handling;
- visible focus not dependent on color alone;
- no horizontal overflow at 320px;
- no clipped text, hidden focus, inaccessible disclosures, duplicate IDs, or invalid ARIA;
- forms only if approved, with labels, instructions, validation summary, inline errors, autocomplete, consent, and generic server errors;
- zero Axe critical or serious findings.

Reduced-motion mode is mandatory. It must remove parallax-like displacement, stagger, spring overshoot, hover lift, and non-essential transforms; present final states immediately; preserve expand/collapse meaning; and keep every CTA and content block fully usable.

## 11. CTA, forms, analytics, privacy, and legal gates

The existing diagnostic Typeform and estimate logic are not automatically approved CTA destinations.

For Preview:

- Default to an access-protected Vercel Preview because baseline positioning and legal copy are not yet approved. Verify protection with an unauthenticated request, not dashboard state alone.
- If access protection is unavailable without new spend, keep the site local until every externally reachable sentence, image, icon, metadata field, social image, structured-data field, and legal notice is approved for public Preview.
- Use an approved contact destination if one exists.
- If no destination is approved, use a truthful non-collecting CTA such as viewing the review requirements or requesting an approved contact decision. Do not invent an email address or enable a dead form.
- Render privacy/terms routes with approved copy. If unavailable, show a clear protected-Preview-only no-collection notice and block any public Preview and Production.
- Do not load analytics, session replay, ad pixels, cookies, CRM scripts, chat widgets, or third-party forms.

For Production:

- Approved legal entity, contact, privacy notice, terms, data-intake explanation, CTA destination, fee wording, product-state wording, and claims are mandatory.
- If a form is approved, use server-side validation, rate limiting, bot controls, origin checks, consent, minimal collection, retention rules, generic error responses, and no PII logging.
- Analytics stays disabled until privacy approval. If approved, document every collected field and prohibit PII/custom-event payloads.

Missing approvals are not implementation failures. They are explicit external blockers with the terminal states and score caps in Sections 17 and 20.

## 12. SEO and metadata contract

Implement and verify:

- unique title and description;
- canonical production URL only when approved;
- one H1 and coherent content hierarchy;
- `robots.ts`, `sitemap.ts`, web manifest, favicons, SVG/icon, and Apple touch icon;
- 1200x630 Open Graph image and Twitter image, visually inspected at actual size;
- theme colors consistent with the design system;
- typed metadata and metadata-file conventions;
- structured data only for registry entries with `claimType: verified-fact`, `evidenceStatus: verified`, and `publicationStatus: approved` for structured data;
- descriptive social copy without unsupported claims;
- correct preview `noindex` behavior and production indexing behavior;
- broken-link, missing-image, duplicate-title, metadata-length, and crawler checks.

Do not invent founding date, address, legal entity, founder count, review rating, offer, pricing, social links, or organization fields for structured data.

## 13. Performance and security budgets

Performance targets on cold-cache Vercel Preview, median of three mobile runs:

- LCP `<2.5s`;
- Total Blocking Time `<200ms` in Lighthouse lab runs;
- scripted interaction latency p95 `<200ms` for the primary CTA, disclosures, navigation, and container interactions using Playwright plus Event Timing/trace evidence;
- field INP `<200ms` becomes a post-launch gate only when an approved, sufficient CrUX or privacy-approved RUM population exists; never infer field INP from navigation Lighthouse;
- CLS `<0.1`;
- Lighthouse Performance `>=90`;
- Lighthouse Accessibility, Best Practices, and SEO `>=95`;
- initial JavaScript `<=180KB` compressed transfer;
- initial mobile transfer `<=1.2MB`;
- initial desktop transfer `<=2MB`;
- no unnecessary client-side hydration;
- images sized, compressed, and responsive;
- motion components do not delay LCP, shift layout, or run work while off-screen;
- no third-party runtime request unless explicitly approved.

Pin Lighthouse, Playwright, browser, and audit-tool versions in `website/`. Store the Lighthouse config, Chrome version, mobile preset, throttling method, run timestamp, raw JSON, and HTML reports under `website/tests/artifacts/`. Define initial JavaScript as the cold-load compressed network transfer of production JS chunks required by `/`, excluding source maps and test/dev tooling. Define page transfer as the sum of cold-load encoded response bytes by request type. Save Playwright traces for the scripted interaction-latency gate.

Security requirements:

- no secrets in repository, bundle, logs, screenshots, or docs;
- no high or critical production dependency vulnerability;
- `pnpm install --frozen-lockfile`, `pnpm audit --prod --audit-level high`, a lockfile-integrity check, and a production license inventory must pass and be recorded;
- verified `nosniff`, Referrer Policy, Permissions Policy, and platform HSTS behavior;
- an enforced, browser-tested CSP appropriate to the final assets is required for 10.0; report-only is an intermediate state and caps the security dimension;
- clickjacking protection through CSP `frame-ancestors` and a compatible `X-Frame-Options` policy, verified from Preview responses;
- external links use safe attributes where needed;
- no user-controlled HTML or unsafe URL handling;
- Preview access/protection decision documented; `noindex` is not privacy.
- every third-party/generated asset passes `ASSET-MANIFEST.md`, rights/license, metadata/EXIF stripping, checksum, and production-approval review.

## 14. Multi-agent execution plan

Use maximum safe parallelism, at most three child agents concurrently. No recursive spawning. No two agents own the same file at the same time. The orchestrator integrates and resolves conflicts.

### Wave 1 - run concurrently

1. **Evidence and publication-safety agent**
   - Claim ledger, source freshness, approved public copy, prohibited wording, legal/privacy blockers.

2. **Market-story and information-architecture agent**
   - Audience questions, page narrative, conversion path, FAQ, evidence sequence, mobile reading order.

3. **Design-research agent**
   - DesignMD shortlist, take/avoid matrix, reference family, interaction inspiration, originality and anti-copy audit.

### Wave 2 - run concurrently

4. **Design-system agent**
   - `PRODUCT.md`, `DESIGN.md`, tokens, typography, grid, art direction, motion grammar, and logistics component system.

5. **Architecture agent**
   - Next.js structure, rendering, content registry, validation scripts, dependency and performance plan.

6. **SEO/legal/security agent**
   - Metadata, crawler rules, structured data, headers, privacy/terms, data-collection boundaries.

### Wave 3 - bounded implementation ownership

7. **Page implementation agent**
   - App routes and section composition.

8. **Motion, logistics-component, and responsive agent**
   - Framer Motion leaves, shipping-container components, local assets, responsive choreography, touch behavior, reduced motion, and performance cleanup.

9. **Content-validation and testing agent**
   - Claims validator, motion-contract validator, unit/content tests, fixtures, type/lint coverage.

### Wave 4 - independent reviewers

10. **Accessibility and browser QA agent**
11. **Performance and security QA agent**
12. **Independent design/content critic**
13. **Deployment verifier**

Review agents may report findings but may not lower thresholds, waive evidence, or rewrite results. The orchestrator repairs all P0/P1 issues and reruns affected checks.

Every agent returns scope, evidence, files, findings, tests, blockers, and next action.

## 15. Engineering and visual verification gates

Run every command from `website/` with pinned project-local tools:

```bash
cd website
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm test:unit --coverage
pnpm test:e2e
pnpm test:visual
pnpm test:motion
pnpm build
pnpm validate:content
pnpm validate:motion
pnpm validate:links
pnpm audit --prod --audit-level high
pnpm licenses list --prod --json
pnpm exec impeccable detect src/
```

`pnpm test` must be a real aggregate test command and may not succeed with zero discovered tests; the named suites remain required for separate evidence.

Use a pinned unit runner with V8/Istanbul-compatible coverage. For `src/content/`, validators, calculation/config logic, and shared utilities require at least 90% statements/lines/functions and 85% branches. Coverage exclusions require file-specific justification and independent reviewer approval; generated metadata images and pure type declarations may be excluded. A passing script that discovers zero tests is a failure.

`validate:motion` performs dependency, import, AST/source, token, and prohibited-pattern checks only. `test:motion` performs instrumented Playwright checks for hydration visibility, reduced motion, enter/exit, hover/touch parity, unmount cleanup, listener/observer leaks, off-screen work, long tasks, layout shift, and interaction latency. Do not claim browser-runtime guarantees from a static script.

Also run:

- Playwright in Chromium, Firefox, and WebKit;
- visual snapshots at 320, 375, 768, 1024, 1440, and 1920;
- both supported color-scheme states if the chosen strategy supports both;
- keyboard-only navigation;
- Axe accessibility checks;
- no-JavaScript rendering checks;
- 200% zoom and long-content stress tests;
- broken-route, 404, external-link, form-disabled, missing-image, and network-failure checks;
- cold-cache Lighthouse three times on Vercel Preview;
- dependency audit and client-bundle inspection;
- content registry to rendered-page traceability;
- preview headers, `noindex`, metadata, OG, favicon, sitemap, robots, and structured-data verification.

Canonical visual snapshots use pinned Chromium with `maxDiffPixelRatio <= 0.005`; Firefox and WebKit require functional/layout assertions and reviewed screenshots. Store reference and diff images by viewport/theme. Any baseline update requires a written reason and approval by a reviewer who did not implement the change. Required checks may be `N/A` only when the feature truly does not exist, with evidence, reason, and independent reviewer approval; truth, content, core routes, responsive, accessibility, motion, performance, and security gates are never `N/A`.

Motion verification must include:

- `motion` with approved `motion/react` imports is the only animation dependency in `package.json` and the lockfile;
- no ScrollWorld/Higgsfield/Xfield code, package, asset, command, or configuration exists;
- no autoplay video, animated image, canvas loop, raw RAF loop, raw scroll listener, or smooth-scroll library exists;
- every motion component has automated reduced-motion coverage;
- enter, exit, hover, focus, press, disclosure, and touch behaviors are tested where implemented;
- all animation durations and springs use shared tokens and remain within the contract;
- no layout shift, trapped interaction, hidden content, or delayed CTA occurs during animation;
- no animation continues off-screen or after unmount;
- runtime has no hydration warning, leaked observer/listener, uncaught error, or long task caused by motion;
- interactions and full content remain understandable when JavaScript is disabled or reduced motion is enabled;
- detectors are not bypassed by generated CSS, inline styles, minification, or test-only flags.

No-JavaScript tests must assert that meaningful SSR text, navigation, CTA context, evidence labels, and process content are visible before hydration. An element rendered at opacity zero or off-screen in server HTML fails even if hydration later reveals it.

Visual review questions:

- Is the first viewport immediately clear about audience, problem, and next step?
- Does the layout feel authored rather than templated?
- Is the hierarchy strong before motion and improved by motion?
- Does every section introduce new information?
- Is proof visually stronger than decoration?
- Do motion and hover mechanics translate into deliberate touch/mobile behavior?
- Are dense regulatory ideas readable and calm?
- Are CTA frequency and prominence appropriate?
- Is any visual likely to be mistaken for customer/product proof?

## 16. Vercel deployment contract

Use Vercel with Root Directory `website/`.

An access-protected Preview deployment is mandatory when authenticated access and protection are available without new spend. Verify both authenticated access and an unauthenticated denial. `noindex` alone is insufficient.

Record in `website/DEPLOYMENT.md`:

- project name and ID;
- Preview URL and deployment ID;
- commit SHA or deterministic source-tree hash;
- Node/pnpm/Next.js versions;
- environment-variable names and scopes, never values;
- build/test timestamp and result links;
- preview indexing/protection state;
- current production target, if any;
- rollback deployment/command;
- unresolved production blockers.

Do not:

- alter DNS;
- attach or replace `sheperd.io`;
- overwrite the current production site;
- create paid resources;
- expose unapproved content or assets on a publicly reachable Preview;
- promote to Production without explicit approval and all publication gates.

If Vercel authentication or project authority is missing, complete and verify the local build, record the exact blocker, and provide the one required user action. Do not fake a deployment result.

## 17. Objective 10/10 rubric

Score from evidence, not confidence:

| Dimension | Points | Full-credit evidence |
|---|---:|---|
| Evidence and publication safety | 20 | Every public claim traced, approved, current, and fail-closed; no unsupported proof. |
| Content and storytelling | 15 | Audience/problem/process/limits/CTA are clear, concise, coherent, and conversion-ready. |
| Visual, interaction, and motion system | 15 | Distinctive documented system; purposeful Framer Motion; original logistics components; no template/slop patterns or copied identity. |
| Architecture and maintainability | 15 | Strict server-first Next.js, minimal dependencies, typed content, clean structure, all engineering checks pass. |
| Responsive UX and accessibility | 15 | All viewports, keyboard, zoom, semantics, contrast, and Axe gates pass. |
| Performance, motion resilience, and security | 10 | Budgets pass; reduced motion and cleanup verified; headers/dependencies/privacy boundary verified. |
| SEO, metadata, deployment, and handoff | 10 | Complete verified metadata, Preview, rollback, documentation, and production gate. |

```text
final_score = earned_points / 10
```

### Visual 15-point subscore

Two independent reviewers score each item `0` or `1` against the approved `DESIGN.md` and canonical screenshots. An item passes only when both reviewers agree and cite the viewport/component evidence. A disagreement goes to a third reviewer whose evidence-backed decision is recorded; average taste scores are not used.

1. Hero identifies audience and problem within the first viewport at 375px and 1440px.
2. Primary CTA is visually singular and readable at all required widths.
3. Typography follows the documented scale, measure, and hierarchy with no accidental style.
4. Grid, spacing, radii, borders, shadows, and color use the documented tokens consistently.
5. The shipping-container language is original, coherent, and not mistaken for operational proof.
6. Each section adds a distinct information job and visual composition.
7. No prohibited AI-slop/template pattern appears.
8. Hover, focus, press, enter, and exit behavior use one motion grammar.
9. Touch interaction is intentionally designed and not a degraded hover copy.
10. Reduced-motion mode remains visually complete.
11. Mobile compositions are deliberately reordered/reframed, not merely scaled.
12. Long copy, zoom, and dense regulatory content preserve rhythm and readability.
13. Static first render is strong before animation begins.
14. Assets, icons, diagrams, and social imagery share one art direction and pass provenance review.
15. Comparison against the chosen DesignMD reference family shows principle-level influence without layout, identity, or asset copying.

Score caps:

- Any red gate caps the score at `5.0`.
- Any unresolved amber gate caps it at `8.0`.
- Missing protected Preview evidence caps it at `9.0`, including unavailable user authentication.
- Any ScrollWorld or Higgsfield/Xfield use, second motion runtime, missing reduced-motion path, motion-caused performance/accessibility failure, unsupported public claim, serious accessibility issue, or skipped required check is a red gate.
- A `10.0` requires all 100 points, all commands passing, all evidence attached, zero unresolved P0/P1 issues, verified Preview, and no waived/skipped checks.

Terminal states:

- `preview_complete`: access-protected Preview verified, all local/Preview checks pass, and every draft is traceable; if any public/legal/brand approval is missing, the state remains amber and score is capped at `8.0`.
- `production_ready`: every claim, legal, privacy, contact, CTA, security, brand, metadata, and domain requirement is approved; all 100 points pass; score is `10.0`; production promotion awaits or records explicit authority.
- `externally_blocked`: credentials, Preview protection, approval, brand/contact, or domain authority prevents the next state after all independent work and three materially different attempts. This is not complete. Record owner, evidence needed, attempts, restart condition, and exact cap.
- A public Preview containing unapproved material is a red failure, not a terminal success.

The independent design/content critic, accessibility reviewer, and performance/security reviewer score separately. The final score uses the lowest supported dimension score after evidence reconciliation, not the orchestrator's preferred score.

## 18. Anti-gaming and stop rules

Forbidden:

- lowering thresholds, muting detectors, deleting tests, marking skipped checks as passed, or widening visual tolerances to force a score;
- checking a blank or alternate route instead of the real homepage;
- hiding overflow rather than fixing layout;
- test-only accessibility content or user-agent-specific behavior;
- fake data, proof, people, customers, results, product screens, testimonials, legal wording, or security claims;
- copying reference sites;
- adding unreviewed motion after automated checks;
- calling Preview a production launch;
- treating Impeccable or Lighthouse as the sole design-quality judge;
- publishing unresolved privacy, fee, contact, product-state, or claim language;
- printing secrets or private customer information.

After three failed attempts against the same external blocker, document it and continue all independent work. Stop only for credentials, paid spend, legal/privacy approval, production brand approval, contact/CTA authority, domain/DNS authority, production promotion, or a destructive conflict with user work. Missing production brand assets do not stop the neutral protected Preview.

Never relax truth, motion discipline, accessibility, security, privacy, performance, or engineering gates to claim completion.

## 19. Exact completion artifacts

At minimum, deliver:

- complete `website/` source tree;
- `website/PRODUCT.md`;
- `website/DESIGN.md`;
- `website/ARCHITECTURE.md`;
- `website/CONTENT-MATRIX.md`;
- `website/ASSET-MANIFEST.md`;
- `website/README.md`;
- `website/QA-REPORT.md`;
- `website/DEPLOYMENT.md`;
- content and motion-contract validators;
- complete test suite and reviewed visual snapshots;
- optimized favicon, icons, manifest, OG, and Twitter assets;
- verified access-protected Vercel Preview when access permits;
- updated link from `SheperD HQ.md` to the website handoff after QA passes.

## 20. Definition of done

The goal is complete only in `production_ready`. `preview_complete` is a valid intermediate delivery; `externally_blocked` is a fail-closed terminal handoff, not completion.

`production_ready` requires:

- the app exists only in `website/` and the Obsidian vault remains intact;
- every public statement passes the evidence and approval registry;
- content tells the full buyer story without invented proof;
- `DESIGN.md` controls a distinctive visual and interaction system with `MOTION_INTENSITY=6` or an adjustment approved by the independent design reviewer before implementation;
- original shipping-container and evidence components have complete semantic, responsive, touch, enter/exit, hover/focus, and reduced-motion behavior;
- final project source, dependency graph, lockfile, scripts, build output, assets, current process inspection, and captured execution log contain no ScrollWorld or Higgsfield/Xfield use; task instructions prohibit agents from invoking them;
- pinned `motion` with approved `motion/react` imports is the only motion runtime and passes token, cleanup, reduced-motion, accessibility, and performance checks;
- lint, typecheck, test, build, content, motion, link, and Impeccable checks pass;
- browser, viewport, keyboard, zoom, accessibility, no-JS, visual, performance, security, and metadata checks pass;
- favicon, metadata, OG, Twitter, manifest, sitemap, robots, canonical policy, and structured-data gates are complete;
- an access-protected Vercel Preview and rollback record are verified;
- all P0/P1 findings are repaired;
- the evidence-backed score is `10.0`, with no waived or skipped check;
- every production publication approval exists; actual production promotion occurs only with explicit authority;
- the final response leads with the result, links artifacts by absolute path, lists checks and scores, distinguishes Preview from Production, and names only genuine external blockers.

If authentication, protection, or approval is unavailable after all independent work, record `externally_blocked`, the actual score/cap, exact unmet criteria, owner, attempts, restart condition, and the finished local/Preview evidence. Do not declare completion because the page looks good or because the blocker is external.

## Related vault context

[[SheperD HQ]] · [[01_Company/Claims and Evidence Register]] · [[01_Company/Product and Business Model]] · [[03_GTM/Website and Content Audit]] · [[04_Operations/Customer Data Intake and Security]]
