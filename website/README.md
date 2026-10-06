# SheperD Website

The website centers on: "You send the invoices. We handle the recovery." It
includes `/how-it-works`, `/for-importers`, `/about`, and a `/contact` form.
The homepage form appears below its closing call to action. `/pilot` redirects
to that form. No upfront cost and recovery-aligned payment are approved copy. See
`docs/RECOVERY-IMPLEMENTATION.md` for the copy deck and reference mapping.

The Recovery Corridor is the public-facing SheperD website. It explains the
shipping-container demurrage and detention recovery workflow. Contact forms
collect name, email, company, inquiry type, and message for replies from SheperD.

## Local setup

Requires Node.js 24.x and pnpm 10.33.2.

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

Open `http://127.0.0.1:3000`.

## Verification

```sh
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
corepack pnpm build
corepack pnpm test:e2e
```

Contact forms render locally, but the default `NEXT_PUBLIC_CONTACT_DELIVERY_ENABLED=false`
setting prevents JavaScript submissions from being sent. The Playwright web
server enables the flag only for tests that mock the Netlify response. The
separate audit form also remains disabled by default; see `DEPLOYMENT.md`.

## Deployment boundary

The repository now includes a Netlify build configuration for this directory.
The live Netlify account, form notifications, final domain, and inbox delivery
remain unverified. Keep the existing Vercel configuration until the account
owner completes and verifies the hosting cutover. Unresolved legal, claims,
privacy, and ownership risks remain in `docs/FACTS-AND-CONSTRAINTS.md`. See
`DEPLOYMENT.md` and `../obsidian/VERCEL.md` for the source settings and cutover steps.
