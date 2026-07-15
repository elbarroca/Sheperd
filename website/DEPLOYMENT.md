# SheperD Website Deployment

Status: repository-ready Vercel Preview; Production publication remains blocked
Checked: 2026-07-15

## Vercel project

- Repository: `https://github.com/elbarroca/Sheperd`
- Production branch: `production` (reserved; do not create yet)
- Deployment Protection: Standard Protection with Vercel Authentication
- Root Directory: `website`
- Framework: Next.js
- Install command: `pnpm install --frozen-lockfile`
- Build command: `pnpm build`
- Node.js: 24.x

Pushes to `main` intentionally create protected Preview deployments. The normal
build creates the evidence-safe, noindex application. Production builds remain
fail-closed with
`PRODUCTION_PUBLICATION_BLOCKED` until the publication gates are approved.

The repository-level two-project setup is documented in `../VERCEL.md`.

## Local verification

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm check
corepack pnpm build
```

Run `corepack pnpm test:e2e` against the optimized server for browser and visual
verification.

## Resend audit-form setup

The form keeps its local no-transmission Preview behavior by default. The
server route validates every field, uses a honeypot, sends plain-text intake to
the approved SheperD inbox, and applies a per-submission idempotency key. It does
not log form data.

Before enabling delivery:

1. Verify the sending domain in Resend and approve the sender and recipient.
2. Approve the privacy notice, intake retention policy, response owner, and a
   durable rate-limit or abuse-control decision for the deployed environment.
3. Set the server-only `RESEND_API_KEY`, `SHEPERD_AUDIT_FROM_EMAIL`, and
   `SHEPERD_AUDIT_TO_EMAIL` values using `.env.example` as the key contract.
4. Set both `FORM_DELIVERY_ENABLED=true` and
   `NEXT_PUBLIC_AUDIT_DELIVERY_ENABLED=true`, rebuild, and test exactly one
   bounded request before broader traffic.

Do not place the Resend API key in a `NEXT_PUBLIC_` variable or commit a local
environment file. If either the server flag or any required server value is
missing, the API returns a non-delivery response and sends nothing.

## Production blockers

1. Verified legal entity, publishable brand identity, and publication owner.
2. Approved company/product positioning and exact claim evidence with named approvers and dates.
3. Approved privacy notice, terms, intake/data controls, and commercial terms.
4. Approved CTA/contact destination and response owner.
5. Canonical origin, indexing, metadata, analytics decision, deployment target, and explicit deploy/domain/DNS authority.

The complete blocker contract is in `docs/FACTS-AND-CONSTRAINTS.md`. A successful
Vercel build proves technical deployability only; it does not approve public
Production publication, domain attachment, indexing, or data collection.
