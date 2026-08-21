# Vercel Deployment

## Project separation

Use the existing `sheperd-founder-intelligence` Vercel project. Set its Root
Directory to `founder-intelligence`. Do not attach the public `website` project
to this directory.

## Required settings

- Framework preset: Next.js.
- Install command: `pnpm install --frozen-lockfile`.
- Build command: `pnpm build`.
- Node.js: 24.x.
- Production branch: `main`.
- Deployment Protection: keep enabled unless anonymous read-only sharing is explicitly required.
- Keep the dashboard read-only and do not introduce customer or case data.
- Do not add customer-data, CRM, analytics, email, or publishing environment variables.

The repository-level two-project setup is documented in `../VERCEL.md`. The
dashboard fetches the FastAPI API server-side. Configure `RESEARCH_API_BASE_URL`
with a public HTTPS API URL in Vercel. A local `127.0.0.1` API is not reachable
from a Vercel deployment.

The read-only API is deployed separately as `sheperd-research-api` from the
`research-agents` directory with the FastAPI preset. Its Vercel environment
contains only the pooled `DATABASE_URL` and `NEON_BRANCH_ID`; migration URLs,
provider keys, and Neon management tokens stay out of the public API. The
dashboard production URL is `https://sheperd-founder-intelligence.vercel.app`.

## Founder sharing gate

1. Run all verification commands from `README.md`.
2. Confirm `RESEARCH_API_BASE_URL` points to the read-only API and contains no credentials.
3. Deploy a preview from the feature branch and verify the routes and API state.
4. Promote to Production only after the preview, backend, and source/report secret scans pass.
5. Verify browser console, routes, responsive layout, and noindex headers.

Deployment does not authorize external outreach, publishing, customer-data intake, or AI execution.
