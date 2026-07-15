---
title: CRM Data Model
type: operations
status: proposed
owner: Michael
updated: 2026-07-15
evidence_status: inference
confidentiality: internal
tags:
  - sheperd/operations
  - sheperd/crm
---

# CRM Data Model

## Principle

Build a minimum viable schema in Week 2, then version it after Weeks 6 and 12. The CRM owns people, companies, activities, and deals. Obsidian owns approved knowledge and de-identified learning.

No live CRM or D2 dataset is admitted. The schema may be tested only with approved synthetic records until the tool, admin, source/permission rules, retention, and access controls are approved.

## Core objects

1. **Account/importer:** stable account ID, legal name, domain, geography, industry, volume/spend proxy, tier, ICP rationale, permitted-source basis, source/provenance, last verified date, duplicate/master state, do-not-contact state, owner.
2. **Contact:** stable contact ID, account ID, function, title, buying role, influence, relationship strength, permitted-source basis, source, last verified date, duplicate/master state, consent/opt-out/do-not-contact state.
3. **Opportunity:** stable opportunity ID, account/contact relationships, pain, stage, commercial-model hypothesis, value range, blocker, next action/date, close-date history, outcome reason.
4. **Activity:** stable activity ID, related object IDs, channel, direction, timestamp, outcome, message version, resulting next step.
5. **Data request/submission:** stable case metadata ID, opportunity ID, checklist version, request/receipt dates, NDA/DPA, secure-storage link, completeness sub-status, validation, rejection reason, owner—metadata only.
6. **Partner/referral:** stable partner/referral IDs, partner type, owner, SLA, referred account ID, acceptance, attribution, quality outcome.
7. **Experiment/cohort:** stable cohort ID, hypothesis, segment, persona, channel, message version, date range, sample, result, decision.
8. **Content/attribution:** stable asset ID, claim-review state, CTA, campaign/UTM, sourced inquiry.
9. **Objection/insight:** stable insight ID, normalized objection, persona, stage, evidence count, approved response.

## Controlled states

- Duplicate: `unique`, `suspected-duplicate`, `merged-to-master`.
- Contact permission: `unknown`, `permitted`, `opted-out`, `do-not-contact`, `suppressed`.
- Source basis: `founder-provided`, `partner-referral`, `direct-inquiry`, `licensed-data`, `public-professional`, `customer-provided`, `unknown`.
- Submission: `requested`, `accepted-request`, `received-pending-validation`, `incomplete`, `rejected`, `validated`.

The CRM configuration must enforce object relationships, required fields by stage, referential integrity where supported, and a master-record audit trail. `unknown` source basis or do-not-contact ambiguity blocks outreach.

## Required opportunity fields

- Account, primary contact, owner, source, cohort.
- Current stage and stage-entered date.
- Pain, qualification evidence, decision roles.
- Data readiness and secure-intake status.
- Product/data reviewer and SLA.
- Next action, owner, date.
- Blocker and outcome reason.
- Message/playbook version.

## Required control fields by object

| Object | Required controls |
|---|---|
| Account/contact | Stable ID; source basis; source record/URL; checked date; permission/consent; opt-out/DNC; duplicate/master; owner; created/updated audit |
| Opportunity | Account/contact/cohort; human stage owner; stage-entered time; qualification evidence; blocker; next action/owner/date; loss/no-decision reason; secure-intake state |
| Activity | Stable event ID; direction; channel; event time; message version; claim approval ID; human actor; outcome; related object IDs |
| Cohort/experiment | Experiment ID; segment; persona; channel; message; warm/cold/partner/inbound; date window; inclusion/exclusion; sample; decision |
| Submission metadata | Case metadata ID; authority/agreement; secure-system link; checklist version; request/receipt/validation times; completeness state; reviewer/SLA; no raw D3 |
| Content/inbound | Asset/version; claim approvals; CTA; source/UTM; consent; inquiry event; qualification remains human-only |

Unknown source, permission, DNC, message approval, secure path, reviewer capacity, or stage evidence blocks the corresponding action.

## Event contract

Every event stores:

`event_id · event_type · occurred_at_utc · recorded_at_utc · actor_id/role · account/contact/opportunity/cohort/experiment/message IDs as applicable · prior_state · proposed/new_state · source · permission state · owner · outcome/reason · correction_of_event_id`

Events are append-only where the CRM supports it. Corrections reference the prior event; they do not silently rewrite measurement history.

Minimum controlled event types:

- `account_received`, `account_admitted`, `account_rejected`, `record_suppressed`;
- `touch_reviewed`, `touch_delivered`, `response_received`, `meeting_booked`, `meeting_held`;
- `qualification_decided`, `stage_decided`, `data_request_accepted`;
- `submission_received`, `submission_incomplete`, `submission_rejected`, `submission_validated`;
- `analysis_completed`, `proposal_delivered`, `commercial_outcome_recorded`;
- `recovery_requested`, `recovery_realized`, `recovery_expired_or_reversed`;
- `approval_requested`, `approval_decided`, `incident_opened`, `incident_closed`.

## Automation boundaries

Automations may flag missing fields, stale records, SLA risk, and draft updates. A human must approve stage changes, qualification, recovery value, outcome, sensitive data, and external messages.

Deterministic controls may append an exception or proposed-action record only. They may not merge, delete, suppress, qualify, move stage, accept data, send, or publish. Every rule records version, input IDs/data class, result, override, latency, error, and rollback.

## Version and migration contract

- Record `schema_version` on exports and experiment datasets.
- Week 6/12 revisions require a field map, backfill rule, denominator impact, owner, test, rollback, and decision record.
- Preserve prior stage/message/cohort definitions for historical reports.
- A broken migration, unreconciled count, or cohort-mixing change blocks reporting and automation until repaired.

## Related

[[03_GTM/Customer Journey and Funnel]] · [[04_Operations/Customer Data Intake and Security]] · [[05_AI/AI Enablement Roadmap]] · [[04_Operations/Operating Cadence and KPI Dictionary]]
