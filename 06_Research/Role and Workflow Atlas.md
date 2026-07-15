---
title: Role and Workflow Atlas
type: workflow-atlas
status: complete-with-blockers
owner: Michael
updated: 2026-07-15
evidence_status: mixed
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/workflow
---

# Role and Workflow Atlas

> [!abstract] Decision answer
> Michael's best-fit title remains **GTM & Revenue Operations Lead**, but the engagement is proposed—not activated. The atlas maps 45 stable workflows: **8 mapped internally, 25 blocked, 8 need an owner, and 4 are outside Michael's independent scope**. Every operating week, formal gate, workstream, CRM/funnel/KPI/content/partner/governance/AI responsibility, and specialist dependency is covered. Time, volume, wait, and exception baselines remain `unknown`. Source: `06_Research/data/workflows.csv`; evidence status: `mixed`; confidence: high on scope mapping and low on operating capacity.

## Role boundary

Michael owns, once authorized:

- Account, cohort, and partner segmentation.
- Controlled outreach, discovery, follow-up, and commercial learning.
- CRM architecture, hygiene, experiment identifiers, and reporting.
- Objection/playbook maintenance and website/content requirements.
- Weekly cadence, scorecards, gates, and capacity tradeoff visibility.

Michael does not independently own:

- Regulatory interpretation, case eligibility, dispute strategy, filing, or settlement.
- Product analysis, customer-data acceptance, recovery value/probability, or delivery SLA.
- Pricing, contracts, business-model approval, partner economics, hiring, or funding.
- Security/privacy decisions, D3 handling, website engineering, or all content production.

Evidence status: `inference` from the proposed engagement and [[03_GTM/Michael Role Charter]]; confidence: medium until signed terms exist.

## Coverage definitions

| State | Meaning |
|---|---|
| `mapped` | Structurally defined for internal research; not proof of external authority |
| `blocked` | A controlling authority, truth, claims, data, system, or capacity gate is open |
| `needs-owner` | Required accountable specialist, implementer, tool owner, or authority is unnamed |
| `out-of-scope` | Michael may support or receive status but must not own the decision/execution |

## RACI

| Area | Michael | Responsible owner | Accountable approver | Current state |
|---|---|---|---|---|
| Segments/cohorts | R | Michael | Michael; Avi for strategic criteria | Blocked |
| Partners/referrals | R | Michael/relationship owner | Avi + legal/commercial | Needs terms/owner |
| Outreach/discovery/follow-up | R | Michael | Michael; Avi for new claims/messages | Blocked |
| CRM/reporting | R | Michael | Avi for tool/resources; product/legal for handoffs | Needs tool/owner |
| Product truth | C | Avi + product/data | Avi | Needs owner/artifacts |
| Claims/regulatory language | C/draft support | Domain/legal reviewer | Reviewer + Avi | Blocked |
| Secure intake/data acceptance | C; metadata only | Product/security + legal/privacy + product/data | Named risk owners | Blocked |
| Analysis/recovery estimate | I/C | Product/data + reviewer | Methodology owner | Out-of-scope |
| Pricing/contracts | C | Avi + legal/commercial | Avi | Out-of-scope |
| Website requirements | R | Michael | Avi + claims/privacy approvers | Mapped internally |
| Website/privacy deployment | C | Website owner + legal/privacy | Avi | Needs owner |
| Content drafting/coordination | R | Michael | Avi + reviewer/customer as needed | Publishing blocked |
| Governance/scorecards | R | Michael | Avi | Mapped internally |
| AI design/pilots | R/C by workflow | Workflow owner | Avi + relevant risk owner | Inactive/blocked |
| Hiring/funding | Advisory | Avi | Avi | Out-of-scope |

`R` responsible, `C` consulted, `I` informed. No combined owner label is proof of accountability; `owner` and `accountable_approver` remain separate in the CSV.

## Responsibility-source dictionary

Every token in `workflows.csv#responsibility_source` resolves through this controlled dictionary. The referenced note is the scope source; it is not proof that the proposed engagement is active.

