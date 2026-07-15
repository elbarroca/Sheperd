---
title: SheperD Content and Distribution System
type: gtmsystem
status: draft-blocked
owner: Michael
updated: 2026-07-15
evidence_status: internal-proposal
confidentiality: internal
tags:
  - sheperd/gtm
  - sheperd/content
  - sheperd/distribution
---

# SheperD Content and Distribution System

> [!danger] Publication boundary
> `DRAFT - HUMAN REVIEW REQUIRED`. This note designs content; it authorizes no publishing, sending, lead capture, analytics deployment, or customer proof. Every external sentence requires exact claim IDs, channel approval, date, expiry, and rollback owner.

## Messaging architecture

| Layer | Controlled direction | Source of truth |
|---|---|---|
| Category | Contingency-based D&D invoice audit and recovery service | [[01_Company/Company Brief]] |
| Buyer | Finance-led U.S. importer/BCO hypothesis with logistics, data, legal, procurement, and security stakeholders | [[03_GTM/ICP and Stakeholder Personas]] |
| Problem | Fragmented invoice, timing, rate, event, and dispute evidence; short review windows; unclear ownership | C-023/C-025 plus buyer hypothesis |
| Offer | Evidence readiness → invoice readiness → reviewed audit → recovery support → future prevention | [[03_GTM/Sales and Objection Playbook#Offer ladder — gated]] |
| Proof | Only approved, permission-controlled, comparable evidence | [[01_Company/Claims and Evidence Register]] |
| Limitation | Case-specific; no refund or recovery promise before review | C-025/C-028 |
| CTA | Evidence-readiness concept before any dollar estimate or file submission | C-027; currently gated |

## Website information architecture — requirements only

1. **Home:** bounded category, buyer, problem, process, limitation, one approved CTA.
2. **How it works:** what is reviewed, what is needed, what the customer receives, current/manual/MVP/roadmap split.
3. **Evidence readiness:** metadata-only checklist; no recovery calculator.
4. **Security and data:** entity, system boundary, subprocessors, access, retention/deletion, incidents, customer requests.
5. **Proof:** only permission-controlled cases with method, population, period, exclusions, recovery form, and reviewer.
6. **Resources:** current-rule explainers with source, checked date, reviewer, expiry, and correction history.
7. **FAQ:** case specificity, timing, routes, evidence, fees, cash/credit, rejection, privacy, workload, and limits.
8. **Legal:** privacy, terms, entity/contact consistency, accessibility, and approved notices.

Implementation remains controlled by [[03_GTM/Website and Content Audit]] and the website publication gate.

## Sales-deck outline

| Slide | Decision purpose | Required claim/evidence |
|---|---|---|
| 1 | Category and audience | C-024/C-026, approved wording |
| 2 | Workflow problem | C-023/C-025 plus labeled buyer hypothesis |
| 3 | Current service truth | Product demonstration and truth table |
| 4 | Evidence-readiness workflow | C-027 plus approved checklist |
| 5 | Human and regulatory boundaries | C-025/C-028 and named reviewer |
| 6 | Security/data flow | Approved privacy/security pack |
| 7 | Commercial model | C-003/C-026 plus approved contract terms |
| 8 | Proof | Permission-controlled comparable outcomes only |
| 9 | Fit/disqualification | [[03_GTM/ICP and Stakeholder Personas]] |
| 10 | Next step | Approved CTA and secure path |

## FAQ structure

- What are demurrage and detention, and which facts control a review? C-023/C-025.
- What does SheperD do today versus manually, in an MVP, or on the roadmap? C-005/C-006/C-015/C-021 plus product truth.
- What information is needed first? C-027 plus approved checklist.
- Does every invoice qualify, and is recovery guaranteed? C-025/C-028.
- What does “recovered” mean for cash, credit, waiver, or cancellation? Blocked pending commercial evidence.
- Who may submit, dispute, file, or settle? Blocked pending authority and route review.
- How is data secured, retained, and deleted? Blocked pending privacy/security evidence.
- How does the fee work? C-003/C-026 plus approved contract terms.

## Founder-led content system

One source-backed idea becomes one reviewed source note, then at most:

1. One long-form explainer.
2. One short founder post.
3. One FAQ answer.
4. One sales enablement card.
5. One partner briefing excerpt.

Each child asset inherits the source, claim IDs, reviewer, approval scope, expiry, and rollback link. Repackaging never upgrades evidence.

## Educational pillars

| Pillar | Safe question | Primary source | Unsafe leap |
|---|---|---|---|
| Invoice readiness | What information should a D&D invoice contain? | Current Part 541, SRC-002 | Declaring a specific invoice invalid |
| Evidence chronology | Which timestamps and records may matter? | SRC-039 plus reviewed process | Automatic eligibility or blame |
| Dispute routes | How do direct, Charge Complaint, formal/small claim, and assistance routes differ? | SRC-021 | Legal advice or filing authority |
| Finance reconciliation | How should requested and realized cash/credit/waiver/cancel outcomes be separated? | Internal proposed KPI contract | Implied recovery rate |
| Intake readiness | Which owners, approvals, and metadata are needed before secure transfer? | [[04_Operations/Customer Data Intake and Security]] | Asking for D3 before approval |
| Prevention versus recovery | When should teams track, audit-before-pay, dispute, or outsource? | SRC-042; category comparison | Superiority or ROI claim |

## Lead magnet — evidence-readiness pack

Replace the unsupported dollar-recovery calculator with a non-economic pack containing:

- owner and authority map;
- invoice-field checklist;
- operational-evidence inventory;
- dispute-route questions for a reviewer;
- secure-transfer readiness checklist;
- requested/realized outcome reconciliation fields;
- missing-evidence action plan.

The pack must not score eligibility, estimate recovery, accept files, or give legal advice. Activation requires C-027 approval, privacy review, analytics/consent review, and an accessible implementation.

## Partner enablement pack

- Fit and disqualification card.
- Permission and account-ownership checklist.
- Approved claim/message sheet with expiry.
- Referral intake and SLA template.
- Secure-data boundary.
- Permitted stage-update matrix.
- Escalation, stop, and capacity rule.

Commercial terms and customer-data sharing remain absent until approved.

## Draft message families

### Email — evidence-readiness

`DRAFT - HUMAN REVIEW REQUIRED`

Subject: `D&D evidence-readiness question`

Body direction: state the permitted trigger fact; ask who owns invoice review and operational evidence; offer a bounded evidence-readiness checklist; state that eligibility and value require case-specific review; request no invoices or sensitive files by email.

Claims: C-025/C-027/C-028. Personalization facts require their own sources. Send state: blocked.

### LinkedIn — educational

`DRAFT - HUMAN REVIEW REQUIRED`

Post direction: explain one current invoice or evidence requirement from the authoritative source; state the checked date and case-specific limitation; link to the source; do not mention SheperD outcomes or recovery estimates.

Claims: C-023/C-025/C-028. Publish state: blocked.

### Partner — referral discovery

`DRAFT - HUMAN REVIEW REQUIRED`

Message direction: ask whether clients repeatedly face D&D invoice/evidence questions; state the proposed evidence-readiness scope and limitations; request no client identity or case data; propose a terms/permission discussion before any introduction.

Claims: C-025/C-027/C-028. Send state: blocked.

## Case-study admission gate

Required before drafting:

- written customer permission and channel scope;
- stable de-identified case/cohort IDs;
- exact population, period, sample, inclusion/exclusion, and comparator;
- requested versus realized cash/credit/waiver/cancellation;
- fee and net-value treatment;
- cycle time, effort, exceptions, and material confounders;
- product/data, finance, legal/privacy, domain, and Avi approval as applicable;
- expiry, withdrawal contact, and rollback location.

Absent any item: no case study, customer logo, quote, metric, or implied outcome.

## 12-week backlog — conditional, not a publishing calendar

| Week | Asset hypothesis | Primary question | Required evidence | Gate |
|---:|---|---|---|---|
| 1 | Invoice-readiness checklist | What must be present? | SRC-002 + reviewer | Claims/product |
| 2 | Evidence chronology explainer | Which records establish the timeline? | SRC-039 + reviewer | Claims |
| 3 | Route comparison | What are the escalation options? | SRC-021 | Domain/legal |
| 4 | Finance reconciliation worksheet | Cash, credit, waiver, cancellation? | Approved KPI/outcome definitions | Finance/commercial |
| 5 | Secure-intake explainer | What happens before files move? | Approved security pack | Privacy/security |
| 6 | Prevention versus recovery guide | Track, audit, dispute, or outsource? | SRC-042 + product truth | Claims/product |
| 7 | CFO FAQ | How are fee, effort, proof, and timing handled? | Approved commercial terms | Commercial/legal |
| 8 | Logistics FAQ | How are facts and carrier relationships handled? | Demonstrated workflow | Product/domain |
| 9 | AP/data checklist | How is submission friction reduced? | Approved intake checklist/SLA | Product/security |
| 10 | Partner briefing | What makes a safe referral? | Approved partner terms/SLA | Commercial/privacy |
| 11 | Product truth page | What is service, MVP, pilot, roadmap? | Founder demo/truth table | Product/Avi |
| 12 | Evidence-backed case format | What proof is publication-safe? | Admitted case and permission | Customer/legal/Avi |

If a gate remains blocked, keep the asset as an internal outline or replace the week with evidence remediation. Do not publish to satisfy cadence.

## Review, expiry, and rollback

1. Author records asset ID, version, channel, audience, exact sentences, claim IDs, sources, and data class.
2. Domain/legal reviews regulated meaning; product checks capability; privacy/security checks data; customer approves customer proof; Avi approves commercial release.
3. Publisher records approval IDs, date, expiry, canonical URL, analytics/consent state, and rollback owner.
4. Deterministic preflight blocks missing, stale, contradicted, or out-of-scope claims.
5. At expiry, source change, product change, complaint, incident, or evidence conflict: unpublish/withdraw, preserve the version and audit log, correct canonical truth, re-review before reuse.

## Measurement

Measure only after approval: asset/version, query/theme, source, channel, impression, qualified inquiry, valid-submission contribution, approval latency, correction, expiry, and rollback. Impressions are not qualified demand; inquiries are not validated opportunities; content does not establish PMF.

## Related

[[03_GTM/Website and Content Audit]] · [[03_GTM/Sales and Objection Playbook]] · [[01_Company/Claims and Evidence Register]] · [[05_AI/Human Approval Policy]]
