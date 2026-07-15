---
title: SheperD Founder Operating System
type: runbook
status: active-internal
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/founder
  - sheperd/data
  - sheperd/gtm
---

# SheperD Founder Operating System

## Answer first

This folder gives founders one local workspace to query, visualize, and prioritize the admitted SheperD research and GTM data. It is a decision-support interface—not a CRM, customer-data store, market-validation result, legal tool, or execution system.

Operating state: **research-only / external activation blocked**.

## Start in one command

From the repository root:

```bash
python3 07_Founder_Operating_System/app.py
```

Open `http://127.0.0.1:8765`. The app binds only to loopback, makes no external requests, and uses Python’s standard library. Stop it with `Ctrl+C`.

## What founders can do

- Inspect current scores and the activation warning.
- Filter every admitted structured table.
- Run bounded read-only SQLite `SELECT`/`WITH` queries.
- Visualize blocker, source, and experiment-state distributions.
- Rank experiments using visible weights for learning value, evidence readiness, lower risk, and lower effort.
- See whether a ranked item is eligible for internal preparation or still blocked.
- Trace each structured record to its canonical Markdown source.

Ranking never overrides a gate. It is not ROI, conversion prediction, causal optimization, product readiness, or permission to execute.

## Data catalog

| Table | Canonical source | What it answers |
|---|---|---|
| `source_ledger` | `06_Research/data/source-ledger.csv` | What evidence exists, at what authority/state/expiry? |
| `workflows` | `06_Research/data/workflows.csv` | What work exists, who owns it, and what blocks it? |
| `ai_opportunities` | `06_Research/data/ai-opportunities.csv` | Which deterministic/assisted/human controls are proposed? |
| `time_savings` | `06_Research/data/time-savings.csv` | What is the low-confidence planning envelope? |
| `blockers` | `data/blockers.csv` | Which P0 gates block which actions and evidence? |
| `experiments` | `data/experiments.csv` | What may be prepared, tested synthetically, or only after approval? |
| `measurements` | `data/measurements.csv` | Which numerator, denominator, timing, sample, and decision are required? |
| `content_backlog` | `data/content_backlog.csv` | Which asset hypotheses depend on which gates? |
| `artifact_manifest` | `data/artifact_manifest.csv` | Where is the canonical decision truth? |

CSV files are loaded into an ephemeral in-memory SQLite database at startup. No database file, query history, or result cache is written.

## Example queries

```sql
SELECT blocker_id, gate, owner, next_action
FROM blockers
WHERE current_state = 'blocked'
ORDER BY blocker_id
```

```sql
SELECT execution_state, COUNT(*) AS experiments
FROM experiments
GROUP BY execution_state
ORDER BY experiments DESC
```

```sql
SELECT source_id, title, evidence_status, confidence, review_expiry
FROM source_ledger
WHERE evidence_status IN ('verified', 'mixed')
ORDER BY source_id
```

```sql
SELECT model_id, scenario, risk_adjusted_hours_pre_cap, sample_size, confidence
FROM time_savings
WHERE scenario = 'base'
ORDER BY CAST(risk_adjusted_hours_pre_cap AS REAL) DESC
```

The interface rejects mutations, comments, multiple statements, filesystem attachment, and more than 500 returned rows.

## Command-line use

```bash
python3 07_Founder_Operating_System/src/sheperd_os.py validate
python3 07_Founder_Operating_System/src/sheperd_os.py tables
python3 07_Founder_Operating_System/src/sheperd_os.py query "SELECT gate, COUNT(*) FROM blockers GROUP BY gate"
python3 07_Founder_Operating_System/src/sheperd_os.py optimize
```

## Founder decision workflow

1. Start with [[../03_GTM/SheperD GTM Validation and Optimization - Control Note|GTM control note]].
2. Query the blocker and artifact tables; open the linked canonical notes.
3. Change ranking weights only to inspect a planning tradeoff.
4. Ignore blocked rankings as execution candidates.
5. Record real decisions in [[../90_Templates/Decision Record|Decision Record]].
6. Update the canonical Markdown/CSV source first; restart the app to reload.
7. Never paste customer, contact, invoice, shipment, contract, credential, or recovery data here.

## Validation

Runtime uses no third-party packages. Engineering checks use the optional dev group:

```bash
cd 07_Founder_Operating_System
uv sync --group dev
uv run ruff check .
uv run mypy src app.py tests scripts
uv run python -m unittest discover -s tests -v
uv run python scripts/validate_workspace.py
```

## Security and privacy boundary

- Loopback binding only; no authentication because it is not network-exposed.
- No external URLs, telemetry, cookies, local storage, file upload, CRM, email, publishing, or AI connector.
- Read-only bounded SQL over D0/D1/internal-proposal CSVs.
- D2 belongs in an approved CRM; D3 belongs in an approved secure case system and remains disabled for AI.
- If network hosting, multi-user access, or customer data is proposed, stop and obtain a separate security/privacy architecture and approval.

## Exact limitations

- Source and vendor claims remain in their recorded evidence states.
- Planning scores are transparent heuristics, not measured performance.
- Modeled hours have sample size 0 and unknown owner/workload caps.
- Public search themes do not establish query volume or demand.
- Synthetic control tests do not establish execution readiness.
- The highest-value next action remains the founder truth-and-gates workshop, not external activation.

## Related

For the founder-shareable briefing, visualizations, Ricardo interpretation, and vector retrieval, use [[../founder-intelligence/README|Founder Intelligence]]. This folder remains the local bounded-SQL workspace.

[[../context/README|Context control layer]] · [[../03_GTM/SheperD GTM Validation and Optimization - Control Note]] · [[../06_Research/SheperD Deep Research - Control Note]] · [[ARTIFACT_MANIFEST]]
