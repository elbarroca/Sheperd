---
title: SheperD GTM Validation and Optimization - Control Note
type: gtm-control
status: active-internal
owner: Michael
updated: 2026-07-15
evidence_status: mixed
confidentiality: internal
tags:
  - sheperd/gtm
  - sheperd/control
  - sheperd/validation
---

# SheperD GTM Validation and Optimization — Control Note

> [!abstract] Current answer
> The internal GTM design is decision-ready and founder-queryable; the market is not validated. SheperD remains **research-only / external activation blocked**. The system can prepare evidence, test deterministic controls on approved synthetic data, and record decisions. It cannot contact customers, publish, accept customer data, qualify, price, file, or execute externally.

## Current state and scores

Scores are internal planning assessments, not launch approval or market evidence.

| Dimension | Prior | Current | Reason for change | Promotion boundary |
|---|---:|---:|---|---|
| Research-system maturity | 9.1/10 | 9.3/10 | Current buyer/category/demand scan and source ledger added | Buyer interviews, CRM, product, and customer evidence remain absent |
| GTM system design | 7.2/10 | 9.2/10 | Control layer, positioning, operator kit, content system, experiment contract, measurement tables, and founder workspace now connect | Design quality does not prove a working motion |
| Real market evidence | 1.8/10 | 1.8/10 | No customer contact, cohort, CRM, willingness-to-pay, submission, outcome, or delivery evidence was authorized | Cannot increase from desk research or synthetic tests |
| Safe execution readiness | 2.5/10 | 3.3/10 | Actions, approvals, stop rules, structured data, and synthetic-only tests are specified | Authority, product truth, claims, security, commercial terms, and capacity remain blocked |

No “proven,” “repeatable,” “optimized,” “scalable,” “launch-ready,” or “PMF” wording is admissible.

## Decision-question register

| ID | Decision question | Required answer | Owner | Current state | Canonical truth |
|---|---|---|---|---|---|
| GQ-01 | Can SheperD and Michael act externally? | Entity, signatory, signed engagement, delegated authority | Avi + counsel + Michael | Blocked | [[06_Research/Company and Founder Dossier]] |
| GQ-02 | What can SheperD deliver today? | Demonstrated current service/MVP/pilot/roadmap truth table | Avi + product/data | Blocked | [[01_Company/Product and Business Model]] |
| GQ-03 | Which exact sentences may leave the company? | Claim ID, source/method, reviewer, channel, approval, expiry | Avi + domain/legal | Blocked | [[01_Company/Claims and Evidence Register]] |
| GQ-04 | Can any customer or CRM data be processed? | Approved privacy/security pack, tools, roles, retention, incidents | Product/security + legal/privacy | Blocked | [[04_Operations/Customer Data Intake and Security]] |
| GQ-05 | Which beachhead merits a controlled cohort? | Comparable segment/persona/channel/message evidence | Michael | Unknown; hypotheses only | [[03_GTM/ICP and Stakeholder Personas]] |
| GQ-06 | Which offer is supportable? | Demonstrated workflow, terms, reviewer, evidence, capacity | Avi + product/data + commercial/legal | Blocked | [[03_GTM/Sales and Objection Playbook]] |
| GQ-07 | Which channel produces qualified learning? | Separate warm/cold/partner/inbound cohorts and quality outcomes | Michael + channel owner | Unknown | [[03_GTM/Partner Strategy]] |
| GQ-08 | Where is the real bottleneck? | Stage, active time, wait, objections, missing loops, capacity | Michael + product/data | Unknown | [[04_Operations/Operating Cadence and KPI Dictionary]] |
| GQ-09 | Which automation is safe and useful? | Approved tool/data/permission plus synthetic baseline, quality, rollback | Workflow owner + risk approver | Design only | [[05_AI/AI Enablement Roadmap]] |
| GQ-10 | What should be funded or staffed next? | Four-week owner capacity plus admitted funnel/delivery evidence | Avi + Michael | Unknown | [[06_Research/Implementation Roadmap]] |

## Blocker-to-evidence matrix

The structured canonical register is `07_Founder_Operating_System/data/blockers.csv`.

| Gate | Blocker IDs | Required evidence | Decision owner | What remains blocked |
|---|---|---|---|---|
| Authority and ownership | GAP-001–003 | Entity/signatory pack, signed engagement, named RACI/backups | Avi + counsel | Representation, systems access, external work |
| Product and proof | GAP-004–005 | Live permitted demo, check catalog, product truth, permission-controlled case ledger | Avi + product/data | Capability, customer, and outcome claims |
| Commercial and domain | GAP-006–007 | Approved terms/recovery definition; named reviewer/route/SLA | Avi + commercial/legal + domain/legal | Pricing, route, filing, case language |
| Claims | GAP-008 | Sentence-level source, method, review, channel approval, expiry | Avi + domain/legal | Send and publish |
| Security and CRM | GAP-009–010 | DPA/privacy/security pack; approved CRM/source/permission/DNC controls | Product/security + legal/privacy + Michael | D2/D3 processing, outreach, intake |
| Capacity and public trust | GAP-011–012 | Measured throughput/SLA; privacy/truth repairs and independent review | Product/data + website/legal/privacy | New activation, inbound, scale |

