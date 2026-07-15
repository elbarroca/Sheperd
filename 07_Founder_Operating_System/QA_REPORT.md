---
title: Founder Operating System QA Report
type: qa-report
status: accepted-internal
owner: Michael
updated: 2026-07-15
evidence_status: internal-observation
confidentiality: internal
tags:
  - sheperd/founder
  - sheperd/qa
---

# Founder Operating System QA Report

> [!abstract] Acceptance result
> The local founder query, visualization, and planning workspace passed its scoped engineering, data, browser, responsive, and fail-closed review gates on 2026-07-15. The review found **zero unresolved P0/P1 defects**. This accepts an internal decision-support artifact only; SheperD remains **research-only / external activation blocked**.

## Reproducible engineering gates

Run from `07_Founder_Operating_System/`:

| Command | Accepted result |
|---|---|
| `uv run ruff check .` | Python lint passes |
| `uv run mypy src app.py tests scripts` | Strict typecheck passes |
| `uv run python -m unittest discover -s tests -v` | 8/8 unit and HTTP tests pass |
| `uv run python scripts/validate_workspace.py` | Scoped YAML, wikilink, claim, label, secret, CSV, and runtime contracts pass |
| `uv run python scripts/adversarial_review.py` | Fail-closed P0/P1 review passes with P0=0 and P1=0 |
| `uv run python scripts/reconcile_research_report.py --check` | Embedded research-report source data equals the current source ledger |
| `python3 -m compileall -q app.py src tests scripts` | Python compilation passes |

## Browser verification

The local server was run on `127.0.0.1:8765` and inspected in the in-app browser.

| Gate | Result |
|---|---|
| Initial render | Scores, source states, experiment states, explorer, query, ranker, rules, and activation warning render |
| Data explorer | Dataset control switches to `experiments`; 8 rows are reported |
| Query | Default bounded query returns 12 blocker rows |
| Ranker | Re-rank interaction completes; blocked items remain visibly blocked |
| Security/browser health | 0 console warnings/errors; 0 error overlays; 0 external resources |
| Desktop layout | 1280×720 has no horizontal document overflow |
| Mobile layout | 390×844 has no horizontal document overflow; priority score/title gap is 12 px |
| Read-only boundary | Mutation request returns HTTP 400; query layer unit and adversarial tests reject mutations, comments, attachments, and multiple statements |

## Adversarial P0/P1 contract

The separate rule pass verifies:

- GAP-001–012 all exist and remain `blocked`.
- Only EXP-001–003 are eligible for internal preparation or synthetic-only work.
- EXP-004–008 remain external, publication, or security blocked.
- Content is only `internal-outline` or `blocked`.
- The 42-row evidence ledger retains its exact controlled-state distribution.
- Every external draft family uses `DRAFT - HUMAN REVIEW REQUIRED`.
- No remote asset, file upload, customer-data store, or external connector exists.
- Read-only SQL and transparent ranking cannot override activation gates.

## Known boundary

The repository already contained unrelated, unstaged website deletions and edits before this package was created. They were not restored, modified for this goal, staged, or included in the scoped commit. Website application checks therefore are not part of this founder-workspace acceptance record.

## Decision

Internal artifact acceptance: **GO**. External activation: **NO-GO** until GAP-001–012 are admitted or explicitly rejected by the named owners.

## Related

[[README]] · [[ARTIFACT_MANIFEST]] · [[../03_GTM/SheperD GTM Validation and Optimization - Control Note]] · [[../06_Research/QA and Acceptance Report]]
