# SheperD Website Product Contract

Status: Preview-safe specification
Date: 2026-07-15
Production publication: Blocked

## Product boundary

The current deliverable is a no-collection, noindex Preview used to verify information architecture, design, motion, accessibility, and engineering. It is not a lead-generation surface and must not imply that product capabilities, commercial terms, outcomes, customer proof, entity details, or intake controls are approved.

Production content remains blocked until every exact sentence and destination passes the claims register and human approval workflow.

## Truth hierarchy

Public content must resolve in this order:

1. Exact approved claim-register row for the intended channel.
2. Current primary government source admitted as `educational-primary-source`.
3. Neutral interface copy that makes no company, product, commercial, legal, or outcome claim.
4. Suppression.

Company-controlled statements, internal proposals, observations, inference, mixed evidence, unresolved evidence, expired sources, and roadmap language never fall through into public copy.

Controlling sources:

- `01_Company/Claims and Evidence Register.md`
- `03_GTM/Website and Content Audit.md`
- `04_Operations/Customer Data Intake and Security.md`
- `05_AI/Human Approval Policy.md`
- `10_Sources/Source - 46 CFR Part 541.md`
- `10_Sources/Source - 46 USC 41301.md`
- `10_Sources/Source - FMC Charge Complaint Guidance.md`

## Runtime modes

| Contract | Preview | Production |
|---|---|---|
| Indexing | `noindex`, `nofollow`, `noarchive`, and crawler disallow | Blocked until canonical URL and indexing approval |
| Data collection | None | Blocked until privacy, security, consent, retention, and intake approval |
| Forms and uploads | Absent | Blocked |
| Analytics and third parties | Absent | Blocked until privacy approval |
| Company positioning | Suppressed | Exact approved copy required |
| Product capability | Suppressed | Demonstrated and approved capability rows required |
| Commercial terms | Suppressed | Approved fee and contract language required |
| Contact CTA | Suppressed | Approved destination and owner required |
| Educational context | Only current source-gated entries | Same gate, with channel approval |
| Legal pages | Preview no-collection notice only | Approved privacy notice and terms required |

`noindex` is not access control. Preview protection must be decided separately before deployment.

## Audience and visitor questions

Primary audience: finance, supply-chain, logistics, operations, and review stakeholders at U.S. importers.

The page must answer, in order:

1. Who the educational material is for.
2. Why a D&D invoice review may require more than the invoice alone.
3. Which records may matter.
4. How a case-specific review path may progress.
5. Why current rules and source dates matter.
6. What the Preview does not determine or collect.
7. Where a visitor can read the primary sources.

The required question, "What can SheperD truthfully do today?", has no publication-safe answer yet. Preview must suppress the capability section entirely. Do not replace it with roadmap, "coming soon," or implied product UI.

## Preview page contract

### Header

- Plain text `SheperD` project wordmark.
- Essential anchors only: Requirements, Process, Sources, Limits.
- One CTA label: `Review requirements`.
- No entity suffix, founder reference, customer count, status dot, or contact link.

### Hero and Container Hero

Purpose: establish audience, educational problem, and the evidence-alignment idea without a company capability claim.

Approved neutral UI copy:

- Audience line: `For importer finance and logistics teams`
- H1: `Start with the record.`
- Support: `Reviewing a D&D invoice may require billing facts, operational evidence, governing terms, and current rules.`
- CTA: `Review requirements`

The support sentence may render only through the `EDU-EVIDENCE-001` registry entry. The CTA targets an on-page section and never opens a form.

### Problem anatomy and Invoice Manifest

Show three evidence classes as a semantic list:

- Billing facts
- Operational facts
- Governing terms and current rules

Rows may show relationships, but cannot label any charge compliant, invalid, eligible, recoverable, or unlawful.

### Review requirements and Evidence Stack

Show generic document categories derived from current FMC guidance. Do not simulate a customer file, upload, portal, audit result, or evidence pack.

Permitted categories after `EDU-EVIDENCE-001` passes:

- Invoice and bill of lading
- Payment record
- Free-time, tariff, or contract terms
- Availability, pickup, return, and terminal timing
- Appointment, hold, closure, and communication records

### Process and Recovery Route

Use a visibly conditional educational path:

`Collect records -> check completeness -> compare applicable facts and rules -> select an appropriate review route -> obtain human review -> record the outcome`

This is not a SheperD workflow claim. Do not say that SheperD performs, automates, files, tracks, or completes any step.

### Regulatory context

Render only the exact registry entries in the educational matrix below. Every entry needs a source URL, checked date, expiry date, approved channel, and approver before use.

Do not render market-size figures, charge totals, complaint totals, recovery figures, percentages, customer outcomes, or comparative claims in Preview.

### Limits

Required neutral copy:

- `Educational context only. This Preview does not provide legal advice or determine whether a charge is recoverable.`
- `This Preview does not collect invoices, shipment records, contact details, or personal information.`
- `Outcomes depend on the applicable rules, route, deadlines, records, and case facts.`

The first and third lines require current educational source entries. The no-collection line is a verified application behavior and must be covered by an automated network and form-absence test.

### Sources

List source title, issuing body, checked date, and direct official URL. Links must open safely and must not be framed as endorsement of SheperD.

Final action: `Open FMC guidance`. This is a distinct external-source intent, not a contact or intake CTA.

### Footer