Unknown evidence remains unknown. Three failed authoritative source attempts produce a diligence action, not a negative conclusion.

## Workflow views

### Prepare now

- Admit founder/entity/engagement/product/claims/security/commercial/capacity evidence.
- Run EXP-001 founder truth-and-gates workshop.
- Test EXP-002/003 only on approved synthetic records.
- Maintain canonical notes, claims, sources, templates, data schemas, and decision records.
- Query and visualize D0/D1/internal-proposal data in [[07_Founder_Operating_System/README|Founder Operating System]].
- Draft assets with `DRAFT - HUMAN REVIEW REQUIRED`; keep send/publish connectors absent.

### Approval required before execution

- CRM/list intake, account admission, outreach, discovery, follow-up, partner referral, inbound capture.
- Customer-data request/receipt, D2/D3 handling, product analysis, case action.
- Any public page, content, sales deck, case study, customer proof, or analytics deployment.
- Any AI/copilot pilot using approved D2; every action still requires its human gate.

### Out of scope / prohibited

- Autonomous send, publishing, qualification, stage decisions, data acceptance, pricing/contracts, recovery/eligibility decisions, filing, settlement, deletion/merge, hiring/funding, or irreversible mutation.
- Customer contact or data intake under this goal.
- D3 in AI or this vault.
- Numerical market, recovery, conversion, savings, ROI, readiness, or scale claims unsupported by admitted data.

## GTM artifact map

| Decision area | Canonical artifact | Structured/queryable view |
|---|---|---|
| Company/product truth | [[01_Company/Company Brief]] · [[01_Company/Product and Business Model]] | `source_ledger`, `blockers` |
| Claims | [[01_Company/Claims and Evidence Register]] | `source_ledger` |
| Market/buyer/competitors/demand | [[02_Domain/Market and Competitive Landscape]] · [[06_Research/Industry Regulatory and Competitive Dossier]] | `source_ledger` |
| ICP/personas/admission | [[03_GTM/ICP and Stakeholder Personas]] | `experiments` |
| Positioning/offers/sales | [[03_GTM/Sales and Objection Playbook]] | `artifact_manifest` |
| Channels/partners | [[03_GTM/Partner Strategy]] | `experiments` |
| Content/distribution | [[03_GTM/Content and Distribution System]] | `content_backlog` |
| Funnel/CRM | [[03_GTM/Customer Journey and Funnel]] · [[04_Operations/CRM Data Model]] | `workflows`, `measurements` |
| Experiments/metrics | [[03_GTM/16-Week Operating Plan]] · [[04_Operations/Operating Cadence and KPI Dictionary]] | `experiments`, `measurements` |
| AI/automation | [[05_AI/AI Enablement Roadmap]] · [[05_AI/Human Approval Policy]] | `ai_opportunities`, `time_savings` |
| Templates | [[90_Templates/GTM Operator Kit]] | `artifact_manifest` |
| Founder query/visualize/rank | [[07_Founder_Operating_System/README]] | All admitted CSV tables |

## Owners and approvals

| Area | Responsible owner | Accountable approval | SLA/state |
|---|---|---|---|
| GTM control, cohorts, CRM, reporting | Michael | Avi at formal gates; Michael for approved operating decisions | Authority not signed |
| Entity, engagement, contracts, pricing | Avi + counsel/commercial | Authorized signatory | Blocked |
| Product truth, intake acceptance, delivery capacity | Product/data owner | Avi + required specialist | Owner/evidence missing |
| Regulatory and claim meaning | Domain/legal reviewer | Reviewer + Avi for commercial use | Reviewer/SLA missing |
| Privacy, security, D2/D3 controls | Legal/privacy + product/security | Named risk owners | Owner/system evidence missing |
| Website/content implementation | Website/analytics owner + Michael requirements | Avi + claims/privacy approvers | Publishing blocked |
| Partner relationship | Named relationship owner | Avi + legal/commercial | Terms/capacity blocked |

No combined owner label is proof of accountability; named people and written authority are required.

## Experiment register

The structured canonical register is `07_Founder_Operating_System/data/experiments.csv`; [[90_Templates/Experiment]] controls every executed record.

| ID | Primary hypothesis | Cohort | State | Decision point |
|---|---|---|---|---|
| EXP-001 | One artifact-led workshop can resolve or precisely assign all P0 gates | Internal founder gate | Prepare now | Day 5 |
| EXP-002 | Deterministic claim prerequisites can block unsafe drafts | Synthetic claims | Synthetic only | Day 20 |
| EXP-003 | CRM provenance/permission/stage rules can be enforced without mutation | Synthetic CRM | Synthetic only | Day 20 |
| EXP-004 | Finance-led warm access produces complete discovery and a valid next step | Warm finance | External blocked | Week 6 |
| EXP-005 | Narrow cold finance research yields permission-safe directional evidence | Cold finance | External blocked | Week 6 |
| EXP-006 | Permissioned partners improve accepted referral and submission quality | Partner | External blocked | Week 12 |
| EXP-007 | Evidence-readiness content produces attributable qualified questions | Inbound | Publication blocked | Week 12 |
| EXP-008 | Metadata checklist reduces missing loops without eligibility decisions | Secure handoff | Security blocked | Day 50 |

