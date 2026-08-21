---
title: Implementation Roadmap
type: implementation-roadmap
status: conditional
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/roadmap
---

# Implementation Roadmap

> [!abstract] Decision answer
> **Now means evidence and instrumentation—not activation.** First pass the founder truth-and-gates workshop. Then prove deterministic controls on 5–10 permitted records before any AI-assisted draft pilot. External outreach, publishing, customer-data handling, and autonomous execution remain unscheduled while the activation gates are blocked. Evidence status: `internal-proposal`; confidence: high on sequencing and low on timing/capacity until owners and hours are admitted.

## Priority matrix

| Horizon | Work | Why now | Gate |
|---|---|---|---|
| Now | WF-001–004 founder truth, written authority, product/claims/security decisions | Removes legal, truth, and data blockers | Avi and named owners |
| Now | WF-008/044 measurement schema and time/latency instrumentation | Replaces assumptions before optimization | Metric owners |
| Now | AI-001/002/003/005/009/010 control design and synthetic tests | Deterministic gates protect later work | WF-042; no live pilot yet |
| Next | CRM MVP, list admission, scorecard reconciliation, decision/capacity controls | Fast learning with lower external risk | Week-2 activation plus D2 controls |
| Next | AI-011/012/013/015/016 reviewed draft pilots | Reduce retrieval/admin burden after guardrails | Deterministic gates, consent, approved tools |
| Next | One bounded warm cohort and one bottleneck experiment | Establish comparable funnel evidence | External activation gate |
| Later | Intake completeness, partner SLA, inbound routing, approved content | Needs live volume, security, permission, and owners | Workflow-specific approvals |
| Later | Product/case automation using D3 | Requires secure case environment and written approval | Not scheduled |
| Do not automate | Eligibility, legal interpretation, recovery value/probability, pricing/contracts, data acceptance, qualification/stage, send/publish/file, hiring/funding, irreversible changes | Accountable judgment or external consequence | Human-only AI-020–026 |
| Do not build now | Bounded agents | Deterministic controls and reviewed drafts cover supported bottlenecks | Reassess only after measured pilots |

## 30-day plan — unblock and instrument

No external activation is implied by dates.

| ID | Owner | Dependency | Decision date | Output | Pilot/measurement | Rollback | Expected learning |
|---|---|---|---|---|---|---|---|
| R-30-01 | Avi + counsel + Michael | Evidence pack | Day 5 | Signed engagement or explicit no-go | Authority checklist | Remain research-only | Whether Michael has safe authority |
| R-30-02 | Avi + product owner | Named owner and demonstration | Day 7 | Current-service/MVP/pilot/roadmap truth table | Demonstrate with permitted synthetic/redacted evidence | Withdraw unsupported capability wording | What exists and who operates it |
| R-30-03 | Avi + domain/legal | Exact claim list and sources | Day 10 | Remove/substantiate/approve decision by claim | 5–10 claim synthetic validation cases | Revert to blocked register | Which wording is usable |
| R-30-04 | Product/security + legal/privacy | Systems/vendors/data map | Day 10 | Approved secure-intake design or no-go | 5–10 synthetic metadata paths | Block intake; manual secure process | Whether D2/D3 handling is lawful and supportable |
| R-30-05 | Michael + metric owners | CRM/KPI definitions | Day 12 | WF/AI/event IDs, timestamps, exception and wait fields | Instrument synthetic events | Remove test data | Whether the system can measure honestly |
| R-30-06 | Michael + Avi | Hours/priorities/budget | Day 12 | Capacity ledger and stop/defer rules | Two-week owner time diary | Revert new scope | Actual owner caps and bottlenecks |
| R-30-07 | Michael + CRM owner | Approved CRM and D2 controls | Day 15 | MVP schema, stage contract, provenance/DNC rules | 5–10 permitted or synthetic records | Restore manual checklist | Record quality and admin burden |
| R-30-08 | Workflow owners | WF-042 approvals | Day 20 | Synthetic test results for AI-001/002/003/005/009/010 | 5–10 scenarios each | Disable rules; preserve logs | Gate recall, precision, maintenance burden |
| R-30-09 | Avi | R-30-01 through 08 | Day 30 | Week-2 activation go/no-go | Formal evidence review | No activation | Whether controlled external learning can start |

## 60-day plan — conditional controlled learning

Execute only if R-30-09 is `go` and each workflow-specific control is approved.