| Token | Canonical note | Relevant section or scope |
|---|---|---|
| `SRC` | [[10_Sources/Source - 16 Week Engagement Plan]] | Complete source capture |
| `PLAN` | [[03_GTM/16-Week Operating Plan]] | Week and gate crosswalk |
| `SCORE` | [[04_Operations/Weekly Scorecards/2026-07-13 - Activation Week]] | Current gate state |
| `Product note` | [[01_Company/Product and Business Model]] | Product truth and commercial model |
| `Claims register` | [[01_Company/Claims and Evidence Register]] | Claim states and publication gates |
| `CH` | [[03_GTM/Michael Role Charter]] | Role boundary and authority |
| `SEC` | [[04_Operations/Customer Data Intake and Security]] | Data intake and security gate |
| `WS1` | [[04_Operations/Workstreams/01 Domain Knowledge]] | Workstream 1 |
| `WS6` | [[04_Operations/Workstreams/06 Customer and Partner Segmentation]] | Workstream 6 |
| `FUN` | [[03_GTM/Customer Journey and Funnel]] | Funnel stages and case handoffs |
| `KPI` | [[04_Operations/Operating Cadence and KPI Dictionary]] | Event, KPI, and cadence definitions |
| `CRM` | [[04_Operations/CRM Data Model]] | CRM object and stage model |
| `ICP` | [[03_GTM/ICP and Stakeholder Personas]] | Account and stakeholder criteria |
| `PART` | [[03_GTM/Partner Strategy]] | Partner and referral responsibilities |
| `Playbook` | [[03_GTM/Sales and Objection Playbook]] | Discovery, objections, and follow-up |
| `WEB` | [[03_GTM/Website and Content Audit]] | Website, content, and analytics scope |
| `HAP` | [[05_AI/Human Approval Policy]] | Human-only and approval boundaries |
| `AI` | [[05_AI/AI Enablement Roadmap]] | AI permission and rollout boundary |
| `Risk register` | [[04_Operations/Risk, Assumption and Decision Register]] | Risks, assumptions, and decisions |
| `goal contract` | [[06_Goals/Goal 1 - Deep Intelligence and AI Operations]] | Research and AI-operations acceptance contract |

## Week and gate crosswalk

| Time | Workflows | Required outcome | State |
|---|---|---|---|
| Week 0 | WF-001–004 | Authority, product truth, claims, secure intake | Blocked |
| Week 1 | WF-002/005–008/011–018 | Immersion, domain, journey, baseline design, CRM/assets/digital planning | Internal work partly mapped |
| Week 2 | WF-009–019 | ICP/list/CRM/assets and explicit activation decision | Gate blocked |
| Week 3 | WF-020–022/030/032 | Cohort, warm introductions, reviewed outreach, CRM/reporting | Blocked |
| Week 4 | WF-023/030/032 | Discovery, qualification, objections, revision | Blocked |
| Week 5 | WF-022–029 | Outreach/partners/data request through downstream case handoff | Blocked; WF-026–029 outside role |
| Week 6 gate | WF-033 | Comparable warm-sprint continue/change/stop | Blocked |
| Week 7 | WF-031 | Sprint 1: one segment/persona/message/channel | Blocked |
| Week 8 | WF-031/032 | Review; change one variable | Blocked |
| Week 9 | WF-031/034 | Sprint 2; approved content only | Blocked |
| Week 10 | WF-024–026/032 | Funnel/partner/data-handoff review | Blocked |
| Week 11 | WF-031 | Sprint 3 | Blocked |
| Week 12 gate | WF-036 | Repeatability evidence and scale/learn/pivot | Blocked |
| Week 13 | WF-037 | Playbook/archetype audit | Future/blocked |
| Week 14 | WF-038/039 | One measured bottleneck test and quick win | Needs baseline/implementer |
| Week 15 | WF-040 | Conditional first-hire/onboarding proposal | Advisory only |
| Week 16 gate | WF-041 | Founder next-90 decision | Future/blocked |
| All weeks | WF-015/042–045 | Governance, AI approval, measurement, capacity change control | Internal/blocked by item |

Coverage check: Week 0 plus 16/16 operating weeks and 4/4 formal gates are mapped.

## Eight workstreams

Business importance and action priority are deliberately separate.

| Workstream | Business importance | Current action priority | Workflow IDs |
|---|---:|---:|---|
| 1 Domain Knowledge | 1 | 1 | WF-003/005/006 |
| 2 Value Proposition/Journey | 1 | 1 | WF-002/007/008/012/025/027–029/037/038 |
| 3 Technology/CRM | 1 | 1 | WF-004/008/013/026/030/032/035/039/043/044 |
| 4 Sales Assets | 2 | 2 | WF-014/034/037/040 |
| 5 Digital Presence | 1 | 2 | WF-016–018/034/035/039 |
| 6 Segmentation | 2 | 1 | WF-009–011/020/021/024/031 |
| 7 Governance | 1 | 1 | WF-001/015/019/033/036/040–045 |
| 8 Live Sales | 1 | 3 | WF-019/021–025/028/031 |

Coverage check: 8/8 workstreams are represented.

## End-to-end workflow groups

| Group | Workflow range | Human decision gate | Primary bottleneck |
|---|---|---|---|
| Safe start | WF-001–004 | Signatory, product, reviewer, security/privacy owners | Authority and named owners |
| Knowledge and truth | WF-005–008 | Founder/product/domain approval | Demonstrable product truth and current sources |
| Data/market foundation | WF-009–019 | List admission, CRM stages, content/claims, activation | Source provenance and gate completion |
| Controlled commercial execution | WF-020–025 | Cohort, send, qualification, data-request authority | External activation and secure path |
| Delivery and economics | WF-026–029 | Data acceptance, analysis, pricing, filing, outcome | Outside Michael; product/legal capacity |
| Learning system | WF-030–039 | Stage, sprint, content, repeatability, experiment/deploy | Comparable data and implementers |
| Scale/governance | WF-040–045 | Hiring, investment, AI, capacity decisions | Measured workload, owner capacity, authority |

