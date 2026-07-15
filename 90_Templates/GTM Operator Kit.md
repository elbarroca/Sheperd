---
title: SheperD GTM Operator Kit
type: template-kit
status: ready-internal
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/template
  - sheperd/gtm
---

# SheperD GTM Operator Kit

> [!warning] Universal boundary
> Internal preparation only. Use D0/D1 or approved synthetic data. Never paste contacts, customer identity, invoices, shipment identifiers, contracts, credentials, raw transcripts, or recovery evidence. `DRAFT - HUMAN REVIEW REQUIRED` applies to every external-facing draft. A completed template does not authorize execution.

## Universal record header

```text
record_id:
version:
owner:
approver:
state: draft | blocked | approved-internal | approved-for-defined-action
data_class: D0 | D1 | approved-synthetic
source_ids:
claim_ids:
created_at:
decision_or_expiry_date:
rollback_owner:
```

## 1. Founder truth-and-gates workshop

```text
Purpose: resolve GAP-001–012 with artifacts or demonstrations, not adjectives.
Required attendees: Avi; Michael; counsel; product/data; domain/legal; security/privacy; website/analytics.
Pre-read admitted: yes/no

Gate | Required evidence | Presenter | Approver | Decision | Missing | Due
Authority/entity | | | | go/no-go/blocked | |
Product truth | | | | go/no-go/blocked | |
Claims | | | | go/no-go/blocked | |
Secure intake | | | | go/no-go/blocked | |
Commercial terms | | | | go/no-go/blocked | |
Capacity/SLA | | | | go/no-go/blocked | |

Decisions recorded:
Explicitly deferred/stopped work:
Activation decision: GO | NO-GO
```

## 2. Product demonstration and truth table

```text
capability_id:
customer-visible job:
demonstration environment: approved-synthetic only
input:
ordered steps:
output:
human owner:
exception path:
audit evidence:
security boundary:
current state: current-service | current-MVP | pilot | roadmap | unknown
supporting artifact:
claim IDs affected:
approved external wording:
approver and expiry:
```

## 3. Evidence-request checklist

```text
request_id:
decision question:
minimum evidence:
accepted authority:
allowed data class: D0 | D1 | approved-synthetic
owner:
approver:
secure system required: no
received date:
admission result: admitted | rejected | incomplete
rejection/missing reason:
canonical note updated:
```

## 4. Role and authority matrix

| Action | Responsible | Accountable approver | Consulted | Informed | Permission evidence | Expiry | State |
|---|---|---|---|---|---|---|---|
| Represent company externally | | | | | | | blocked |
| Approve product wording | | | | | | | blocked |
| Approve regulatory wording | | | | | | | blocked |
| Accept customer data | | | | | | | blocked |
| Qualify/change CRM stage | | | | | | | blocked |
| Approve pricing/contract | | | | | | | blocked |
| Send/publish/file | | | | | | | blocked |

## 5. ICP/account-admission rubric

```text
account_id: synthetic only until CRM approval
source basis:
source checked date:
permission/DNC state:
segment/persona/channel/message/cohort:
problem signal and evidence:
finance owner known: 0/1/2
operations owner known: 0/1/2
D&D exposure evidence: 0/1/2
evidence readiness: 0/1/2
carrier/port concentration: 0/1/2
relationship path: 0/1/2
urgency trigger: 0/1/2
mandatory gates pass: yes/no
score and rationale:
human admission decision:
disqualifier:
```

## 6. Stakeholder research brief

```text
stakeholder_role:
account/cohort ID:
permitted public sources:
current responsibilities:
incentives:
likely trigger — hypothesis:
likely objection — hypothesis:
decision rights — unknown unless sourced:
evidence required:
questions to validate:
facts versus inferences separated: yes/no
reviewer:
```

## 7. Account brief

```text
account_id:
cohort_id:
source and permission:
checked date:
segment rationale:
known facts with source:
unknowns:
stakeholder map:
trigger evidence:
approved message version:
claim IDs:
disqualifiers:
next research action:
human reviewer:
```

## 8. Discovery guide

```text
meeting_id:
consent/recording state:
persona and cohort:
current process and owner:
active time versus wait:
invoice/evidence systems — metadata only:
repeated exceptions:
business impact — customer statement, not fact:
authority and decision path:
secure-data readiness:
timing/trigger:
objections:
next action/owner/date:
missing evidence:
qualification decision by human:
```

## 9. Qualification rubric

All mandatory items must pass; scoring cannot override a failure.

