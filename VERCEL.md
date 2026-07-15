# SheperD Vercel Projects

Connect the private `elbarroca/Sheperd` GitHub repository to Vercel twice. Each
application has its own lockfile and must be a separate Vercel project.

## Public website Preview

| Setting | Value |
| --- | --- |
| Suggested project name | `sheperd-website` |
| Root Directory | `website` |
| Framework | Next.js |
| Install command | `pnpm install --frozen-lockfile` |
| Build command | `pnpm build` |
| Node.js | 24.x |
| Production branch | `production` (reserved; do not create yet) |
| Deployment Protection | Standard Protection with Vercel Authentication |

The current build is an evidence-safe Preview with noindex/no-follow headers.
Do not change the build command to `pnpm build:production`: that command is an
intentional negative gate until the business, legal, claim, privacy, contact,
and publication approvals in `website/docs/FACTS-AND-CONSTRAINTS.md` resolve.

Resend delivery is disabled by default. Keep all form flags false and omit the
server-only Resend values until the approval checklist in
`website/DEPLOYMENT.md` is complete.

## Founder intelligence dashboard

| Setting | Value |
| --- | --- |
| Suggested project name | `sheperd-founder-intelligence` |
| Root Directory | `founder-intelligence` |
| Framework | Next.js |
| Install command | `pnpm install --frozen-lockfile` |
| Build command | `pnpm build` |
| Node.js | 24.x |
| Production branch | `production` (reserved; do not create yet) |
| Deployment Protection | Standard Protection with Vercel Authentication |

This application contains private founder research and has no application-level
authentication. Enable Vercel Deployment Protection before sharing any URL and
keep Production private until an approved authentication and authorization
layer exists. `noindex` is not access control.

## Connection sequence

1. Log in to Vercel and import the same private Git repository twice.
2. Apply the Root Directory, reserved Production branch, and commands above to
   each project before the first deployment.
3. Enable Standard Protection with Vercel Authentication on both projects.
4. Push or redeploy `main`, then confirm each result is classified as Preview.
5. Verify the website remains noindex and the founder dashboard cannot be
   opened in a signed-out browser.
6. Keep domains, indexing, form delivery, analytics, and public Production
   publication disabled until their separate approval gates resolve.

Once both projects are connected, a push to `main` can trigger two independent,
protected Preview builds. Both applications also reject `VERCEL_ENV=production`
at build time, so an accidental Production deployment fails closed.
