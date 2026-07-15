---
title: SheperD Deep Research - Control Note
type: research-control
status: accepted
owner: Michael
updated: 2026-07-15
evidence_status: mixed
confidentiality: internal
tags:
  - sheperd/research
  - sheperd/control
---

# SheperD Deep Research — Control Note

> [!abstract] Current answer
> The evidence-controlled research package passed final QA with zero unresolved P0/P1 findings. The seven questions are answered to the admitted evidence frontier; every remaining unknown is mapped to an interview, evidence, decision, or measurement action. The vault remains **research-only / external activation blocked**. Acceptance does not approve outreach, publishing, customer-data intake, or AI execution.

## Controlling boundaries

- Current operating state: [[04_Operations/Weekly Scorecards/2026-07-13 - Activation Week]].
- Evidence contract: [[00_System/Vault Operating Manual]] and [[00_System/Knowledge Retrieval Contract]].
- Publication gate: [[01_Company/Claims and Evidence Register]].
- Human gate: [[05_AI/Human Approval Policy]].
- Unknown values remain `unknown`, never zero.
- Capacity results mean modeled capacity released, not guaranteed savings, headcount reduction, or revenue.

## Controlled evidence states

Use only: `verified`, `company-claim`, `internal-proposal`, `internal-observation`, `internal-data`, `internal-decision`, `inference`, `unverified`, `mixed`, and `policy`.

## Research-question register

| ID | Decision question | Required answer state | Primary artifact | Status |
|---|---|---|---|---|
| RQ-01 | What is SheperD, what is verified, and what remains claimed or unresolved? | Facts, claims, conflicts, unknowns | [[06_Research/Company and Founder Dossier]] | Accepted; blockers mapped |
| RQ-02 | Who is publicly presented as founding and operating it, and which diligence gaps matter? | Public professional evidence only | [[06_Research/Company and Founder Dossier]] | Accepted; blockers mapped |
| RQ-03 | How does the U.S. D&D audit/recovery market work? | Current primary-source rules, routes, buyers, competitors, economics, timing | [[06_Research/Industry Regulatory and Competitive Dossier]] | Accepted; blockers mapped |
| RQ-04 | What is Michael expected to own during 16 weeks, and what is blocked or unsafe to accept? | Complete responsibility crosswalk and ownership gaps | [[06_Research/Role and Workflow Atlas]] | Accepted; blockers mapped |
| RQ-05 | What are the workflows, costs, handoffs, gates, data classes, and bottlenecks? | Stable workflow IDs; unknowns explicit | [[06_Research/Role and Workflow Atlas]] | Accepted; blockers mapped |
| RQ-06 | What stays human-only versus assisted, deterministic, or bounded-agent? | One initial class per step; permission and rollback gates | [[06_Research/AI Opportunity Register]] | Accepted; blockers mapped |
| RQ-07 | What capacity can realistically be released, at what cost/risk, and in what order? | Reproducible low/base/high model without double counting | [[06_Research/Time Savings Model]] | Accepted; blockers mapped |

## Artifact manifest

| Artifact | Purpose | Acceptance state |
|---|---|---|
| `06_Research/SheperD Deep Research - Control Note.md` | Scope, questions, manifest, acceptance | Accepted |
| `06_Research/Company and Founder Dossier.md` | Company/founder diligence | Accepted |
| `06_Research/Industry Regulatory and Competitive Dossier.md` | Industry, rules, routes, market, competitors | Accepted |
| `06_Research/Role and Workflow Atlas.md` | Responsibility, RACI, workflows, bottlenecks | Accepted |
| `06_Research/AI Opportunity Register.md` | Automation classification and controls | Accepted |
| `06_Research/Time Savings Model.md` | Formula, scenarios, sensitivities | Accepted |
| `06_Research/Implementation Roadmap.md` | Now/next/later, 30/60/90, capacity tradeoffs | Accepted |
| `06_Research/Research Gaps and Interview Guide.md` | Prioritized unknowns and measurement actions | Accepted |
| `06_Research/data/source-ledger.csv` | Reproducible source ledger | Accepted |
| `06_Research/data/workflows.csv` | Stable workflow and step dataset | Accepted |
| `06_Research/data/ai-opportunities.csv` | Opportunity and control dataset | Accepted |
| `06_Research/data/time-savings.csv` | Scenario inputs and computed outputs | Accepted |
| `06_Research/QA and Acceptance Report.md` | Commands, results, findings, repairs | Accepted |
| `06_Research/SheperD Interactive Report.html` | Standalone offline decision report | Accepted |