| Mandatory item | Pass evidence | Pass/fail | Source |
|---|---|---|---|
| ICP rationale | | | |
| Named economic and operational owner | | | |
| Relevant problem and trigger | | | |
| Case-specific path without outcome promise | | | |
| Permitted source/message/cohort | | | |
| Approved secure-data path | | | |
| Product/data reviewer and capacity | | | |
| Next action/owner/date | | | |

```text
human decision: qualified | not-qualified | needs-evidence
reason:
approver:
```

## 10. Objection library

| Objection ID | Exact de-identified wording | Persona | Stage | Count | Interpretation | Alternative explanation | Safe response direction | Claim IDs | Proof missing | Approver |
|---|---|---|---|---:|---|---|---|---|---|---|

## 11. Reviewed follow-up

```text
DRAFT - HUMAN REVIEW REQUIRED
draft_id:
recipient/cohort ID:
permission state:
message version:
meeting facts and source:
agreed next action/owner/date:
exact external sentences:
claim IDs per sentence:
no sensitive attachment requested: yes/no
reviewer:
send approver:
send connector: absent
```

## 12. Secure data-request handoff

```text
handoff_id:
opportunity_id:
customer authority state:
NDA/DPA state:
approved system/link owner:
checklist version:
requested metadata:
requested D3 categories — record categories only, never values:
product/data reviewer and SLA:
request/receipt/validation timestamps:
missing-item loop:
acceptance decision: human-only
retention/deletion policy ID:
incident contact:
```

No email attachments, Obsidian uploads, credentials, or AI processing are implied.

## 13. Partner intake and referral SLA

```text
partner_id:
partner type:
relationship owner:
permission to introduce:
referred account ownership:
channel-conflict check:
approved message/claim IDs:
commercial terms state:
accepted/rejected reason:
acknowledgement due:
fit decision due:
permitted stage updates:
secure-data boundary accepted:
capacity check:
stop/escalation rule:
```

## 14. CRM stage contract

Use the canonical stages in [[03_GTM/Customer Journey and Funnel]]. For each stage change record:

```text
opportunity_id:
prior_stage:
proposed_stage:
entry evidence:
required fields complete:
exit evidence from prior stage:
human decision owner:
decision timestamp:
cohort/message/source preserved:
reason or exception:
rollback/correction record:
```

## 15. Required CRM fields

Minimum for every active opportunity:

- stable account, contact, opportunity, cohort, and source IDs;
- source basis, checked date, permission, opt-out/DNC, duplicate/master state;
- segment, persona, channel, warm/cold, message/playbook version;
- stage and stage-entered timestamp;
- pain/trigger evidence, decision roles, data-readiness state;
- next action, owner, date, blocker, outcome/loss/no-decision reason;
- product/data reviewer, SLA, secure-intake metadata state;
- experiment/activity IDs and created/updated audit fields.

Unknown required values block the relevant action; they are never coerced to zero or blank success.

## 16. Weekly scorecard

Use [[90_Templates/Weekly Scorecard]]. Every percentage includes numerator, denominator, sample, cohort, message version, period, and exclusions. Active time, wait time, objections, submission friction, and capacity must remain separate.

## 17. Experiment brief

Use [[90_Templates/Experiment]]. One experiment means one segment, persona, message, channel, cohort, and primary hypothesis. Warm, cold, partner, and inbound never share a denominator.

## 18. Content brief

```text
DRAFT - HUMAN REVIEW REQUIRED
asset_id/version:
decision question:
audience and journey stage:
query/theme evidence:
content pillar:
one approved CTA:
exact draft sentences:
claim IDs per sentence:
primary sources and checked dates:
product truth dependency:
customer permission dependency:
domain/product/privacy/commercial approvers:
approval scope/date/expiry:
analytics and consent state:
canonical URL/location:
rollback owner and trigger:
```

## 19. Decision record

Use [[90_Templates/Decision Record]]. A valid decision identifies owner, scope, evidence, alternatives, consequences, review trigger, and superseded record.

## 20. Capacity and stop/defer ledger

| Change ID | New work | Trigger | Owner hours/skills required | Dependency capacity | Continue first | Stop/defer | Approver | Decision date | State |
|---|---|---|---|---|---|---|---|---|---|

```text
capacity evidence period:
active time:
wait time:
backlog/SLA state:
new activation allowed: yes/no
reason:
next review:
```

If new work lacks an explicit stopped/deferred item, owner, capacity evidence, or approval, it remains blocked.

## Related

[[03_GTM/SheperD GTM Validation and Optimization - Control Note]] · [[04_Operations/CRM Data Model]] · [[05_AI/Human Approval Policy]]
