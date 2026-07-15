---
title: Market Evidence and Source Map
type: research-index
status: active
owner: Research orchestrator
updated: 2026-07-15
evidence_status: mixed
confidentiality: public
tags:
  - sheperd/research
  - sheperd/market
  - sheperd/competition
  - sheperd/sources
---

# Market Evidence and Source Map

> [!abstract] Decision answer
> D&D is a meaningful operational and financial problem. Official sources establish material charges, formal complaint activity, relief, enforcement, and case-specific failures. Public practitioner reports and research describe invoice opacity, dwell-time causes, documentation gaps, and congestion. What remains unproven is the recoverable market, willingness to pay, SheperD's win rate, and delivery economics. Therefore `problem_materiality = supported`, while `TAM`, `SAM`, `SOM`, and product-market fit remain `unknown`.

> [!warning] Research boundary
> Spend, importer counts, complaint relief, penalties, vendor claims, academic findings, and Reddit anecdotes describe different populations. They must not be multiplied or combined into a recoverable-market estimate.

## Start here

| Need | Canonical document | What it contains |
|---|---|---|
| Industry, rules, market materiality, direct competitors | [[06_Research/Industry Regulatory and Competitive Dossier]] | D&D lifecycle, current U.S. rules, complaint routes, market limits, and nine direct/adjacent competitors |
| All admitted links and source states | [[06_Research/data/source-ledger.csv]] | Source ID, authority, URL/path, date, claim supported, status, confidence, conflict, use, and review date |
| Market, congestion, importer universe, sizing boundaries | [[10_Sources/Source - Industry Congestion and Market Reports - 2026-07-15]] | Census, FMC, World Bank, UNCTAD, New York Fed, IMF, port, and commercial-estimate sources |
| Papers and community questions | [[10_Sources/Source - Research Papers and Community Evidence - 2026-07-15]] | Peer-reviewed/working papers and bounded Reddit/practitioner evidence |
| Competition and named public pain | [[10_Sources/Source - Competitor and Public Pain Signals - 2026-07-15]] | Direct, adjacent, enterprise alternatives, sponsored article, and official enforcement examples |
| Demand-search work | [[10_Sources/Source - GTM Market and Demand Scan - 2026-07-15]] | Search themes, buyer questions, content hypotheses, and missing volume data |
| Company truth and proof gaps | [[06_Research/Company and Founder Dossier]] | Entity, authority, product, outcomes, economics, data, security, and ownership gaps |
| Questions required to close the unknowns | [[06_Research/Research Gaps and Interview Guide]] | Founder, product, legal, security, customer, partner, and measurement questions |

## Evidence layers

| Layer | Sources | What it can prove | What it cannot prove |
|---|---|---|---|
| Primary government/court | FMC, eCFR, U.S. Code, D.C. Circuit, Census | Current rules, reported populations, enforcement, complaint activity, importer universe | SheperD eligibility, win rate, buyer intent, or economics |
| Port and multilateral reports | World Bank CPPI, UNCTAD, IMF PortWatch, Port of Los Angeles | Port/trade context, congestion and disruption indicators | Invoice invalidity or recoverability |
| Research papers | Transportation Research Part C, University of Debrecen journal, New York Fed, IMF | Mechanisms, observed causes, models, and measurement methods | U.S. addressable revenue or SheperD outcomes |
| Company/vendor surfaces | SheperD and competitor sites, gCaptain sponsored article | Public positioning, offer mechanics, pricing signals, product claims | Independent performance or market truth |
| Community evidence | Reddit logistics/import threads | Problem language, workflow friction, questions, and research hypotheses | Prevalence, legality, authenticity, or willingness to pay |
| First-party operating evidence | Authorized cohorts, CRM, invoices, event logs, credits/refunds | Segment response, case quality, delivery effort, realized outcomes, net economics | Nothing exists yet at an admitted comparable-cohort level |

## Is this a meaningful problem?

