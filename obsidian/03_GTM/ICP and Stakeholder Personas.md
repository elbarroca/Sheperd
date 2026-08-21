---
title: ICP and Stakeholder Personas
type: gtminput
status: hypothesis
owner: Michael
updated: 2026-07-15
evidence_status: inference
confidentiality: internal
tags:
  - sheperd/gtm
  - sheperd/customer
---

# ICP and Stakeholder Personas

## ICP hypothesis

The strongest initial account is likely a U.S. importer/BCO with recurring container volume, material D&D spend, centralized finance ownership, accessible invoice and event evidence, and concentration across a manageable carrier/port set.

This remains a beachhead hypothesis. Company size, revenue, and TEU volume are context signals—not eligibility, qualification, or expected-recovery evidence.

## Account score — v0

Score each factor 0–2; use it for prioritization, not automatic exclusion.

| Factor | 0 | 1 | 2 |
|---|---|---|---|
| D&D exposure | Unknown/low | Episodic | Material recurring |
| Data availability | Unknown | Partial | Invoice + operational evidence accessible |
| Economic owner | None | Diffuse | Named finance owner |
| Operational owner | None | Indirect | Named logistics/ops owner |
| Complexity | Highly fragmented | Moderate | Concentrated carriers/ports |
| Relationship | Cold/no path | Reachable | Warm introduction/trusted partner |
| Urgency | None | General concern | Active audit, margin, or dispute pressure |

Keep score, rationale, evidence, and source in the CRM.

## Admission rule

An account may enter a future research cohort only when all mandatory fields below are present. A score never overrides a failed gate.

| Gate | Pass evidence | Fail-closed result |
|---|---|---|
| Source and permission | Permitted source basis, source URL/record, checked date, DNC/opt-out state | Do not contact |
| Cohort isolation | One segment, persona, channel, message version, warm/cold state, and date window | Do not include in experiment |
| Problem signal | Dated, sourceable D&D/audit/reconciliation trigger or explicit unknown | Research only; do not imply pain |
| Data path | Metadata-only readiness; approved secure path required before any case request | No data request |
| Delivery capacity | Named product/data owner and available review SLA | No activation |
| Claim/message approval | Exact message version and claim IDs approved for channel | No send |

Prioritization score: `0–6` low information, `7–10` research candidate, `11–14` higher-priority research candidate. These bands are internal proposals and do not constitute qualification.

## Beachhead hypotheses to compare after activation

| Hypothesis | Inclusion signal | Primary stakeholder | Main learning | Disqualifier |
|---|---|---|---|---|
| Finance-owned recurring review | Recurring D&D coding plus named finance owner | Controller / AP lead | Whether reconciliation and auditability create a valid next step | No owner or no evidence path |
| Concentrated port/carrier exposure | Manageable carrier/port mix plus recurring exceptions | Head of logistics | Whether narrower evidence patterns reduce submission friction | Highly fragmented mix without support capacity |
| Partner-referred importer | Permissioned introduction from broker/3PL/advisor | Finance plus logistics | Whether trusted access improves held meetings and valid submissions | No consent, account ownership, or referral terms |
| Audit/pay adjacency | Existing freight-audit workflow lacking D&D depth | Freight audit owner | Partner/embed versus direct-service fit | Channel conflict or unclear data rights |

Do not run these together or promote any before comparable outcomes, loss reasons, cycle time, and delivery effort exist.

## Stakeholder map

### Finance — CFO, VP Finance, Controller, AP

- Cares about: realized cash/credit, auditability, net recovery, effort, fee, timing.
- Fears: speculative estimates, hidden workload, control loss, unverified claims.
- Evidence needed: recovery mechanics, fee definition, audit trail, case proof, security.
- Likely triggers to test: finance close, recurring accessorial review, material carrier credits, margin pressure, audit finding.
- Purchasing path to map: pain owner → finance owner → legal/procurement/security → authorized signer.

### Supply chain/logistics leadership

- Cares about: carrier accountability, recurring patterns, exception reduction, less escalation work.
- Fears: damaged carrier relationships, operational blame, shallow invoice review.
- Evidence needed: factual timelines, carrier/port knowledge, collaboration model.
- Likely triggers to test: repeated carrier/terminal exception, closure/hold, portal or tariff change, escalation backlog.

### Operations/AP/data owner

- Cares about: clear checklist, secure intake, minimal rework, status visibility.
- Fears: a large manual data project and duplicate systems.
- Evidence needed: exact fields, formats, turnaround, ownership, support.
- Likely triggers to test: missing-document loops, invoice backlog, reconciliation failure, unclear internal ownership.

### Legal/procurement/security

- Cares about: authority, data processing, retention, confidentiality, liability, terms.
- Fears: sensitive shipping data exposure and unsupported regulatory statements.
- Evidence needed: contracts, privacy/security controls, subprocessors, access model.
- Procurement questions: authority to dispute, recovered-value definition, fee/clawback, liability, insurance, termination, audit rights.
- Security questions: system boundaries, D2/D3 flow, regions, least privilege, logs, retention/deletion, incident response.

### Partner — broker, 3PL, auditor, consultant

- Cares about: client value, trust preservation, referral clarity, speed, economics.
- Fears: channel conflict, client poaching, weak delivery, unclear attribution.
- Evidence needed: referral SLA, account ownership, reporting, quality proof.
- Trigger to test: repeated client questions that the partner cannot resolve efficiently without creating channel conflict.

## Disqualification criteria

- No permitted source or explicit DNC/opt-out ambiguity.
- No named problem owner, no current trigger, or no relevant U.S. ocean D&D exposure.
- No lawful and secure evidence path.
- Requested outcome requires guaranteed recovery, unapproved legal advice, or unsupported claim.
- Product/data or reviewer capacity is unavailable.
- Economics, authority, geography, carrier/port coverage, or data rights are outside approved scope.

## Learning rule

Do not promote a persona or segment from hypothesis to validated until cohort evidence covers response, meeting, valid submission, opportunity, outcome, cycle time, and loss reasons.
