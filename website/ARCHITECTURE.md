# SheperD Website Architecture

Status: Verified local Preview architecture
Date: 2026-07-15
Production publication: Blocked

## System boundary

This project is a static, server-first Next.js marketing Preview. It explains a review structure without claiming that SheperD performs a service, accepting records, collecting leads, or reaching case conclusions.

```text
typed content registry
        |
        v
server-rendered App Router pages ----> static metadata routes
        |
        +----> isolated Motion client leaves
        |
        +----> local, rights-recorded Preview image
```

There is no database, API route, server action, form, upload, authentication layer, analytics runtime, CMS, CRM, cookie, or external client request.

## Runtime modes

`SITE_PUBLICATION_TARGET` is the controlling environment variable.

| Value | Result |
|---|---|
| unset, `preview`, or any unknown value | Builds the noindex, no-collection Preview |
| `production` | Runs the production validator and fails while any required approval is unresolved |

`VERCEL_ENV` is a fallback only when the explicit site target is absent. `NODE_ENV` never decides publication state.

Preview and Production are separate publication contracts. A successful optimized Preview build is not production approval.

## Rendering model

- App Router routes are statically generated.
- Page composition and all core copy are Server Components.
- Client Components exist only under `src/components/motion/`.
- Client leaves use `motion/react-mini` for baseline WAAPI choreography, `motion/react` for reduced-motion and in-view state, and one interaction-loaded `AnimatePresence` panel.
- The hero H1, action, requirements, route, sources, FAQ, limits, and legal notices exist in server HTML.
- Native `details`, lists, links, and a `<noscript>` checklist preserve the reading path without JavaScript.
- CSS performs layout and responsive recomposition; JavaScript does not measure the viewport.

## Content and publication controls

| Module | Responsibility |
|---|---|
| `src/content/site.ts` | Neutral navigation, prompts, and tested Preview behavior |
| `src/content/legal.ts` | Explicitly non-production Preview notices |
| `src/content/sources.ts` | Current official source metadata and direct HTTPS links |
| `src/content/claims.ts` | Candidate exact claims plus sources, dates, expiry, channels, and approvals |
| `src/content/publication.ts` | Target resolution and fail-closed publication predicate |
| `src/content/blockers.ts` | Exact unresolved production authority registry |
| `scripts/validate-content.ts` | Preview leakage/prohibited-copy scan and Production hard gate |

A factual candidate publishes only when its evidence state is allowed, sources are present, the exact channel is approved, a named approver and approval date exist, and the record is unexpired. No candidate currently meets that predicate. The rendered Preview therefore uses neutral questions and official link metadata only.

## Motion architecture

Motion intensity is `6`, implemented as a small explanatory layer:

- `ContainerAssembly`: one coordinated hero assembly.
- `SectionReveal`: once-only section hierarchy cue.
- `RelationLine`: once-only relationship reveal.
- `EvidenceDisclosure`: selected checklist panel replacement with enter and exit.
- `SealLink`: press feedback.

All values come from `src/components/motion/tokens.ts`. Baseline choreography uses Motion's mini WAAPI layer; the heavier React motion component and genuine `AnimatePresence` load only after disclosure interaction. Reduced motion removes displacement and presents final states immediately. CSS contains no keyframes. There is no raw animation frame loop, scroll listener, canvas loop, smooth-scroll runtime, autoplay media, ScrollWorld, Higgsfield, or Xfield code.

## Styling and asset architecture

The global stylesheet is the smallest viable styling layer. It implements the normative tokens and component contracts in `DESIGN.md`; no component framework or CSS runtime is installed.

The selected hero image is local and illustrative. Responsive AVIF files plus a JPEG fallback render from tablet widths upward; mobile keeps the semantic container modules and omits the nonessential image request. The asset is never a product screenshot, customer document, carrier relationship, or operational event. Its exact generation prompt, hashes, dimensions, and restrictions are in `MEDIA-PROVENANCE.md`.

## Metadata, crawler, and security behavior

- Preview emits `noindex`, `nofollow`, `noarchive` in metadata and `X-Robots-Tag`.
- `robots.txt` disallows all crawlers and the Preview sitemap contains no URLs.
- Canonical URL, `og:url`, JSON-LD, and organization facts are absent.
- OG and Twitter routes generate 1200 by 630 artwork from neutral project text and geometry.
- SVG favicon and generated Apple icon are Preview artifacts, not approved brand marks.
- Security headers include `nosniff`, strict referrer policy, disabled unused browser features, frame denial, DNS prefetch off, and an enforced CSP.
- `upgrade-insecure-requests` is added only on real Vercel HTTPS builds so local browser verification does not rewrite localhost resources.
- HSTS is not asserted by application code without domain authority; the deployed platform response must be inspected separately.

## Dependency policy

Runtime dependencies are limited to Next.js, React, React DOM, and Motion. Development dependencies cover strict TypeScript, ESLint, Vitest, Playwright, and Axe. Versions are pinned in `package.json` and one pnpm lockfile.

No secret is required by the application. Environment documentation records variable names and scopes only.

## Verification boundaries

Local verification can prove build integrity, browser behavior, accessibility automation, visual baselines, local transfer size, and header generation. It cannot prove cold-cache Vercel metrics, Preview protection, platform HSTS, deployment identity, rollback, or production authority without authenticated Vercel access.

The exact evidence and limits are recorded in `QA-REPORT.md` and `DEPLOYMENT.md`.
