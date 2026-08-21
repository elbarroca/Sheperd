---
title: Vault Operating Manual
type: system
status: active
owner: Michael
updated: 2026-07-15
evidence_status: policy
confidentiality: internal
tags:
  - sheperd/system
---

# Vault Operating Manual

## Purpose

This vault stores approved company knowledge, strategy, de-identified learning, operating playbooks, and source evidence. It does not replace the CRM, secure file storage, contract repository, or case-management system.

## System of record

| Information | System of record |
|---|---|
| Accounts, contacts, activities, opportunities, partners | CRM |
| Invoices, shipment records, evidence, contracts, PII | Approved secure storage or case system |
| Company truth, approved claims, strategy, playbooks | This vault |
| Website analytics and campaign events | Analytics platform |
| Final legal or regulatory advice | Named qualified reviewer and approved repository |

## Note contract

Every durable note should contain:

1. YAML properties: `type`, `status`, `owner`, `updated`, `evidence_status`, `confidentiality`, and tags.
2. A short answer or purpose near the top.
3. Facts separated from claims, inferences, and open questions.
4. External sources or links to atomic notes in `10_Sources/`.
5. Related wikilinks rather than duplicated paragraphs.

## Evidence states

`status` describes the note lifecycle. `evidence_status` describes the authority of its contents and must use one of these values:

- `verified`: supported by a current primary or authoritative source.
- `company-claim`: stated in company-controlled material but not independently verified.
- `internal-proposal`: proposed internally; not yet a decision.
- `internal-observation`: observed internally or in a dated audit; not automatically publication-safe.
- `internal-data`: measured in an approved internal system with method and period recorded.
- `internal-decision`: explicitly approved by its accountable owner for the recorded scope.
- `inference`: reasoned synthesis that must remain labeled.
- `unverified`: insufficient evidence.
- `mixed`: the note intentionally combines evidence states or unresolved source tension.
- `policy`: a controlling internal rule, not an external fact.

`contradicted` and `approved` belong on individual claim-register rows, with scope and dates, rather than as note-level `evidence_status` values.

## Update rules

- Change the canonical note first, then update links—not copied summaries.
- Date every source check and decision.
- Never silently upgrade a claim from `company-claim` to `verified`.
- Record meaningful changes in [[04_Operations/Risk, Assumption and Decision Register]].
- Move obsolete notes to `99_Archive/`; do not erase decision history.
- Review regulatory sources before external use if the source check is older than 30 days.

## Privacy rule

Do not place customer names, personal contact details, invoice data, shipment identifiers, contracts, call transcripts without consent, or recovery evidence in this vault. Store only de-identified insight and CRM record links.

## Start-of-day load order

1. [[SheperD HQ]]
2. Relevant workstream note in `04_Operations/Workstreams/`
3. Canonical topic note
4. [[01_Company/Claims and Evidence Register]] when drafting external language
5. The smallest necessary source note set
