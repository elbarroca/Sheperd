---
title: AI Enablement Roadmap
type: ai
status: proposed
owner: Michael
updated: 2026-07-15
evidence_status: inference
confidentiality: internal
tags:
  - sheperd/ai
---

# AI Enablement Roadmap

## Principle

Use AI first for retrieval, drafting, summarization, and quality control. Use deterministic workflows for permissions, routing, required fields, deadlines, and retention. Keep regulatory judgment, customer-data acceptance, and external action human-owned.

No workflow below is active. [[05_AI/Human Approval Policy]] is still proposed; Avi plus the relevant legal/privacy, product/security, and domain owners must approve it before any pilot.

## Layered control model

| Layer | Scope | Current state | Release boundary |
|---|---|---|---|
| 0 — deterministic controls | Claim/source/expiry; permission/DNC; required fields; duplicate candidates; routing; timers; attribution; KPI reconciliation; capacity/approval alerts | Designed; synthetic tests only | Append pass/block/exception/proposal; never execute material action |
| 1 — reviewed copilots | Cited research/account briefs; meeting prep; structured notes; CRM drafts; objections; content; metric narratives | Designed; blocked | `DRAFT - HUMAN REVIEW REQUIRED`; least privilege; named approval |
| 2 — future monitored internal agents | Approved D0/D1 aggregation; experiment comparison; stale-evidence monitoring; backlog/decision proposals | Not approved | Requires bounded state machine, tools, owner, audit, synthetic failures, fallback, rollback |
| 3 — prohibited until separate approval | Auto-send/publish; qualification/stage; data acceptance; eligibility/recovery; pricing/contracts; filing; irreversible mutation | Prohibited | Human-only; no connector or execution permission |

## Universal workflow contract

Every deterministic, copilot, or future-agent workflow must record:

1. Owner and accountable approver.
2. Purpose, trigger, eligibility, exclusion, and stop condition.
3. Permission, tools/systems, and least-privilege scope.
4. Allowed data class, region, subprocessor, and retention.
5. Versioned inputs, sources, rules/prompts/models, and output schema.
6. Human review and prohibited actions.
7. Audit log, correction, override, incident, and expiry.
8. Manual baseline, pilot sample, quality, active-time, and wait metrics.
9. False-positive and missed-opportunity cost.
10. Continue/change/stop threshold.
11. Fallback and rollback.
12. Decision date and evidence state.

Missing any item blocks the workflow. A prompt cannot substitute for absent technical permission or connector controls.

## Data classes

- **D0 — public:** public sources and approved public claims.
- **D1 — internal non-sensitive:** operating notes, de-identified learning, templates, and approved aggregate metrics.
- **D2 — controlled commercial:** CRM business contacts, activities, pipeline, and consent/permission state.
- **D3 — restricted case data:** invoices, contracts, shipment identifiers/events, credentials, dispute evidence, and customer-linked recovery data.

D2 requires an approved enterprise tool, least privilege, retention, and audit logging. D3 is disabled for AI until the secure case environment, subprocessors, permissions, and written reviewer approval exist.

## Prioritized workflows