| Signal | Evidence | Safe conclusion | Boundary |
|---|---|---|---|
| D&D charges | FMC reports about $15.4B collected by nine major carriers from 2020-04-01 through 2025-03-31 | The reported charge pool is financially material | Not the invalid, disputable, recoverable, or obtainable amount |
| Charge Complaints | FMC reports 296 complaints received, 164 accepted, about $2.89M FY2025 relief, and over $6.1M cumulative relief | A formal route exists and produces measured relief | Excludes direct disputes and is not a recovery-rate denominator |
| Enforcement | 2026 FMC actions concerning MSC and Maersk, plus the earlier Hapag-Lloyd settlement | Billing/liability practices can create material enforcement exposure | Civil penalties are not customer recoveries or SheperD revenue |
| Importer universe | Census preliminary 2024 profile reports 239,231 identified U.S. importers, including 232,804 SMEs | There is a large top-of-funnel company universe | It includes non-ocean importers and does not identify D&D exposure |
| Operations and congestion | World Bank CPPI, UNCTAD, PortWatch, GSCPI, and port statistics | Disruption and port inefficiency are measurable and recurrent | Macro pressure does not identify a recoverable invoice |
| Research | D&D regime and consignee dwell-time studies | Tariff design, cash flow, information flow, and physical flow affect dwell and cost | Study geographies and samples do not establish U.S. market size |
| Practitioner reports | Public Reddit posts describe surprise charges, exam holds, missing backup, deadlines, and dispute uncertainty | The language is useful for interviews, content, and workflow design | Anecdotal, self-reported, and not prevalence evidence |
| Category supply | At least 14 direct, adjacent, and enterprise providers were observed | Buyers have alternatives and the category is competitively congested | Vendor count is not market demand or competitor traction |

## TAM / SAM / SOM contract

| Layer | Current state | Valid future calculation | Required evidence |
|---|---|---|---|
| TAM | `unknown` | Eligible U.S. ocean-container D&D charges × independently supported disputable share × realized recovery share × approved fee | Invoice-level denominator, rule/fact eligibility, realized outcomes, fee contract |
| SAM | `unknown` | TAM restricted to target importer profile, ports/carriers, evidence access, geography, and delivery capability | Named-account universe, ocean/container filter, recurring exposure, secure data access, reviewer coverage |
| SOM | `unknown` | Capacity-constrained authorized cases × qualification rate × submission rate × realized recovery × fee | One or more comparable cohorts, case capacity, cycle time, quality, approvals, cash/credit reconciliation |

### Context values that are not TAM

- **$15.4B FMC collected-charge population:** materiality context only.
- **239,231 identified U.S. importers:** broad company universe, not ocean-importer or buyer count.
- **$6.1M+ cumulative Charge Complaint relief:** one public route, not all disputes or market value.
- **Commercial freight-audit reports:** published estimates conflict materially and use opaque methods; excluded from admitted sizing.
- **Competitor savings/error claims:** vendor-controlled and non-comparable; excluded from sizing.

## Competitive map

| Category | Observed alternatives | Buyer job | SheperD implication |
|---|---|---|---|
| D&D recovery specialists | Unwaived, HarborClaim, AuditDray, MiraLedger, Portside Recovery | Review charges, assemble disputes, track recovery | Success-fee recovery is not a unique category position |
| Audit, prevention, and drayage platforms | BlueCargo, Dockline, Intelligent Audit, GoComet | Prevent, validate, audit, and analyze charges | Evidence-to-decision workflow must outperform broader platforms on a defined cohort |
| Enterprise freight audit/payment | nVision Global, Trax, Cass, CT Logistics, Data2Logistics/Loop | Multi-modal invoice audit, payment, governance, and spend intelligence | Enterprise platforms can expand into D&D and already own finance data/workflows |
| Human/service alternatives | Internal AP/logistics, brokers, consultants, counsel, recovery firms | Manual review, escalation, filing, and negotiation | The comparison must include labor, risk, control, and realized outcome—not software features alone |
| Do nothing / pay | Pay invoice, short-pay, or abandon low-value dispute | Avoid time, data, and relationship cost | SheperD must prove net value after fee and customer workload |

