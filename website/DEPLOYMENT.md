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

## Pilot intake remains disabled

Keep `PILOT_DELIVERY_ENABLED` and `NEXT_PUBLIC_PILOT_DELIVERY_ENABLED` false or
unset in every environment. This release adds a native dialog and a direct
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
