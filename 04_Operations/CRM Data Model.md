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

## Automation boundaries

Automations may flag missing fields, stale records, SLA risk, and draft updates. A human must approve stage changes, qualification, recovery value, outcome, sensitive data, and external messages.

## Related

[[03_GTM/Customer Journey and Funnel]] · [[04_Operations/Customer Data Intake and Security]] · [[05_AI/AI Enablement Roadmap]] · [[04_Operations/Operating Cadence and KPI Dictionary]]
