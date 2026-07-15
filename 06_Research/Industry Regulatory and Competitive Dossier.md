---
title: Industry Regulatory and Competitive Dossier
type: research-dossier
status: complete-with-review-boundary
owner: Domain reviewer
updated: 2026-07-15
evidence_status: mixed
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/regulatory
  - sheperd/market
---

# Industry, Regulatory, and Competitive Dossier

> [!abstract] Decision answer
> U.S. D&D audit/recovery is a material, evidence-heavy process governed by invoice content, short timing rules, contracts/tariffs, operational facts, and route-specific procedures. Current primary sources support factual audit, deadline discipline, evidence assembly, and reviewed dispute support—not blanket refund claims, automated legal conclusions, or a recoverable-market percentage. Evidence status: `mixed`; confidence: high on current rules and low on addressable economics. Sources: SRC-002–003, SRC-006–012, SRC-019–022, SRC-030–038.

> [!warning] Boundary
> This dossier is operational research, not legal advice. Case eligibility, proper-party liability, accrual, applicability, reasonableness, route, remedy, filing, and settlement require the current rule, governing terms, facts, and named reviewer.

## D&D operating lifecycle

| Stage | Actors | Controlling inputs | Common failure | Safe optimization |
|---|---|---|---|---|
| Contract setup | BCO, VOCC, NVOCC, MTO, drayage | Effective tariff/contract, negotiated free time, liability basis | Wrong or stale version | Version checks and required-field controls |
| Arrival/release | VOCC, MTO, customs, NVOCC | Discharge, availability, freight/customs releases, holds, notices | Missing timestamp or dependency | Timeline extraction with source links |
| Terminal pickup | Terminal, drayage, consignee | Appointments, gate hours/closures, availability, transaction logs | Treating one operational event as dispositive | Evidence checklist and exception flag |
| Inland/return | Drayage, warehouse, equipment provider | Out-gate, unload, return instructions, rejection, in-gate | Portal instruction overwritten | Timestamped capture and change alert |
| Invoice audit | Billing party, AP | §541.6 fields, issuance date, rates, arithmetic, certifications | Wrong dates/rate tier, duplicate, late invoice | Deterministic checks; human legal boundary |
| Direct dispute | Billed party, auditor | Evidence chronology, governing deadline, submission, correspondence | Missed deadline or incomplete proof | Deadline alert and reviewed packet draft |
| Escalation | Counsel, FMC, domain reviewer | Accrual, payment, injury, route-specific package | Mixing enforcement and adjudicatory routes | Route checklist; human selection and filing |
| Close | Finance, auditor | Actual credit/refund/waiver/cancellation and reconciliation | Counting requested rather than realized value | Deterministic reconciliation; human approval |

Evidence status: `inference` grounded in current primary rules and operating requirements; confidence: medium-high. Sources: [[02_Domain/D&D and OSRA Primer]], SRC-002, SRC-021.

## Current Part 541 controls

Current eCFR displayed Title 46 current through 2026-07-13 and last amended 2026-06-30. Evidence status: `verified`; confidence: high. Source: [[10_Sources/Source - 46 CFR Part 541]].

| Rule | Current operational meaning | Automation boundary |
|---|---|---|
| §541.4 | Reserved after the 2025 court decision and ministerial removal | Do not encode the vacated categorical billing-party rule |
| §541.5 | Missing required minimum information eliminates obligation to pay the applicable invoice | Deterministic completeness check; reviewer handles reissue/applicability |
| §541.6 | Requires identifying, timing, rate/governing-term, dispute, liability-basis, and certification information | Extract and compare fields; no legal conclusion |
| §541.7(a) | Carrier/MTO billing generally within 30 days after the charge was last incurred | Date arithmetic and alert |
| §541.7(b) | NVOCC billing generally within 30 days after the **issuance date** of the invoice it received | Date arithmetic; CCR-001 corrected prior receipt-date summary |
| §541.7(c) | Specified notice by an NVOCC in both roles triggers an additional 30-day dispute window | Rule trigger and alert; human confirms facts |
| §541.7(d) | Wrong-person correction must still issue within 30 days after the charge was last incurred | Date check; human liability review |
| §541.8 | At least 30 days after invoice issuance to request mitigation/refund/waiver; billing party attempts resolution within 30 days after receipt unless mutually extended | Timers and reminders; no autonomous send or outcome decision |