Original contract check: the initial 14/14 artifacts passed at acceptance. Later authorized extensions, including [[06_Research/Market Evidence and Source Map]], are tracked in [[06_Research/QA and Acceptance Report]].

## Preflight record

| Check | Result | Evidence state |
|---|---|---|
| Current date | 2026-07-15, Europe/Lisbon | internal-observation |
| Repository | Vault present; no Git repository detected; Git was not initialized | internal-observation |
| Local instructions | No project-level `AGENTS.md` or project spec bank detected | internal-observation |
| Obsidian CLI | Executable unavailable; use filesystem, YAML, link, Base, and Canvas validation fallback | internal-observation |
| Defuddle | Installed; use for public standard webpages when direct extraction is needed | internal-observation |
| Bases and Canvas | Existing files inspected; no new `.base` or `.canvas` artifact is required by the contract | internal-observation |

## Acceptance state

- [x] All exact artifacts exist and cross-link.
- [x] Material facts have evidence state, confidence, and citation.
- [x] Role/week/gate/workstream coverage is complete or explicitly classified.
- [x] Models recompute from CSV without double counting.
- [x] Offline HTML passes zero-network, interaction, accessibility, responsive, print, privacy, and math QA.
- [x] Independent review has zero unresolved P0/P1 findings.

## Conflict and change records

### CCR-001 — NVOCC invoice timing summary

| Field | Record |
|---|---|
| Old state | The primer and atomic Part 541 note said an NVOCC generally had 30 days from the date it received the underlying invoice. They omitted §541.7(c) and §541.7(d). |
| New state | Current §541.7(b) measures the NVOCC's 30 days from the **issuance date** of the D&D invoice it received. Section 541.7(c) provides an additional 30-day dispute window after specified notice when the NVOCC is both billed and billing party. Section 541.7(d) permits a corrected-party invoice only within 30 days after the charge was last incurred. |
| Source authority | Current 46 CFR §541.7, eCFR, Federal Maritime Commission; authoritative but unofficial current codification |
| Checked | 2026-07-15; eCFR displayed Title 46 current through 2026-07-13 |
| Reviewer | Research orchestrator verified exact text; named domain/legal reviewer remains required before external or case-specific use |
| Affected artifacts | [[02_Domain/D&D and OSRA Primer]]; [[10_Sources/Source - 46 CFR Part 541]]; [[06_Research/Industry Regulatory and Competitive Dossier]]; source ledger; final report |
| Reason | Correct a material timing-key error and add omitted NVOCC/corrected-party distinctions before downstream analysis |

### CCR-002 — Diagnostic formula evidence

| Field | Record |
|---|---|
| Old state | The diagnostic URL and logic capture were missing; volume-times-75 behavior was a dated internal observation and C-019 treated the formula as an unverified model. |
| New state | The live Typeform URL and form ID were identified. Current configuration applies annual container volume × $75; port and stated D&D spend do not affect the result. The formula behavior is directly observed, while its validity as a recovery estimate remains unverified and blocked from publication. |
| Source authority | Company-controlled live Typeform configuration; proves current form behavior, not recoverability |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; Avi plus product/data and domain/legal reviewers required for methodology or external use |
| Affected artifacts | [[10_Sources/Source - SheperD Diagnostic Typeform - 2026-07-15]]; [[01_Company/Claims and Evidence Register]]; [[01_Company/Product and Business Model]]; company dossier; source ledger; final report |
| Reason | Separate verified interface behavior from unverified economic or recovery meaning |

### CCR-003 — Evergreen opinion date

| Field | Record |
|---|---|
| Old state | The market note referred to a July 2026 appellate decision, conflating the FMC report date with the court opinion date. |
| New state | The D.C. Circuit opinion is dated 2026-04-28. The FMC published its report on 2026-07-08. The fact-specific freight-fluidity boundary is unchanged. |
| Source authority | D.C. Circuit opinion and FMC report |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; named domain/legal reviewer required before external or case-specific use |
| Affected artifacts | [[02_Domain/Market and Competitive Landscape]]; [[10_Sources/Source - Evergreen 2026 Decision]]; industry dossier; source ledger; final report |
| Reason | Preserve the distinction between decision date and regulator-publication date |