No conversion target is invented. Warm, cold, partner, and inbound never share a denominator. A missing baseline converts the first run into a measurement cohort, not a lift test.

## Measurement register

The structured canonical register is `07_Founder_Operating_System/data/measurements.csv`.

| Decision family | Measurement IDs | Required decision use |
|---|---|---|
| Time, approvals, capacity | MT-001/002/014 | Separate active work, elapsed wait, owner caps, and stop/defer |
| CRM, source, funnel | MT-003–005 | Trust records, admit cohorts, locate stage bottleneck |
| Submission and product | MT-006/007 | Measure missing loops, throughput, quality, exception, SLA |
| Claims and assistance | MT-008–010 | Measure citation/correction, edit burden, alert precision/recall |
| Partner, outcomes, incidents | MT-011–013 | Decide channel quality, reconcile realized outcomes, stop on incident |

Every rate requires numerator, denominator, sample, period, cohort, version, and exclusions. Wait-time reduction is not labor savings. Small samples remain directional.

## Weekly decision cadence

| When | Evidence reviewed | Required output |
|---|---|---|
| Daily async | Blockers, owner, next action, new incident | Updated state; no silent unblock |
| Monday | One hypothesis, owner capacity, stopped/deferred work | One bounded priority |
| Wednesday | Claims, domain, product, security questions | Approval/rejection/incomplete decisions |
| Friday | Cohort events, stage movement, objections, wait, submission friction | Reconciled scorecard and blocker update |
| Biweekly | Equivalent-cohort evidence and confounders | Continue/change-one-variable/stop |
| Monthly | Authority, product, claims, security, capacity, incidents | Founder risk and investment decision |
| Weeks 2/6/12/16 | Formal gate pack | Explicit go/no-go or continue/change/stop |

No meeting without a decision owner, evidence link, due date, and stopped/deferred consequence counts as governance completion.

## Optimization contract

The founder workspace ranks experiments using user-visible planning weights for learning value, evidence readiness, lower risk, and lower effort. Inputs are internal-proposal scores; blocked work stays blocked regardless of rank. Ranking is prioritization—not causal optimization, expected ROI, conversion prediction, or authorization.

The learning loop is:

1. Admit cohort and message version.
2. Execute only after every gate passes.
3. Capture events, quality, time, wait, objections, friction, losses, and no-decisions.
4. Reconcile CRM and scorecard.
5. Change one variable.
6. Compare equivalent cohorts with sample and exclusions.
7. Record continue/change/stop.
8. Update the playbook only from admitted evidence.

## Risks and stop rules

- Missing authority, owner, permission, secure path, or approver: block execution.
- Missing baseline, cohort, sample, metric, comparator, or rollback: block experiment or label measurement-only.
- Missing product or claim evidence: label `unknown` or `company-claim`; withdraw unsupported wording.
- Any DNC/consent failure, sensitive-data exposure, unsupported material claim, unapproved external action, or material-record mutation: stop, preserve logs, assess, correct, and reauthorize.
- Product/data or reviewer capacity misses the approved SLA: stop new activation and data requests.
- Cohort mix changes or sample is small: no repeatability, optimization, or scale claim.
- Scope expands: name the work that stops or defers and obtain approval.
- Never weaken evidence, legal, privacy, math, accessibility, or security gates to finish.

## 30/60/90 conditional roadmap

- **30 days:** resolve GAP-001–012; finish authority/product/claims/security decisions; approve CRM/KPI contracts; test deterministic controls on synthetic records; record activation go/no-go.
- **60 days, only after go:** run one bounded warm cohort; instrument discovery/submission friction; pilot only approved CRM/reporting/meeting/knowledge assistance; hold continue/change/stop.
- **90 days, only after evidence:** run one comparable revised cohort; test one partner or inbound hypothesis; consolidate playbook v1; measure delivery/reviewer capacity; decide next-90 investment.

Detailed owners, dependencies, dates, rollbacks, and learning questions remain canonical in [[06_Research/Implementation Roadmap]].

## Highest-value next decision

Hold EXP-001: the founder truth-and-gates workshop. Admit or reject the exact evidence for GAP-001–012 and record one explicit activation `GO` or `NO-GO`. Until then, only internal preparation and synthetic deterministic checks may proceed.

## Verification state

The scoped founder workspace passed lint, typecheck, unit/HTTP tests, data/vault validation, report reconciliation, desktop interaction checks, 390 px responsive inspection, and a separate fail-closed P0/P1 rule pass. The reproducible record is [[07_Founder_Operating_System/QA_REPORT]]. Passing QA accepts the internal artifacts only; it does not change any activation gate.

## Related

[[SheperD HQ]] · [[06_Research/SheperD Deep Research - Control Note]] · [[06_Research/QA and Acceptance Report]] · [[07_Founder_Operating_System/README]] · [[07_Founder_Operating_System/QA_REPORT]]