The exact trigger, inputs, systems, ordered step classes, outputs, owners, approvers, failures, data class, dependencies, KPI, and measurement source for every workflow are in `06_Research/data/workflows.csv`.

## Funnel and submission bottleneck

```text
Sourced account
  → admitted/permission-safe
  → reviewed contact
  → held discovery
  → human qualification
  → accepted secure request
  → received pending validation
  → human-validated submission
  → human analysis/value decision
  → approved proposal/contract
  → authorized case action
  → realized cash/credit/waiver/cancellation
```

The likely bottleneck is the path from qualified meeting to secure, complete, product/data-valid submission, but this remains an `inference` until MP-03/MP-04 measure stage and wait time. Confidence: medium. Source: [[03_GTM/Customer Journey and Funnel]].

## Data classes and human gates

| Data | Workflow use | Boundary |
|---|---|---|
| D0 | Public research, approved claims | Source/state review still required |
| D1 | Internal non-sensitive plans, decisions, aggregates | No silent promotion to external fact |
| D2 | CRM contacts, activities, pipeline, permission | Approved enterprise controls only |
| D3 | Invoices, contracts, shipment/case/outcome data | Approved secure case system; disabled for AI |

Every ordered step has a stable `WF-XXX-SYY` ID and exactly one class: `human-only`, `ai-assisted`, or `deterministic-automation`. WF-043 is only a draft-only, human-reviewed test; no bounded-agent step is specified or approved.

## Failure and stop map

| Failure | Stop consequence |
|---|---|
| Written authority incomplete | No representation, outreach, systems access, or data handling |
| Product/claim truth unresolved | No product-capability or outcome claims |
| Permission or DNC unknown | No outreach |
| Secure data path or product capacity missing | No data request or intake |
| Reviewer absent or stale source | No regulatory statement or case advance |
| Comparable cohort/event definitions absent | No conversion/repeatability claim |
| Baseline/sample/caps absent | No final capacity or savings promotion |
| Scope expands without deferral | Record blocked change; Avi decides what stops |

## Measurement plans

| Plan | Workflows | Required capture | Decision |
|---|---|---|---|
| MP-01 Approval latency | WF-001–004/015/019/033/036/041/042 | Request/due/decision dates, owner, wait reason, rework | Governance bottleneck and SLA |
| MP-02 List admissibility | WF-009/010/020–022 | Received/admitted/duplicate/suppressed/permission/source/cohort | Reachable baseline |
| MP-03 Funnel transitions | WF-008/021–032/035/036 | Entry/exit, owner, reason, source, cohort, message, loss/no-decision | Stage conversion and wait |
| MP-04 Intake friction | WF-025–027 | Authority/request/receipt/validation, missing loops, active review, queue wait | Submission bottleneck/capacity |
| MP-05 Partner quality | WF-011/024 | Referral, acceptance, qualification, submission, outcome, attribution, cycle | Partner continuation |
| MP-06 Digital attribution | WF-016–018/034/035/039 | Approval/deploy, claim/permission/UTM, inquiry→submission | Qualified digital contribution |
| MP-07 CRM quality | WF-013/030/032 | Completeness, stale, correction, duplicate, formula reconciliation | Reporting trust |
| MP-08 Time study | All high-impact | ≥5 observations: actor, active/wait, exception/rework, context | Replace low/base/high assumptions |
| MP-09 AI pilot | WF-042/043 | Baseline/assisted/review, quality, false/missed, override, incident, rollback, cost | Continue/change/stop |
| MP-10 Capacity | WF-015/040–045 | Signed hours, allocation, dependency wait, deferred/stopped work | Scope and hiring tradeoff |

Wait and approval latency are service-level measures, not labor savings.

## Incompatible expectations and unsafe acceptance

Michael should not accept:

- “Work first, formalize later,” or accountability before signed authority.
- Deal, inbound, segment-validation, or scale outcomes without baseline, controllable inputs, delivery capacity, and agreed hours.
- Regulatory-expert, recovery-estimate, dispute-filing, product-analysis, or security-acceptance ownership.
- Website engineering, all content production, hiring, funding, or a fixed two-year CRM design.
- Unsourced lists, unknown permission, unsupported claims, or customer proof without consent.
- Additional parallel work without an explicit capacity tradeoff naming what stops or defers.

## Acceptance checks

- 45/45 IDs present and unique.
- 45/45 required fields populated; unknown measures remain `unknown`.
- 16/16 weeks, Week 0, 4/4 gates, and 8/8 workstreams mapped.
- Owner and accountable approver separated for 45/45 workflows.
- Role scope, business importance, action priority, data class, human decisions, KPI, and measurement source present.
- Product/data, domain/legal, security/privacy, website/analytics, and founder dependencies are explicit.
- No external activation, D3 AI, auto-send, publish, qualification, stage change, pricing, recovery judgment, filing, or irreversible action is authorized.

## Related

[[06_Research/AI Opportunity Register]] · [[06_Research/Time Savings Model]] · [[06_Research/Implementation Roadmap]]
