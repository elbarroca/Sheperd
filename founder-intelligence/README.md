# SheperD Founder Intelligence

Private, Vercel-ready briefing dashboard for Michael to share with Avi and the founders. It condenses the admitted SheperD research, Ricardo's interpretation, Michael's workflow implications, and the prioritized improvement system without mixing those layers.

Operating state: **research-only / external activation blocked**.

## Repository boundary

| Folder | Job |
|---|---|
| `../context/` | Curated founder brief, Ricardo notes, and knowledge contract |
| `../website/` | Public marketing website; separate project and deployment |
| `../founder-intelligence/` | This private dashboard |
| Root numbered folders | Canonical research vault |

The dashboard is a generated view. Canonical truth remains in the root Markdown and CSV artifacts.

## Start locally

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`.

## What it includes

- Founder brief with current posture, observed facts, next decision, and a gated operating flow.
- Five-question research synthesis showing what was studied, what was found, and the separate founder and Michael consequences.
- Screenshot-informed control-room UI with a compact task bar, responsive active navigation, and a dark-to-light analytical rhythm.
- Complete 88-file evidence library with folder/layer filtering, lazy section retrieval, full source paths, and explicit empty states.
- Data-backed readiness, corpus-shape, and evidence-state charts with exact-data fallbacks.
- Evidence mix with direct counts and clearly labeled planning heuristics.
- Six decision clusters covering all twelve activation blockers.
- Michael's stakeholder ownership map, 45-workflow reconciliation, five-step weekly loop, admitted cadence, responsibility boundary, and sixteen-week operating path.
- Ricardo's source-to-interpretation-to-consequence analysis.
- A dependency-first experiment queue whose weights cannot unlock external work.
- Local TF-IDF retrieval with explicit loading, empty, malformed-response, network-error, and source inspection states.

## Rebuild the knowledge index

```bash
pnpm index:build
```

This scans the canonical repository folders and writes committed deployment artifacts to `src/generated/`. It makes no network or embedding-provider call. On a Vercel build where parent folders are unavailable, the script validates and reuses the committed generated artifacts.

## Verification

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm validate:data
pnpm build
```

## Security boundary

- D0/D1 research only.
- No customer identities, contact lists, invoices, contracts, credentials, or D3 case data.
- No database, CRM, email, analytics, publishing, or AI connector.
- Read-only search; no Server Actions or data mutations.
- `noindex` metadata and response headers.
- Vercel Deployment Protection is required before founder sharing.

See [PRODUCT.md](./PRODUCT.md), [DESIGN.md](./DESIGN.md), [COMPREHENSION_AUDIT.md](./COMPREHENSION_AUDIT.md), [DEPLOYMENT.md](./DEPLOYMENT.md), [DATA_CONTRACT.md](./DATA_CONTRACT.md), and [QA_REPORT.md](./QA_REPORT.md).
