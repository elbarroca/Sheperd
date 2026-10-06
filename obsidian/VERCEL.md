# SheperD Website Hosting

The repository has separate `website` and `founder-intelligence` applications.
Older deployment notes described both as Vercel projects. The website source
now includes Netlify build settings, while its existing Vercel configuration
remains in the repository until the owner verifies a hosting cutover.

| Application | Root | Source configuration | Live status |
| --- | --- | --- | --- |
| Website | `website` | Root `netlify.toml`; existing Vercel files retained | Netlify account, domain, and delivery are unverified |
| Founder intelligence | `founder-intelligence` | Separate Vercel setup | Not changed or checked in this migration |

## Website Netlify settings in source

- Base directory: `website`
- Build command: `pnpm build:production`
- Publish directory: `.next`
- Node.js: `24`
- pnpm: `10.33.2`
- `PNPM_FLAGS=--shamefully-hoist`

The production context enables client submission behavior. Other contexts keep
contact submissions disabled. See `website/DEPLOYMENT.md` for form detection,
notification setup, and live verification steps.

## Required owner verification

1. Connect the repository to the company-managed Netlify account.
2. Enable form detection and confirm both form names appear after deployment.
3. Add a notification for each form to `michaelk@sheperd.io`.
4. Confirm the final domain and its apex/`www` behavior.
5. Submit both forms and verify every field, inbox delivery, and visitor Reply-to.

Source configuration and mocked local tests do not prove account ownership,
domain routing, Netlify receipt, or email delivery. This update does not approve
indexing, analytics, or publication of unsupported claims.
