# SheperD Website Deployment

Status: Netlify migration prepared in source; account, domain, and live delivery are unverified.
Checked: 2026-10-06

## Netlify build settings

The repository-root `netlify.toml` sets the website base directory to `website`.
The source repository sets these build values:

- Build command: `pnpm build:production`
- Publish directory: `.next` (relative to the `website` base directory)
- Node.js: `24`
- pnpm: `10.33.2`, from `website/package.json`
- `PNPM_FLAGS`: `--shamefully-hoist`
- Contact submissions: disabled by default; enabled for the production build

The package manifest declares Node `24.x` and pnpm `10.33.2`. Its `build`
script selects Preview, so Netlify must use `build:production`.

## Netlify Forms setup

`website/public/__forms.html` defines `contact-home` and `contact-page` for
deploy-time detection. The shared forms post URL-encoded fields to
`/__forms.html`; each includes Netlify's `bot-field` honeypot. The visitor field
is named `email` so Netlify can use it as Reply-to.

After connecting the repository to the company-managed Netlify account:

1. Enable form detection and confirm Netlify spam filtering is active, then deploy.
2. Confirm Netlify lists `contact-home` and `contact-page`.
3. Add one email notification for each form to `michaelk@sheperd.io` under
   Forms → Submission notifications.
4. Confirm the final domain and its apex/`www` behavior with the account owner.
5. Submit one test from each form. Confirm both Netlify records and inbox emails
   contain all fields, and confirm Reply-to addresses the visitor's `email`.

Local Playwright tests mock `/__forms.html`. They verify client encoding and
success/error states, but they do not confirm Netlify receipt or email delivery.

## Existing Vercel configuration

The repository still contains its Vercel configuration. This source change does
not remove that configuration, connect a Netlify account, change DNS, or verify
which provider currently serves the final domain. Keep it until the account
owner completes and verifies the cutover. The founder-intelligence project has
its own deployment setup.

## Separate audit intake

The existing audit form and Resend API use separate flags and server values.
Their local no-delivery behavior remains unchanged. Keep
`FORM_DELIVERY_ENABLED` and `NEXT_PUBLIC_AUDIT_DELIVERY_ENABLED` false until the
audit intake approvals, server values, and bounded delivery test are complete.
See `.env.example` for the server-only variable names. Never expose the Resend
API key with a `NEXT_PUBLIC_` prefix.

## Unresolved publication risks

1. Confirm the final domain, apex/`www` behavior, and deployment owner.
2. Approve the privacy notice, retention period, and data-processing terms.
3. Confirm contact notification setup and test live inbox delivery.
4. Resolve remaining legal, claims, intake, and ownership items in
   `docs/FACTS-AND-CONSTRAINTS.md`.

The local source configuration does not approve publication, indexing,
analytics, domain attachment, or live form delivery.