### CCR-004 — Public commercial-model provenance

| Field | Record |
|---|---|
| Old state | [[01_Company/Product and Business Model]] listed no subscription, integration, or commitment as publicly stated. |
| New state | Current admitted public website evidence supports no-upfront and success-fee wording, but not the broader no-subscription, no-integration, or no-commitment assertions. Those terms return to `unknown` unless source provenance is supplied. |
| Source authority | Current company website capture and source audit |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; Avi/commercial owner required to confirm terms |
| Affected artifacts | [[01_Company/Product and Business Model]]; company dossier; source ledger; final report |
| Reason | Prevent an uncited commercial term from being presented as a public fact |

### CCR-005 — Apple episode metadata URL

| Field | Record |
|---|---|
| Old state | The source ledger linked to the public Apple Podcasts episode page, which returned an Apple server error during final link QA. |
| New state | The source now links to Apple's iTunes Lookup API response for podcast collection `1388206004`; that response returned 200 and includes exact episode track ID `1000517897345`, title, collection, and 2021-04-20 release date. |
| Source authority | Apple iTunes Lookup API; first-party episode metadata, not credential certification |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; founder claims remain bounded by corroborating professional sources |
| Affected artifacts | [[10_Sources/Source - Avi Manaim Professional History - 2026-07-15]]; source ledger; final report |
| Reason | Replace a currently failing presentation URL with a reproducible first-party metadata endpoint without changing the admitted claim |

### CCR-006 — Section 41301 official-link fallback

| Field | Record |
|---|---|
| Old state | The source ledger linked only to the House Office of the Law Revision Counsel preliminary-edition page. That host timed out in repeated final QA requests. |
| New state | The ledger and atomic source note use GovInfo's official most-recent-edition HTML resolver, which returned 200 and resolves to the 2024 U.S. Code edition. The 2026-07-15 current-preliminary check remains recorded as the original admission basis. |
| Source authority | U.S. Government Publishing Office / GovInfo, official U.S. Code edition; House OLRC preliminary edition used for current-through-check admission |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; domain/legal reviewer remains required for case-specific application or later amendments |
| Affected artifacts | [[10_Sources/Source - 46 USC 41301]]; source ledger; final report |
| Reason | Provide a reproducible official link while preserving the difference between the latest published Code edition and the current preliminary-edition check |

### CCR-007 — LinkedIn automation access boundary

| Field | Record |
|---|---|
| Old state | SRC-014 linked directly to Avi's LinkedIn profile; final automated GET checks received LinkedIn status 999. |
| New state | SRC-014 resolves to the dated atomic source note containing the admitted observations and evidence boundary. That note retains the public profile URL and records the automation restriction. |
| Source authority | Company-controlled LinkedIn surface captured on 2026-07-15; local atomic note is the reproducible evidence record |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; no private-person profiling or access bypass attempted |
| Affected artifacts | [[10_Sources/Source - SheperD LinkedIn - 2026-07-15]]; source ledger; final report |
| Reason | Preserve the access limitation and keep the evidence reproducible without treating an anti-bot response as a negative factual result |

### CCR-008 — Company LinkedIn automation access boundary

| Field | Record |
|---|---|
| Old state | SRC-023 linked directly to SheperD's LinkedIn company profile; final automated GET checks received status 429. |
| New state | SRC-023 resolves to the dated atomic source note containing the admitted company-profile observations. That note retains the public company URL and records the automation restriction. |
| Source authority | Company-controlled LinkedIn surface captured on 2026-07-15; local atomic note is the reproducible evidence record |
| Checked | 2026-07-15 |
| Reviewer | Research orchestrator; no access bypass attempted |
| Affected artifacts | [[10_Sources/Source - SheperD LinkedIn - 2026-07-15]]; source ledger; final report |
| Reason | Preserve the access limitation and keep the evidence reproducible without treating rate limiting as a negative factual result |

## Related

[[SheperD HQ]] · [[06_Research/Market Evidence and Source Map]] · [[01_Company/Open Questions and Diligence]] · [[04_Operations/Risk, Assumption and Decision Register]]