- Plain text wordmark only.
- `Preview only. No information is collected.`
- Privacy and Terms links to Preview notices.
- No address, email, phone, social account, founder, legal entity, copyright entity, or claim language until approved.

## Educational content matrix

These are candidate exact texts, not automatic publication approval. The content registry must fail the build unless every required field is complete and the entry state is `educational-primary-source`.

| ID | Candidate exact text | Primary source | Required expiry |
|---|---|---|---|
| `EDU-EVIDENCE-001` | Reviewing a D&D invoice may require billing facts, operational evidence, governing terms, and current rules. | FMC Charge Complaint Guidance; current 46 CFR Part 541 | No later than 2026-08-15 |
| `EDU-541-001` | Current 46 CFR Part 541 contains invoice content, issuance timing, and dispute-process requirements. | Current 46 CFR Part 541 | No later than 2026-08-15 |
| `EDU-41301-001` | The three-year period in 46 U.S.C. 41301 is a complaint limitation, not blanket refund eligibility. | 46 U.S.C. 41301 | No later than 2026-08-15 |
| `EDU-FMC-001` | FMC investigations do not represent the complainant and do not guarantee a refund. | FMC Charge Complaint Guidance | No later than 2026-08-15 |
| `EDU-CASE-001` | Outcomes depend on the applicable rules, route, deadlines, records, and case facts. | Current 46 CFR Part 541; 46 U.S.C. 41301; FMC Charge Complaint Guidance | No later than 2026-08-15 |

Before rendering, a named domain or legal reviewer must approve the exact wording and channel. If an entry expires, disappears, conflicts with current law, or lacks approval, suppress its entire dependent block.

## Public content matrix

| Content | Preview behavior | Production requirement |
|---|---|---|
| `SheperD` wordmark | Allowed as project label | Brand and entity approval |
| Audience marker | Neutral UI copy | Content approval |
| Educational requirements | Source-gated | Current source and reviewer approval |
| Company description | Suppress | `approved-company-description` entry |
| Current service or MVP | Suppress | Demonstration plus exact approved entry |
| Portal, automation, or AI | Suppress | Demonstration plus exact approved entry |
| Free audit, fee, pricing | Suppress | Approved commercial terms |
| Recovery or eligibility | Suppress | Approved methodology, evidence, and reviewer |
| Customers, logos, quotes, cases | Suppress | Permission plus exact approved evidence |
| Team, founder, entity, address | Suppress | Verified source plus publication approval |
| Contact or intake | Suppress | Approved owner, destination, privacy, and security flow |
| Privacy and terms | Preview notice only | Counsel-approved documents |
| Structured data | None beyond safe page metadata | Verified organization facts only |

## FAQ contract

Preview may answer only these questions:

1. `Does this Preview accept invoices?` Answer from tested application behavior: no.
2. `Does a billing issue guarantee recovery?` Answer through `EDU-FMC-001` and `EDU-CASE-001`: no.
3. `Does the three-year period make every prior invoice refundable?` Answer through `EDU-41301-001`: no.
4. `Where can I verify the rules?` Link only to current official sources in the registry.

Do not answer case eligibility, likely value, timing, success rate, fee, product availability, security controls, or legal interpretation.

## Content implementation contract

Every factual public sentence must come from a typed registry entry with:

```text
claimId
exactText
evidenceStatus
sourceIds
sourceUrls
checkedDate
expiresOn
approvedFor
approvedBy
approvalDate
notes
```

Neutral navigation labels and interaction instructions live in a separate typed UI-copy object. They cannot contain numbers, company capability, commercial language, legal conclusions, or outcome language.

Rendering rules:

- Components receive approved content objects, never freehand claim strings.
- A missing or unsafe registry entry removes the whole dependent block.
- Production mode fails at build time if any required production field is unresolved.
- Preview mode fails if any form, upload, analytics, third-party runtime, contact destination, or indexable metadata appears.
- Validation reports IDs and file locations, never sensitive content.

## Route contract

| Route | Preview content | Production gate |
|---|---|---|
| `/` | Neutral education and source links | Approved positioning, capability, proof, and CTA |
| `/privacy` | No-collection Preview notice | Approved privacy notice |
| `/terms` | Preview limitation notice | Approved terms |
| `robots.txt` | Disallow and noindex support | Approved indexing policy |
| `sitemap.xml` | Omit Preview routes | Approved canonical production URL |

No additional public route may be added without a content-owner and claim-registry review.

## Accessibility and resilience acceptance

- Semantic content is complete in server HTML and without JavaScript.
- One H1, logical headings, landmarks, skip link, descriptive source links, and visible focus.
- Disclosures use buttons with `aria-expanded` and persistent headings.
- No interaction depends on hover, color, animation, or pointer precision.
- At 320px and 200% zoom, content remains readable with no horizontal overflow.
- Reduced motion preserves every fact, source, action, and disclosure state.
- Empty, loading, expired, and failure states never invent replacement proof.

## Production blockers

Production promotion is blocked until all are supplied and approved:

- Exact company positioning and current product-state wording.
- Registered entity, contact, footer, privacy notice, and terms.
- Data-intake, security, retention, consent, and subprocessor controls.
- Commercial and fee wording.
- Approved contact destination and response owner.
- Claim-level evidence, source freshness, approvers, dates, and channel scope.
- Permissioned customer proof, or a deliberate decision to launch without it.
- Canonical URL, indexing, analytics, and structured-data policy.
- Rights-cleared photography or an approved visual plan without photography.