| Priority | Workflow | Owner | Trigger | Allowed data | Tool category | Expected value | Principal risk | Human gate | Pilot success / rollback | State | Horizon |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | Knowledge copilot | Michael | Approved question against the vault | D0–D1 | Retrieval + LLM draft | Faster cited answers and visible gaps | Claim-state leakage | Review before external reuse | ≥95% material statements cited; zero unsafe upgrades. Roll back prompt/index on any unsafe upgrade. | Inactive | Weeks 1–2 |
| P0 | Meeting prep/notes | Michael | Approved meeting created or consented notes available | D0–D2; no D3 transcript until approved | Template + summarization | Less preparation and admin time | PII leakage or invented actions | Operator reviews every output/update | ≥90% required fields correct and ≥25% time reduction; stop on privacy incident. | Inactive | Weeks 1–3 |
| P0 | CRM hygiene | Michael | Daily/weekly schema check | D2 | Deterministic rules + alert drafting | More complete, current CRM | Incorrect material changes | Operator confirms every change | ≥20% fewer missing/stale fields; false alerts <10%; disable rule on repeated false alerts. | Inactive | Weeks 2–4 |
| P0 | Claims/objection copilot | Michael + domain reviewer | Draft response requested | D0–D1 | Retrieval + constrained drafting | Faster consistent responses | Regulatory or commercial overclaim | Avi/domain approval before send | 100% claim IDs and sources; zero invented claims; revert content set on failure. | Inactive | Weeks 2–4 |
| P1 | Account research | Michael | Account admitted with permitted source basis | D0–D2 | Search/retrieval + draft | Faster qualification prep | Stale facts or impermissible profiling | Operator validates facts and priority | ≥90% critical fields source-linked; stop source on access/quality issue. | Inactive | Weeks 3–6 |
| P1 | Outreach drafting | Michael | Approved account, permission, and message version | D0–D2 | Template + LLM draft | Lower drafting time | Unauthorized send or false personalization | Individual review; no auto-send | ≥30% time reduction, zero false material facts; disable auto-draft source on incident. | Inactive | Weeks 3–6 |
| P1 | Funnel analyst | Michael | Versioned weekly CRM export | D1–D2 | Deterministic metrics + analysis draft | Faster scorecard and anomaly detection | Wrong denominator or cohort mixing | Humans validate and decide | Totals reconcile 100%; zero cohort mixing; roll back query/version on mismatch. | Inactive | Weeks 4–8 |
| P1 | Content repurposing | Michael | Approved source and consent record | D0–D2; no D3 | Retrieval + LLM draft | Reuse approved learning | Unapproved proof or customer disclosure | Avi + customer/legal as needed | 100% approval/claim links; stop on permission gap. | Inactive | Weeks 5–10 |
| P2 | Intake completeness | Product/data owner | Approved case metadata received | D2 metadata only; D3 disabled | Deterministic checklist + draft | Less missing-item coordination | Treating completeness as eligibility | Operator approves; specialist validates | ≥20% faster completeness cycle, zero acceptance decisions by AI; revert to manual checklist on error. | Inactive | Weeks 6–10 |
| P2 | Partner operations | Relationship owner | Referral or SLA event | D2 | Deterministic alerts + drafts | Fewer missed follow-ups | Incorrect attribution or spam | Relationship owner approves | ≥95% SLA-alert precision; disable noisy rule. | Inactive | Weeks 7–10 |
| P2 | Inbound triage | Michael | Approved form submission | D2 only | Deterministic routing + draft | Faster acknowledgment | PII leakage or false qualification | Human qualifies and responds | 100% routing-rule compliance; stop on security or consent failure. | Inactive | Weeks 8–12 |

## Pilot standard

For each workflow:

1. Use 5–10 permitted records.
2. Define the baseline time/error rate.
3. Version prompts and rules.
4. Require citations for factual output.
5. Log human corrections and false positives.
6. Use least-privilege access.
7. Decide continue/change/stop before expanding.
8. Record owner, data class, tool, permissions, success threshold, rollback, and state change.
9. Use `DRAFT - HUMAN REVIEW REQUIRED` exactly for every assisted output.
10. Preserve active time, review time, wait, false positives, missed alerts, overrides, and incidents separately.

## Initial stack shape

- Obsidian: approved knowledge and operating context.
- CRM: accounts, contacts, activities, stages, and experiments.
- Secure storage/case system: invoices and operational evidence.
- Workflow automation: deterministic alerts and draft creation.
- LLM: cited retrieval, summarization, drafting, and analysis—not final authority.

## Evaluation metrics

- Minutes saved per meeting or record.
- Citation coverage and factual correction rate.
- CRM completeness and stale-record reduction.
- Draft acceptance/edit distance.
- False alert and missed-alert rates.
- User confidence and override rate.
- Privacy/security incidents: target zero.

## Future-agent admission test

Layer 2 remains blocked until Layer 0 passes critical-gate recall on approved synthetic failures, Layer 1 demonstrates citation/quality and review value on permitted records, owners and retention are approved, and the bounded agent has no external/material execution tool. One failure involving sensitive data, unsupported regulatory meaning, unauthorized action, or material record mutation stops the pilot and returns the process to the manual fallback.

## Related

[[00_System/Knowledge Retrieval Contract]] · [[05_AI/Human Approval Policy]] · [[04_Operations/CRM Data Model]]
