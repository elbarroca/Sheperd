---
title: AI Opportunity Register
type: ai-register
status: proposed-blocked
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/ai
---

# AI Opportunity Register

> [!abstract] Decision answer
> No AI or automation pilot is active. Deterministic gates should come first; AI may later draft or retrieve under review; material decisions and external actions remain human-only. No bounded agent is defensible today because authority, tools, retention, data paths, owners, and controls are not approved. Evidence status: `internal-proposal`; confidence: high on control boundaries and low on measured benefit. Sources: [[05_AI/AI Enablement Roadmap]], [[05_AI/Human Approval Policy]], `06_Research/data/ai-opportunities.csv`.

## Non-negotiable release rules

- Every pilot is blocked until WF-042 approves the policy, tool, data path, owner, approver, retention, logging, baseline, and rollback.
- D0/D1 is the default. D2 requires approved enterprise controls, least privilege, audit logging, and retention. D3 remains disabled for automation/LLM use.
- Every AI output begins exactly `DRAFT - HUMAN REVIEW REQUIRED`, cites sources, and flags missing evidence.
- Outbound, publishing, dispute filing, qualification, stage changes, pricing, recovery estimates, data acceptance, deletion, and merging permissions must be absent—not merely discouraged in a prompt.
- Any sensitive-data exposure, invented regulatory claim, unauthorized external action, or material-record change stops the workflow and preserves logs.

## Permission and audit codes

| Code | Meaning |
|---|---|
| PERM-D | Least-privilege read; append validation, alert, or proposed queue item only; no material execution |
| PERM-A | Least-privilege read; append labeled draft and audit log only |
| PERM-H | Named human decides and authorizes downstream action; AI has no decision permission |
| AUD-D | Timestamp, rule/opportunity version, input references/class, result, override, latency, error, rollback |
| AUD-A | AUD-D plus prompt/model/source IDs, citations, draft hash, label, edits, approval/rejection |
| AUD-H | Named actor/approver, basis, decision, timestamp, downstream authorization, correction |
| RET-0 | Duration unset; activation blocked until approved; no raw D2/D3 in telemetry |
| RET-H | Decision record follows approved legal/contract schedule; D3 stays in secure case system |

## Thresholds and rollback

| Code | Continue | Change | Stop |
|---|---|---|---|
| TH-G | 100% critical-gate recall; ≥95% other accuracy; zero prohibited action/incident | 80–94% noncritical accuracy with no critical miss | Any critical miss, bypass, exposure, or unauthorized action |
| TH-D | ≥95% precision/recall; ≥25% median time reduction; zero incident | 80–94% or <25% time reduction | <80%, prohibited action, or incident |
| TH-A | 100% material claims cited; ≥85% minor-edit acceptance; ≥25% time reduction | 60–84% acceptance or <25% reduction | Unsupported material claim, privacy breach, auto-action, or <60% acceptance |
| TH-M | Totals reconcile 100%; zero cohort mixing; ≥25% time reduction | Presentation defect only | Numeric mismatch, cohort mixing, or unsupported causal claim |
| TH-H | 100% named decisions/approvals logged; zero bypass | 90–99% documentation or missed SLA | Bypass, AI decision, or unauthorized irreversible action |

- `RB-D`: disable rule, restore manual checklist, remove only reversible queue artifacts, preserve logs.
- `RB-A`: disable prompt/index/source, quarantine drafts, restore manual drafting, preserve logs.
- `RB-H`: stop downstream workflow, escalate, preserve evidence, correct under human authority.

## Deterministic controls — first priority

| ID | Priority | Workflows | Control | Owner | Gate | State |
|---|---:|---|---|---|---|---|
| AI-001 | P0 | WF-002/003/006/014/016/018/034/037 | Claim/source/state/expiry validation | Michael | Avi + domain reviewer | Blocked |
| AI-002 | P0 | WF-001/003/014/017/022/025/028/029/034/039 | External-release prerequisite lock | Michael | Action-specific approver | Blocked |
| AI-003 | P0 | WF-004/025/026/042/043 | Data-class/tool/intake gate | Product/data | Legal/privacy + product/security | Blocked |
| AI-004 | P1 | WF-025/026 | Metadata completeness exceptions; never eligibility | Product/data | Specialist/operator | Blocked |
| AI-005 | P0 | WF-009/013/021/022/023/030/035/039 | CRM provenance, consent, freshness, DNC, duplicate candidate, next action | Michael | Record owner | Blocked |
| AI-006 | P1 | WF-009/010/011/020/023/024 | Nonbinding rubric-factor calculation; no qualification | Michael | Opportunity owner | Blocked |
| AI-007 | P1 | WF-011/024/030/032 | Partner attribution and SLA alerts | Relationship owner | Relationship owner | Blocked |
| AI-008 | P1 | WF-035/039 | Inbound route and consent exception; no qualification | Michael | Michael | Blocked |
| AI-009 | P0 | WF-008/032/033/036/038/044 | KPI reconciliation, cohort and denominator controls | Michael | Avi + Michael | Blocked |
| AI-010 | P0 | WF-015/019/031/033/036/038/041/045 | Decision, SLA, capacity, and scope-change alerts | Avi + Michael | Avi | Blocked |

