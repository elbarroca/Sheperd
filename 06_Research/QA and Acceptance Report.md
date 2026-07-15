---
title: QA and Acceptance Report
type: research-qa
status: accepted
owner: Michael
updated: 2026-07-15
evidence_status: internal-observation
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/qa
---

# QA and Acceptance Report

> [!abstract] Acceptance result
> The exact 14-artifact research package passed the evidence, vault, CSV, formula, cross-reference, privacy, offline-browser, interaction, accessibility, responsive, print, no-JavaScript, link, lint, typecheck, and test gates on 2026-07-15. Independent adversarial review found no P0, 11 P1, and 4 P2 defects; every P1 and P2 was repaired and the affected gates were rerun. The later GTM extension and founder workspace also passed their scoped engineering, browser, data, and fail-closed review. There are **zero unresolved P0/P1 findings**. This accepts the internal artifacts, not external activation: SheperD remains **research-only / external activation blocked**.

## Acceptance summary

| Gate | Result | Evidence |
|---|---|---|
| Exact artifact contract | Pass | 14/14 files exist; no extra file exists under `06_Research/` |
| Evidence and legal boundaries | Pass | 42 source rows; controlled evidence states; current Part 541, §41301, route, Evergreen, FTC, FMC audit, port-volume, and GTM source boundaries preserved |
| Vault integrity | Pass | YAML parsed; internal wikilinks resolved; dated source notes follow the property contract |
| Workflow coverage | Pass | 45/45 workflows; Week 0, 16/16 weeks, 4/4 gates, 8/8 workstreams; every row classified |
| Step and AI traceability | Pass | Stable workflow-step IDs; 26/26 opportunities resolve to same-class steps; no bounded-agent step is active |
| Capacity math | Pass | 30 rows; formulas recompute at six-decimal precision; low/base/high order holds; counted step IDs are disjoint |
| HTML data integrity | Pass | Embedded source, workflow, opportunity, and capacity rows exactly equal the four CSV datasets |
| Offline/browser behavior | Pass | 54/54 browser checks; zero console errors, page errors, or network requests |
| Accessibility | Pass | Axe 4.12.1: 0 violations, including 0 critical/serious; custom WCAG AA contrast check passed |
| Responsive/print/resilience | Pass | 320/375/768/1024/1440/1920; no overflow; print and no-JavaScript views passed |
| Public-link integrity | Pass | 30/30 direct HTTP(S) ledger targets returned 2xx/3xx; 8/8 local evidence paths resolved |
| Repository engineering checks | Pass | Website lint, typecheck, and 7 tests passed |
| Independent review | Pass | 0 unresolved P0; 0 unresolved P1; 0 unresolved P2 |

Final regression set completed at: `2026-07-15 02:01:38 WEST (+0100)`.

## Reproducible validation record

Commands were run from the vault root unless a working directory is shown.

| Command/check | Result |
|---|---|
| `python3 /tmp/sheperd_validate.py` | Pass: 1,694 checks, 0 failures; 75 YAML notes parsed; internal wikilinks resolved |
| `python3 /tmp/sheperd_link_check.py` | Pass: 30 checked, 30 successful, 0 failed |
| `NODE_PATH=/Users/barroca888/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules /Users/barroca888/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node /tmp/sheperd_browser_check.js` | Pass: 54 checks, 0 failures; Axe 0 violations |
| `pnpm lint` in `website/` | Pass: ESLint exit 0 |
| `pnpm typecheck` in `website/` | Pass: `tsc --noEmit` exit 0 |
| `pnpm test` in `website/` | Pass: 2 files, 7 tests |
| Visual inspection of `/tmp/sheperd-report-1440.png` | Pass: content, tables, charts, filters, roadmap, and gap views rendered without visible clipping or decorative-only output |

The validator checks exact artifacts, YAML, wikilinks, CSV width/schema/IDs/references, controlled step classes, stable step IDs, opportunity-to-step class agreement, formula recomputation, scenario order, disjoint counting keys, totals across CSV/Markdown/HTML, exact embedded data, local evidence paths, zero network APIs, and common secret/PII patterns.

## Data and math reconciliation

| Dataset | Rows | Controlled result |
|---|---:|---|
| `source-ledger.csv` | 42 | 17 verified; 15 company-claim; 6 mixed; 2 unverified; 1 internal-proposal; 1 internal-observation |
| `workflows.csv` | 45 | 25 blocked; 8 needs-owner; 8 mapped; 4 out-of-scope |
| `ai-opportunities.csv` | 26 | 10 deterministic; 9 assisted; 7 human-only; 0 bounded-agent |
| `time-savings.csv` | 30 | 10 models × low/base/high |

| Scenario | Baseline h/month | Gross release h/month | Risk-adjusted pre-cap h/month |
|---|---:|---:|---:|
| Low | 24.75 | 0.45 | 0.19 |
| Base | 80.08 | 34.83 | 22.06 |
| High | 201.58 | 140.16 | 118.15 |

The totals aggregate six-decimal row outputs and round only for presentation. They are low-confidence planning assumptions with sample size 0. Eligible-workload and owner-capacity caps remain unknown; therefore final capacity, money value, payback, revenue, savings, headcount, or readiness claims remain blocked.

## Independent adversarial review and repair ledger

The seventh bounded assignment was independent and did not author the reviewed material.

