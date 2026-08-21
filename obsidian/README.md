# SheperD

SheperD research, operating system, and publication-gated website.

## Start here

- [SheperD HQ](./SheperD%20HQ.md): current company state, blockers, and canonical entry points.
- [Research control note](./06_Research/SheperD%20Deep%20Research%20-%20Control%20Note.md): evidence and research frontier.
- [GTM control note](./03_GTM/SheperD%20GTM%20Validation%20and%20Optimization%20-%20Control%20Note.md): scores, gates, experiments, and next decision.
- [Context control layer](./context/README.md): curated founder brief, Ricardo interpretation, and knowledge contract.
- [Founder intelligence dashboard](../founder-intelligence/README.md): public read-only Next.js briefing, visualizations, vector search, and priority lab.
- [Research agents](../research-agents/README.md): local Neon-backed Tavily/OpenRouter maritime research service and reviewed exports.
- [Local founder operating system](./07_Founder_Operating_System/README.md): bounded SQLite query and transparent planning workspace.
- [Website](../website/README.md): local setup, verification, and publication boundaries.
- [Vercel deployment](./VERCEL.md): two-project public Production setup.

## Founder intelligence dashboard

```bash
cd ../founder-intelligence
pnpm install --frozen-lockfile
pnpm dev
```

Open `http://localhost:3000`. The public dashboard is a generated, read-only view of the admitted D0/D1 research and contains no customer data.

## Local analytical workspace

```bash
python3 07_Founder_Operating_System/app.py
```

Open `http://127.0.0.1:8765`. This local workspace supports bounded read-only SQL over admitted D0/D1 planning data. It does not authorize outreach, publication, customer-data intake, or external execution.

## Website verification

```bash
cd ../website
pnpm install --frozen-lockfile
pnpm check
```

The website is publicly deployed with noindex headers and form delivery disabled.
The unresolved company, legal, claims, contact, brand, and canonical risks remain documented.