A nonconforming invoice is not necessarily permanently extinguished: a compliant invoice may be reissued if the timing rule still allows it. Evidence status: `verified`; confidence: high. Source: SRC-002. Case application remains human-only.

## §541.4 change

The D.C. Circuit set aside only §541.4 on 2025-09-23; the FMC removed it effective 2025-12-29; current eCFR reserves it. Evidence status: `verified`; confidence: high. Sources: [[10_Sources/Source - World Shipping Council Part 541 Opinion - 2026-07-15]], [[10_Sources/Source - Part 541 Section 541.4 Removal - 2026-07-15]], SRC-007.

Current guidance must not state that only a contracting party or consignee may be invoiced. Proper-party liability is case-specific, while §541.6 still requires the invoice to state its liability basis.

## Complaint and recovery routes

| Route | Scope | Key boundary | Human owner |
|---|---|---|---|
| Direct billing-party request | Mitigation, refund, waiver, correction, evidence exchange | Contract/tariff deadlines and facts vary | Customer/authorized representative + reviewer |
| FMC Charge Complaint | Potentially non-compliant common-carrier charge under §41310 | Enforcement intake, not representation or refund guarantee; current procedure interim | Authorized submitter + domain/legal review |
| Formal complaint | Adjudicatory route | Pleading, accrual, injury, remedy, evidence, and procedure case-specific | Counsel/domain reviewer |
| Small claim | Adjudicatory route for appropriate disputes | Separate procedure; do not combine with Charge Complaint | Counsel/domain reviewer |
| CADRS/assistance | Informal dispute-resolution assistance | Not a substitute for deadlines or adjudication | Human case owner |

Current interim Charge Complaint guidance generally excludes pre-2022-06-16 charges, MTO-only charges not assessed on behalf of a carrier, charges not yet invoiced, transactions outside the described U.S. import/export nexus, and non-charge conduct. An unsuccessful Charge Complaint does not itself bar later formal or small-claim filing. Evidence status: `verified`; confidence: high. Source: [[10_Sources/Source - 46 USC 41310 and FMC Complaint Routes - 2026-07-15]].

## Three-year limitation

46 U.S.C. §41301 permits a reparations request when the complaint is filed within three years after the claim accrues. It is a limitation, not blanket eligibility or a guarantee for every prior-36-month invoice. Evidence status: `verified`; confidence: high. Source: [[10_Sources/Source - 46 USC 41301]].

Keep separate:

1. Contract/carrier dispute deadline.
2. Part 541 invoice and dispute timing.
3. Charge Complaint scope.
4. Formal/small-claim limitation and remedy.
5. OSRA applicability and non-retroactivity.
6. Contract, tariff, facts, causation, payment, injury, and evidence.

## Evergreen freight-fluidity decision

The D.C. Circuit opinion is dated 2026-04-28; the FMC report is dated 2026-07-08. It upheld a fact-specific conclusion that detention during closed gates did not promote freight fluidity where earlier return was impossible. It did not create a blanket closure, weekend, or once-on-detention rule. Evidence status: `verified`; confidence: high. Sources: SRC-038, [[10_Sources/Source - Evergreen 2026 Decision]].

## Market evidence and its limits

| Measure | Population and period | Safe conclusion | Unsafe leap |
|---|---|---|---|
| About $15.4B collected | Nine named carriers; 2020-04-01 through 2025-03-31 | D&D spend is material in the reported population | Invalid, unlawful, disputable, recoverable, or obtainable share |
| About $8.9B billed / $6.9B collected | Different two-year 2020–2022 rulemaking population/window | Historical billing/collection context | Combine with the five-year dataset as a recovery rate |
| 296 complaints; 164 accepted; $2,893,937.98 FY2025 relief; >$6.1M cumulative | FMC Charge Complaints | The route generates real measured relief | Total direct disputes, vendor outcomes, TAM, or recovery percentage |

Evidence status: `verified`; confidence: high on reported values and high that the limitations apply. Sources: [[10_Sources/Source - FMC D&D Data]], [[10_Sources/Source - FMC FY2025 Annual Report - 2026-07-15]].