| Finding | Priority | Repair | Retest |
|---|---:|---|---|
| Control note showed in-progress questions and non-contract manifest entries | P1 | Reduced manifest to the exact 14 artifacts; closed question statuses only after final QA | Artifact and link validator |
| Compound/non-controlled evidence-state labels | P1 | Replaced combined labels with one controlled state per claim/row | Evidence-state scan and data validator |
| Secondary/interview sources overstated as verified | P1 | SRC-025/027/028 changed to `mixed`; claims and limitations narrowed | Ledger counts, HTML, embedded-data equality |
| Workflow responsibility tokens were not reproducible | P1 | Added a complete token-to-canonical-note dictionary | Wikilinks and coverage review |
| Opportunities referenced workflows rather than steps; double counting was not mechanical | P1 | Added stable `WF-XXX-SYY` IDs, bound opportunities to same-class steps, and added disjoint `counted_step_ids` | 1,000+ step/reference checks and formula validator |
| WF-043 implied an unspecified bounded agent | P1 | Reclassified the step as draft-only `ai-assisted`; confirmed zero bounded-agent steps/opportunities | Step-class validator and register review |
| Portfolio totals aggregated prematurely rounded row outputs | P1 | Stored formula outputs at six decimals; aggregated before two-decimal presentation | Formula and cross-artifact totals |
| Impact/effort/risk table rendered `undefined` | P1 | Added explicit Low–medium and Medium–high risk labels | Browser render and literal scan |
| HTML gap/measurement IDs conflicted with canonical registers | P1 | Replaced views with canonical GAP-001–012 and MT-001–014 meanings | Browser and content comparison |
| Bar spans used prohibited ARIA attributes | P1 | Marked decorative bars `aria-hidden`; retained adjacent numeric equivalents | Axe 4.12.1 and semantic audit |
| Claims/conflicts/gaps/interviews/measurements were not jointly filterable | P1 | Added one keyboard-operable evidence/action search with no-result state | Browser interaction and keyboard checks |
| Embedded source data was stale after source repair | P2 | Rebuilt embedded JSON from all four current CSV files | Exact JSON equality check |
| Four dated source notes lacked `updated` | P2 | Added `updated: 2026-07-15`; scanned every source checked that day | YAML/property scan |
| Evergreen summary contained an unsupported delay-cost clause | P2 | Removed the unsupported clause while preserving the fact-specific boundary | Dossier review |
| HQ final links were absent | P2 | Added only after the package passed QA | Wikilink validator |

## GTM extension acceptance — 2026-07-15

The GTM extension added the validation control note, current market/demand scan, buyer and channel refinements, claims, content and operator templates, experiment and measurement registers, AI controls, and the local founder query/visualization/ranking workspace. Its reproducible record is [[07_Founder_Operating_System/QA_REPORT]].

| Gate | Result |
|---|---|
| Python lint | Pass: Ruff |
| Strict typecheck | Pass: mypy over 8 source files |
| Unit and HTTP tests | Pass: 8/8 |
| Scoped vault/data validator | Pass: 470 checks |
| Fail-closed adversarial rules | Pass: 22 checks; P0=0; P1=0 |
| Research-report reconciliation | Pass: 42 embedded source rows equal the current ledger |
| Browser interaction and health | Pass: explorer/query/ranker; 0 console warnings/errors; 0 overlays; 0 external resources |
| Responsive inspection | Pass: 1280×720 and 390×844; no document overflow; mobile score/title defect repaired and retested |

The GTM scores are separate planning assessments: research system `9.3/10`, GTM design `9.2/10`, real market evidence `1.8/10`, and safe execution readiness `3.3/10`. Only the system/design scores improved; no market-validation claim was promoted.

## Link and access fallbacks

- Obsidian CLI was unavailable. Filesystem, YAML, wikilink, Base/Canvas inspection, and browser checks were used; the absence did not block any acceptance criterion.
- Defuddle encountered an eCFR metadata-extraction limitation. Current primary legal content was checked directly and recorded in dated atomic notes.
- LinkedIn returned automated-access status 999 for the founder profile and 429 for the company profile. No bypass was attempted. SRC-014 and SRC-023 point to the dated local atomic capture, which retains both public URLs and the access boundary.
- The Apple presentation URL, House OLRC timeout, and LinkedIn automated-access failures were replaced in the ledger by reproducible first-party or local evidence paths through CCR-005–008. No factual claim was upgraded by those fallbacks.

## Remaining blockers are business blockers, not QA defects

The package passes, while these operating gates remain open:

1. Written entity, signatory, engagement, role, authority, compensation, IP, confidentiality, and data terms.
2. Demonstrated current manual service, product/MVP, check catalog, portal, integrations, case capacity, and roadmap boundaries.
3. Exact claim evidence, domain/legal review, approval, and expiry.
4. Approved secure intake, storage, access, retention, deletion, incident, subprocessor, and cross-border controls.

Customer proof, commercial mechanics, reviewer/product capacity, CRM/list permission, funding/runway, owner time, and costs also remain unknown or blocked. These are mapped to GAP-001–024 and MT-001–014 in [[06_Research/Research Gaps and Interview Guide]].

## Final decision

The research artifact set is accepted. It must not be described as launch approval, a proven product, a verified recovery business, legal advice, guaranteed savings, available headcount, or an authorization to contact, publish, ingest customer data, file, or execute AI.

Next highest-value decision: hold one founder truth-and-gates workshop with Avi and the named legal, product/data, domain, security/privacy, website/analytics, and operating owners; admit the evidence pack; then record an explicit activation go/no-go.

## Related

[[06_Research/SheperD Deep Research - Control Note]] · [[06_Research/SheperD Interactive Report.html]] · [[SheperD HQ]]
