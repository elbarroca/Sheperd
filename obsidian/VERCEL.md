# SheperD Vercel Projects

The private `elbarroca/Sheperd` GitHub repository is connected to two public
Vercel projects. Each application has its own lockfile and project root.

| Project | Root Directory | Framework | Install | Build | Node.js | Production branch | Protection |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `sheperd-website` | `website` | Next.js | `pnpm install --frozen-lockfile` | `pnpm build` | 24.x | `main` | Disabled |
| `sheperd-founder-intelligence` | `founder-intelligence` | Next.js | `pnpm install --frozen-lockfile` | `pnpm build` | 24.x | `main` | Disabled |

All generated Vercel URLs are public. The website keeps noindex headers and
form delivery disabled. The founder dashboard remains read-only, noindex, and
limited to the committed D0/D1 research package; it must not contain customer,
invoice, contract, credential, or case data.

## Release sequence

1. Run lint, typecheck, tests, data validation, and builds locally.
2. Review generated founder data for unintended sensitive material.
3. Push the verified commit to `main`.
4. Wait for both Git-connected Production deployments to report `READY`.
5. Verify anonymous HTTP 200 responses, key routes, headers, and runtime logs.

Public deployment was explicitly authorized on 2026-07-15. It does not approve
indexing, form delivery, analytics, custom domains, or unsupported claims.