No authoritative buyer count, invalid-charge share, recoverable share, SheperD-obtainable recovery, or unit economics was found. These remain `unknown`. Confidence: high after source-stop rules.

## Buyers and economics

The beachhead remains a hypothesis: U.S.-importing BCOs with recurring D&D spend, centralized finance ownership, accessible invoice and event evidence, concentrated carrier/port exposure, and a named operations/data owner. Evidence status: `inference`; confidence: low until CRM cohorts and delivery economics exist. Source: [[03_GTM/ICP and Stakeholder Personas]].

Buying group:

- Finance: realized cash/credit, auditability, net economics, timing, workload.
- Supply chain/logistics: operational causation, carrier relationships, repeat exposure.
- AP/operations/data: checklist, secure intake, rework, status, ownership.
- Legal/procurement/security: authority, data processing, claims, liability, terms.
- Partners: client trust, attribution, account ownership, quality, economics.

Timing tailwinds include auditable invoice fields, short deadlines, operational-evidence relevance, material collections, and an established complaint path. Constraints include proof/security gaps, case specificity, buyer data friction, delivery capacity, and stale public regulatory content. Evidence status: `inference`; confidence: medium. Tailwind is not market-size proof.

## Competitor matrix

Every row is vendor-controlled `company-claim`; confidence is medium on displayed positioning and low on performance. Sources: [[10_Sources/Source - Competitor Websites - 2026-07-15]], SRC-030–037.

| Vendor | Buyer/category | Public offer | Pricing signal | Technology/proof signal | Limitation |
|---|---|---|---|---|---|
| BlueCargo | BCOs, forwarders, drayage; audit/prevention/disputes | Freight audit and D&D/per-diem workflow | Free tier; Pro from $18,126/year; enterprise custom | Vendor outcomes | OSRA FAQ repeats vacated §541.4 and receipt-date NVOCC rule |
| Unwaived | BCOs, NVOCCs, 3PLs, audit/pay | Recovery-as-a-service | Same page conflicts between 20% and 25–35% | Evidence packets, filing, credit tracking | Public pilot snapshot shows zero invoices/recovery |
| HarborClaim | Importers/finance/logistics | Review, packets, follow-up | Free review; typical 30% recovered value | No named outcomes observed | Performance unverified |
| AuditDray | D&D invoice operators | AI audit and dispute generation | First three months free; later share undisclosed | High recovery/performance figures | Unsupported and page metrics inconsistent |
| MiraLedger | Importers/logistics | Tariff audit, dispute packs, recovery/prevention queue | Pilot/volume plans; quote | Unnamed pilots; legal language | Maturity/outcomes unverified |
| Intelligent Audit | Enterprise shippers | Broad multimodal freight audit | Enterprise quote | Anonymized 24% reduction case | Audit-point counts vary; D&D is one accessorial |
| GoComet | Global-trade teams | Visibility, procurement, tracking, D&D prevention | Basic tracker free; advanced quote | Broad supply-chain outcomes | Prevention alternative, not recovery validation |

SheperD must prove—not merely claim—better comparable recovery, faster evidence-to-dispute and dispute-to-credit cycles, lower customer workload, accepted audit trail, secure intake, carrier/port depth, and net economics.

## Advertising substantiation

Objective recovery, error-rate, automation, turnaround, customer-outcome, and market claims require reasonable support before dissemination. Evidence status: `verified`; confidence: high. Source: [[10_Sources/Source - FTC Advertising Substantiation]]. Legal review determines the evidence needed for each exact sentence and channel.

## Human versus automation boundary

Safe assistance: structured extraction, invoice-field completeness, date arithmetic, duplicate/rate comparison, cited timeline construction, deadline alerts, reviewed packet drafting, and credit reconciliation.

Human-only: proper-party liability, governing-term interpretation, accrual, applicability, reasonableness/unlawfulness, causation, recovery value/probability, route selection, filing, settlement, external sending, and final outcome classification.

Evidence status: `policy`; confidence: high. Sources: [[05_AI/Human Approval Policy]], SRC-002, SRC-021.

## Related

[[06_Research/SheperD Deep Research - Control Note]] · [[06_Research/AI Opportunity Register]] · [[06_Research/Research Gaps and Interview Guide]]
