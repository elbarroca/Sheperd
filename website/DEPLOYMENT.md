# SheperD website deployment

## Existing project

- Repository: https://github.com/elbarroca/Sheperd
- Vercel project: `sheperd-website` (`prj_3mhF2TaczFJn4qudpafnzSde0Oso`)
- Team: `elbarrocas-projects`
- Root directory: `website`
- Production branch: `main`
- Canonical origin: https://sheperd-website.vercel.app
- Framework: Next.js, Node.js 24.x, pnpm 10.33.2
- Install: `pnpm install --frozen-lockfile`
- Build: `pnpm build`

The approved September 2026 redesign releases to this existing project. The
founder dashboard and research API are separate projects. Do not deploy this
website through the repository root's research deployment configuration.

Keep the project's Preview Vercel Toolbar setting off. The toolbar injects an
external script that conflicts with this site's self-only script policy. A
setting change needs a fresh build to remove previously bundled toolbar code.

## Build and search policy

`lib/seo.ts` owns metadata, robots, and sitemap policy. Vercel's build-time
`VERCEL_ENV=production` enables indexing for the homepage. Preview, development,
and ordinary local builds stay excluded. The configuration serializes the same
policy for server and client rendering, avoiding hydration changes to metadata.

The pilot, privacy, and terms pages retain `noindex`; the production sitemap
contains only the homepage. Production robots allows crawling so search engines
can read these directives. Preview robots disallows crawling. Every canonical
and social URL uses the production origin.

`pnpm build:production` explicitly emulates production indexing locally; it does
not deploy. Do not use it for Vercel preview builds.

## Verification

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm check
corepack pnpm build
corepack pnpm test:e2e --workers=3
```

Playwright starts an optimized server on port 3100 and covers Chromium, Firefox,
and WebKit. Chromium owns the manually reviewed visual baselines. Review the
render before updating them with `pnpm test:visual --update-snapshots`.

Validate the feature-branch deployment first, then merge the reviewed website
change to `main`. Verify the production commit and alias, rendering, HTTP and
HTML indexing directives, social image, robots, sitemap, and disabled intake.
Report Lighthouse lab measurements separately from field Core Web Vitals.

## Motion delivery

The full-width hero uses an optimized silent video loop over a responsive
Next.js image. Playback starts after the image loads and stops when the section
is offscreen, the tab is hidden, or reduced motion is requested. The static
artwork also covers unsupported or blocked autoplay. No visible player or pause
control is rendered, following the approved motion revision.

The GIF export is retained in `public/media/recovery-terminal-loop.gif`; normal
page loading uses WebM or the H.264 fallback. Asset provenance and the generation
prompt are in `docs/ASSET-PROVENANCE.md`; `scripts/render-hero-loop.sh` rebuilds
the derivatives with FFmpeg. Scroll reveals use the installed Motion mini API.
Section-specific groups bind to scroll progress, including reverse scrolling:
editorial lines, process assembly, side-entry evidence, terminal light, converging
pilot columns, quiet trust content, and the closing headline. A fixed viewport
distance at each boundary keeps tall sections still and opaque while reading.
Keyboard focus restores static content; pointer focus freezes control positions.
Reduced motion and hidden tabs stop work; offscreen sections release controls.
Server-rendered content remains readable without JavaScript.

Lenis 1.3.26 loads on the client for gentle wheel and anchor scrolling. Touch
scrolling stays native. Reduced motion and an open pilot dialog disable Lenis;
hidden tabs stop its animation frame loop. Skip navigation remains immediate.

## Pilot intake remains disabled

Keep `PILOT_DELIVERY_ENABLED` and `NEXT_PUBLIC_PILOT_DELIVERY_ENABLED` false or
unset in every environment. The build also forces the public flag off, so a
public environment flag alone cannot enable collection. Future activation needs
a separately reviewed change to that build guard. This release adds a native dialog and a direct
`/pilot` page. Both explain availability before the disabled fields. No request
is transmitted or persisted through the disabled interface, and no receipt is
claimed. Forms use POST even without JavaScript; disabled fields are never
serialized into a URL.

The existing `/api/pilot` payload and delivery contract are unchanged. An empty
request with the expected form header must return 503 while delivery is disabled.
A request without the form header returns 403. Production checks use no personal
data and do not test live delivery.

Future activation requires separate approval of the response owner, sending and
receiving addresses, provider configuration, privacy and retention terms, and
abuse controls. It is outside this release. Existing legacy audit delivery flags
also remain disabled. Do not add advertising trackers, change domains, or enable
email as part of the redesign.

### Resend activation handoff

The installed Resend SDK already receives a plain-text message, an approved
sender and recipient, the visitor's address as `replyTo`, and a submission-based
idempotency key. `tests/unit/pilot-api.test.ts` exercises this route with a mocked
provider, including disabled configuration, invalid input, and delivery failures.
These checks do not prove inbox delivery.

Before the separate activation release:

1. Confirm the response owner and exact sender/recipient. The public contact
   address is not automatically the intake recipient.
2. Verify the sending domain in Resend, including SPF and DKIM. Configure a
   sending-only API key in Vercel's server environment. Keep it out of public
   variables and Git. See [Resend domain setup](https://resend.com/docs/dashboard/domains/introduction).
3. Agree privacy, retention, and response handling; add rate limiting or
   equivalent abuse controls. The existing custom header and honeypot alone are
   not sufficient protection for a public sending endpoint.
4. Release the reviewed public build-guard change and matching server flag to a
   controlled preview. Update unavailable messaging at the same time. Run one
   separately authorized delivery to the approved recipient and verify the
   provider result and actual mailbox receipt.
5. Enable production only after those checks. Monitor provider failures without
   logging form contents. To stop delivery, set `PILOT_DELIVERY_ENABLED=false`;
   restore the disabled public build and redeploy so visitors cannot enter data.

The dialog keeps its native modal state until its exit animation finishes.
Reduced motion and route changes bypass the exit delay. FAQ disclosures use
native exclusive `details` groups, so keyboard and no-JavaScript access work
without a separate accordion library.
