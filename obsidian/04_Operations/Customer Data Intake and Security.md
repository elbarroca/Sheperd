---
title: Customer Data Intake and Security
type: operations
status: proposed
owner: Product and legal owners
updated: 2026-07-15
evidence_status: policy
confidentiality: internal
tags:
  - sheperd/operations
  - sheperd/security
---

# Customer Data Intake and Security

## Purpose

Move prospects from interest to a valid analysis package without placing invoices, contracts, shipment records, credentials, or PII in email, Obsidian, or unapproved AI tools.

## Activation requirements

- Registered contracting entity and authorized signatory confirmed.
- Engagement terms, customer authorization, NDA/DPA, and privacy notice approved where required.
- Secure storage, region, encryption, identity, access, retention, deletion, and subprocessors documented.
- Product/data owner and response SLA assigned.
- Incident and customer-request process defined.

## Proposed flow

1. **Scope first:** collect non-sensitive volume, carrier/port, period, and problem metadata.
2. **Authority:** confirm who may release the data and what agreement is required.
3. **Secure request:** issue a named checklist and expiring least-privilege upload link.
4. **Receipt:** malware scan, checksum, access log, and case ID in the approved system.
5. **Validation:** product/data owner checks completeness; CRM stores status and secure case link only.
6. **Analysis:** permitted tools operate in the approved environment; exceptions route to a human.
7. **Result:** reviewed output separates invoice defect, factual/rate issue, reasonableness theory, confidence, and missing evidence.
8. **Close:** record customer outcome, apply retention schedule, revoke access, and delete when required.

## Minimum request metadata

- Requested period, carriers, ports, invoice count, and known charge types.
- Invoice, BOL, contract/tariff, free-time, availability/return, appointment, hold/closure, correspondence, and payment-evidence status.
- Customer authority and agreement state.
- Missing item, owner, and due date.
- Date requested, received, validated, completed, retained, and deleted.

## Access model

- Customer data is case-scoped and need-to-know.
- Michael can see commercial status; raw files require an explicit role.
- AI receives only the minimum permitted fields and never portal credentials.
- Downloads, sharing, and exports are logged and time-bounded.
- Departing users lose access immediately.

## Never store here

Customer names tied to case facts, contact details, invoices, BOL/container numbers, contracts, shipment events, credentials, raw transcripts, dispute packets, or recovery evidence.

## Human gates

- Legal/privacy approves the workflow and agreements.
- Product/data owner accepts completeness and analysis.
- Domain/legal reviewer approves case-specific regulatory language.
- Customer authorizes any case study or public result.

## Metrics

Time to authority, request acceptance, days to complete submission, missing-item count, review SLA, unauthorized-access events, deletion SLA, and customer security objections.

## Related

[[03_GTM/Customer Journey and Funnel]] · [[04_Operations/CRM Data Model]] · [[05_AI/Human Approval Policy]]