| ID | Owner | Dependency | Decision date | Output | Pilot | Rollback | Expected learning |
|---|---|---|---|---|---|---|---|
| R-60-01 | Michael | Admitted list, permission, CRM | Day 35 | First comparable warm cohort | Bounded cohort from approved plan | Stop touches; preserve records | Contactability and message evidence |
| R-60-02 | Michael | AI-005, consent, tool approval | Day 40 | CRM hygiene decision | 5–10 permitted records | Disable rule; manual audit | Precision, missing/stale reduction, time |
| R-60-03 | Michael | AI-009, stable export | Day 42 | Reconciled scorecard decision | Two weekly runs | Manual reconciliation | Numeric integrity and reporting time |
| R-60-04 | Michael | Consent and enterprise D2 tool | Day 45 | Meeting-admin decision | 5–10 consented meetings | Manual template | Prep/admin time, corrections, privacy |
| R-60-05 | Michael + reviewer | AI-001 and approved corpus | Day 48 | Knowledge/claims decision | 5–10 questions/drafts | Disable prompt/index | Citation coverage and reviewer burden |
| R-60-06 | Product/data | Secure metadata and AI-003 | Day 50 | Submission-friction baseline | 5 permitted metadata-only packages | Manual checklist | Missing loops, active time, wait time |
| R-60-07 | Michael | Comparable records | Day 60 | Week-6 continue/change/stop | Cohort and workflow retrospective | Stop activation expansion | Whether any segment/message/channel merits next sprint |

## 90-day plan — conditional consolidation

| ID | Owner | Dependency | Decision date | Output | Pilot/measurement | Rollback | Expected learning |
|---|---|---|---|---|---|---|---|
| R-90-01 | Michael | R-60 evidence | Day 70 | One revised cohort with one changed variable | Comparable second cohort | Stop/change one variable | Whether evidence replicates |
| R-90-02 | Relationship owner | Approved partner terms/data | Day 75 | Partner SLA/attribution decision | 5–10 events | Manual partner tracker | Referral quality and admin load |
| R-90-03 | Website/analytics + Michael | Privacy/truth repairs and consent | Day 75 | Inbound attribution baseline | 5–10 synthetic/permitted events | Manual routing | Source-to-valid-submission visibility |
| R-90-04 | Michael + reviewers | Approved sources and permission | Day 80 | One content pilot decision | 5 source assets; no autonomous publish | Manual drafting; no release | Draft time, proof/permission burden |
| R-90-05 | Product/data + finance | Permitted outcomes and method | Day 85 | Delivery/cash-credit capacity evidence | 5 representative cases where available | Preserve manual process | Throughput, exception, outcome, cash-cycle economics |
| R-90-06 | Avi + Michael | Owner time diary, pilots, cohorts | Day 90 | Next-90 investment and capacity decision | Formal review | Keep current scope | What to scale, stop, defer, or staff |

## Instrumentation-first order

1. Stable event IDs and workflow/opportunity IDs.
2. Eligible versus attempted/completed/excluded unit counts.
3. Primary operator and reviewer active minutes.
4. Trigger, handoff, approval, completion, and elapsed wait timestamps.
5. Exception reason, rework minutes, correction, override, and rollback.
6. Data class, permission, tool, version, source, and approver.
7. Outcome and confidence—not just activity.

No high-impact assumption can be promoted above low confidence before five representative observations or instrumented logs.

## Capacity allocation and stop/defer rules

Hours are unknown until MT-014 completes. Allocation is therefore ordinal, not numeric.

| When new work is added | Continue first | Stop or defer first | Approver |
|---|---|---|---|
| Founder/product truth work expands | Written gates, evidence admission, instrumentation | Content roadmap, partner expansion, AI drafts | Avi |
| External cohort activates | CRM hygiene, discovery quality, secure submission, weekly measurement | Broad outbound, multiple personas/channels, unsourced content | Avi + Michael |
| Product/data backlog or SLA fails | Existing-submission quality and customer communication | New outreach/data requests | Product/data + Avi |
| Reviewer SLA fails | Current claims/cases and safe wording | New claims, new content, experimental messages | Domain/legal + Avi |
| Website implementation expands | Michael keeps requirements/acceptance only | Website engineering and production ownership remain outside role | Avi + website owner |
| One AI pilot starts | Baseline, review, logging, rollback for that pilot | All other new AI pilots | Workflow owner + risk approver |
| Partner pilot starts | One partner type and comparable events | Broad partner roster and new economics | Avi + relationship owner |
| Unplanned obligation appears | P0 gates, active cohort, required measurement | Lowest-priority future item; record explicit tradeoff | Avi + Michael |

Michael should not accept accountability for deal volume, product analysis, legal conclusions, secure-data controls, website engineering, hiring/funding, or multiple parallel experiments without controllable inputs, named owners, and an explicit stopped/deferred item.

## Pilot decision template

Every roadmap item records:

`owner · approver · workflow/opportunity ID · data class · permission · tool · baseline · sample · quality metric · time metric · false positive · missed alert · incident · continue/change/stop threshold · rollback · decision date · expected learning`

## Stop conditions

- Any critical gate miss, privacy/security incident, unsupported material claim, or unauthorized external/material action.
- No owner, permission, secure path, review gate, baseline, measurable pilot, retention, or rollback.
- Product/data or reviewer capacity cannot meet the committed SLA.
- Small-sample activity is being promoted as a validated segment, scalable motion, or guaranteed capacity.
- Scope expands without a recorded stop/defer decision.

## Related

[[06_Research/Role and Workflow Atlas]] · [[06_Research/AI Opportunity Register]] · [[06_Research/Time Savings Model]] · [[06_Research/Research Gaps and Interview Guide]]
