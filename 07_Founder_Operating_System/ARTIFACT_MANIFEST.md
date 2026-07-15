---
title: Founder Operating System Artifact Manifest
type: manifest
status: active
owner: Michael
updated: 2026-07-15
evidence_status: internal-observation
confidentiality: internal
tags:
  - sheperd/founder
  - sheperd/manifest
---

# Founder Operating System Artifact Manifest

## Control and decisions

- [[../03_GTM/SheperD GTM Validation and Optimization - Control Note]]
- [[../04_Operations/Risk, Assumption and Decision Register]]
- [[../06_Research/Research Gaps and Interview Guide]]

## Market and GTM

- [[../02_Domain/Market and Competitive Landscape]]
- [[../03_GTM/ICP and Stakeholder Personas]]
- [[../03_GTM/Sales and Objection Playbook]]
- [[../03_GTM/Partner Strategy]]
- [[../03_GTM/Content and Distribution System]]
- [[../90_Templates/GTM Operator Kit]]

## Data and controls

- `data/blockers.csv`
- `data/experiments.csv`
- `data/measurements.csv`
- `data/content_backlog.csv`
- `data/artifact_manifest.csv`
- `../06_Research/data/source-ledger.csv`
- `../06_Research/data/workflows.csv`
- `../06_Research/data/ai-opportunities.csv`
- `../06_Research/data/time-savings.csv`

## Runtime and verification

- `app.py` — local entrypoint.
- `src/sheperd_os.py` — catalog, read-only query, validation, and ranking.
- `src/server.py` — loopback-only API/static server.
- `web/` — offline dashboard.
- `tests/` — unit and HTTP checks.
- `scripts/validate_workspace.py` — YAML, wikilink, CSV, claim, draft-label, secret-pattern, and runtime checks.
- `scripts/adversarial_review.py` — fail-closed P0/P1 activation, data, query, and network-boundary checks.
- [[QA_REPORT]] — reproducible validation and visual-review record.

No file in this manifest authorizes outreach, publishing, customer-data intake, regulatory judgment, pricing, filing, or external execution.