## Research-paper map

| Paper/report | Use for | Do not use for |
|---|---|---|
| [Effects of demurrage and detention regimes on dry-port-based inland container transport](https://doi.org/10.1016/j.trc.2018.01.012) | D&D effects on scheduling, consolidation, transport mode, and dwell | U.S. recovery rate or buyer demand |
| [Long Container Dwell Time at Seaport Terminals](https://ojs.lib.unideb.hu/IJEMS/article/view/9774) | Consignee-side information, cash, and physical-flow causes | Population prevalence outside the study |
| [The GSCPI: A New Barometer of Global Supply Chain Pressures](https://www.newyorkfed.org/research/staff_reports/sr1017) | Macro supply-chain pressure measurement | Case-level invoice eligibility |
| [Nowcasting Country-Level Trade Estimates Using IMF PortWatch](https://doi.org/10.5089/9798229046893.001) | AIS-based trade monitoring and limitations | Buyer count or D&D exposure |
| [Container Port Performance Index 2025](https://www.worldbank.org/en/topic/transport/publication/cppi) | Vessel time-in-port and contextual port-performance comparison | Assigning blame or inferring invalid charges |

## Public problem-language map

| Question observed | Example source | Research use |
|---|---|---|
| “What can I do after a long exam hold creates a large bill?” | [30+ day exam hold update](https://www.reddit.com/r/logistics/comments/1nkbihf/) | Interview prompt on evidence, control, owner, and escalation |
| “How do I validate charges without carrier/forwarder backup?” | [Customs exam charges from freight forwarder](https://www.reddit.com/r/logistics/comments/1r6iyd1/customs_exam_charges_from_freight_forwarder/) | Invoice-document checklist and source-provenance workflow |
| “Are demurrage, handling, and exam charges reasonable?” | [Outrageous inspection charges](https://www.reddit.com/r/logistics/comments/1r26mfj/outrageous_inspection_charges/) | Charge taxonomy and itemization questions |
| “How should freight invoices be audited?” | [Do you audit your invoices?](https://www.reddit.com/r/logistics/comments/vwkbtd/do_you_audit_your_invoices/) | Baseline workflow and exception-threshold interview |

Community sources are discovery inputs only. Do not reuse advice from comments as law, policy, or product logic.

## Highest-value gaps

1. Obtain a de-identified invoice denominator by importer, carrier, port, charge type, date, amount, and governing terms.
2. Record rule/fact eligibility separately from “looks wrong” or “customer dislikes charge.”
3. Measure requested, waived, credited, refunded, rejected, and collected value separately.
4. Admit a named target-account universe filtered to ocean-container exposure and accessible evidence.
5. Run one permissioned cohort with response, submission, case quality, work time, review time, cycle, and realized outcome.
6. Export Search Console/Keyword Planner data with query, geography, period, match type, and metric definition.
7. Capture competitor win/loss, price, implementation burden, security requirements, and customer switching reason.
8. Interview finance/AP, logistics, broker/3PL, and domain/legal reviewers before publishing market-size or superiority claims.

## Decision rule

- **Supported now:** material problem, evidence complexity, workflow friction, category competition, need for traceability.
- **Hypothesis:** target segment, trigger, offer, channel, and differentiated workflow.
- **Blocked:** recoverable TAM/SAM/SOM, repeatable outcomes, unit economics, scalability, superiority, and external activation.

## Related

[[06_Research/Industry Regulatory and Competitive Dossier]] · [[06_Research/Company and Founder Dossier]] · [[10_Sources/Source - GTM Market and Demand Scan - 2026-07-15]] · [[03_GTM/ICP and Stakeholder Personas]]