## AI-assisted drafts — after deterministic gates

| ID | Priority | Workflows | Draft output | Owner | Approver | State |
|---|---:|---|---|---|---|---|
| AI-011 | P1 | WF-005/006/014/023/037 | Cited vault answer with gaps | Michael | Intended-use reviewer | Blocked |
| AI-012 | P1 | WF-002/005/007/012/015/023/024/033/036/041 | Meeting brief, notes, proposed tasks | Michael | Meeting owner | Blocked |
| AI-013 | P1 | WF-009/010/020/021/022 | Source-linked account brief | Michael | Opportunity owner | Blocked |
| AI-014 | P1 | WF-021/022/023/024/035 | Outreach/follow-up draft; send connector absent | Michael | Michael; Avi for new claim/version | Blocked |
| AI-015 | P1 | WF-003/014/023/030/037 | Cited objection response with uncertainty | Michael + reviewer | Avi/domain reviewer | Blocked |
| AI-016 | P1 | WF-032/033/036/038/044 | Descriptive metric narrative; no causal claim | Michael | Avi + Michael | Blocked |
| AI-017 | P2 | WF-016/018/034 | Permission-linked content/case-study draft | Michael | Avi + customer/legal as needed | Blocked |
| AI-018 | P2 | WF-025/026 | Missing-item request from reviewed exceptions | Product/data | Operator/specialist | Blocked |
| AI-019 | P1 | WF-007/012/019/031/033/036/038/041/045 | Retrospective/decision memo | Michael | Avi | Blocked |

## Human-only gates

| ID | Workflows | Decision | Human owner/approver | Fallback |
|---|---|---|---|---|
| AI-020 | WF-009/010/011/013/019/020/023/024/030/033/036/041 | Admission, qualification, stage, partner rating | Michael/opportunity owner; Avi at gates | Keep prior state; escalate |
| AI-021 | WF-004/017/025/026/042/043 | Data acceptance, tools, security, subprocessors, retention | Legal/privacy + product/security; Avi | Block intake; secure manual process |
| AI-022 | WF-002/003/006/023/027/029 | Regulatory interpretation and case eligibility | Domain/legal reviewer | State uncertainty; do not advance |
| AI-023 | WF-027/029 | Recovery value, probability, guarantee language | Product/data + required reviewer | No estimate; disclose unknown |
| AI-024 | WF-012/028/041 | Pricing, contract, business model | Avi + authorized legal/commercial | Use last approved terms or pause |
| AI-025 | External-action workflows | Send, publish, disclose, file | Action owner + matrix approver | Do not release |
| AI-026 | WF-019/033/036/040/041/045 and irreversible changes | Hiring, funding, scale, capacity, deletion/merge | Avi + relevant authorized owner | Maintain current state |

## Data-class boundary

| Class | Content | Initial use |
|---|---|---|
| D0 | Public sources and approved public claims | Deterministic and assisted only after approval |
| D1 | Internal non-sensitive notes, de-identified learning, templates, aggregates | Deterministic and assisted after approval |
| D2 | Contacts, activities, pipeline, permission state | Approved enterprise tool only; least privilege and audit |
| D3 | Invoices, contracts, shipment data, credentials, disputes, customer-linked outcomes | Disabled for AI; human-only in approved secure case system |

## Pilot contract

Every candidate pilot:

1. Uses 5–10 permitted records or approved synthetic scenarios.
2. Measures the manual baseline before assistance.
3. Versions rules, prompts, model, sources, and permissions.
4. Logs human corrections, false positives, missed alerts, time, overrides, incidents, and rollbacks.
5. Applies the opportunity-specific threshold from `06_Research/data/ai-opportunities.csv`.
6. Records continue/change/stop before expansion.

High-risk pilots wait even if theoretical hours are high. No recommendation may advance without owner, permission, secure path, review gate, measurable baseline, retention, audit log, and rollback.

## Bounded-agent decision

**Now: none.** Deterministic rules and human-reviewed drafts cover the supported bottlenecks with less risk. A later bounded-agent proposal would require explicit inputs, permissions, tools, state machine, output, owner, approver, fallback, audit log, retention, stop conditions, synthetic failure tests, and no external/material execution. Evidence status: `internal-proposal`; confidence: high.

## Related

[[06_Research/Role and Workflow Atlas]] · [[06_Research/Time Savings Model]] · [[06_Research/Implementation Roadmap]]
