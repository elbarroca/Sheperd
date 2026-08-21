---
title: AI SDR and Market Intelligence Open-Source Landscape
type: research
status: research_only
owner: Michael
updated: 2026-08-11
evidence_status: mixed
confidentiality: internal
tags:
  - ai-sdr
  - market-intelligence
  - open-source
  - hubspot
---

# AI SDR and Market Intelligence Open-Source Landscape

> [!warning] Research-only decision record
> Snapshot: 2026-08-10. This dossier authorizes no deployment, scraping run, data purchase, contact ingestion, HubSpot write, email send, follow-up, credential use, or third-party code execution. Every operational output remains **DRAFT - HUMAN REVIEW REQUIRED**.

> [!tip] Current Ric-facing document
> Use [[SheperD AI SDR Operating Blueprint - Ric]] for the concise architecture, operating map, curated repository shortlist, implementation phases, and Ric review questions. This note is the technical appendix: it preserves the broader repository catalog, exact-SHA audits, licensed-data analysis, and source register for traceability.

## 1. Technical summary

No reviewed end-to-end AI SDR product is safe to adopt unchanged for SheperD. The strongest products combine useful research and workflow patterns with autonomous email, LinkedIn automation, broad connector permissions, opaque enrichment vendors, or direct CRM writes. Popularity and aggregate scores do not override those hard-gate failures.

The recommended architecture is a small, proposal-only pipeline assembled from narrow components:

1. Collect only from approved public sources and separately contracted data APIs.
2. Preserve source identity, rights, checked date, and raw evidence before interpretation.
3. Resolve accounts deterministically around normalized domain, legal name, and stable provider identifiers.
4. Produce evidence packs and score proposals; never convert unknowns into zeros or passes.
5. Let AI explain and draft only after deterministic gates pass.
6. Require a named human to approve account admission, stage changes, CRM mutations, and sending separately.
7. Represent the final CRM step as a **HubSpotChangeProposal**, not a write, until separately authorized.

Recommended starting components:

| Need | Default | Why | Boundary |
|---|---|---|---|
| Static collection | Scrapy or simple HTTP clients | Mature, inspectable, low orchestration burden | Approved public sources only; respect terms, robots, rate limits, and retention |
| JavaScript collection | Crawl4AI, conditionally | Structured extraction and browser support | Allowlisted domains only; no stealth, account login, evasion, or arbitrary browser actions |
| Official-feed monitoring | Miniflux | Simple self-hosted RSS ingestion | Prefer publisher feeds; retain canonical article URL and publication time |
| Page-change monitoring | changedetection.io, conditionally | Useful for official regulatory and port pages | Disable notifications, browser steps, proxies, and webhooks during the research pilot |
| PDF/document parsing | Docling | Strong local document extraction | Parsing does not confer source rights or factual validity |
| Manual cleanup | OpenRefine | Human-visible normalization and reconciliation | Export proposals; do not write through to HubSpot |
| Typed AI output | PydanticAI patterns, only when needed | Typed schemas, evaluations, and explicit tool approval | No tools or side effects in the first pilot |
| Entity resolution | Deterministic aliases first; Splink later | Avoids premature probabilistic complexity | Introduce Splink only after a labeled duplicate benchmark exists |
| CRM boundary | Official HubSpot SDK | Supported API surface | Proposal/dry-run first; stable IDs, idempotency, retries, least privilege |
| Audit trail | Existing database or append-only JSONL receipts | Minimal, reviewable, portable | Do not add Langfuse or a vector database until measured need exists |

Open source cannot reliably supply company-level U.S. importer identity, shipment volume, current decision-maker identity, deliverable email addresses, permission, or DNC status on its own. Census and FMC sources support aggregate market intelligence and regulatory context, not company-level qualification. A useful production system will therefore be hybrid: open-source control plane plus separately approved and contracted data providers.

## 2. Scope, method, and evidence standard

### 2.1 Scope

This report evaluates open-source and source-available components for:

- account discovery and importer research;
- web, feed, and document collection;
- identity resolution, enrichment, and email verification;
- agent and workflow control;
- HubSpot integration and outreach references;
- market-intelligence monitoring, observability, evaluation, and retrieval;
- licensed data gaps for importer volume and business contacts.

It does not evaluate deliverability tactics, inbox warm-up, campaign copy performance, or legal eligibility to contact any person. Those require separate approvals and evidence.

### 2.2 Research procedure

- Screened top GitHub topic and search results for **ai-sdr**, **lead-generation**, **sales-automation**, **enrichment**, **email-verification**, **market-intelligence**, and **competitive-intelligence**.
- Deduplicated forks, mirrors, renamed repositories, examples, and vendor-maintained copies to the canonical repository.
- Baseline pass: 47 canonical repositories. The expansion pass adds 75 verified repositories/tools, for 122 unique canonical entries.
- Baseline pass: 16 exact-SHA deep audits. The expansion adds 24 exact-SHA audits, for 40 total. Each audit inspected README/documentation, license and nested license markers, release/activity signal, security policy, architecture, dependency manifests, tests/CI, connectors, persistence, commercial dependencies, approval controls, and external side effects without executing repository code.
- Used repository metadata current at the snapshot. **Activity** means the canonical repository's latest observed push date, not proof of a stable release, security response, or healthy maintenance.
- Used only official repositories, vendor pages, government pages, and official terms for material claims and prices.
- Executed no reviewed third-party repository code.

### 2.3 Evidence labels

| Label | Meaning |
|---|---|
| observed | Directly present in an official source or exact-SHA repository tree |
| corroborated | Consistent across at least two independent authoritative records |
| vendor_claim | Stated by the provider but not independently validated |
| inferred | A clearly labeled conclusion drawn from observed architecture or terms |
| disputed | Authoritative records conflict |
| unknown | Evidence is missing, inaccessible, stale, or insufficient |

Unknown is a terminal evidence state, not a numeric zero, negative answer, or permission to proceed.

## 3. SheperD constraints

This dossier reconciles recommendations with:

- [[06_Research/SheperD Deep Research - Control Note|SheperD Deep Research Control Note]]
- [[04_Operations/CRM Data Model|CRM Data Model]]
- [[03_GTM/ICP and Stakeholder Personas|ICP and Stakeholder Personas]]
- [[03_GTM/Customer Journey and Funnel|Customer Journey and Funnel]]
- [[05_AI/AI Enablement Roadmap|AI Enablement Roadmap]]
- [[05_AI/Human Approval Policy|Human Approval Policy]]
- [[06_Research/AI Opportunity Register|AI Opportunity Register]]

The resulting operating rules are:

1. Importers and channel partners remain distinct account types. A partner introduction is an explicit association to the importer and opportunity, never a merged identity.
2. The commercial lifecycle remains **Target → Outreach → Conversation → Pilot → Client → Invoices Submitted → Recovery → Money Collected**. Research software cannot move a record between these stages.
3. Company size and container-volume signals are prioritization evidence only. They do not prove D&D exposure, invoice validity, commercial qualification, recoverability, or expected recovery value.
4. Unknown identity, TEU, source rights, permission, or DNC state blocks the dependent action.
5. AI may research, classify, score, explain, summarize, and draft. A human decides admission, stage, association, CRM mutation, and sending.
6. D2 enterprise data requires approval and a defined purpose, source, retention period, and deletion path. D3 data is prohibited.
7. LinkedIn evasion, guessed-email sending, autonomous follow-up, irreversible CRM actions, and silent field overwrites are prohibited.
8. Automation may append evidence, exceptions, and change proposals. It may not silently rewrite source records.
9. HubSpot may become the operational source of truth only through official APIs, stable identifiers, deterministic deduplication, retries, idempotency, least privilege, audit receipts, and current request-signature validation.

## 4. AI SDR system decomposition

### 4.1 Conceptual flow

**SourceRecord → AccountCandidate → EvidencePack → ScoreProposal → OutreachDraft → Human Approval → HubSpotChangeProposal**

Market intelligence branches as:

**SourceRecord → SignalEvent → AccountMatch → Weekly Brief**

The two branches may share evidence, but a market signal never promotes an account or establishes D&D exposure by itself.

### 4.2 Shared control envelope

Every object carries these fields:

| Field | Required behavior |
|---|---|
| object_id and schema_version | Stable internal identity and explicit schema evolution |
| source_id, source_uri, source_record_id | Identifies the authoritative origin; no unattributed facts |
| source_checked_at_utc | UTC verification time, distinct from publication or event time |
| source_published_at_utc and effective_at_utc | Preserved when known; unknown remains explicit |
| evidence_status | One of observed, corroborated, vendor_claim, inferred, disputed, unknown |
| evidence_hash | Immutable hash of retained evidence or normalized snapshot |
| confidence | Calibrated 0–1 estimate; never overrides a gate |
| rights_status | approved, restricted, denied, or unknown |
| permission_state and dnc_state | allowed, denied, or unknown; unknown blocks outreach |
| rule_version and model_version | Exact deterministic rule set and model/prompt identity |
| approval_state | draft, pending_review, approved, rejected, expired, or revoked |
| approved_by and approved_at_utc | Required for approval; model identity cannot populate approved_by |
| retention_class and delete_after | Data-minimization and deletion control |
| parent_ids | Traceable lineage to upstream objects |

### 4.3 Object-specific contracts

| Object | Purpose | Minimum additional fields | Cannot assert |
|---|---|---|---|
| SourceRecord | Immutable normalized observation | source type, fetch method, raw locator, terms basis, content hash | Truth, permission, or qualification |
| AccountCandidate | Proposed importer or partner identity | legal/display name, account type, normalized domain, address, stable external IDs, duplicate status | TEU, D&D exposure, or CRM admission |
| EvidencePack | Bounded evidence for one proposition | claim, supporting and conflicting records, freshness, quality, unknowns | More than its cited evidence supports |
| ScoreProposal | Explainable prioritization proposal | rubric version, feature values, missingness, gate results, component scores, rationale | Eligibility when any hard gate fails |
| OutreachDraft | Unsent human-review artifact | target role, approved evidence references, claims used, prohibited-claim check, DNC/permission state | Delivery, consent, or factual certainty |
| HubSpotChangeProposal | Dry-run CRM diff | portal, object type, stable object ID, before/after fields, associations, idempotency key, expected version | Applied change |
| SignalEvent | Time-bounded market observation | event type, geography, port/carrier/industry scope, event and publication times | Account-level impact |
| AccountMatch | Proposed link between signal and account | match rules, supporting identifiers, ambiguity set | Qualification or stage movement |
| Weekly Brief | Human-readable intelligence summary | covered period, source list, corrections, unknowns, candidate follow-ups | Operational instruction |

### 4.4 CRM reconciliation map

| Research concept | Proposed HubSpot representation | Authority rule |
|---|---|---|
| Importer AccountCandidate | Company with account_type = importer and stable external IDs | Human admits or rejects the company |
| Channel partner AccountCandidate | Separate Company with account_type = channel_partner | Never merge with an introduced importer |
| Partner introduction | Labeled association among partner company, importer company, and opportunity | Human approves the relationship and opportunity |
| Target segment | Proposed company property backed by EvidencePack | AI may classify; human accepts the CRM value |
| Estimated TEU/container volume | Value, method, period, coverage, provider/source ID, confidence, and evidence status | Never store a bare number; unknown does not become 0 |
| Priority/account score | ScoreProposal ID, rubric version, components, missingness, and explanation | Score does not override gates; human sets operational priority |
| Lead source | Canonical first-source identity plus later corroborating sources | Preserve lineage; never overwrite attribution silently |
| Commercial motion and prospecting status | Explicit proposed properties | Human-controlled; no autonomous sequence enrollment |
| Decision-maker/contact | Separate Contact proposal with company association, title evidence, source, freshness, permission, and DNC state | Unknown identity/permission/DNC blocks outreach |
| Lifecycle stage | Existing Target → Outreach → Conversation → Pilot → Client → Invoices Submitted → Recovery → Money Collected model | Only authorized humans/operational systems move stage |
| Research or draft activity | Internal research receipt; optionally a proposed CRM note after approval | An unsent draft is not an outreach activity |
| Invoice, recovery, and money-collected facts | Existing operational/finance evidence linked to opportunity/client | Never inferred from trade, news, or company-size data |

## 5. Reference architecture

~~~mermaid
flowchart LR
    subgraph Sources["Approved source boundary"]
        GOV["Census, FMC, ports, regulators"]
        WEB["Allowlisted public pages and RSS"]
        TRADE["Contracted trade-data API"]
        CONTACT["Contracted contact-data API"]
    end

    subgraph Research["Research-only control plane"]
        SR["SourceRecord and immutable receipt"]
        AC["AccountCandidate and deterministic dedupe"]
        EP["EvidencePack"]
        SP["ScoreProposal"]
        OD["OutreachDraft"]
        SE["SignalEvent"]
        AM["AccountMatch"]
        WB["Weekly Brief"]
    end

    subgraph Human["Human control"]
        QA["Evidence and rights review"]
        APPROVE["Named approval"]
    end

    subgraph Protected["Protected operational boundary"]
        HCP["HubSpotChangeProposal"]
        HS["HubSpot mutation"]
        SEND["Email or follow-up"]
    end

    GOV --> SR
    WEB --> SR
    TRADE --> SR
    CONTACT --> SR
    SR --> AC --> EP --> SP --> OD
    SR --> SE --> AM --> WB
    AC --> AM
    EP --> QA
    SP --> QA
    OD --> QA
    WB --> QA
    QA --> APPROVE
    APPROVE --> HCP
    HCP -. "separate write authorization" .-> HS
    OD -. "separate send authorization" .-> SEND
~~~

The dotted edges are deliberately unimplemented authorization boundaries. Approval of an evidence pack does not automatically approve a CRM write or an email.

## 6. Decision gates and scoring

### 6.1 Hard gates

A project or deployment profile must pass every gate before scoring:

| Gate | Pass condition | Fail-closed result |
|---|---|---|
| Identifiable license | Relevant code and bundled enterprise modules have reviewable terms | reject or quarantine |
| Controllable data rights | Each source route has an approved collection and reuse basis | quarantine until route-level review |
| No mandatory prohibited action | Product can operate without LinkedIn evasion, guessed-email sending, autonomous follow-up, or direct CRM mutation | quarantine runtime; patterns may still be borrowed |
| Human approval support | Side-effectful steps can be separated, previewed, and explicitly approved | reject operational use |
| Auditable state | Inputs, outputs, versions, approvals, errors, and retries can be retained | reject operational use |
| Secrets and retention | Least privilege, secret isolation, purpose limitation, expiry, deletion, and subprocessor review are manageable | quarantine |
| Maintenance and security | Acceptable activity, dependency hygiene, vulnerability handling, and security reporting path | observe or quarantine |

### 6.2 Scoring rubric

Survivors are scored 0–5 on eight equally weighted dimensions. For **external dependency burden**, 5 means the lowest burden. The maximum is 40. Scores compare suitability for SheperD's constrained research pipeline, not general product quality.

| Score | Meaning |
|---|---|
| 0 | Absent, incompatible, or unacceptable |
| 1 | Major custom work or material weakness |
| 2 | Weak fit with significant controls required |
| 3 | Usable with bounded adaptation |
| 4 | Strong fit with limited adaptation |
| 5 | Native fit and strong evidence |

| Project or constrained profile | Workflow fit | Provenance | Human control | HubSpot fit | License / self-hosting | Maturity | Simplicity | Low external burden | Total / 40 | Class |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| HubSpot official SDK | 3 | 5 | 3 | 5 | 5 | 4 | 4 | 4 | 33 | adopt |
| Scrapy | 3 | 4 | 5 | 2 | 5 | 5 | 4 | 5 | 33 | adopt |
| Miniflux | 3 | 4 | 5 | 1 | 5 | 5 | 4 | 5 | 32 | adopt |
| pgvector | 2 | 5 | 5 | 1 | 5 | 5 | 4 | 5 | 32 | observe |
| OpenRefine | 2 | 5 | 5 | 1 | 5 | 5 | 3 | 5 | 31 | adopt |
| Splink | 3 | 5 | 5 | 1 | 5 | 5 | 2 | 5 | 31 | borrow |
| changedetection.io, restricted profile | 4 | 4 | 3 | 2 | 5 | 4 | 4 | 4 | 30 | adopt |
| PydanticAI, no-tool profile | 4 | 4 | 5 | 2 | 5 | 4 | 3 | 3 | 30 | borrow |
| LangGraph, interrupted proposal graph | 4 | 4 | 5 | 2 | 5 | 5 | 2 | 3 | 30 | borrow |
| Dedupe | 3 | 5 | 5 | 1 | 5 | 4 | 3 | 4 | 30 | borrow |
| Docling | 3 | 4 | 5 | 1 | 5 | 4 | 3 | 4 | 29 | adopt |
| Activepieces, community core | 4 | 3 | 4 | 4 | 4 | 4 | 2 | 2 | 27 | observe |
| OpenFang, approval-only profile | 4 | 4 | 4 | 1 | 5 | 3 | 2 | 3 | 26 | borrow |
| n8n, internally licensed profile | 4 | 3 | 4 | 4 | 2 | 5 | 2 | 2 | 26 | observe |
| Crawl4AI, allowlisted profile | 4 | 3 | 3 | 1 | 5 | 4 | 2 | 3 | 25 | adopt |
| Langfuse, self-hosted core | 3 | 5 | 4 | 1 | 4 | 5 | 1 | 2 | 25 | observe |
| Firecrawl, self-hosted core | 4 | 3 | 3 | 1 | 3 | 5 | 1 | 2 | 22 | observe |
| GTM Skills | 3 | 2 | 3 | 1 | 5 | 2 | 4 | 2 | 22 | borrow |
| Playwright, restricted browser worker | 2 | 3 | 5 | 0 | 5 | 5 | 3 | 4 | 27 | borrow |
| SearXNG, approved-engine profile | 2 | 2 | 5 | 0 | 3 | 5 | 3 | 3 | 23 | observe |
| Unstructured, local library | 3 | 3 | 5 | 1 | 5 | 5 | 2 | 3 | 27 | observe |
| Reacher, verification-only profile | 2 | 2 | 5 | 1 | 3 | 4 | 3 | 3 | 23 | quarantine |
| CrewAI, no-side-effect profile | 3 | 3 | 3 | 1 | 5 | 4 | 2 | 2 | 23 | observe |
| AutoGen, no-side-effect profile | 3 | 3 | 3 | 1 | 5 | 5 | 2 | 2 | 24 | observe |
| Windmill, community proposal-only profile | 3 | 4 | 4 | 2 | 3 | 5 | 2 | 3 | 26 | observe |
| Huginn, restricted agent set | 3 | 3 | 3 | 2 | 5 | 4 | 3 | 4 | 27 | borrow |
| Twenty | 2 | 4 | 4 | 0 | 3 | 4 | 1 | 3 | 21 | observe |
| Frappe CRM | 2 | 4 | 4 | 0 | 3 | 4 | 1 | 3 | 21 | observe |
| EspoCRM | 2 | 4 | 4 | 0 | 3 | 4 | 2 | 4 | 23 | observe |
| FreshRSS | 3 | 4 | 5 | 1 | 3 | 5 | 3 | 5 | 29 | observe |
| OpenLIT | 3 | 4 | 4 | 1 | 5 | 4 | 2 | 3 | 26 | borrow |
| Phoenix | 3 | 5 | 4 | 1 | 2 | 5 | 2 | 3 | 25 | observe |
| Ragas | 3 | 4 | 5 | 1 | 5 | 4 | 3 | 3 | 28 | borrow |
| Qdrant | 2 | 5 | 5 | 1 | 5 | 5 | 2 | 3 | 28 | observe |
| Chroma | 2 | 4 | 5 | 1 | 5 | 4 | 3 | 3 | 27 | observe |

**Interpretation:** class is the decision. Score is supporting evidence only. The two official HubSpot SDKs share the same score because their role and boundary are equivalent. Projects failing a hard gate—OpenOutreach runtime, YALC runtime, OneShot runtime, the B2B SDR template, Leadpoet pending a complete security/side-effect audit, the no-license LangGraph outreach example, generic browser-use deployment, email-sleuth, Mautic/listmonk send profiles, and RSSHub without route-level approval—are intentionally not scored.

### 6.3 Classification meanings

| Class | Meaning |
|---|---|
| adopt | Preferred component under the constraints stated; not deployment authorization |
| borrow | Reuse architecture, schema, tests, or control patterns without adopting the runtime |
| observe | Revisit only when a measured requirement justifies its cost or risk |
| quarantine | Keep outside the system until a named blocker is removed and re-reviewed |
| reject | Not suitable for this scope |

## 7. GitHub screening and exclusions

Screening favored canonical repositories with inspectable licenses, maintained dependency manifests, tests, explicit state, and separable side effects. Stars informed discovery only.

| Result or pattern | Disposition | Reason |
|---|---|---|
| Forks, mirrors, generated tutorials, and near-identical examples | reject | Deduplicated to canonical upstream; no independent maintenance signal |
| aitit-inc/leadace | reject | No identifiable license at review and an automated-sending product shape |
| gtm-api/linkedin-mcp | quarantine | LinkedIn automation/scraping conflicts with SheperD policy and platform restrictions |
| StaffSpy LinkedIn tooling | reject | Platform-evasion use case is prohibited regardless of permissive code license |
| omkarcloud/google-maps-scraper | reject | Weak importer/TEU relevance and unresolved route-level source rights |
| kiryano/Scout and generic social scrapers | reject | No importer-data advantage; identity and platform-rights burden exceeds value |
| Generic trading or finance “market intelligence” repositories | reject | Domain mismatch |
| kaymen99/sales-outreach-automation-langgraph | reject | No license, stale example, and outreach side effects |

## 8. Repository landscape

### 8.1 End-to-end GTM and SDR

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenOutreach | End-to-end GTM/SDR | Prospect research, sequencing, SMTP/IMAP outreach, follow-up | GPL-3.0 | Last push 2026-08-10 | Django, SQLite, SMTP/IMAP, BetterContact | Self-hosted web app | No native reviewed adapter; custom | Automatic sending/follow-up; mailbox permissions; paid discovery; promotional email side effect | quarantine | [Official repository](https://github.com/eracle/OpenOutreach) |
| YALC | End-to-end GTM/SDR | Declarative GTM operating system and multi-provider actions | MIT core | Last push 2026-07-01 | Node.js, TypeScript, SQLite/Turso, Drizzle, multiple APIs | Local/server CLI and service | Native HubSpot adapter | High-confidence auto-commit; email/LinkedIn actions; many vendors and secrets | borrow | [Official repository](https://github.com/Othmane-Khadri/YALC-the-GTM-operating-system) |
| OpenFang | End-to-end agent OS | Agent hands, approval, scheduling, audit, local state | MIT or Apache-2.0 | Last push 2026-07-02 | Rust, SQLite, vector/search, model APIs | Local binary/server | Custom tool needed | Pre-1.0; broad autonomous tools; security-support/version inconsistency | borrow | [Official repository](https://github.com/RightNow-AI/openfang) |
| OneShot GTM | End-to-end GTM/SDR | Agentic enrichment, queues, multichannel cadences | MIT | Last push 2026-07-20 | Bun, TypeScript, SQLite, proprietary OneShot API, payments | Local CLI/service | Custom | Email/SMS/voice sending; automatic cadence; proprietary paid API; force override | borrow | [Official repository](https://github.com/oneshot-agent/oneshot-gtm) |
| B2B SDR Agent Template | End-to-end template | CRM, enrichment, email, WhatsApp/Telegram SDR recipe | MIT | Last push 2026-07-13 | OpenClaw, Jina, messaging and email services | Script/template | Custom | Broad side effects, messaging credentials, thin independent control plane | quarantine | [Official repository](https://github.com/iPythoning/b2b-sdr-agent-template) |
| GTM Skills | End-to-end skills | Reusable GTM agent instructions and tasks | MIT | Last push 2026-02-08 | Agent runtime and external services vary by skill | Prompt/skill package | Indirect | Instructions can hide data/vendor assumptions; limited runtime guarantees | borrow | [Official repository](https://github.com/gtm-skills/gtm) |
| Leadpoet | End-to-end GTM/SDR | Lead research and outreach automation | MIT | Last push 2026-08-10 | Model, enrichment, and outreach services | Application/service | Custom | Very early project; vendor and send boundaries require audit | observe | [Official repository](https://github.com/leadpoet/leadpoet) |
| LangGraph outreach example | End-to-end example | Sales outreach graph demonstration | No license identified | Last push 2025-01-15 | Python, LangGraph, model/email services | Example scripts | Custom | No reuse license; stale; sending-oriented example | reject | [Official repository](https://github.com/kaymen99/sales-outreach-automation-langgraph) |

### 8.2 Collection and parsing

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| Crawl4AI | Collection | Browser-assisted structured web extraction | Apache-2.0 | Last push 2026-07-30 | Python, Playwright/Patchright, SQLite, optional models | Library, local service, Docker | Export/custom adapter | Browser attack surface; past RCE/SSRF/LFI fixes; stealth features; source rights | adopt | [Official repository](https://github.com/unclecode/crawl4ai) |
| Firecrawl | Collection | Crawl, scrape, map, search, and structured extraction | AGPL-3.0 core; permissive SDKs | Last push 2026-08-10 | Node/Python services, Redis, PostgreSQL, queues, browsers, optional models | Managed API or complex self-host | Custom/n8n paths | AGPL boundary, proxies and interactions, operational complexity, hosted dependency | observe | [Official repository](https://github.com/firecrawl/firecrawl) |
| Scrapy | Collection | Deterministic HTTP crawling and extraction | BSD-3-Clause | Last push 2026-08-10 | Python, Twisted, selectors | Library/worker | Export/custom adapter | Route-level terms, robots, rate limits, and schema drift remain operator duties | adopt | [Official repository](https://github.com/scrapy/scrapy) |
| Playwright | Collection | Browser automation | Apache-2.0 | Last push 2026-08-10 | Node.js or language bindings, browser binaries | Library/worker | None | Arbitrary browser actions, credential exposure, anti-bot/evasion misuse | borrow | [Official repository](https://github.com/microsoft/playwright) |
| browser-use | Collection/agent | Model-controlled browser tasks | MIT | Last push 2026-08-06 | Python, browser, model providers, optional cloud | Local/cloud agent | Custom | Model-directed side effects, credential exposure, platform-policy violations | quarantine | [Official repository](https://github.com/browser-use/browser-use) |
| SearXNG | Collection/search | Federated metasearch | AGPL-3.0 | Last push 2026-08-10 | Python, Redis optional, upstream engines | Self-hosted service | None | Upstream terms, result provenance, rate limits, and engine instability | observe | [Official repository](https://github.com/searxng/searxng) |
| Docling | Collection/parsing | PDF and document conversion and extraction | MIT | Last push 2026-08-10 | Python, document/ML packages, optional OCR | Local library/CLI/service | Export/custom adapter | Resource cost; OCR/extraction errors; parsing does not establish truth | adopt | [Official repository](https://github.com/docling-project/docling) |
| Unstructured | Collection/parsing | Document partitioning, cleaning, and chunking | Apache-2.0 | Last push 2026-08-04 | Python, format/OCR extras, optional hosted API | Library, API, Docker | Custom | Large optional dependency surface; managed API and model dependencies | observe | [Official repository](https://github.com/Unstructured-IO/unstructured) |

### 8.3 Identity, enrichment, and email checks

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| OpenRefine | Identity/enrichment | Human-assisted cleanup, clustering, and reconciliation | BSD-3-Clause | Last push 2026-08-07 | Java, browser UI, optional reconciliation services | Local desktop/server | CSV/export only | Manual transformation lineage must be retained; external reconciliation can disclose data | adopt | [Official repository](https://github.com/OpenRefine/OpenRefine) |
| Dedupe | Identity resolution | Supervised probabilistic record linkage | MIT | Last push 2025-07-29 | Python, C extensions, labeled training pairs | Library/batch job | Custom | Requires representative labels and threshold calibration; false merges are costly | borrow | [Official repository](https://github.com/dedupeio/dedupe) |
| Splink | Identity resolution | Probabilistic linkage at scale | MIT | Last push 2026-08-10 | Python, DuckDB/Spark/PostgreSQL backends | Library/batch job | Custom | Model complexity; labeled evaluation required; premature for a small CRM | borrow | [Official repository](https://github.com/moj-analytical-services/splink) |
| Reacher | Email verification | SMTP/domain-level email verification | AGPL-3.0 or commercial | Last push 2026-03-17 | Rust, DNS, SMTP, optional hosted service | Self-hosted/API | Custom | Verification is not permission; SMTP probing, network reputation, dual-license boundary | quarantine | [Official repository](https://github.com/reacherhq/check-if-email-exists) |
| email-sleuth | Email discovery | Guess and test likely email patterns | MIT | Last push 2025-12-20 | Python/Node tooling and network checks | Script/library | Custom | Guessed identity; unknown deliverability; prohibited guessed-email sending | quarantine | [Official repository](https://github.com/buyukakyuz/email-sleuth) |

### 8.4 Agent and workflow control

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| PydanticAI | Agent/workflow | Typed model outputs, tools, approvals, durable integrations, evals | MIT | Last push 2026-08-10 | Python, Pydantic, model providers, optional workflow engines | Library/service | Custom tool | Provider cost/data handling; tool grants; framework unnecessary for deterministic phase 0 | borrow | [Official repository](https://github.com/pydantic/pydantic-ai) |
| LangGraph | Agent/workflow | Stateful graphs, checkpoints, interrupts, durable execution | MIT | Last push 2026-08-10 | Python/JS, SQLite/PostgreSQL checkpoints, model providers | Library/service | Custom; ecosystem connectors | Operational complexity; optional commercial LangSmith; side effects depend on tools | borrow | [Official repository](https://github.com/langchain-ai/langgraph) |
| CrewAI | Agent/workflow | Role-based multi-agent orchestration | MIT | Last push 2026-08-10 | Python, model and tool providers | Library/platform | Custom | Agent autonomy and nondeterminism; tracing/cloud dependencies; no phase-0 need | observe | [Official repository](https://github.com/crewAIInc/crewAI) |
| AutoGen | Agent/workflow | Multi-agent conversations and tool execution | MIT code; CC-BY documentation | Last push 2026-04-15 | Python/.NET, model providers, extensions | Library/studio | Custom | Experimental surfaces, autonomous tool loops, broad provider surface | observe | [Official repository](https://github.com/microsoft/autogen) |
| Activepieces | Agent/workflow | Visual workflows, connectors, human approval, agents | MIT core plus commercial enterprise modules | Last push 2026-08-10 | Node.js, PostgreSQL, Redis/queues, many connectors | Self-hosted/cloud | Native pieces | Connector blast radius, mixed-license boundary, secret and worker isolation | observe | [Official repository](https://github.com/activepieces/activepieces) |
| n8n | Agent/workflow | Visual automation and agent workflows | Sustainable Use License plus enterprise modules | Last push 2026-08-10 | Node.js, database, queue mode, many connectors | Self-hosted/cloud | Native node | Source-available, not OSI open source; broad credentials; easy direct writes/sends | observe | [Official repository](https://github.com/n8n-io/n8n) |
| Windmill | Agent/workflow | Scripts, flows, workers, approvals, scheduling | AGPL core, Apache clients, proprietary enterprise modules | Last push 2026-08-10 | Rust/TypeScript, PostgreSQL, workers, optional enterprise images | Self-hosted/cloud | Custom scripts | Mixed licenses/images, broad code execution, secrets and worker isolation | observe | [Official repository](https://github.com/windmill-labs/windmill) |
| Huginn | Agent/workflow | Event agents, schedules, feeds, and webhooks | MIT | Last push 2026-08-08 | Ruby on Rails, database, worker queue | Self-hosted service | Webhook/custom | Legacy operational stack; agents can call arbitrary endpoints and send notifications | borrow | [Official repository](https://github.com/huginn/huginn) |

### 8.5 CRM and outreach references

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| HubSpot API Python SDK | CRM integration | Official generated CRM API client | Apache-2.0 | Last push 2026-02-24 | Python, HTTP/OpenAPI runtime | Application library | Native | SDK does not supply dedupe, idempotency policy, approval, or webhook validation | adopt | [Official repository](https://github.com/HubSpot/hubspot-api-python) |
| HubSpot API Node SDK | CRM integration | Official generated CRM API client | Apache-2.0 | Last push 2026-07-01 | Node.js, HTTP/OpenAPI runtime | Application library | Native | Same application-control duties; generated surface can change by version | adopt | [Official repository](https://github.com/HubSpot/hubspot-api-nodejs) |
| Twenty | CRM reference | Modern open CRM and workflow platform | Mostly AGPL-3.0; MIT SDKs; commercial files | Last push 2026-08-10 | TypeScript, PostgreSQL, Redis, workers | Self-hosted/cloud | Alternative CRM, not adapter | Duplicates HubSpot; migration and mixed-license burden; broad platform scope | observe | [Official repository](https://github.com/twentyhq/twenty) |
| Frappe CRM | CRM reference | Open CRM on Frappe framework | AGPL-3.0 | Last push 2026-08-10 | Python, JavaScript, MariaDB, Redis, Frappe | Self-hosted/cloud | Alternative CRM | Duplicates HubSpot; heavy platform and operational migration | observe | [Official repository](https://github.com/frappe/crm) |
| EspoCRM | CRM reference | Open CRM | AGPL-3.0 | Last push 2026-08-10 | PHP, SQL database, web server | Self-hosted | Alternative CRM | Duplicates HubSpot; extension and migration burden | observe | [Official repository](https://github.com/espocrm/espocrm) |
| Mautic | Outreach reference | Marketing automation and campaigns | GPL-3.0 | Last push 2026-08-10 | PHP, database, queues, mail provider | Self-hosted | Connector/custom | Designed for campaign execution; sending, tracking, consent, and deliverability side effects | quarantine | [Official repository](https://github.com/mautic/mautic) |
| listmonk | Outreach reference | Mailing-list and campaign manager | AGPL-3.0 | Last push 2026-08-10 | Go, PostgreSQL, SMTP/provider | Self-hosted | Export/custom | Sending-first system; list consent, unsubscribes, and deliverability obligations | quarantine | [Official repository](https://github.com/knadh/listmonk) |

### 8.6 Intelligence, observability, evaluation, and storage

| Project | Category | Function | License | Activity | Dependencies | Deployment | HubSpot fit | Principal risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| RSSHub | Market intelligence | Generates feeds from thousands of sites/routes | AGPL-3.0 | Last push 2026-08-10 | Node.js, Redis optional, route-specific services/proxies | Self-hosted/public instances | Custom | Route fragility, private APIs, login/proxy support, source-specific terms | observe | [Official repository](https://github.com/DIYgod/RSSHub) |
| Miniflux | Market intelligence | Feed reader and ingestion API | Apache-2.0 | Last push 2026-08-09 | Go, PostgreSQL | Self-hosted service | Custom/export | Feed content rights and retention still require source-level review | adopt | [Official repository](https://github.com/miniflux/v2) |
| FreshRSS | Market intelligence | Feed aggregation and reading | AGPL-3.0 | Last push 2026-08-10 | PHP, SQL database, web server | Self-hosted | Custom/export | More UI/platform than required; same feed-rights obligations | observe | [Official repository](https://github.com/FreshRSS/FreshRSS) |
| changedetection.io | Market intelligence | Webpage-change detection and notifications | Apache-2.0 | Last push 2026-08-07 | Python, datastore, optional Playwright and Apprise | Self-hosted/cloud | Webhook/custom | Browser steps, proxying, notifications, false changes, and route-level terms | adopt | [Official repository](https://github.com/dgtlmoon/changedetection.io) |
| Langfuse | Observability | LLM traces, prompts, evaluations, datasets | MIT core plus commercial enterprise modules | Last push 2026-08-10 | PostgreSQL, ClickHouse, Redis, object storage | Self-hosted/cloud | Indirect | Heavy operations, sensitive trace retention, mixed-license features | observe | [Official repository](https://github.com/langfuse/langfuse) |
| OpenLIT | Observability | OpenTelemetry-based LLM observability and evaluations | Apache-2.0 | Last push 2026-08-10 | OpenTelemetry, database/dashboard stack | Self-hosted/cloud options | Indirect | Telemetry may capture PII/prompts; operational overhead | borrow | [Official repository](https://github.com/openlit/openlit) |
| Phoenix | Observability/evaluation | AI tracing, evaluation, datasets, experiments | Elastic License 2.0 | Last push 2026-08-10 | Python, storage, OpenTelemetry, optional cloud | Local/self-hosted/cloud | Indirect | Source-available rather than OSI open source; trace PII and storage burden | observe | [Official repository](https://github.com/Arize-ai/phoenix) |
| Ragas | Evaluation | Retrieval and agent evaluation framework | Apache-2.0 | Last push 2026-02-24 | Python, model/embedding providers, datasets | Library/service | Indirect | Model-based evaluator bias/cost; benchmarks need labeled SheperD cases | borrow | [Official repository](https://github.com/vibrantlabsai/ragas) |
| pgvector | Retrieval/storage | Vector similarity in PostgreSQL | PostgreSQL License | Last push 2026-08-08 | PostgreSQL extension | Existing/self-hosted PostgreSQL | Indirect | Premature retrieval layer; embedding provenance and deletion complexity | observe | [Official repository](https://github.com/pgvector/pgvector) |
| Qdrant | Retrieval/storage | Dedicated vector database | Apache-2.0 | Last push 2026-08-10 | Rust service, persistent storage | Self-hosted/cloud | Indirect | Adds a separate database, backup, access-control, and deletion surface | observe | [Official repository](https://github.com/qdrant/qdrant) |
| Chroma | Retrieval/storage | Embedding database and retrieval | Apache-2.0 | Last push 2026-08-07 | Python/Rust components, persistence, embedding providers | Embedded/server/cloud | Indirect | Extra persistence and embedding governance without a measured requirement | observe | [Official repository](https://github.com/chroma-core/chroma) |

**Baseline catalog count: 47 canonical repositories.** The expansion in section 17 adds 75 canonical repositories/tools (**122 total**). “Adopt” means preferred if and when an approved implementation begins; it does not change this dossier's research-only status.

## 9. Exact-commit deep audits

These are static repository audits, not runtime certifications. A clean architecture or test suite does not establish data rights, legal compliance, production security, or fitness for SheperD.

### 9.1 Audit index

| Repository | Exact audited commit | Commit date | Release signal at audit | Gate result | SheperD decision |
|---|---|---|---|---|---|
| OpenOutreach | [2834d5ac887fc8b9c38ef6621aa5650ae421fbf6](https://github.com/eracle/OpenOutreach/tree/2834d5ac887fc8b9c38ef6621aa5650ae421fbf6) | 2026-08-07 | No tagged release identified | fail: prohibited operational actions | quarantine runtime |
| YALC | [ffc6e372d68270f26478160d11c5999df982f37b](https://github.com/Othmane-Khadri/YALC-the-GTM-operating-system/tree/ffc6e372d68270f26478160d11c5999df982f37b) | 2026-06-26 | v0.13.4 | fail for current runtime; reusable patterns | borrow adapters and previews |
| OpenFang | [acf2587e46be174c10200489c9a2d23a39a98aeb](https://github.com/RightNow-AI/openfang/tree/acf2587e46be174c10200489c9a2d23a39a98aeb) | 2026-05-12 | v0.6.9 | conditional | borrow approval and audit patterns |
| OneShot GTM | [989802edb81b8ae6c8c44263e1588cdd042ad91c](https://github.com/oneshot-agent/oneshot-gtm/tree/989802edb81b8ae6c8c44263e1588cdd042ad91c) | 2026-06-24 | v0.6.0 | fail: send/cadence actions | borrow receipts and idempotency |
| B2B SDR Agent Template | [e71bfd4da4a56153ab5ef05a4bd684d370b8c90c](https://github.com/iPythoning/b2b-sdr-agent-template/tree/e71bfd4da4a56153ab5ef05a4bd684d370b8c90c) | 2026-07-10 | whatsapp-onboarding-v0.5 tag | fail: broad external actions | quarantine |
| Crawl4AI | [7e801521428ee12509994d39151006f64055ebe3](https://github.com/unclecode/crawl4ai/tree/7e801521428ee12509994d39151006f64055ebe3) | 2026-07-15 | README identifies v0.9.2 | conditional | adopt restricted profile |
| Firecrawl | [5b21116fd818283e0d4dfc5b23f754ed0b128361](https://github.com/firecrawl/firecrawl/tree/5b21116fd818283e0d4dfc5b23f754ed0b128361) | 2026-08-10 | Active tagged-release practice | conditional | observe |
| PydanticAI | [640d5171fe5795e58553b5af414cbcac3e0c7673](https://github.com/pydantic/pydantic-ai/tree/640d5171fe5795e58553b5af414cbcac3e0c7673) | 2026-08-10 | v2.27.0 | pass for no-tool profile | borrow typed-control patterns |
| LangGraph | [d56666f7fbf0d380ad84cdf0cbe5aa48ab0cc086](https://github.com/langchain-ai/langgraph/tree/d56666f7fbf0d380ad84cdf0cbe5aa48ab0cc086) | 2026-08-10 | Python package 1.2.10 | pass for interrupted proposal graph | borrow |
| Activepieces | [d05fd537ad3651dc3038c8ce4541635d96c07701](https://github.com/activepieces/activepieces/tree/d05fd537ad3651dc3038c8ce4541635d96c07701) | 2026-08-10 | Frequent releases | conditional | observe |
| n8n | [c04825d4c4762da827318d7df795728b2ef1133e](https://github.com/n8n-io/n8n/tree/c04825d4c4762da827318d7df795728b2ef1133e) | 2026-08-10 | Frequent releases | conditional; not OSI open source | observe |
| Splink | [e22dacdda967988fe701368d5bc21a54eebba0cf](https://github.com/moj-analytical-services/splink/tree/e22dacdda967988fe701368d5bc21a54eebba0cf) | 2026-08-10 | 5.0.0.dev4 in tree | pass | borrow after benchmark |
| HubSpot API Python SDK | [a2a528a97f4c1131d7f65d0303bfbd2e523a8eba](https://github.com/HubSpot/hubspot-api-python/tree/a2a528a97f4c1131d7f65d0303bfbd2e523a8eba) | 2026-02-24 | v.10.0.0 tag | pass as client library | adopt at protected boundary |
| changedetection.io | [aac6fcfa594f17511b8ff73e5eaa4f6c33899de0](https://github.com/dgtlmoon/changedetection.io/tree/aac6fcfa594f17511b8ff73e5eaa4f6c33899de0) | 2026-08-04 | 0.55.8 | conditional | adopt restricted profile |
| RSSHub | [6a992800aaddb78734506a7ca1f8dd7f001460e5](https://github.com/DIYgod/RSSHub/tree/6a992800aaddb78734506a7ca1f8dd7f001460e5) | 2026-08-10 UTC snapshot | No release tag relied upon | conditional per route | observe |
| Langfuse | [2aa50493a3c7bc3e45ff64f06be051567da15743](https://github.com/langfuse/langfuse/tree/2aa50493a3c7bc3e45ff64f06be051567da15743) | 2026-08-10 | v4.6.0 | conditional | observe |

### 9.2 OpenOutreach

- **Architecture and state:** Django application with local SQLite persistence and explicit campaign, lead, email, and follow-up state.
- **Dependencies and connectors:** SMTP/IMAP mailbox access and BetterContact-powered contact discovery are material dependencies. The repository also contains an optional freemium promotional-email path from the user's mailbox.
- **Tests and security:** Automated tests are present. No evidence in the audited tree converts mailbox-level access and automated sends into a least-privilege research profile.
- **External side effects:** Email delivery, inbox polling, and follow-up execution are core product behavior rather than isolated proposal outputs.
- **Decision:** quarantine the runtime. The data model for lead and sequence state is useful reference material, but using the product would collapse research, approval, and sending into one trust boundary.

### 9.3 YALC

- **Architecture and state:** TypeScript/Node operating system with declarative resources, Drizzle-backed SQLite/Turso state, manifests, adapters, and a preview/commit model.
- **Dependencies and connectors:** Reviewed integrations include HubSpot, People Data Labs, Brevo, Unipile, Crustdata, Firecrawl, FullEnrich, Instantly, and Anthropic.
- **Tests and security:** Tests, CI, and security documentation were present at the audited SHA.
- **External side effects:** High-confidence auto-commit paths and email/LinkedIn actions conflict with SheperD's explicit human-decision boundary. Each adapter also brings separate terms, credentials, retention, and subprocessors.
- **Decision:** borrow the declarative adapter contract, dry-run preview, manifest, and change-set concepts. Do not adopt the runtime or Unipile/LinkedIn execution path.

### 9.4 OpenFang

- **Architecture and state:** Rust agent operating system with SQLite-backed memory/state, vector capabilities, schedulers, approval modules, and Merkle-style audit structures.
- **Dependencies and connectors:** Supports model providers and broad “hand” capabilities, including lead and collection activities.
- **Tests and security:** Large test surface and security documentation were present. The README identified v0.6.9 while the security policy named support for 0.3.x, creating an unresolved support-policy mismatch at the snapshot.
- **External side effects:** General-purpose autonomous hands can exceed the narrow research mandate unless tools are removed and approvals are mandatory.
- **Decision:** borrow its tamper-evident audit, permission, approval, and capability-separation patterns. Observe runtime maturity before considering any deployment.

### 9.5 OneShot GTM

- **Architecture and state:** Bun/TypeScript service with local SQLite state, jobs, queues, receipts, approval concepts, and idempotency controls.
- **Dependencies and connectors:** Core functionality calls a proprietary pay-per-use OneShot API with signed requests/receipts and a USDC payment model.
- **Tests and security:** Tests and CI were present. Queue/receipt mechanics are unusually relevant to safe proposal handling.
- **External side effects:** Email, SMS, and voice delivery plus automatic cadences are product capabilities. A force option can bypass normal scale controls.
- **Decision:** borrow signed receipt, approval queue, retry, and idempotency patterns. Quarantine the runtime and all communications actions.

### 9.6 B2B SDR Agent Template

- **Architecture and state:** Primarily scripts, templates, and operating instructions rather than an independently bounded application.
- **Dependencies and connectors:** Depends on OpenClaw plus CRM, Jina, email, WhatsApp, and Telegram integrations.
- **Tests and security:** The audited material did not demonstrate a control plane proportionate to its connector and credential surface.
- **External side effects:** Automated CRM and messaging actions are intertwined with the workflow.
- **Decision:** quarantine. The template accelerates a demo, not a fail-closed production system.

### 9.7 Crawl4AI

- **Architecture and state:** Python extraction library/service using browser automation and local caches/state, with structured extraction and optional model use.
- **Dependencies and connectors:** Playwright/Patchright, SQLite, browser binaries, and optional model providers.
- **Tests and security:** Substantial tests, CI, and security work are present. The project's published security history includes fixes for serious RCE, SSRF, and local-file issues, so version pinning and network isolation are mandatory.
- **External side effects:** Browser hooks, interactions, stealth options, proxies, and unrestricted target URLs materially expand the attack and compliance surface.
- **Decision:** adopt only a restricted profile: exact version pin, allowlisted public domains, loopback/authenticated service, private-network denial, no stealth, no account login, no arbitrary hooks, immutable fetch receipts, and rate limits.

### 9.8 Firecrawl

- **Architecture and state:** Multi-service crawl platform with queues, workers, browsers, structured extraction, and managed/self-hosted modes.
- **Dependencies and connectors:** Redis, PostgreSQL, browser workers, Node/Python components, optional model providers, and a hosted API path.
- **Tests and security:** Large test and CI surface. The AGPL core and separately permissive SDKs require an architecture-specific license review.
- **External side effects:** Proxying, browser interactions, webhook/callback behavior, and managed-service data transfer are all configurable risks.
- **Decision:** observe. Scrapy and restricted Crawl4AI cover the pilot with less operational and license burden.

### 9.9 PydanticAI

- **Architecture and state:** Typed Python agent library centered on Pydantic schemas, model abstraction, tools, durable execution integrations, evaluations, and OpenTelemetry.
- **Dependencies and connectors:** Multiple model providers plus optional Temporal, Prefect, and DBOS integrations.
- **Tests and security:** Extensive tests and CI were present. No root security policy was identified at the audited SHA.
- **External side effects:** Side effects arise from user-granted tools rather than being mandatory. Model providers still create data-processing, retention, and cost dependencies.
- **Decision:** borrow typed result schemas, evaluation cases, and explicit tool approval. A first pilot should use deterministic functions; add PydanticAI only if structured model calls become materially complex.

### 9.10 LangGraph

- **Architecture and state:** Stateful graph runtime with durable checkpoints, explicit interrupts, resumability, and SQLite/PostgreSQL persistence.
- **Dependencies and connectors:** Python/JavaScript packages, model providers, checkpointers, and optional LangSmith services.
- **Tests and security:** Strong tests and CI. No root security policy was identified at the audited SHA.
- **External side effects:** Safety depends entirely on node/tool definitions and correct interrupt placement.
- **Decision:** borrow checkpoint and interrupt patterns. Use only if a measured multi-step workflow cannot be represented as ordinary deterministic state transitions.

### 9.11 Activepieces

- **Architecture and state:** TypeScript visual workflow platform with versioned flows, queues/workers, connectors, agents, and human-approval actions.
- **Dependencies and connectors:** PostgreSQL, queues/Redis, HubSpot, Apollo, email, and a large connector catalog.
- **Tests and security:** Broad tests and CI are present. The tree separates MIT community code from commercially licensed enterprise modules; no root security policy was identified in the audited tree.
- **External side effects:** Connector credentials and workers can mutate CRM or send messages unless deployment permissions are aggressively restricted.
- **Decision:** observe for a later orchestration layer. It is unnecessary for a proposal-only pilot and increases the credential blast radius.

### 9.12 n8n

- **Architecture and state:** Mature visual automation platform with workflows, queue mode, tool approval features, and a very large connector/action ecosystem.
- **Dependencies and connectors:** Node.js, database and queue workers, HubSpot, email, AI tools, and more than a thousand actions.
- **Tests and security:** Large test suite, CI, and a documented security process.
- **License:** Sustainable Use License plus enterprise-licensed modules. It is source-available, not OSI open source.
- **Decision:** observe. It can express the workflow, but its license, connector breadth, secret surface, and ease of direct side effects make it a poor default for phase 0.

### 9.13 Splink

- **Architecture and state:** Probabilistic linkage toolkit supporting DuckDB, Spark, and PostgreSQL-style execution with explainable linkage parameters.
- **Dependencies and connectors:** Python and analytical backends; no direct CRM or sending connector.
- **Tests and security:** Tests, CI, and CodeQL were present. No root security policy was identified at the audited SHA.
- **Model risk:** Thresholds, blocking rules, and training assumptions can create false merges. A false merge can contaminate permission, DNC, partner, and opportunity associations.
- **Decision:** borrow after deterministic normalized-domain/legal-name matching reaches a measured ceiling and a labeled duplicate/non-duplicate set exists.

### 9.14 HubSpot API Python SDK

- **Architecture and state:** Official generated OpenAPI client exposing HubSpot CRM objects and endpoints.
- **Dependencies and connectors:** HTTP/OpenAPI runtime with application-managed authentication.
- **Tests and security:** Basic tests and CI are present. No root security policy was identified at the audited SHA.
- **Control gap:** The SDK does not supply SheperD-specific account-type rules, deduplication, optimistic concurrency, idempotency, approval, retry policy, association semantics, or inbound request validation.
- **Decision:** adopt only inside a protected adapter that accepts an approved HubSpotChangeProposal. Until write authority is separately granted, use it for schema/read validation or dry-run construction only.

### 9.15 changedetection.io

- **Architecture and state:** Python application that snapshots pages, computes changes, and can notify through Apprise/webhooks; Playwright browser steps are optional.
- **Dependencies and connectors:** Local datastore, browser workers when enabled, proxies, notification providers, and webhooks.
- **Tests and security:** Extensive tests, CI, and CodeQL were present. No root security policy was identified at the audited SHA.
- **External side effects:** Notifications, webhooks, scripted browser steps, proxies, and noisy layout changes can create unreviewed actions or false signals.
- **Decision:** adopt a restricted profile for official pages: static fetch where possible, notifications/webhooks off, no login or browser scripts, rate limits, content selectors, and SourceRecord receipts.

### 9.16 RSSHub

- **Architecture and state:** Node.js route framework that converts more than 5,000 site patterns into feeds, with optional Redis cache and public/self-hosted instances.
- **Dependencies and connectors:** Route-specific websites, private APIs, logins, proxies, headless browsers, and caches vary materially.
- **Tests and security:** Large test suite, CI, CodeQL, and security guidance are present.
- **Data-rights risk:** There is no safe project-wide approval. Each route has different terms, authentication, stability, and provenance, and public instances add another trust boundary.
- **Decision:** prefer official RSS plus Miniflux. Consider an RSSHub route only after route-level rights and stability review, then self-host it with a pinned commit.

### 9.17 Langfuse

- **Architecture and state:** LLM trace, prompt, dataset, experiment, and evaluation platform with MIT core and commercial enterprise modules.
- **Dependencies and connectors:** PostgreSQL, ClickHouse, Redis, object storage, workers, and model/telemetry SDKs.
- **Tests and security:** Extensive CI, tests, security documentation, and active releases.
- **Data risk:** Traces can retain prompts, contact data, evidence, and model outputs across several persistence layers. Deletion and access control therefore become first-order requirements.
- **Decision:** observe. Append-only receipts and ordinary database records are sufficient for the pilot; add Langfuse only when run volume and debugging cost justify its operational footprint.

## 10. Licensed-data gap analysis

### 10.1 What public U.S. sources can and cannot establish

The [Census USA Trade Online availability guide](https://www.census.gov/foreign-trade/reference/products/UTOAvailableData.pdf) describes official aggregate trade statistics by product, geography, transport mode, customs district, port, value, weight, and containerized-vessel measures. It also explains the confidentiality boundary around business-level importer/exporter identity. This makes Census appropriate for market sizing and trend context, not for producing a named importer target list or company TEU estimate.

The [FMC detention and demurrage page](https://www.fmc.gov/detention-and-demurrage/) reports aggregate carrier data and regulatory material. It does not identify which prospect has a valid invoice or recovery. The [FMC charge-complaint procedure](https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/) requires transaction-specific evidence such as bills of lading, invoices, and payment material; market signals cannot substitute for that evidence.

Regulatory logic must be versioned and reviewed. For example, the FMC reported that the D.C. Circuit [set aside 46 CFR 541.4](https://www.fmc.gov/articles/u-s-court-of-appeals-issues-decision-in-case-on-demurrage-and-detention-billing-practices/) in 2025. This dossier makes no legal conclusion about a particular invoice, carrier, or outreach practice.

| Public source | Safe use | Cannot establish |
|---|---|---|
| Census trade statistics | Industry, commodity, port, mode, weight, value, and containerized-volume trends | Named importer, decision-maker, company TEU, D&D exposure, permission |
| FMC D&D reporting | Carrier-level and regulatory trend context | Prospect-specific charges, invoice validity, recoverability |
| FMC decisions and guidance | Trigger legal/regulatory review and dated intelligence signals | Automatic legal rule, account qualification, outreach claim |
| Port, terminal, rail, carrier, and agency notices | SignalEvent with geography, event time, and cited source | Which account experienced delay or incurred a recoverable charge |

### 10.2 Importer and shipment-volume providers

Coverage and quality claims below are **vendor_claim** until SheperD validates a sample. Prices are public list prices observed on 2026-08-10; taxes, contracts, usage caps, exports, API rights, and retention terms may differ. “Unknown” means no current official public price was found.

| Provider | Officially described coverage | Public price at snapshot | Access and terms boundary | Potential SheperD use | Decision |
|---|---|---|---|---|---|
| ImportYeti | U.S. ocean import records with company/supplier views, filters, and enterprise API; TEU-oriented filtering is described | Free $0 human search; Professional $50/month billed annually ($600/user/year), or $130 for 30 days; Enterprise starts $1,000/organization/month | API is enterprise; free browser access is not automation authorization | Lowest-friction human benchmark for importer identity, aliases, and approximate volume | benchmark candidate; no automation without contract |
| ImportGenius | U.S. Customs maritime bills of lading plus international datasets and company/shipment search | USA Essentials Flex starts $229/month; USA Pro Flex starts $449/month; Global Enterprise starts $1,999/month | Search/export caps vary; API is enterprise/custom | Compare BOL-level company, consignee, commodity, and shipment histories | obtain sample and rights schedule |
| Descartes Datamyne | Daily U.S. BOL data, standardized company names, TEUs, HS codes, and described contact fields; U.S. history to 2004 | unknown; contact sales | Contract must define API/bulk export, derivative records, retention, and CRM use | Enterprise benchmark for standardized identities and volume | quote only after pilot rubric is fixed |
| Panjiva by S&P Global | Large transaction and company graph with importer/exporter, product, trade, and company enrichment | unknown; request demo | Enterprise license and delivery terms required | Broad international coverage and company relationships | evaluate only against a fixed test set |
| Trademo data license | Standardized customs, bill-of-lading, shipping, and commercial-invoice datasets; vendor states 3B+ shipments | unknown; talk to sales | Site terms prohibit automated scraping; only a contracted data/API license is eligible | International trade transaction comparison | do not scrape; request licensed sample only |
| PIERS by S&P Global | Detailed BOL-level U.S. import/export data, standardized company details, U.S. history from 2003, and international markets | unknown; request demo | Enterprise license; data delivery and downstream-use rights must be explicit | Comparable BOL-level importer and volume source | evaluate with Panjiva/Datamyne samples, not by brand |
| Global Trade Atlas by S&P Global | Official monthly bilateral merchandise statistics by commodity/country and additional aggregate dimensions | unknown; request demo | Aggregate trade-statistics subscription, not inherently company-level prospect data | Macro market intelligence and industry/commodity trend validation | observe for intelligence; not an importer-list substitute |
| Veson Oceanbolt | Inferred vessel, port-call, voyage, commodity, congestion, and trade-flow analytics | unknown; request demo | Inferred maritime-flow methodology and API terms require review | Port congestion, turnaround, and bulk trade SignalEvents | observe; not U.S. importer identity evidence |

Official pricing and product sources: [ImportYeti pricing](https://www.importyeti.com/pricing/supply-chain?source=survey), [ImportYeti API](https://www.importyeti.com/yeti-api), [ImportYeti filters](https://www.importyeti.com/filter-guide), [ImportGenius pricing](https://w3.importgenius.com/pricing), [Descartes Datamyne](https://www.datamyne.com/our-product/datamyne-pricing/), [Panjiva](https://www.spglobal.com/market-intelligence/en/solutions/products/panjiva-supply-chain-intelligence), [Trademo data licensing](https://www.trademo.com/data-license), [Trademo terms](https://www.trademo.com/terms), [PIERS](https://www.spglobal.com/market-intelligence/en/solutions/products/resources/piers-request), [Global Trade Atlas](https://www.spglobal.com/market-intelligence/en/solutions/products/maritime-global-trade-atlas), and [Veson data and analytics](https://veson.com/products/data-and-analytics/).

#### Volume-evidence controls

Provider “TEU” values are not interchangeable. Before SheperD stores or ranks on volume, the contract and benchmark must establish:

- whether the value is observed container count, normalized TEU, inferred TEU, shipment count, weight-derived proxy, or a provider model;
- treatment of forty-foot containers, partial loads, less-than-container-load cargo, blanks, corrections, and duplicate BOL versions;
- master versus house bills, NVOCCs, notify parties, beneficial cargo owners, consignee aliases, and freight-forwarder records;
- import date basis, rolling window, country/mode coverage, excluded shipments, and historical revisions;
- confidence interval or quality flag when the provider supplies one;
- right to retain raw rows, derived annual estimates, and provider identifiers in HubSpot or the research store.

The normalized field should be **estimated_teu_value** plus **estimated_teu_method**, **period_start**, **period_end**, **coverage**, **source_id**, **evidence_status**, and **confidence**. A missing or incomparable estimate remains unknown.

### 10.3 Contact and company-enrichment providers

An email finder or verifier does not establish identity, permission, legitimate purpose, DNC clearance, or compliance. A vendor's “valid” result is a vendor claim about deliverability at a point in time.

| Provider | Officially described capability | Public price at snapshot | Material terms/data issue | Potential pilot role | Decision |
|---|---|---|---|---|---|
| Apollo | Company/person search, enrichment, contact data, and APIs | Plan price unknown from an accessible official static source; API enrichment is documented at roughly 1–9 credits/person depending on data returned | Terms permit bounded internal B2B use but prohibit scraping; contributor features can involve customer contact/mailbox data | Coverage comparison only with contributor/mailbox features off | legal/privacy review before sample |
| People Data Labs | Person and company APIs and bulk/data-license products | Free $0/100 records monthly with obfuscation; Person Pro starts $98/month for 350 records; Company Pro starts $100/month for 1,000 records; enterprise custom | Data license, purpose, output retention, deletion, and source lineage need contract review | Transparent API benchmark for company and person matching | benchmark candidate after D2 approval |
| Hunter | Domain search, email finder, and email verification | Free $0/50 credits monthly; Starter $34/month billed annually; Growth $104/month; Scale $209/month; enterprise custom | Finder/verification is not permission; “unknown” verifier result must stay unknown | Narrow email finder/verifier comparison after account and person approval | benchmark candidate, no sending |
| BetterContact | Multi-vendor contact waterfall and email verification | Starter $15/month for 200 credits; Pro $49/month for 1,000; Enterprise from $799/month | Each waterfall vendor/subprocessor expands provenance, deletion, and contract obligations | Coverage benchmark only when subprovider lineage is available | hold pending DPA/subprocessor review |
| Prospeo | Email finder, verifier, enrichment, APIs, and integrations | Free 100 credits/month; current paid amount unknown from the accessible official pricing material | Provider validity claims require validation; terms, retention, and permitted CRM use need review | Small comparison sample | observe |
| Explorium | Business/company/person data and enrichment marketplace | Free trial $0/100 credits; Starter $99.99 for 2,500; Growth $749.99 for 25,000; Scale $7,500 for 500,000; enterprise custom | Credit cost varies by enrichment; credits have stated duration/nonrefund conditions; source-level lineage varies by dataset | Broad data-coverage benchmark if a specific dataset wins on evidence | observe until narrower vendors fail |

Official sources: [Apollo API credit documentation](https://docs.apollo.io/docs/api-pricing), [Apollo terms](https://www.apollo.io/terms), [Apollo credit guide](https://www.apollo.io/pricing/about-credits), [People Data Labs person pricing](https://www.peopledatalabs.com/pricing/person), [People Data Labs account guide](https://docs.peopledatalabs.com/docs/create-an-account), [Hunter pricing](https://hunter.io/pricing/), [Hunter verifier](https://hunter.io/email-verifier), [BetterContact pricing](https://bettercontact.rocks/pricing/), [BetterContact DPA](https://bettercontact.rocks/dpa/), [Prospeo plans](https://help.prospeo.io/en/article/plans-and-pricing-overview-cdloq9/), [Prospeo pricing](https://prospeo.io/pricing), [Explorium pricing](https://www.explorium.ai/pricing/), and [Explorium credit details](https://www.explorium.ai/credit-details/).

### 10.4 Provider evaluation protocol

No provider should be selected by row count or demo screenshots. Use one immutable, pre-labeled benchmark:

1. Obtain Michael/Ric approval for the D2 evaluation purpose, fields, provider, test size, retention, and deletion date.
2. Execute a contract/DPA review covering automation/API rights, internal derived use, HubSpot storage, export limits, source lineage, subprocessors, model training, sale/sharing, breach notice, correction, deletion, and termination.
3. Prepare 50 known companies spanning clear importers, aliases, non-importers, partners/NVOCCs, and deliberately ambiguous identities. Keep expected identities and observed shipment evidence sealed until scoring.
4. Submit only the minimum necessary fields. Do not ingest results into HubSpot.
5. Score exact company match, false match, alias resolution, observed period coverage, TEU-method transparency, missingness, revision stability, decision-maker title/person precision, email status agreement, provenance, and cost per accepted record.
6. Preserve disputed and unknown results. Never let one provider corroborate itself through a downstream reseller.
7. Delete the test extract on schedule and retain only permitted aggregate evaluation results and immutable procurement receipts.

The initial importer benchmark should start with manual ImportYeti review because the public cost and access boundary are transparent. This is a comparison candidate, not an endorsement or automation permission. For contacts, People Data Labs and Hunter provide the clearest narrow comparison surfaces; Apollo, BetterContact, Prospeo, and Explorium remain useful challengers subject to terms and provenance.

## 11. Recommended SheperD stack

### 11.1 Minimal target stack

| Layer | Recommended default | Deferred alternatives | Reason for deferral |
|---|---|---|---|
| Object contracts | Strict typed models in the implementation language | Full agent framework | Deterministic schemas and state transitions are sufficient initially |
| Operational store | Existing PostgreSQL if already approved; otherwise local SQLite for an isolated pilot | New distributed databases | One bounded writer and ordinary relational constraints are enough |
| Evidence receipts | Append-only JSONL or database rows with hashes | Langfuse/Phoenix | Trace platform adds sensitive persistence and operations |
| Static collection | Simple HTTP client/Scrapy | Firecrawl | Lower side-effect, license, and infrastructure burden |
| Browser collection | Restricted Crawl4AI only when static fetch fails | browser-use/general browser agent | Browser agents are broader than the task |
| Feed monitoring | Official RSS into Miniflux | RSSHub/FreshRSS | Prefer direct publisher feeds and simpler operations |
| Page monitoring | Restricted changedetection.io | General browser workflow | Narrow diffing meets the need |
| Document parsing | Docling | Unstructured service | Local, narrow parser first |
| Entity resolution | Domain/legal-name/stable-ID rules | Splink/Dedupe | Probabilistic linkage needs labeled evidence |
| AI drafting | Single structured model call, no tools | PydanticAI/LangGraph/CrewAI | Add a framework only after workflow complexity is measured |
| Search | PostgreSQL text search and explicit metadata filters | pgvector/Qdrant/Chroma | No demonstrated semantic-retrieval requirement |
| CRM | Official HubSpot SDK behind proposal adapter | Alternate CRM or generic automation platform | HubSpot is the intended source of truth |

### 11.2 Deterministic gates before AI

Before any model call, code should produce explicit pass/fail/unknown results for:

- account type and stable identity;
- duplicate/alias status;
- source and reuse rights;
- evidence freshness;
- target segment;
- importer evidence and volume-method comparability;
- permission and DNC state;
- prohibited-source and prohibited-claim checks;
- stage and association authority.

The model may explain the gate result and draft from approved evidence. It cannot change a result, infer a missing permission, or omit conflicting evidence.

### 11.3 HubSpot interface

The adapter accepts an approved HubSpotChangeProposal and returns a receipt. It must:

- address companies, contacts, opportunities, activities, and partner/referral associations through stable object IDs;
- search/deduplicate by normalized domain and stored external IDs before proposing creation;
- use explicit before/after field diffs and expected current values to prevent silent overwrites;
- separate importer and channel-partner account types and preserve the introduction association;
- batch conservatively, handle 429 responses, retry only safe operations, and use application-level idempotency keys;
- request only the scopes needed for the approved object/operation;
- log request class, object IDs, response code, attempt, and result without secrets or unnecessary PII;
- retain failed and partial outcomes as exceptions, never as success;
- use [CRM Associations v4](https://developers.hubspot.com/docs/api-reference/crm-associations-v4/guide) for explicit labeled relationships where applicable;
- follow HubSpot's [platform usage guidance](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines).

For inbound HubSpot requests, current [request validation](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/request-validation) uses the v3 signature: read **X-HubSpot-Signature-v3**, reject timestamps older than five minutes, apply the documented URI decoding rules, concatenate method + URI + body + timestamp, compute HMAC-SHA-256 with the client secret, Base64-encode it, and compare in constant time. Reverify this algorithm against the current official page when implementation begins.

No adapter write is authorized by this dossier. The first implementation must stop after rendering a dry-run proposal.

### 11.4 Market-intelligence branch

The weekly brief should be evidence-first:

1. Ingest approved FMC, Census, port, terminal, rail, carrier, and trade-publication sources.
2. Normalize each item into a SignalEvent with event time, publication time, geography, entities, source rights, and evidence status.
3. Deduplicate syndications and updates while retaining correction lineage.
4. Propose AccountMatch links using explicit identifiers, port/industry overlap, and ambiguity.
5. Summarize the week by signal type, affected market, evidence, uncertainty, and suggested human research question.

Signals that create a timely reason to investigate include new FMC guidance, material port dwell changes, terminal/rail disruptions, announced logistics-footprint changes, or sustained commodity/import shifts. They are not proof that an account incurred D&D or should receive outreach.

## 12. Phased pilot

Each phase requires a named entry decision and an evidence-based exit decision. No phase below authorizes deployment or third-party execution now.

| Phase | Scope | Outputs | Exit gate |
|---|---|---|---|
| 0 — Contract and golden set | Approve object schemas, field dictionary, rights/DNC states, score rubric, and 50-account provider benchmark | Versioned schemas, golden records, failure cases, provider request specification | Ric/Michael approve definitions; every unknown path fails closed; no source-rights ambiguity |
| 1 — Offline source-to-evidence prototype | Use saved/approved sample documents only; normalize SourceRecord, AccountCandidate, EvidencePack, SignalEvent | Immutable receipts, deterministic duplicates, evidence packs, sample weekly brief | 100% lineage; zero silent merges; conflicts/unknowns visible; no network or CRM effects |
| 2 — Bounded live research | After source approval, collect a small allowlisted set and run one licensed provider sample | Up to 25 candidate accounts, provider benchmark, 10 unsent outreach drafts, weekly brief | Human reviewers can reproduce every claim; provider error/unknown rates measured; zero sends/writes |
| 3 — HubSpot dry-run | Read approved schema/records and render change proposals only | Before/after diffs, associations, idempotency keys, retry simulations, approval receipts | Duplicate and partial-failure tests pass; least-privilege scopes approved; still zero mutations |
| 4 — Separately authorized operation | Outside this dossier | A narrowly approved write or send run with rollback/exception handling | Requires new written authorization, legal/compliance review, named operator, and production evidence |

Suggested pilot acceptance metrics:

- 100% of output claims trace to retained source records.
- 100% of records include rights, evidence, permission, DNC, rule/model, and approval states.
- 0 guessed-email sends, LinkedIn automation attempts, follow-ups, or HubSpot mutations.
- 0 false deterministic merges in the golden set.
- Provider match, false-match, unknown, freshness, and cost metrics reported separately.
- Human reviewers agree that draft claims are supported; disagreements are retained, not averaged away.
- Every retry and partial failure terminates in an auditable state.

## 13. Quarantine list

| Item | Blocker | Release condition |
|---|---|---|
| OpenOutreach runtime | Automatic email/follow-up and mailbox-level effects | Not recommended; would require removal of send paths and a new security review |
| YALC runtime, Unipile, and auto-commit actions | LinkedIn/email execution and autonomous commit | Use patterns only; no runtime release proposed |
| OneShot GTM runtime | Proprietary paid API and email/SMS/voice cadences | Use receipts/idempotency patterns only |
| B2B SDR Agent Template | Broad messaging/CRM effects without proportional control plane | Reject as implementation base |
| browser-use and general browser agents | Model-directed navigation, credentials, and arbitrary interactions | Only after a distinct approved browser-use case and isolation design |
| Reacher and email-sleuth operational use | Verification/guessing can be mistaken for identity or permission | Never send based on these results; separate permission evidence required |
| Mautic and listmonk | Sending-first systems | Separate campaign authorization and compliance control system |
| RSSHub unreviewed routes/public instances | Route-specific terms, private APIs, proxies, provenance | Approve one route and self-host pinned code |
| n8n/Activepieces/Windmill production connectors | Broad credentials and direct side effects | Connector allowlist, secret isolation, proposal-only permissions, security review |
| Alternate CRMs | Duplicate source of truth and migration scope | Only if HubSpot is formally replaced |
| Vector databases | No measured semantic-retrieval requirement | Add only after text/filter baseline fails a defined benchmark |
| Any no-license repository | No reuse right | Identifiable compatible license added and reverified |
| LinkedIn scraping/evasion tools | SheperD prohibition and platform rules | No release condition within this project |
| D3 data or unknown source rights | Prohibited or uncontrolled data | No D3; unknown rights must become explicitly approved before collection |
| Guessed-email sending and autonomous follow-up | Explicit policy violation | No release condition within this dossier |

[LinkedIn's prohibited-software guidance](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en), [User Agreement](https://www.linkedin.com/legal/user-agreement), and [Crawling Terms](https://www.linkedin.com/legal/crawling-terms) independently reinforce the project-level prohibition. For email, the [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) states that commercial B2B email is not categorically exempt and that senders retain responsibilities including accurate headers, identification, a postal address, opt-out, and timely suppression. Legal counsel must review any operational outreach design.

## 14. Open decisions before implementation

1. The exact importer ICP filters and measurement window for container volume.
2. Whether TEU is a required admission field, a ranking feature, or an optional research signal.
3. Which BOL party types qualify as the importer/beneficial cargo owner for SheperD.
4. Approved public-source domains, access methods, crawl rates, retention, and evidence storage.
5. D2 procurement owner, DPA requirements, geographic storage constraints, and deletion SLA.
6. HubSpot property internal names, stable external-ID properties, association labels, and field ownership.
7. The authoritative DNC/permission source and how expiry, revocation, and suppression propagate.
8. Human approvers for account admission, score acceptance, draft acceptance, HubSpot mutation, and sending; these are separate decisions.
9. Maximum pilot sample, spend, and model/provider data policy.
10. Correction and appeal workflow when a company, contact, source, or provider disputes a record.

## 15. Dated source register

All sources below were checked on **2026-08-10**. Each canonical repository link in section 8 and each exact commit link in section 9 is part of this register. GitHub activity dates were read as repository metadata; exact-SHA findings were read from the pinned tree. Pricing and terms must be rechecked before procurement or implementation.

### 15.1 Government, regulatory, platform, and legal sources

| Source | Used for | Checked |
|---|---|---|
| [Census USA Trade Online available data](https://www.census.gov/foreign-trade/reference/products/UTOAvailableData.pdf) | Aggregate fields and business-confidentiality boundary | 2026-08-10 |
| [FMC detention and demurrage](https://www.fmc.gov/detention-and-demurrage/) | Aggregate D&D and regulatory context | 2026-08-10 |
| [FMC charge-complaint procedure](https://www.fmc.gov/ocean-shipping-reform-act-of-2022-implementation/guidance-on-charge-complaint-interim-procedure/) | Account-specific evidence boundary | 2026-08-10 |
| [FMC court-decision notice](https://www.fmc.gov/articles/u-s-court-of-appeals-issues-decision-in-case-on-demurrage-and-detention-billing-practices/) | Current-rule change warning | 2026-08-10 |
| [HubSpot request validation](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/request-validation) | V3 inbound signature algorithm | 2026-08-10 |
| [HubSpot platform usage guidance](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines) | Limits, retries, batching, caching, webhooks | 2026-08-10 |
| [HubSpot CRM Associations v4](https://developers.hubspot.com/docs/api-reference/crm-associations-v4/guide) | Labeled account/contact/opportunity/partner links | 2026-08-10 |
| [LinkedIn prohibited software](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en) | Automation prohibition | 2026-08-10 |
| [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement) | Platform-use boundary | 2026-08-10 |
| [LinkedIn Crawling Terms](https://www.linkedin.com/legal/crawling-terms) | Crawler boundary | 2026-08-10 |
| [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) | U.S. commercial-email baseline | 2026-08-10 |

### 15.2 Trade-data sources

| Source | Used for | Checked |
|---|---|---|
| [ImportYeti pricing](https://www.importyeti.com/pricing/supply-chain?source=survey) | Public plan prices | 2026-08-10 |
| [ImportYeti API](https://www.importyeti.com/yeti-api) | Enterprise/API boundary | 2026-08-10 |
| [ImportYeti filters](https://www.importyeti.com/filter-guide) | Available filter concepts | 2026-08-10 |
| [ImportGenius pricing](https://w3.importgenius.com/pricing) | Public plan prices and coverage tiers | 2026-08-10 |
| [Descartes Datamyne product/pricing](https://www.datamyne.com/our-product/datamyne-pricing/) | U.S. BOL, TEU, history, quote boundary | 2026-08-10 |
| [Panjiva supply-chain intelligence](https://www.spglobal.com/market-intelligence/en/solutions/products/panjiva-supply-chain-intelligence) | Transaction/company coverage and demo boundary | 2026-08-10 |
| [Trademo data license](https://www.trademo.com/data-license) | Licensed dataset scope | 2026-08-10 |
| [Trademo transactional data](https://www.trademo.com/data-license/trade-transactional-data) | Transaction-field coverage | 2026-08-10 |
| [Trademo terms](https://www.trademo.com/terms) | No-scraping and platform-use restrictions | 2026-08-10 |
| [PIERS request page](https://www.spglobal.com/market-intelligence/en/solutions/products/resources/piers-request) | BOL-level/company coverage and demo boundary | 2026-08-10 |
| [Global Trade Atlas](https://www.spglobal.com/market-intelligence/en/solutions/products/maritime-global-trade-atlas) | Aggregate international trade statistics | 2026-08-10 |
| [Veson data and analytics](https://veson.com/products/data-and-analytics/) | Maritime flow/congestion comparison | 2026-08-10 |
| [Veson trade-flow methodology](https://help.veson.com/oceanbolt/trade-flow-identification-and-tracking) | Inferred voyage/commodity/volume boundary | 2026-08-10 |

### 15.3 Contact-data sources

| Source | Used for | Checked |
|---|---|---|
| [Apollo API pricing](https://docs.apollo.io/docs/api-pricing) | API credit use | 2026-08-10 |
| [Apollo terms](https://www.apollo.io/terms) | Permitted use, scraping, and contributor boundary | 2026-08-10 |
| [Apollo credit guide](https://www.apollo.io/pricing/about-credits) | Credit mechanics | 2026-08-10 |
| [People Data Labs person pricing](https://www.peopledatalabs.com/pricing/person) | Public person-plan prices | 2026-08-10 |
| [People Data Labs account guide](https://docs.peopledatalabs.com/docs/create-an-account) | Free account/record allowance | 2026-08-10 |
| [Hunter pricing](https://hunter.io/pricing/) | Public plan prices | 2026-08-10 |
| [Hunter email verifier](https://hunter.io/email-verifier) | Verification result meaning | 2026-08-10 |
| [BetterContact pricing](https://bettercontact.rocks/pricing/) | Public plan prices and waterfall | 2026-08-10 |
| [BetterContact DPA](https://bettercontact.rocks/dpa/) | Data-processing and subprocessors review entry | 2026-08-10 |
| [Prospeo plans](https://help.prospeo.io/en/article/plans-and-pricing-overview-cdloq9/) | Free allowance and plan structure | 2026-08-10 |
| [Prospeo pricing](https://prospeo.io/pricing) | Current pricing page; paid figure unavailable | 2026-08-10 |
| [Explorium pricing](https://www.explorium.ai/pricing/) | Public plan prices | 2026-08-10 |
| [Explorium credit details](https://www.explorium.ai/credit-details/) | Credit cost, duration, and refund conditions | 2026-08-10 |

## 16. Decision

Proceed with a component-level, evidence-first pilot design—not an end-to-end AI SDR deployment. Use deterministic state and narrow collectors first, benchmark licensed importer/contact data separately, keep every AI artifact as a draft, and stop at HubSpotChangeProposal. Any CRM write or outreach send requires a new, explicit authorization after the relevant evidence, rights, security, and human-control gates pass.

## 17. Expansion pass: 100+ OSS/free candidates

### 17.1 Expansion scope and cost qualification

This pass was a discovery and static-audit expansion, not a deployment test. It adds 75 unique canonical repositories/tools to the 47-entry baseline (**122 total**). Redirects, forks, mirrors, examples, unofficial client packages, and duplicate vendor editions were collapsed to the upstream project. `source_kind` distinguishes a code repository from an official API or public dataset; the latter can be a useful source without pretending that it is reusable software.

Cost classes are deliberately separate from license and decision class:

| Cost class | Meaning | Strict-shortlist rule |
|---|---|---|
| `strict_free_self_hosted` | Compatible code can run locally or self-hosted; no paid service is required for the bounded path | Include only after source rights, model/data terms, storage, compute, bandwidth, and maintenance are named |
| `free_local_cli` | Local command/library path is free, but the tool is narrow, archived, or not a service | Include only for a bounded offline utility; no hosted fallback assumed |
| `optional_external_service` | Local core exists, but useful connectors, models, feeds, proxies, or enrichment are external | Exclude from strict shortlist until each dependency is approved |
| `free_hosted_tier` | Public/free endpoint or dataset exists, subject to rate limits and terms | Never treat a free endpoint as an automation right or a source-rights grant |
| `paid_only` | The useful path requires a paid plan, contract, or commercial edition | Paid gap only |
| `unknown` | License, rights, cost, or operational boundary is not established | Hard-gate failure; never a pass |

No row below treats “free” as zero operating cost. Local inference still consumes hardware and electricity; search indexes consume disk and rebuild time; crawlers consume bandwidth and review time; hosted datasets impose rate, retention, attribution, and terms constraints. Strict-free candidates are code/data-path candidates, not permission to collect personal data or contact anyone.

### 17.2 Expanded repository/tool matrix

Every row includes the required function, license/terms, activity signal, dependencies/deployment, HubSpot fit, cost/free path, risks, classification, and official source. `HubSpot fit` means adapter shape only; it never authorizes a write.

#### Prospecting, GTM, and OSINT discovery

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| SalesGPT | repository | Context-aware sales agent with stage prompts, tools, voice, email, SMS, and payment demos | MIT code; provider and demo terms separate | HEAD 2024-09-16; release continuity unknown | Python/Poetry, web frontend, Docker, model/Stripe/messaging providers | Custom proposal exporter only | `optional_external_service`; local code, but model, telephony, SMTP, Stripe, and hosting are external | README demonstrates autonomous selling, payment links, and multi-channel contact; no-send policy fails | quarantine | [Official repository](https://github.com/filip-michalsky/SalesGPT) |
| LeadCMS | repository | Extendable headless CMS with customer-journey, license, email-sync, and SMS plugins | MIT core; plugin and dependency terms require review | HEAD 2026-06-04; active CI | .NET 8, PostgreSQL, Elasticsearch, Docker Compose, pluggable plugins | Export/proposal adapter; not a HubSpot connector | `strict_free_self_hosted`; core is local; database, Elastic, backups, and operator time remain | Product/CMS scope is not importer discovery; email/SMS plugins create send and secret surfaces | observe | [Official repository](https://github.com/LeadCMS/leadcms.core) |
| OpenOSINT | repository | Natural-language OSINT REPL/MCP/web UI over email, identity, DNS, breach, and network tools | MIT code; commercial license and sponsor/provider terms also present | HEAD 2026-08-09; release workflow present | Python, Docker, Ollama or hosted models, optional proxies/APIs, local sessions | Evidence export only; no safe native HubSpot boundary | `optional_external_service`; free local core, but proxies, Shodan/VirusTotal/Censys-style providers, and data rights are external | Breach/compromised-credential and identity lookup features violate D3 and source-control gates | quarantine | [Official repository](https://github.com/OpenOSINT/OpenOSINT) |
| SpiderFoot | repository | Broad OSINT automation with 200+ modules and graph/report outputs | MIT; module/provider terms vary | HEAD 2026-04-13; active repository | Python, SQLite, web UI/CLI, optional API keys and Tor/proxies | Evidence export only | `optional_external_service`; local scan path, but module APIs, bandwidth, storage, and review are costs | Broad identity/network enumeration, breach-adjacent modules, false joins, and route-specific rights | quarantine | [Official repository](https://github.com/smicallef/spiderfoot) |
| Taranis AI | repository | Feed/web/news collection, analyst review, enrichment, and intelligence reports | EUPL-1.2; source/feed terms separate | HEAD 2026-08-10; active CI/release signal | Python/Node services, workers, database, feeds, optional models | Weekly-brief export; proposal-only account matching | `optional_external_service`; self-hosted code, but feeds, models, storage, and analyst time remain | News/intelligence workflow is useful, but feed rights, model provenance, and automation boundaries require review | observe | [Official repository](https://github.com/taranis-ai/taranis-ai) |
| recon-ng | repository | Modular reconnaissance framework for security assessments | GPL-3.0; module terms vary | HEAD 2024-11-01; maintenance signal stale for current snapshot | Python, SQLite, API modules, CLI/workspace | None without risky custom adapter | `free_local_cli`; local code, but API keys, targets, and network traffic are not free permissions | Security reconnaissance and target enumeration are out of scope; no importer-specific evidence | reject | [Official repository](https://github.com/lanmaster53/recon-ng) |

#### Collection, parsing, search, and indexing

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| trafilatura | repository | Web discovery, crawling, boilerplate removal, metadata, and structured text export | Apache-2.0 | HEAD 2026-07-31; tests/CI present | Python, lxml/selectors, optional language extras; library/CLI | EvidencePack text/metadata exporter | `strict_free_self_hosted`; no database required; bandwidth, parsing review, and source rights remain | Robots/terms, content retention, language/date extraction errors | adopt | [Official repository](https://github.com/adbar/trafilatura) |
| newspaper4k | repository | Article and source extraction, metadata, summaries, and feeds | MIT core; optional extras have their own terms | HEAD 2026-07-19; CI/package workflow | Python 3.10+, requests/parsers/NLP, CLI/library; optional parallel fetch | EvidencePack article exporter | `strict_free_self_hosted`; local parser; concurrent downloads and content storage cost time/bandwidth | Source terms, parser drift, concurrency, and summary hallucination if model helpers are used | adopt | [Official repository](https://github.com/AndyTheFactory/newspaper4k) |
| selectolax | repository | Fast HTML parsing and CSS/XPath-like selection | MIT | HEAD 2026-07-15; release signal current | Python bindings to Rust/C parser; library/batch worker | Collector normalizer; no direct CRM mutation | `strict_free_self_hosted`; local library; native build and malformed-HTML testing remain | Parser is not a crawler; malformed or hostile HTML and source rights remain operator duties | adopt | [Official repository](https://github.com/rushter/selectolax) |
| Whoogle Search | repository | Historical privacy-preserving Google result proxy | MIT; upstream notice says project ended | HEAD 2026-07-24; README states no further fixes/releases | Python/Flask, Docker, Google query dependency; local service | None | `free_local_cli`; code is free but upstream search path no longer works and maintenance is ended | Dead upstream and Google access boundary; reject even though license is permissive | reject | [Official repository](https://github.com/benbusby/whoogle-search) |
| YaCy | repository | Distributed/self-hosted search engine and crawler | GPL-2.0 | HEAD 2026-07-14; active release signal | Java, embedded index, peer/network modes; self-hosted service | Search result export only | `strict_free_self_hosted`; local index is free; crawl bandwidth, disk, peers, and ranking operations are not | Crawl rights, peer sharing, result provenance, and large operational footprint | observe | [Official repository](https://github.com/yacy/yacy_search_server) |
| Meilisearch | repository | Typo-tolerant full-text and faceted search | MIT core; hosted/enterprise terms separate | HEAD 2026-08-10; active releases | Rust service, local persistent index, HTTP API; self-hosted/cloud | Evidence/account lookup API adapter | `strict_free_self_hosted`; local core; RAM/SSD, backups, and reindexing are hidden costs | Adds another stateful service; index deletion, PII retention, and schema drift need controls | observe | [Official repository](https://github.com/meilisearch/meilisearch) |
| Typesense | repository | Search-as-you-type, faceting, and typo tolerance | GPL-3.0 core; hosted Cloud is separate | HEAD 2026-08-10; active releases | C++ service, persistent index, HTTP API; self-hosted/cloud | Evidence/account lookup API adapter | `strict_free_self_hosted`; local core; RAM/SSD, backup, and operational support remain | GPL obligations, separate search store, and duplicate identity state | observe | [Official repository](https://github.com/typesense/typesense) |
| OpenSearch | repository | Distributed search, analytics, and vector/index services | Apache-2.0 core; plugin/data terms require review | HEAD 2026-08-09; active CI/security | Java/Gradle, JVM cluster, persistent shards, REST, optional dashboards/plugins | Search/evidence adapter only | `strict_free_self_hosted`; code is local; JVM, nodes, snapshots, and security operations are material | Heavy cluster for phase 0; PII retention, plugin licenses, and access-control complexity | observe | [Official repository](https://github.com/opensearch-project/OpenSearch) |
| Heritrix3 | repository | Extensible archival web crawler | Apache-2.0 | HEAD 2026-08-05; active maintenance signal | Java, crawler scope/frontier/state, HTTP fetchers; self-hosted | Raw evidence ingestion after route approval | `strict_free_self_hosted`; code is free; bandwidth, storage, politeness, and legal review dominate | Archival crawl is not prospecting permission; robots, copyright, PII, and replay storage | observe | [Official repository](https://github.com/internetarchive/heritrix3) |
| Mozilla Readability | repository | Main-content and metadata extraction from DOM documents | Apache-2.0 | HEAD observed 2026-08-10; release history present | JavaScript, DOM implementation such as jsdom; library | EvidencePack article parser | `strict_free_self_hosted`; local parser; DOM memory, sanitization, and upstream page retrieval remain | Untrusted HTML, script injection if unsanitized, and no source-rights grant | adopt | [Official repository](https://github.com/mozilla/readability) |

#### Identity, company normalization, and public registries

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| libpostal | repository | International address parsing and normalization | MIT; model data bundled separately | HEAD 2025-12-06; CI present | C library and statistical model resources; local library/bindings | Normalize company/location evidence before proposal | `strict_free_self_hosted`; local preprocessing; native build and model storage cost | Address normalization is not identity proof or geocoding; model/data provenance still matters | adopt | [Official repository](https://github.com/openvenues/libpostal) |
| usaddress | repository | Probabilistic U.S. address parsing | MIT | HEAD 2025-08-07; release signal current | Python, parser model, batch/library | Normalize U.S. facility evidence | `strict_free_self_hosted`; local Python library; model accuracy and review cost remain | Ambiguous addresses and false joins; no company or person proof | adopt | [Official repository](https://github.com/datamade/usaddress) |
| RapidFuzz | repository | Fast fuzzy string matching and edit-distance metrics | MIT | HEAD 2026-08-10; release/CI present | Python/C++; embedded library | Deterministic candidate duplicate/alias signals | `strict_free_self_hosted`; local library; threshold calibration and labeled review cost | Similarity is not identity; language/abbreviation bias and false merges | adopt | [Official repository](https://github.com/rapidfuzz/RapidFuzz) |
| recordlinkage | repository | Python toolkit for probabilistic record linkage | BSD-3-Clause | HEAD 2024-02-21; maintenance signal stale | Python/pandas/scikit-learn; batch notebook/job | Candidate duplicate proposal, never automatic merge | `strict_free_self_hosted`; local library; labels, feature engineering, and compute cost | Stale maintenance signal and false merges; must preserve unresolved state | borrow | [Official repository](https://github.com/J535D165/recordlinkage) |
| cleanco | repository | Strip legal entity suffixes and infer possible business type/jurisdiction | MIT; PyPI 2.3 release 2024-05-15 | Repository activity unknown; release is observable | Python, zero runtime dependencies; local library | Normalize legal-name aliases | `free_local_cli`; tiny local utility; legal suffix dictionaries need updates and review | Heuristic jurisdiction inference is not legal identity or sanctions clearance | adopt | [Official repository](https://github.com/psolin/cleanco) |
| phonenumbers | repository | Parse, validate, and format international phone numbers | Apache-2.0; metadata has upstream release terms | HEAD 2026-08-01; active release signal | Python port of libphonenumber metadata; local library | Normalize phone evidence only | `strict_free_self_hosted`; local metadata; update cadence and number portability limits remain | Valid format does not prove ownership, permission, or DNC status | borrow | [Official repository](https://github.com/daviddrysdale/python-phonenumbers) |
| OpenCorporates API | official_api | Company/register search and corporate identity data | Provider API terms and plan limits; not an OSS repository | Official docs checked 2026-08-10 | Hosted HTTP API; credentials and provider retention apply | Candidate identity enrichment proposal | `optional_external_service`; public/free access is limited; paid quotas, attribution, and contract terms unknown | Third-party rights, freshness, jurisdiction coverage, and rate limits | observe | [Official API documentation](https://api.opencorporates.com/documentation/API-Reference) |
| SEC EDGAR APIs | official_api | U.S. company filings, submissions, and XBRL facts | U.S. public-record access with SEC fair-access rules; source content rights vary | Official docs checked 2026-08-10 | Hosted JSON/HTTP endpoints; user-agent/email required; local cache optional | EvidencePack filing links and company identifiers | `free_hosted_tier`; public endpoint; rate limits, caching, bandwidth, and filing review are costs | Fair-access policy, filing interpretation, personal data in filings, and no importer-volume proof | observe | [SEC EDGAR developer documentation](https://www.sec.gov/edgar/sec-api-documentation) |
| Wikidata | public_dataset | Entity identifiers, aliases, and linked public knowledge | Data CC0; individual statements may have source-specific provenance | Official access docs checked 2026-08-10 | Hosted SPARQL/API or downloadable dumps; local mirror optional | Stable-ID/alias hints only | `free_hosted_tier`; free public service; rate limits, dump storage, and statement-quality review remain | Community-edited data is not authoritative identity, contact permission, or TEU evidence | observe | [Wikidata data access](https://www.wikidata.org/wiki/Wikidata:Data_access) |
| OpenSanctions | repository | Sanctions, PEP, entity matching, crawlers, and lineage | MIT code; data CC BY-NC 4.0 and dataset-specific terms | HEAD 2026-08-10; active CI/security | Python/Zavod, Docker, UI, APIs, crawlers, review UI, external datasets | Compliance evidence flag only; no autonomous exclusion | `optional_external_service`; local code path exists; data license, API, storage, and review are material | Commercial-use restriction, sensitive-person data, false positives, and sanctions decisions need specialist review | quarantine | [Official repository](https://github.com/OpenSanctions/opensanctions) |
| python-stdnum | repository | Validate and normalize government/business identifier formats | LGPL-2.1-or-later | HEAD observed 2026-08-10; release signal current | Python, local regex/check-digit modules; library | Identifier validation before proposal | `strict_free_self_hosted`; local library; country coverage and version updates cost review time | Format validity is not ownership, active status, or sanctions clearance | adopt | [Official repository](https://github.com/arthurdejong/python-stdnum) |

#### Agent frameworks and research orchestration

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| smolagents | repository | Small agent library with code agents, tools, MCP, and model adapters | Apache-2.0; Hub/tool/model terms separate | HEAD 2026-07-11; tests/CI/security present | Python, local/hosted models, optional Docker/E2B/Modal/Blaxel sandboxes | Draft/evidence tools only; no code tool in pilot | `strict_free_self_hosted`; local model and no-tool path; sandbox/GPU/provider costs otherwise apply | Code agents can execute arbitrary actions; Hub imports and MCP tools create provenance/secret risk | borrow | [Official repository](https://github.com/huggingface/smolagents) |
| DSPy | repository | Declarative LM programs, prompt/weight optimization, classifiers, RAG, and agents | MIT | HEAD 2026-08-10; tests/CI/security present | Python, model/retriever adapters, optimizer/eval datasets; library | Structured ScoreProposal/OutreachDraft generator | `strict_free_self_hosted`; local models/retrievers possible; optimization tokens/compute and dataset labeling are hidden costs | Optimization can overfit, call external providers, or erase evidence unless schemas are fixed | borrow | [Official repository](https://github.com/stanfordnlp/dspy) |
| Haystack | repository | Explicit RAG/agent pipelines with components, routing, tools, and evaluation | Apache-2.0; Enterprise platform is separate | HEAD 2026-08-10; broad tests/CI/security | Python, async pipelines, databases/vector stores, model providers, Docker | EvidencePack/Weekly Brief graph with explicit gates | `strict_free_self_hosted`; local pipeline path; model, vector, and deployment compute remain | Large connector surface and agent tool calls; enterprise/cloud boundary and trace PII | observe | [Official repository](https://github.com/deepset-ai/haystack) |
| LlamaIndex | repository | Data connectors, indexing, retrieval, agents, and workflow abstractions | MIT core; integrations/provider terms vary | HEAD 2026-08-09; active release signal | Python/TypeScript, many loaders/vector stores/model providers; library/service | Evidence ingestion and brief drafting adapter | `strict_free_self_hosted`; local core; connector/model/vector storage and maintenance are hidden costs | Connector sprawl, prompt/data leakage, persistence and provenance complexity | observe | [Official repository](https://github.com/run-llama/llama_index) |
| Semantic Kernel | repository | Multi-language agent SDK, plugins, memory, process workflows, MCP/OpenAPI | MIT; README directs new work to Microsoft Agent Framework | HEAD 2026-08-10; active CI/security but migration underway | Python/.NET/Java, model providers, plugins, vector stores; library/service | Proposal-only process/plugin adapter | `strict_free_self_hosted`; local model/plugin path; provider, vector, and runtime costs remain | Successor migration risk; plugins can call APIs; model and memory persistence require controls | observe | [Official repository](https://github.com/microsoft/semantic-kernel) |
| Letta | repository | Stateful agents with memory, tools, and model/provider adapters | Apache-2.0 core; hosted/enterprise terms separate | HEAD 2026-08-01; active release signal | Python/TypeScript, database/vector persistence, model providers; local/server/cloud | Evidence review workspace only | `strict_free_self_hosted`; local server/model possible; persistent memory, DB, and model inference cost | Long-lived memory can retain PII; tool permissions and autonomous loops require isolation | observe | [Official repository](https://github.com/letta-ai/letta) |
| Mem0 | repository | Memory layer for AI apps and agents with extraction/retrieval | Apache-2.0 core; hosted platform terms separate | HEAD 2026-08-07; active CI/release signal | Python/TypeScript, vector/graph/relational stores, model providers | Optional EvidencePack memory, not CRM truth | `strict_free_self_hosted`; local stores/models possible; embeddings, storage, deletion, and evaluation cost | Memory staleness, hidden PII retention, cross-account leakage, and unbounded recall | observe | [Official repository](https://github.com/mem0ai/mem0) |
| Dify | repository | Visual LLM apps, agents, workflows, RAG, model/provider management | Apache-2.0 core; commercial/hosted features and connector terms vary | HEAD 2026-08-10; active release/CI | Python/TypeScript, PostgreSQL, Redis, object storage, workers, model providers; Docker/Kubernetes | Proposal workflow/custom HTTP adapter | `optional_external_service`; self-hosted core; models, queues, storage, and enterprise features are costs | Easy to expose tools, direct writes, and secrets; mixed feature/license boundary | observe | [Official repository](https://github.com/langgenius/dify) |
| Flowise | repository | Visual builder for LLM chains, agents, RAG, and tool flows | Apache-2.0 core; hosted/enterprise terms vary | HEAD 2026-08-10; active release/CI | Node.js, database, vector stores, model/provider connectors; Docker/cloud | Draft-only HTTP export | `strict_free_self_hosted`; local builder path; model, vector, queue, and hosting costs remain | Connector credentials and autonomous flows; audit/approval must be added outside the UI | observe | [Official repository](https://github.com/FlowiseAI/Flowise) |
| Langflow | repository | Visual authoring/runtime for components, agents, and MCP integrations | MIT core; hosted service terms separate | HEAD observed 2026-08-10; active release signal | Python/React, database, model/vector connectors; local/Docker/cloud | Proposal-only custom component | `strict_free_self_hosted`; local runtime; providers, storage, and exposed API hardening cost | Broad component/plugin surface, arbitrary tools, and direct HTTP side effects | observe | [Official repository](https://github.com/langflow-ai/langflow) |
| OpenHands | repository | Self-hosted agent canvas for coding agents and scheduled automations | MIT core; enterprise directory is source-available/commercial | HEAD 2026-08-10; CI/release/security present | Node.js/TypeScript, agent servers, Docker/VM/cloud backends, Slack/GitHub/Linear webhooks | None safe by default; proposal worker only after sandboxing | `strict_free_self_hosted`; local agent canvas; model, sandbox, VM, storage, and operator costs remain | README warns unsandboxed agents have full filesystem access; arbitrary scheduled actions and webhooks fail gates | quarantine | [Official repository](https://github.com/OpenHands/OpenHands) |
| LangChain | repository | General LLM/agent abstractions, tools, retrievers, and integrations | MIT core; provider/integration terms vary | HEAD observed 2026-08-10; active release signal | Python/TypeScript, broad connector ecosystem, optional LangSmith | Borrow schemas/adapters only; not an autonomous runtime | `strict_free_self_hosted`; local core; connector/model/trace costs remain | Very broad API surface, tool execution, and optional commercial tracing; deterministic pipeline is simpler | observe | [Official repository](https://github.com/langchain-ai/langchain) |
| MetaGPT | repository | Role-based multi-agent software and research workflows | MIT; model/provider terms separate | HEAD observed 2026-08-10; active project signal | Python, multi-agent roles, files/tools, model APIs; local/cloud | No direct HubSpot fit; borrow decomposition patterns | `strict_free_self_hosted`; local model possible; agent turns, context, and compute are hidden costs | Autonomous role loops and file/tool effects; not suitable for CRM admission or sending | quarantine | [Official repository](https://github.com/geekan/MetaGPT) |
| AgentScope | repository | Agent application framework, message passing, tools, memory, and multi-agent workflows | Apache-2.0 | HEAD observed 2026-08-10; active CI/release signal | Python, model/tool adapters, message runtime, optional distributed deployment | Proposal graph adapter only | `strict_free_self_hosted`; local path available; provider, distributed runtime, and telemetry costs remain | Multi-agent concurrency and tool permissions need stricter controls than phase 0 requires | observe | [Official repository](https://github.com/modelscope/agentscope) |

#### Local models and inference runtimes

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| Ollama | repository | Local model packaging, serving, REST API, and embeddings | MIT code; model weights have their own licenses | HEAD 2026-08-10; tests/release/security present | Go daemon, local model files, CPU/GPU; desktop/Docker/server | Drafting/evaluation endpoint only | `strict_free_self_hosted`; local API; model downloads, disk, GPU/RAM, electricity, and model terms remain | Local API exposure, unreviewed model weights, prompt retention, and insufficient structured-evidence controls | borrow | [Official repository](https://github.com/ollama/ollama) |
| llama.cpp | repository | Portable C/C++ inference, quantization, and OpenAI-compatible local server | MIT code; model weights have separate terms | HEAD 2026-08-10 UTC; broad CI/backend matrix | C/C++, CPU/GPU backends, GGUF model files; local binary/server | Drafting/evaluation endpoint only | `strict_free_self_hosted`; local inference; compilation, model storage, hardware, and electricity remain | Model-license mismatch, context truncation, output validation, and local server access control | borrow | [Official repository](https://github.com/ggml-org/llama.cpp) |
| vLLM | repository | High-throughput model serving and batching | Apache-2.0; model/provider terms separate | HEAD 2026-08-10; active CI/release | Python/CUDA/C++/GPU, distributed workers, OpenAI-compatible API; server/cloud | Drafting endpoint only | `strict_free_self_hosted`; code is local; GPUs, orchestration, drivers, and monitoring dominate cost | Operationally oversized for pilot; endpoint auth, multi-tenant data, and model rights | observe | [Official repository](https://github.com/vllm-project/vllm) |
| LocalAI | repository | OpenAI-compatible local inference server for multiple backends | MIT code; model licenses separate | HEAD 2026-08-10; active release signal | Go, backend binaries, model files, CPU/GPU; Docker/local | Drafting/evaluation endpoint only | `strict_free_self_hosted`; local server; backend/model download, hardware, and maintenance costs remain | Large backend surface, model provenance, endpoint exposure, and weak evidence guarantees | observe | [Official repository](https://github.com/mudler/LocalAI) |
| llamafile | repository | Single-file local executable packaging for LLMs | Apache-2.0 code; packaged model licenses separate | HEAD observed 2026-08-10; active project signal | C/C++, executable model bundles; local desktop/server | Offline drafting/evaluation endpoint | `strict_free_self_hosted`; local binary; bundle size, model license, RAM, CPU/GPU, and distribution storage remain | Model supply-chain and provenance review; no CRM or permission controls | borrow | [Official repository](https://github.com/mozilla-ai/llamafile) |
| LiteLLM | repository | Unified SDK/proxy gateway for 100+ model providers, keys, budgets, and routing | MIT core; `enterprise/` has separate commercial license | HEAD 2026-08-10; extensive CI/security | Python proxy, databases/Redis, provider SDKs, optional hosted gateway; self-host/cloud | Guarded model adapter only | `optional_external_service`; local proxy possible; provider spend, key management, DB/Redis, and enterprise boundary remain | Mixed license, broad credential surface, provider data retention, and direct gateway power | observe | [Official repository](https://github.com/BerriAI/litellm) |
| Open WebUI | repository | Local web UI for model servers, tools, files, and knowledge | `Open WebUI License` / source-available terms; verify current edition | HEAD 2026-08-10; active release signal | Python/Node, database, model servers, optional plugins; local/cloud | Human review UI only; no direct CRM writes | `optional_external_service`; local UI path; model server, storage, auth, and plugin maintenance remain | Mixed terms and plugin/tool surface; prompt/file retention and accidental action paths | observe | [Official repository](https://github.com/open-webui/open-webui) |
| Text Generation Inference | repository | Production model serving with batching, streaming, and telemetry | Apache-2.0; model/provider terms separate | HEAD observed 2026-08-10; release/CI signal | Rust/Python/CUDA, GPU containers, model registry/files; self-host/cloud | Drafting endpoint only | `strict_free_self_hosted`; code path local; GPU, container, model, and operations are material | High ops burden, endpoint auth, model rights, and no native evidence/approval layer | observe | [Official repository](https://github.com/huggingface/text-generation-inference) |

#### ETL, data movement, and durable orchestration

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| Airbyte | repository | API/database/file connectors and ELT movement for warehouses and AI apps | Elastic License 2.0 for platform; connector licenses vary | HEAD 2026-08-10; CI/security/release present | Java/Python/TypeScript, Docker/Kubernetes, metadata DB, workers, 600+ connectors | Potential staged export; not direct write | `optional_external_service`; self-host OSS path exists; connectors, storage, workers, secrets, and Cloud/enterprise features cost | Mixed licensing, connector credential blast radius, retries/duplication, and vendor terms | observe | [Official repository](https://github.com/airbytehq/airbyte) |
| dlt | repository | Python-native loading from APIs/files into typed destinations | Apache-2.0 | HEAD 2026-08-10; active tests/release signal | Python, local state/schema files, warehouse/database destinations; library/CLI | Stage SourceRecord tables; no direct CRM mutation | `strict_free_self_hosted`; local pipeline; destination storage, API quotas, and schema maintenance remain | Source-specific terms, secrets, incremental-state correctness, and PII retention | borrow | [Official repository](https://github.com/dlt-hub/dlt) |
| Meltano | repository | Singer-based ELT project management, taps/targets, and schedules | MIT core; plugin licenses vary | HEAD 2026-08-10; active CI/release | Python, Singer plugins, local project state, optional scheduler/cloud | Staged evidence export only | `strict_free_self_hosted`; local core; tap/target licenses, credentials, and warehouse costs remain | Connector trust and version drift; plugin code can make arbitrary network calls | observe | [Official repository](https://github.com/meltano/meltano) |
| Singer Python | repository | Reference protocol and SDK for tap/target data streams | MIT; individual taps/targets have independent terms | HEAD observed 2026-08-10; repository activity/release signal limited | Python protocol, JSON lines, user-supplied taps/targets; local/worker | Append-only evidence staging | `strict_free_self_hosted`; protocol/library local; each connector, API quota, and persistence layer must be reviewed | Unbounded connector behavior, schema drift, and no built-in approval/idempotency | borrow | [Official repository](https://github.com/singer-io/singer-python) |
| Dagster | repository | Asset-aware orchestration, schedules, sensors, retries, and lineage | Apache-2.0 core; Dagster+ terms separate | HEAD 2026-08-10; broad CI/security | Python/GraphQL/TypeScript UI, daemon, metadata DB, workers; self-host/cloud | Proposal pipeline orchestration; HubSpot step disabled | `strict_free_self_hosted`; community core; DB, workers, and operator time are hidden costs | Larger control plane than phase 0; sensors can trigger side effects; cloud feature boundary | observe | [Official repository](https://github.com/dagster-io/dagster) |
| Kestra | repository | Declarative event-driven workflows, schedules, retries, and plugins | Apache-2.0 core; hosted/enterprise terms vary | HEAD 2026-08-10; active release/CI | Java, PostgreSQL/Elasticsearch, workers, plugin catalog; self-host/cloud | Proposal workflow and weekly brief scheduler | `strict_free_self_hosted`; local core; JVM, DB, workers, plugins, and retention cost | Plugin/network side effects and broad UI permissions; too much machinery for first pilot | observe | [Official repository](https://github.com/kestra-io/kestra) |
| Temporal | repository | Durable workflow execution with retries, timers, queues, and state history | MIT server; SDKs and cloud terms separate | HEAD 2026-08-10; active release/CI | Go server, persistence DB/visibility store, workers, Web UI; self-host/cloud | Safe proposal worker orchestration, never automatic approval | `strict_free_self_hosted`; local dev/server; database, cluster, worker, and history retention costs remain | Durable retries can repeat external actions unless activities are idempotent; heavy ops | observe | [Official repository](https://github.com/temporalio/temporal) |
| Prefect | repository | Python flows, scheduling, retries, state, and orchestration | Apache-2.0 core; Prefect Cloud/enterprise terms separate | HEAD 2026-08-10; active release/CI | Python, server/database, workers, optional cloud | Proposal pipeline scheduler; CRM node disabled | `strict_free_self_hosted`; local server/core; workers, DB, logs, and cloud features cost | Flow retries and task side effects need idempotency; broad connector/runtime surface | observe | [Official repository](https://github.com/PrefectHQ/prefect) |
| Apache Airflow | repository | DAG scheduling, task orchestration, retries, and lineage hooks | Apache-2.0 | HEAD 2026-08-10; active release/security | Python, scheduler/webserver/workers, metadata DB, queues/executors; self-host/cloud | Evidence collection schedule only; no send/write task | `strict_free_self_hosted`; local core; workers, DB, logs, and maintenance are material | Complex deployment, credential connections, retries, and easy accidental external mutations | observe | [Official repository](https://github.com/apache/airflow) |

#### Market intelligence and public evidence

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| GDELT | official_api | Global news/event, tone, entity, and media monitoring datasets/APIs | Public data/service terms; source-media rights remain separate | Official data/docs checked 2026-08-10 | Hosted APIs/files; optional local mirrors and batch processing | SignalEvent/Weekly Brief evidence source | `free_hosted_tier`; public access; rate, bandwidth, storage, and source-rights review remain | Entity resolution/noise, media copyright, duplicate stories, and no importer-level proof | observe | [Official GDELT data](https://www.gdeltproject.org/data.html) |
| Common Crawl | public_dataset | Open web crawl archives and indexes | Public dataset access; crawled content retains source-rights constraints | Official docs/indexes checked 2026-08-10 | Hosted WARC/index files; local selective downloads | Evidence discovery only | `free_hosted_tier`; free index/data access; S3 bandwidth, WARC storage, parsing, and rights review cost | PII/copyright, freshness, robots/terms ambiguity, and enormous data volume | observe | [Official Common Crawl](https://commoncrawl.org/) |
| Internet Archive | official_api | Public archive search, metadata, and item retrieval | Item-level licenses/rights vary; API/service terms apply | Official developer docs checked 2026-08-10 | Hosted APIs/downloads; optional local cache | EvidencePack source links only | `free_hosted_tier`; public access; download bandwidth, retention, and item-rights review remain | Item rights and availability vary; archive presence is not permission to republish | observe | [Internet Archive developer docs](https://archive.org/developers/) |
| MISP | repository | Structured intelligence event store, correlation, sharing, and workflows | AGPL-3.0; feed/object terms vary | HEAD 2026-07-29; security/CI present | PHP/Cake, database, workers, sync APIs, on-prem/cloud | None for SheperD; unrelated intelligence store | `strict_free_self_hosted`; code is local; feeds, operations, and sensitive data handling cost | Cyber/breach-intelligence domain and sharing connectors conflict with D3 and SheperD source controls | quarantine | [Official repository](https://github.com/MISP/MISP) |
| OpenCTI | repository | Cyber-threat knowledge graph, connectors, reports, and observables | Apache-2.0 core; connector/data terms vary | HEAD observed 2026-08-10; active release/security signal | Python/TypeScript, Elastic, Redis, RabbitMQ, workers, Docker/Kubernetes | No safe HubSpot path; generic export only | `strict_free_self_hosted`; local core; graph/search cluster, connectors, and threat-data rights cost | Cyber/breach scope, sensitive observables, connector side effects, and overbuilt graph for market briefs | quarantine | [Official repository](https://github.com/OpenCTI-Platform/opencti) |
| OpenAlex | official_api | Scholarly works, institutions, authors, concepts, and citations | CC0 data; API usage and polite-pool rules apply | Official docs checked 2026-08-10 | Hosted API or downloadable snapshot; local cache optional | Research signal source only | `free_hosted_tier`; free public API; rate limits, snapshots, and irrelevant-domain filtering cost | Not importer/port evidence; entity ambiguity and source-quality differences | observe | [Official OpenAlex docs](https://docs.openalex.org/) |

#### Evaluation, observability, and quality controls

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| MLflow | repository | Tracing, evaluation, prompt/model registry, gateway, and experiment tracking | Apache-2.0 core; managed/enterprise features separate | HEAD 2026-08-10; active CI/security | Python/Java, tracking server, backend DB, artifact store, optional gateway | Indirect receipts/evaluation; no CRM writes | `strict_free_self_hosted`; local server; DB/object storage, trace PII, and retention are costs | Broad platform, sensitive prompt/artifact retention, and gateway credentials | observe | [Official repository](https://github.com/mlflow/mlflow) |
| OpenTelemetry Collector | repository | Vendor-neutral telemetry pipelines, receivers, processors, exporters | Apache-2.0 | HEAD 2026-08-10; security/CI present | Go binary, config-driven pipelines, exporters/backends; self-host/agent | Trace/metric export only | `strict_free_self_hosted`; local collector; backend storage, cardinality, and PII scrubbing cost | Misconfigured exporters leak prompts/identifiers; telemetry is not an audit receipt by itself | borrow | [Official repository](https://github.com/open-telemetry/opentelemetry-collector) |
| OpenLLMetry | repository | OpenTelemetry instrumentation for LLM/agent frameworks | Apache-2.0 | HEAD 2026-08-10; active CI | Python/TypeScript instrumentation, OTEL collector/backend; library/agent | Trace metadata only | `strict_free_self_hosted`; instrumentation/local collector; backend storage and scrubbing remain | Captures prompts/tool args by default unless redacted; instrumentation drift | borrow | [Official repository](https://github.com/traceloop/openllmetry) |
| OpenInference | repository | OpenTelemetry semantic conventions and instrumentation for AI | Apache-2.0 | HEAD observed 2026-08-10; active project signal | Python/JS instrumentation, OTEL backends; library | Evidence/trace schema alignment only | `strict_free_self_hosted`; local instrumentation; backend and redaction cost | Semantic convention does not guarantee provenance, approval, or source rights | borrow | [Official repository](https://github.com/Arize-ai/openinference) |
| promptfoo | repository | Prompt/model test cases, red-team checks, assertions, and CI evals | MIT | HEAD 2026-08-10; active CI/release | Node.js, local files, model/provider adapters; CLI/CI | Evaluate draft generation; no send/write | `strict_free_self_hosted`; local tests possible; model calls, tokens, and test-fixture governance cost | Test fixtures can contain PII; model drift and evaluator leakage; no production gate unless wired | borrow | [Official repository](https://github.com/promptfoo/promptfoo) |
| DeepEval | repository | Python evaluation metrics for LLM/RAG/agents | Apache-2.0; hosted platform terms separate | HEAD 2026-08-10; active release signal | Python, pytest-style tests, model/embedding providers; local/CI | Draft/evidence quality checks only | `strict_free_self_hosted`; local test path; judge-model calls, embeddings, and labeled cases cost | Model-judge bias, trace/Pii leakage, and false confidence from synthetic tests | borrow | [Official repository](https://github.com/confident-ai/deepeval) |
| Inspect AI | repository | Evaluation framework for agents, models, tools, and safety tasks | MIT; model/task terms vary | HEAD observed 2026-08-10; active project signal | Python, task suites, sandbox/model providers; local/CI | Offline proposal benchmark only | `strict_free_self_hosted`; local task runner; model compute, sandbox, and benchmark maintenance cost | Tool/sandbox execution can create side effects; scores do not establish data rights or deliverability | borrow | [Official repository](https://github.com/UKGovernmentBEIS/inspect_ai) |

#### CRM references

| Tool | source_kind | Function | License / terms | Activity | Dependencies + deployment | HubSpot fit | Cost class; free path / hidden cost | Risks | Class | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| SuiteCRM | repository | Mature open CRM with accounts, contacts, activities, and workflows | AGPL-3.0; extensions/hosting have separate terms | HEAD 2026-07-31; security/release signal | PHP/LAMP, MySQL/MariaDB, web server, persistent CRM; self-host/cloud | Alternative CRM/reference only; no migration implied | `strict_free_self_hosted`; code is local; hosting, upgrades, extensions, and support cost | Duplicates HubSpot source of truth and includes direct workflow side effects | observe | [Official repository](https://github.com/SuiteCRM/SuiteCRM) |
| ERPNext | repository | ERP/CRM platform with customer, sales, and operations modules | GPL-3.0; Frappe Cloud/support separate | HEAD 2026-08-10; active CI/release | Python/JavaScript, MariaDB, Redis, workers; self-host/cloud | Alternative CRM reference only | `strict_free_self_hosted`; core local; broad ERP operations, upgrades, and hosting cost | Scope far exceeds SDR research; direct business-state mutations and migration burden | observe | [Official repository](https://github.com/frappe/erpnext) |
| Dolibarr | repository | Modular ERP/CRM for third parties, products, proposals, and projects | GPL-3.0; modules/hosting vary | HEAD 2026-08-10; active release signal | PHP, database, web server, modules; self-host/cloud | Alternative CRM reference only | `strict_free_self_hosted`; local core; modules, hosting, support, and migration cost | Duplicate CRM state and direct workflow/email surfaces; not a HubSpot adapter | observe | [Official repository](https://github.com/dolibarr/dolibarr) |
| YetiForce | repository | Process-oriented open CRM with customizable entities and workflows | GPL-3.0 core; extensions/hosting terms require review | HEAD 2024-09-26; current repo activity is limited | PHP/Yii, database, web server, modules; self-host | Alternative CRM reference only | `strict_free_self_hosted`; local core; older activity, modules, upgrades, and hosting cost | Maintenance uncertainty, migration burden, and direct CRM side effects | observe | [Official repository](https://github.com/YetiForceCompany/YetiForce) |

**Expansion catalog count: 75 new entries; 122 unique canonical repositories/tools including the 47-entry baseline.** No row is an endorsement of a vendor, data source, or contact strategy.

### 17.3 Additional exact-SHA deep-audit index

The following 24 repositories were inspected at the exact commit shown. The review was static: README/docs, root and nested license markers, manifests, deployment files, persistence/queue references, tests/CI, security policy/advisories, connectors, credential/model dependencies, preview/approval behavior, retries/idempotency, and external side effects were read without installing or executing the projects. A hard-gate failure prevents scoring; popularity cannot override it.

| Audit | Exact audited commit | Commit date | Static review signal | Gate result | Cost class | Decision |
|---|---|---|---|---|---|---|
| SalesGPT | [7cd1d4f9fae2a5610fac76e1c0edc38a2fafd388](https://github.com/filip-michalsky/SalesGPT/tree/7cd1d4f9fae2a5610fac76e1c0edc38a2fafd388) | 2024-09-16 | MIT, Poetry/Docker, frontend/backend, CI tests, tool and provider examples | fail: autonomous multi-channel selling/payment actions | `optional_external_service` | quarantine runtime; borrow stage schema |
| LeadCMS | [e02d7447717f6f0aa26989f2152345b4f7425234](https://github.com/LeadCMS/leadcms.core/tree/e02d7447717f6f0aa26989f2152345b4f7425234) | 2026-06-04 | MIT, .NET solution, Docker Compose, PostgreSQL/Elastic, plugin migrations/tests, SendGrid/SMS/email-sync plugins | pass code license; no SDR approval/HubSpot boundary | `strict_free_self_hosted` | observe |
| OpenOSINT | [3740cacd3e8cb50bae8c8e946222a6dae71423e4](https://github.com/OpenOSINT/OpenOSINT/tree/3740cacd3e8cb50bae8c8e946222a6dae71423e4) | 2026-08-09 | MIT, Python/uv, Docker, MCP/web/REPL, local sessions, SECURITY, provider integrations | fail: breach/credential and unrestricted OSINT paths | `optional_external_service` | quarantine |
| trafilatura | [c1bc9531a2a978326112ca9987e1382745116136](https://github.com/adbar/trafilatura/tree/c1bc9531a2a978326112ca9987e1382745116136) | 2026-07-31 | Apache-2.0, Python package/CLI, no DB, parser/crawler modules, tests/CodeQL | pass restricted allowlist; source rights remain external | `strict_free_self_hosted` | adopt restricted collector |
| newspaper4k | [b53a81fc01ff54601faaeae68d6b4a6d2f18efcb](https://github.com/AndyTheFactory/newspaper4k/tree/b53a81fc01ff54601faaeae68d6b4a6d2f18efcb) | 2026-07-19 | MIT, Python 3.10+, pyproject/requirements, CLI/library, ThreadPool fetch, pipeline tests | pass restricted allowlist; no permission inference | `strict_free_self_hosted` | adopt parser |
| Whoogle Search | [13e52132e3b45328de4146818762c891b7e3d6f4](https://github.com/benbusby/whoogle-search/tree/13e52132e3b45328de4146818762c891b7e3d6f4) | 2026-07-24 | MIT, Flask/Docker, Google dependency, tests/workflows, explicit end-of-life notice | fail: upstream stopped and search path no longer works | `free_local_cli` | reject |
| OpenSearch | [e2342cac9f6db74df1748f6920008a93181507b5](https://github.com/opensearch-project/OpenSearch/tree/e2342cac9f6db74df1748f6920008a93181507b5) | 2026-08-09 | Apache-2.0, Java/Gradle, cluster/shards/REST, security, plugins, extensive CI | pass license/security; complexity and PII retention require bounded profile | `strict_free_self_hosted` | observe |
| libpostal | [25099c506612b34b23b1bfe286ca6321fcf06f35](https://github.com/openvenues/libpostal/tree/25099c506612b34b23b1bfe286ca6321fcf06f35) | 2025-12-06 | MIT, C library, model resources/bootstrap, bindings, Make/autotools, test workflow | pass local normalization; no identity or external side effect | `strict_free_self_hosted` | adopt |
| RapidFuzz | [24f2ac526bf1ec91db90e7ff02e52816e6bcb603](https://github.com/rapidfuzz/RapidFuzz/tree/24f2ac526bf1ec91db90e7ff02e52816e6bcb603) | 2026-08-10 | MIT, C++/Python, pyproject/CMake, coverage/release workflows, no persistence | pass local similarity; thresholds require labeled review | `strict_free_self_hosted` | adopt |
| OpenSanctions | [39be3376e222f56021ab4dc448a9b51cee36d694](https://github.com/OpenSanctions/opensanctions/tree/39be3376e222f56021ab4dc448a9b51cee36d694) | 2026-08-10 | MIT code, CC BY-NC data notice, Docker/Make, crawlers, UI review, API, SECURITY/CI | fail: data-use restriction and sensitive-person/breach-adjacent scope | `optional_external_service` | quarantine |
| smolagents | [e3a5b8994b301983b91c0325546e9dc82eab8cf0](https://github.com/huggingface/smolagents/tree/e3a5b8994b301983b91c0325546e9dc82eab8cf0) | 2026-07-11 | Apache-2.0, Python/pyproject, CodeAgent, Hub/MCP/tools, optional Docker/E2B/Modal, tests/security | pass only no-code/no-side-effect profile | `strict_free_self_hosted` | borrow |
| DSPy | [80553206bc1a6f807c414f53b01ba4d168c6466c](https://github.com/stanfordnlp/dspy/tree/80553206bc1a6f807c414f53b01ba4d168c6466c) | 2026-08-10 | MIT, Python/uv, optimizer/eval modules, provider adapters, tests/SECURITY/CI | pass no-tool structured generation; provider data remains external | `strict_free_self_hosted` | borrow |
| Haystack | [5b791afa448ff81059e04055db6e789b34d17d62](https://github.com/deepset-ai/haystack/tree/5b791afa448ff81059e04055db6e789b34d17d62) | 2026-08-10 | Apache-2.0, Python pipelines/agents, integrations, async, Docker, fuzz/CodeQL/tests/security | pass proposal-only components; connector/model terms remain | `strict_free_self_hosted` | observe |
| Semantic Kernel | [76b54649d6b16a3ac70ff0d742d9cb72e3e61b2c](https://github.com/microsoft/semantic-kernel/tree/76b54649d6b16a3ac70ff0d742d9cb72e3e61b2c) | 2026-08-10 | MIT, Python/.NET/Java, plugins/MCP/OpenAPI, process/memory, multi-runtime CI/security | conditional: successor migration and tool grants | `strict_free_self_hosted` | observe |
| OpenHands | [be636f7141095e7b45e33bead116f070a2446a6e](https://github.com/OpenHands/OpenHands/tree/be636f7141095e7b45e33bead116f070a2446a6e) | 2026-08-10 | MIT core plus enterprise boundary, Node/TS, Agent Canvas, Docker/VM/cloud backends, webhooks, CI/security | fail operational side-effect gate; unsandboxed full filesystem warning | `strict_free_self_hosted` | quarantine |
| Ollama | [a836eb8c3cc21a30020aadc70a1cc06012a4ef01](https://github.com/ollama/ollama/tree/a836eb8c3cc21a30020aadc70a1cc06012a4ef01) | 2026-08-10 | MIT, Go daemon, model store, REST API, Docker/app, tests/security/release | pass local inference; model terms and endpoint controls remain | `strict_free_self_hosted` | borrow |
| llama.cpp | [030ebb558a5820b444a8f836ed5cdd46c9b4bd7a](https://github.com/ggml-org/llama.cpp/tree/030ebb558a5820b444a8f836ed5cdd46c9b4bd7a) | 2026-08-10 UTC | MIT, C/C++, GGUF/model files, CPU/GPU backends, REST server, broad CI | pass local inference; model rights and hardware remain | `strict_free_self_hosted` | borrow |
| LiteLLM | [444b275ac363e835c051ff1acb5eebf200e3984e](https://github.com/BerriAI/litellm/tree/444b275ac363e835c051ff1acb5eebf200e3984e) | 2026-08-10 | MIT outside enterprise, Python proxy, provider map, DB/Redis/keys, extensive CI/security | fail strict-license/provider gate for a free-only runtime | `optional_external_service` | observe |
| Airbyte | [a65bba879e685874be339c8e67a6cc5f11c2b6c4](https://github.com/airbytehq/airbyte/tree/a65bba879e685874be339c8e67a6cc5f11c2b6c4) | 2026-08-10 | ELv2 platform, MIT/varied connectors, Java/Python/TS, workers/state DB, Docker/K8s, CI/security | fail strict OSS gate; connector credentials and Cloud boundary | `optional_external_service` | observe |
| Dagster | [c741afaeacf960dc58558a4c216fd8f50a6a8207](https://github.com/dagster-io/dagster/tree/c741afaeacf960dc58558a4c216fd8f50a6a8207) | 2026-08-10 | Apache-2.0, Python daemon/UI, asset metadata DB, sensors/schedules, workers, CI/security | pass; heavy control plane and sensor side effects require limits | `strict_free_self_hosted` | observe |
| Temporal | [917f20c16633916990987ce98ea3c73346cb0322](https://github.com/temporalio/temporal/tree/917f20c16633916990987ce98ea3c73346cb0322) | 2026-08-10 | MIT, Go server, durable history/persistence, queues/timers, Web UI, Docker, CI/security | pass only idempotent proposal activities; no auto-send/write | `strict_free_self_hosted` | observe |
| MISP | [5d150ae89a1645eb126bb1f5896eb8964bc4e0b0](https://github.com/MISP/MISP/tree/5d150ae89a1645eb126bb1f5896eb8964bc4e0b0) | 2026-07-29 | AGPL-3.0, PHP/Cake, DB, sync/workflows, feed/import tools, security/CI | fail domain/data gate: cyber and breach-intelligence scope | `strict_free_self_hosted` | quarantine |
| MLflow | [7109e837c49cfe5748f706478be3dd4adf8b8d40](https://github.com/mlflow/mlflow/tree/7109e837c49cfe5748f706478be3dd4adf8b8d40) | 2026-08-10 | Apache-2.0, Python server, tracking DB/artifacts, traces/evals/gateway, CI/security | pass self-hosted telemetry profile; redact and retain minimally | `strict_free_self_hosted` | observe |
| SuiteCRM | [d6bca97a0159ec019a969b86eca32affab3beb7c](https://github.com/SuiteCRM/SuiteCRM/tree/d6bca97a0159ec019a969b86eca32affab3beb7c) | 2026-07-31 | AGPL-3.0, PHP/LAMP, MySQL/MariaDB, persistent workflows/APIs, unit tests/security | pass as reference only; direct CRM mutations are outside this dossier | `strict_free_self_hosted` | observe |

#### Deep-dive notes

##### A1. SalesGPT — send-oriented agent, not a proposal runtime

- **Architecture/state:** The pinned tree contains Python/Poetry backend and frontend packages, Docker files, a web/API surface, conversation-stage logic, and examples for tools and provider integrations. State is application/provider state rather than a SheperD append-only evidence ledger.
- **Security/quality:** CI unit-test workflow and an MIT file were present; no reviewed control establishes source-rights, DNC, or HubSpot idempotency. The repository advertises voice, email, SMS/WhatsApp, Stripe payment links, and hosted demos.
- **Side effects/control:** The product's value proposition includes autonomous selling and payment creation. It has no required human release boundary for SheperD's separate approval of account admission, stage, CRM mutation, and send; exact retries and duplicate-safe activity are not sufficient for this scope.
- **Free path/cost:** Code is free, but model calls, telephony, SMTP, messaging, Stripe, hosting, and mailbox data are external costs/permissions. Map only its stage vocabulary to `OutreachDraft`; never connect its send tools.

##### A2. LeadCMS — useful plugin/tenant patterns, wrong system boundary

- **Architecture/state:** .NET 8 solution with PostgreSQL and Elasticsearch Docker services, core plus runtime plugins, migrations, tests, and logging. The plugin model can inform bounded adapters and migration receipts.
- **Security/quality:** MIT root license, build/test workflows, and plugin-level files were observed. SendGrid, SMS, email-sync, and reverse-proxy plugins expand secrets and network paths; none proves least privilege or human approval for SheperD.
- **Side effects/control:** A CMS/customer-journey system can create licenses, trials, emails, and SMS. It does not provide importer evidence, TEU provenance, dedupe, DNC state, or a safe HubSpotChangeProposal boundary.
- **Free path/cost:** Self-hosted core is free; PostgreSQL, Elastic, Docker, backups, upgrades, and operator time are not. Borrow plugin isolation and migration tests only; classify the runtime `observe`.

##### A3. OpenOSINT — hard-gated despite a local core

- **Architecture/state:** Python/uv package with CLI/REPL, web UI, MCP registry integration, Docker, local session files, and 19 tool paths. The README states that real binaries execute tool calls and lists optional sponsor/provider integrations.
- **Security/quality:** MIT code plus `COMMERCIAL-LICENSE.md`, `SECURITY.md`, CI/release files, and explicit paid/proxy integrations were present. Tool outputs are not automatically provenance- or permission-bound to a source ledger.
- **Side effects/control:** Breach/compromised-credential lookup, email/identity lookup, proxying, and unrestricted network recon conflict with D3, no-evasion, source-rights, and DNC gates. Local Ollama does not repair those gates.
- **Free path/cost:** Local install is free; providers, proxy bandwidth, model inference, and sensitive-data retention are material. Keep in quarantine; do not borrow its tool catalog.

##### A4. trafilatura — strongest narrow local collector

- **Architecture/state:** Apache-2.0 Python package/CLI with sitemap/feed discovery, URL management, downloads, extraction, metadata, and multiple exports. No database or queue is required; a caller can persist immutable raw URL/hash/evidence rows.
- **Security/quality:** Test and CodeQL workflows, packaging metadata, documentation, and a license were present. It has no credential or CRM connector in the bounded path; extraction failures remain explicit rather than silently “no data.”
- **Side effects/control:** HTTP retrieval is the only material effect. An allowlist, robots/terms check, rate limiter, retention policy, and per-source receipt must sit outside the library; no browser evasion or login is needed.
- **Free path/cost:** Fully local and Apache-2.0; bandwidth, source review, parser regression tests, and storage are the costs. Map to `SourceRecord → EvidencePack`; adopt only the restricted profile.

##### A5. newspaper4k — article extraction with an explicit concurrency hazard

- **Architecture/state:** MIT Python package with CLI/API, source discovery, metadata/NLP, and `ThreadPoolExecutor` article downloads. `pyproject.toml`, requirements, CI, and tests are present; persistence is caller-owned.
- **Security/quality:** Package/test/publish workflows and a license were observed. Optional extras and source-specific features must be checked independently; a parser output is not a verified fact.
- **Side effects/control:** Calling `build()`/download methods fetches pages and can issue concurrent requests. SheperD must cap concurrency, preserve response URL/date/hash, and disable any cloudflare/bypass behavior; no outbound email or CRM write exists in the library.
- **Free path/cost:** Local MIT path is free; network, CPU, content storage, and analyst review are not. Map to `EvidencePack` and `SignalEvent`; adopt for allowlisted feeds/pages only.

##### A6. Whoogle — license pass, maintenance fail

- **Architecture/state:** MIT Flask/Docker service historically proxied Google results through a local app/config. The pinned README explicitly says Google closed the supported query paths and project work/releases/support ended.
- **Security/quality:** Workflows and a test surface exist, but the upstream end-of-life notice is a current maintenance/security signal. The service depends on a provider path outside the repository's control.
- **Side effects/control:** Querying a search engine is not itself a CRM side effect, but upstream access and terms are unresolved. No useful evidence pipeline can depend on a dead proxy.
- **Free path/cost:** Local code costs little, but it no longer supplies a working free path. Reject; do not count it in the strict shortlist.

##### A7. OpenSearch — capable evidence index, overbuilt for phase 0

- **Architecture/state:** Apache-2.0 Java/Gradle project with clustered nodes, persistent shards, REST APIs, optional dashboards/plugins, and extensive CI/security files. It provides durable search/index state, not source truth.
- **Security/quality:** `SECURITY.md`, CodeQL/Gradle checks, release workflows, and license/notice files were present. Plugin and bundled-code terms must be checked per distribution.
- **Side effects/control:** No outbound side effect is inherent, but indexing PII and vectors creates deletion, access, backup, and retention duties. REST credentials and bulk retries need an application envelope.
- **Free path/cost:** Self-hosting is possible under Apache-2.0; JVM nodes, storage, snapshots, upgrades, and operations dominate the hidden cost. Observe until PostgreSQL search is demonstrably insufficient.

##### A8. libpostal — deterministic normalization, not identity proof

- **Architecture/state:** MIT C library with statistical model resources, autotools/bootstrap build, language bindings, and test workflows; no service, queue, or persistent database is required.
- **Security/quality:** License, CI, build files, and model-resource documentation were inspected. Model data and downstream bindings have independent update/provenance obligations.
- **Side effects/control:** Pure local normalization has no network side effect. It can normalize a `SourceRecord` address before comparison, but must not assert the company, facility, or importer identity.
- **Free path/cost:** Local self-hosted path is free; native compilation, model storage, and regression fixtures cost maintenance. Adopt as a narrow `AccountCandidate` feature.

##### A9. RapidFuzz — useful primitive with a false-merge ceiling

- **Architecture/state:** MIT C++/Python library with pyproject/CMake, wheels, benchmarks, coverage, and release workflows; no persistence or network behavior.
- **Security/quality:** CI, security, and documentation are present. It is mature as a similarity primitive but provides no labeled threshold or entity policy.
- **Side effects/control:** Compute a similarity proposal only; preserve both values, features, threshold/model version, and human decision. Never auto-merge HubSpot records from a score.
- **Free path/cost:** Local code is strict-free; labels, threshold calibration, multilingual cases, and review time are the cost. Adopt for duplicate/alias candidate generation.

##### A10. OpenSanctions — excellent lineage concepts, incompatible data boundary

- **Architecture/state:** MIT code with Docker/Make, dataset crawlers, Zavod extraction, dedupe/matching, API, UI review, and lineage-oriented FollowTheMoney entities. State is database/files/API-backed and includes external dataset content.
- **Security/quality:** Root/nested licenses, `SECURITY.md`, CI, dataset READMEs, and human review UI were inspected. The repository explicitly separates MIT code from CC BY-NC 4.0/data-specific terms.
- **Side effects/control:** Crawlers, entity matching, and sanctions/PEP data can create sensitive-person records and compliance decisions. That fails SheperD's commercial-rights and specialist-review gates, even if the code is self-hosted.
- **Free path/cost:** Local code can run free of license fees; data, API, storage, update jobs, legal review, and false-positive handling are not free. Quarantine; borrow only lineage vocabulary after counsel approval.

##### A11. smolagents — borrow typed tool boundaries, not CodeAgent execution

- **Architecture/state:** Apache-2.0 Python library with `CodeAgent`, tool abstractions, MCP/Hub integrations, model adapters, and optional Docker/E2B/Modal/Blaxel sandboxes. State/checkpoints are caller-owned.
- **Security/quality:** README, pyproject, tests, quality workflows, `SECURITY.md`, and model/tool integrations were present. The default examples encourage web search and code execution.
- **Side effects/control:** A no-tool `Agent`/structured-output profile can draft an explanation; `CodeAgent`, Hub tools, browser tools, and MCP must be disabled. Approval must occur before any external tool, not after a generated plan.
- **Free path/cost:** Local model and local library are strict-free; sandbox, model, GPU, and Hub/provider costs are optional. Borrow only schemas/approval patterns; never delegate CRM or sending.

##### A12. DSPy — programmable optimization with overfitting risk

- **Architecture/state:** MIT Python package with modular signatures, predictors, optimizers, retrieval/agent examples, provider adapters, tests, and `uv.lock`; state is program/dataset-owned.
- **Security/quality:** `SECURITY.md`, CI, tests, and package metadata were present. Optimizers can call models repeatedly and change prompts/weights based on evaluation data.
- **Side effects/control:** Use fixed typed outputs for `ScoreProposal` or `OutreachDraft`; preserve prompt/model/rule versions and evaluator receipts. Do not let optimization alter hard gates or consume unapproved contact data.
- **Free path/cost:** Local model path is strict-free; optimizer calls, GPU, labels, and data retention are hidden costs. Borrow after a labeled offline benchmark exists.

##### A13. Haystack — explicit pipelines, still a broad connector surface

- **Architecture/state:** Apache-2.0 Python components compose pipelines and agents with branches, loops, async calls, retrieval, memory, and tool hooks. Persistence is delegated to document stores/vector stores; Docker and integration packages broaden deployment.
- **Security/quality:** Extensive tests, CodeQL/fuzzing, release workflows, license compliance, and `SECURITY.md` were present. The README advertises lifecycle hooks and tool-call/token monitoring, useful for fail-closed proposals.
- **Side effects/control:** Use components with read-only sources and a final structured output. Do not enable arbitrary tools, remote MCP, or provider callbacks until secrets, retries, and approval receipts are wrapped by SheperD.
- **Free path/cost:** Local pipeline and local model are strict-free; database/vector/model operations and evaluation datasets are not. Observe until a measured RAG/brief requirement exists.

##### A14. Semantic Kernel — mature concepts with a migration warning

- **Architecture/state:** MIT multi-language SDK with plugins, OpenAPI/MCP, memory/vector connectors, planning, process workflows, and model adapters. Python/.NET/Java test workflows and security files are present.
- **Security/quality:** The pinned README states Semantic Kernel is now succeeded by Microsoft Agent Framework. That is an explicit maintenance/migration risk despite current activity and broad CI.
- **Side effects/control:** Plugins and OpenAPI/MCP can call external systems; disable them for phase 0. Borrow process/state interfaces only after version pinning and a migration decision.
- **Free path/cost:** Local plugin/model path is strict-free; providers, vectors, runtime support, and migration work are hidden costs. Observe, do not make it the control-plane dependency.

##### A15. OpenHands — arbitrary automation fails the side-effect gate

- **Architecture/state:** MIT core with enterprise source-available boundary; Agent Canvas is a Node/TypeScript control center for local, Docker, VM, cloud, ACP, Slack, GitHub, Linear, and webhook automations. State and conversations are persistent across backends.
- **Security/quality:** CI, release, Docker, E2E, and security files were inspected. The README explicitly warns that an unsandboxed agent has full filesystem access and presents scheduled/webhook automations.
- **Side effects/control:** It can run arbitrary coding agents and external automations; even a local model does not make those effects proposal-only. Quarantine as a research reference; do not connect to HubSpot, browser, inbox, or shell.
- **Free path/cost:** Local install is available but requires agent/model, sandbox/VM, storage, and operational controls. The enterprise directory's separate terms also fail a simple OSS assumption.

##### A16. Ollama — practical local inference boundary, not a policy engine

- **Architecture/state:** MIT Go daemon with model store, REST API, desktop/Docker packaging, runners, and integration examples. Model files persist locally; calls are synchronous API requests unless the caller adds a queue.
- **Security/quality:** Go module, Dockerfile, tests/release workflows, and `SECURITY.md` were present. The API exposes chat/generation/embeddings but not evidence provenance, DNC, or human approval.
- **Side effects/control:** Restrict bind address, model pulls, and file permissions. Require JSON-schema validation and immutable prompts/versions around it; no tool/function calling or outbound connectors in the pilot.
- **Free path/cost:** Code and local serving are strict-free; model weights, hardware, disk, power, and model licenses remain. Borrow as an optional drafting/evaluation runtime, never as an autonomous agent.

##### A17. llama.cpp — smallest local serving primitive, with model supply-chain duties

- **Architecture/state:** MIT C/C++ project with quantization, CPU/GPU backends, GGUF model files, CLI, and OpenAI-compatible server. No database or queue is required; callers own request receipts and retention.
- **Security/quality:** Large CI matrix covers backends, builds, sanitizers, server, and releases. The project has a broad native code surface that needs pinned binaries and patch monitoring.
- **Side effects/control:** Local inference is read-only from SheperD's perspective, but model downloads and server endpoints are network/file effects. Bind locally, pin model hashes/licenses, and validate structured output.
- **Free path/cost:** Strict-free code path; compilation, model storage, RAM/VRAM, and energy are the real cost. Borrow for deterministic, offline drafting benchmarks.

##### A18. LiteLLM — useful gateway, mixed-license and credential risk

- **Architecture/state:** MIT outside `enterprise/`; Python SDK/proxy with provider map, virtual keys, spend tracking, routing, DB/Redis, admin UI, and many CI/security workflows. State includes keys, budgets, logs, and provider metadata.
- **Security/quality:** Root/enterprise license split, code scanning, tests, and provider auto-update workflows were inspected. The breadth makes provider and price metadata drift a material concern.
- **Side effects/control:** A gateway centralizes powerful credentials and can call any provider. It must sit behind least privilege, redaction, rate limits, and no-send/no-write tool policy; a local-only model path is simpler.
- **Free path/cost:** Local core is available, but provider inference, database/Redis, enterprise features, and support are external. Observe; do not include in strict-free shortlist.

##### A19. Airbyte — connector breadth is not a free control plane

- **Architecture/state:** Platform repository contains Java/Python/TypeScript services, connector SDKs, workers, state/metadata databases, Docker/Kubernetes deployment, and hundreds of connectors. Sync state, secrets, retries, and logs persist.
- **Security/quality:** The README and license docs distinguish ELv2 platform, MIT components, connector licenses, Cloud, and Enterprise; CI, CodeQL, and security handling are substantial.
- **Side effects/control:** Connectors can read/write external systems and retry. A HubSpot connector would be a prohibited direct mutation until a proposal adapter, idempotency key, diff, approval, and audit receipt exist.
- **Free path/cost:** Self-hosting exists but connector, worker, storage, secret, bandwidth, and upgrade costs are large. Observe; borrow connector contract ideas only.

##### A20. Dagster — lineage-friendly orchestration, heavy for the first pilot

- **Architecture/state:** Apache-2.0 Python assets/jobs use daemons, schedules, sensors, runs, metadata storage, queues/executors, and a web UI. Deployment can be self-hosted or Dagster+.
- **Security/quality:** Root license, Python package manifests, CI/docs/security workflows, and extensive tests were present. The asset model is useful for versioned evidence artifacts.
- **Side effects/control:** Sensors and ops can call arbitrary resources. The first profile should run allowlisted read-only collectors and emit proposals; disabled ops must be impossible to schedule accidentally.
- **Free path/cost:** Community core is strict-free; DB, workers, logs, backups, and operator time are not. Observe until schedules/retries justify it; simpler append-only jobs are preferred first.

##### A21. Temporal — durable retries require activity idempotency

- **Architecture/state:** MIT Go server with workflow histories, timers, task queues, persistence/visibility stores, workers, and Web UI. Durable state survives worker failures and is explicitly designed to retry activities.
- **Security/quality:** License, architecture docs, Docker/development compose, Go test/linters, and security/release workflows were observed. The server is mature but operationally significant.
- **Side effects/control:** A retried email/CRM activity can duplicate an irreversible action unless the activity is idempotent and protected by an external proposal receipt. Use only for research jobs and human-review timers in the pilot.
- **Free path/cost:** Self-hosted server is strict-free; persistence, cluster operations, worker compute, history retention, and backups are the cost. Observe; borrow retry/state patterns.

##### A22. MISP — technically strong, domain-incompatible

- **Architecture/state:** AGPL-3.0 PHP/Cake platform with database, event/object/attribute storage, correlation, sharing groups, synchronization, workflows, import tools, and APIs. State is explicitly designed for sensitive threat intelligence.
- **Security/quality:** `SECURITY.md`, CodeQL/main workflows, installer docs, tests, and feed/import tooling were inspected. Extensions and synchronized feeds have independent terms and trust boundaries.
- **Side effects/control:** Its purpose is cyber/breach intelligence sharing and distribution. That conflicts with D3 and SheperD's source-rights/retention limits; a local install does not remove the prohibited-domain gate.
- **Free path/cost:** Code is self-hosted and AGPL; feeds, operations, security response, and sensitive-data governance are not free. Quarantine/reject for SheperD.

##### A23. MLflow — evidence for model behavior, not prospect truth

- **Architecture/state:** Apache-2.0 Python platform with tracking server, backend DB, artifact store, traces, evaluation, prompt/model registry, and optional gateway. It persists prompts, inputs, outputs, metrics, and artifacts.
- **Security/quality:** License, CI/security workflows, server setup, and GenAI tracing/eval docs were inspected. The project has useful experiment/run IDs but no automatic redaction of SheperD-sensitive fields.
- **Side effects/control:** Use a self-hosted, redacted profile for model/evaluator receipts. Do not log raw contact data, DNC lists, credentials, or full source documents by default; retention/deletion must be explicit.
- **Free path/cost:** Local server/core is strict-free; DB/object storage, trace volume, judge-model calls, and operations are not. Observe until evaluation repeatability is measured.

##### A24. SuiteCRM — reference data model, not a second source of truth

- **Architecture/state:** AGPL-3.0 PHP/LAMP application with MySQL/MariaDB, accounts/contacts/activities, workflow extensions, APIs, persistent UI, and unit tests. SuiteCRM 8 is a separate core repository; this audit is SuiteCRM 7.
- **Security/quality:** License, release/security links, compatibility/install docs, unit tests, and multiple extension licenses were inspected. Hosted/support/extension offerings are commercial boundaries.
- **Side effects/control:** It can directly mutate CRM records, workflows, and communications. That is useful for comparing object schemas but incompatible with an unapproved duplicate CRM; no migration or write is proposed.
- **Free path/cost:** Self-hosted code is strict-free under AGPL; PHP/database hosting, upgrades, extensions, and migration are material. Observe as a reference only.

### 17.4 Expansion scores and hard-gate outcomes

The table scores only bounded profiles that passed the relevant hard gates. The dimensions remain the existing eight: workflow fit, provenance, human control, HubSpot fit, license/self-hosting, maturity, operating simplicity, and low external-dependency burden. Each value is 0–5 and totals are recomputed from the eight cells. Unscored profiles failed a gate and retain an explicit reason.

| Profile | WF | Prov | Human | HS | License / self-host | Maturity | Simple | Low external burden | Total / 40 | Class |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LeadCMS, export-only profile | 2 | 3 | 4 | 1 | 5 | 4 | 2 | 4 | 25 | observe |
| trafilatura, allowlisted collector | 4 | 4 | 5 | 1 | 5 | 5 | 5 | 5 | 34 | adopt |
| newspaper4k, allowlisted parser | 4 | 3 | 5 | 1 | 5 | 4 | 4 | 5 | 31 | adopt |
| OpenSearch, evidence-index profile | 3 | 5 | 5 | 2 | 5 | 5 | 1 | 3 | 29 | observe |
| libpostal, normalization-only profile | 3 | 5 | 5 | 1 | 5 | 4 | 5 | 5 | 33 | adopt |
| RapidFuzz, candidate-similarity profile | 4 | 5 | 5 | 1 | 5 | 5 | 5 | 5 | 35 | adopt |
| smolagents, no-tool structured profile | 3 | 3 | 4 | 1 | 5 | 4 | 4 | 3 | 27 | borrow |
| DSPy, no-tool structured profile | 3 | 4 | 5 | 1 | 5 | 4 | 4 | 3 | 29 | borrow |
| Haystack, proposal-only pipeline | 4 | 4 | 5 | 1 | 5 | 5 | 3 | 3 | 30 | observe |
| Semantic Kernel, no-plugin profile | 3 | 4 | 4 | 1 | 5 | 4 | 3 | 3 | 27 | observe |
| Ollama, local inference endpoint | 3 | 4 | 4 | 1 | 5 | 5 | 4 | 4 | 30 | borrow |
| llama.cpp, local inference endpoint | 3 | 4 | 4 | 1 | 5 | 5 | 4 | 5 | 31 | borrow |
| Dagster, read-only proposal jobs | 3 | 5 | 4 | 1 | 5 | 5 | 2 | 4 | 29 | observe |
| Temporal, idempotent proposal activities | 4 | 5 | 4 | 1 | 5 | 5 | 2 | 3 | 29 | observe |
| MLflow, redacted self-hosted receipts | 3 | 5 | 4 | 1 | 5 | 5 | 2 | 4 | 29 | observe |
| SuiteCRM, schema reference only | 2 | 4 | 3 | 1 | 3 | 5 | 2 | 3 | 23 | observe |

The following audited profiles are **not scored** because a hard gate failed: SalesGPT (autonomous selling/payment actions), OpenOSINT (breach/credential and unrestricted OSINT), Whoogle (ended/non-working upstream), OpenSanctions (data-use and sensitive-person boundary), OpenHands (arbitrary agent/webhook/filesystem effects), LiteLLM (mixed-license/provider credential gateway for a free-only path), Airbyte (ELv2/mixed connector and credential boundary), and MISP (cyber/breach-intelligence domain). The same rule applies to un-audited matrix rows classified `quarantine`, `reject`, or `unknown`.

### 17.5 Strict-free shortlist, free hosted sources, and paid gaps

#### Strict-free/self-hosted or local candidates

These are **cost-qualified only**. They still require the matrix classification, source-rights review, security review, and human approval policy before any use. The expansion identifies 56 `strict_free_self_hosted` paths plus three `free_local_cli` paths (59 cost-qualified candidates), more than the 30-entry acceptance threshold:

`LeadCMS`, `trafilatura`, `newspaper4k`, `selectolax`, `Whoogle Search` (historical only), `YaCy`, `Meilisearch`, `Typesense`, `OpenSearch`, `Heritrix3`, `Mozilla Readability`, `libpostal`, `usaddress`, `RapidFuzz`, `recordlinkage`, `cleanco`, `phonenumbers`, `python-stdnum`, `smolagents` (no-code profile), `DSPy`, `Haystack`, `LlamaIndex`, `Semantic Kernel`, `Letta`, `Mem0`, `Flowise`, `Langflow`, `OpenHands` (quarantined), `LangChain`, `MetaGPT`, `AgentScope`, `Ollama`, `llama.cpp`, `vLLM`, `LocalAI`, `llamafile`, `Text Generation Inference`, `dlt`, `Meltano`, `Singer Python`, `Dagster`, `Kestra`, `Temporal`, `Prefect`, `Apache Airflow`, `MISP` (quarantined), `OpenCTI` (quarantined), `MLflow`, `OpenTelemetry Collector`, `OpenLLMetry`, `OpenInference`, `promptfoo`, `DeepEval`, `Inspect AI`, `SuiteCRM`, `ERPNext`, `Dolibarr`, `YetiForce`, and `recon-ng` (rejected security scope).

“Strict-free” does **not** make these safe: MISP, OpenCTI, MetaGPT, OpenHands, and any code/tool agent remain quarantined or observed because of domain, tool, or side-effect gates. Local model candidates also require model-weight license and provenance checks; free weights are not assumed.

#### Free hosted/public sources (not strict-free software)

GDELT, Common Crawl, Internet Archive, SEC EDGAR, Wikidata, and OpenAlex have public/free access paths. Their rate limits, source-content rights, attribution, fair-access rules, snapshots, bandwidth, retention, and relevance filters remain explicit unknowns or operating costs. They can feed `SourceRecord` only after an allowlist and receipt are defined.

#### Optional, freemium, or paid gaps

OpenCorporates API, OpenSanctions APIs/data, provider-backed OpenOSINT/SpiderFoot modules, LiteLLM provider calls, hosted agent/model services, and all importer/contact vendors in section 10 remain `optional_external_service`, `free_hosted_tier`, `paid_only`, or `unknown` as marked. The strict shortlist does not include ImportYeti, ImportGenius, Datamyne, Panjiva, Trademo, Apollo, People Data Labs, Hunter, BetterContact, Prospeo, or Explorium. A free signup, trial, or browser UI is not an automation license, a data license, or permission to email.

### 17.6 SheperD interface compatibility map

| SheperD object / stage | Good-fit expansion candidates | Required wrapper and hard stop |
|---|---|---|
| `SourceRecord` | trafilatura, newspaper4k, Mozilla Readability, selectolax, GDELT, Common Crawl, Internet Archive, SEC EDGAR, Wikidata, OpenAlex | Store canonical URL/identifier, retrieval and publication times, content hash, source terms, checked date, retention class, and raw evidence before parsing; robots/terms and rate limit gate first |
| `AccountCandidate` | libpostal, usaddress, RapidFuzz, cleanco, phonenumbers, python-stdnum, OpenCorporates, SEC identifiers | Preserve all aliases and unresolved matches; unknown identity never becomes a merge; public-registry evidence does not prove importer status or permission |
| `EvidencePack` | trafilatura/newspaper4k/Readability, Docling baseline, OpenSearch/Meilisearch/Typesense as deferred indexes, OpenTelemetry/OpenInference receipt fields | Evidence is append-only and source-linked; index deletion/retention must be reversible; parser output is not a fact without provenance |
| `ScoreProposal` | DSPy, smolagents no-tool, Haystack, LlamaIndex, Semantic Kernel no-plugin, RapidFuzz | Typed schema, rule/model/version, feature-level evidence, uncertainty, and evaluator receipt; AI cannot change hard-gate results or treat unknown as zero |
| `OutreachDraft` | Ollama, llama.cpp, vLLM/LocalAI/TGI, promptfoo, DeepEval, Inspect AI | Local/no-tool model call, approved EvidencePack only, no guessed addresses, no LinkedIn, no send/follow-up; draft requires named human approval |
| `SignalEvent` | Taranis AI, GDELT, Common Crawl, Internet Archive, OpenAlex, Miniflux/RSSHub baseline | Source rights, event time, dedupe key, confidence, and account-match evidence; an event is not a qualification or CRM stage change |
| `Weekly Brief` | Taranis AI, GDELT/OpenAlex feeds, Dagster/Kestra/Temporal/Prefect/Airflow proposal jobs, MLflow redacted receipts | Run IDs, source list, changed-since cursor, unresolved items, and human editorial approval; no direct account mutation |
| `HubSpotChangeProposal` | HubSpot official SDK baseline, dlt/Singer staged export, narrow custom adapter | Stable HubSpot IDs, normalized-domain dedupe, before/after diff, expected-version check, idempotency key, retry class, least privilege, request-signature validation, and separate write authorization |

### 17.7 Revised free-first recommended stack

1. **Collection:** direct approved feeds/HTTP plus trafilatura, selectolax, newspaper4k, or Mozilla Readability. Crawl4AI remains the conditional browser fallback from the baseline; no stealth, login, or unrestricted browser agent.
2. **Identity:** deterministic domain/legal-name/identifier rules, libpostal/usaddress, cleanco, RapidFuzz, and phonenumbers. Add recordlinkage/Splink only after a labeled duplicate benchmark.
3. **Public intelligence:** Miniflux/direct publisher feeds, SEC EDGAR, GDELT, OpenAlex, and selected Common Crawl/Internet Archive evidence. Keep OpenCorporates and shipment/contact vendors in a separately approved provider lane.
4. **State:** existing approved PostgreSQL or isolated SQLite plus append-only JSONL receipts. Defer OpenSearch, Meilisearch, Typesense, vector stores, and memory frameworks until a measured retrieval requirement exists.
5. **AI:** one local Ollama or llama.cpp endpoint for structured explanation/drafting, with DSPy/PydanticAI/LangGraph patterns borrowed rather than installed. Use promptfoo/DeepEval/Inspect AI for offline tests; no tools, code execution, or provider fallback in the first profile.
6. **Scheduling:** ordinary bounded jobs first. Dagster, Temporal, Kestra, Prefect, Airflow, and Taranis are observe/borrow candidates only after retries, queues, and human review are demonstrably needed.
7. **CRM:** official HubSpot SDK behind a proposal-only adapter. dlt/Singer can stage data, but neither may write to HubSpot. HubSpot remains the intended operational source of truth; this dossier creates no record.

### 17.8 Expanded quarantine and rejection list

| Candidate | Reason | Re-entry condition |
|---|---|---|
| SalesGPT, OpenOutreach, OneShot GTM, Mautic, listmonk | Autonomous or send-oriented email/SMS/voice/payment effects | Separate send authorization, consent/DNC evidence, preview, idempotency, and deliverability review |
| OpenOSINT, SpiderFoot, recon-ng, MISP, OpenCTI | Breach/security reconnaissance, sensitive observables, or broad target enumeration | Remove prohibited modules and obtain specialist source-rights/retention approval |
| browser-use, OpenHands, MetaGPT, unrestricted smolagents CodeAgent | Arbitrary browser/code/file/tool effects | Sandboxed read-only tools, allowlist, approval before each side effect, full audit receipt |
| OpenSanctions | Data license and sensitive-person/sanctions decision boundary | Counsel-approved commercial data basis and specialist human review |
| Whoogle Search | Upstream ended and no longer works | A maintained, terms-compliant search source with provenance |
| LiteLLM, Airbyte, n8n, Activepieces, Dify | Mixed/source-available licensing and broad provider/credential connectors | Edition/license inventory, secret isolation, dry-run adapter, and operator ownership |
| Any unknown-license or unknown-cost candidate | Hard gate failed | Canonical license, source rights, cost, maintenance, security, and retention evidence |

### 17.9 Expansion source register

All sources in this expansion were checked on **2026-08-10** unless an exact commit date is shown in section 17.3. Repository source links in sections 17.2 and 17.3 are canonical upstreams; API/dataset links are the official provider documentation. Git metadata came from read-only `git ls-remote`/shallow static inspection; no repository code was executed.

| Source group | Official sources | Use |
|---|---|---|
| Prospecting/GTM/OSINT | [SalesGPT](https://github.com/filip-michalsky/SalesGPT), [LeadCMS](https://github.com/LeadCMS/leadcms.core), [OpenOSINT](https://github.com/OpenOSINT/OpenOSINT), [SpiderFoot](https://github.com/smicallef/spiderfoot), [Taranis AI](https://github.com/taranis-ai/taranis-ai), [recon-ng](https://github.com/lanmaster53/recon-ng) | Function, licenses, provider integrations, side effects, and maintenance signals |
| Collection/search | [trafilatura](https://github.com/adbar/trafilatura), [newspaper4k](https://github.com/AndyTheFactory/newspaper4k), [selectolax](https://github.com/rushter/selectolax), [Whoogle](https://github.com/benbusby/whoogle-search), [YaCy](https://github.com/yacy/yacy_search_server), [Meilisearch](https://github.com/meilisearch/meilisearch), [Typesense](https://github.com/typesense/typesense), [OpenSearch](https://github.com/opensearch-project/OpenSearch), [Heritrix3](https://github.com/internetarchive/heritrix3), [Readability](https://github.com/mozilla/readability) | Parser/crawler/index architecture, license, activity, and deployment |
| Identity/company | [libpostal](https://github.com/openvenues/libpostal), [usaddress](https://github.com/datamade/usaddress), [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz), [recordlinkage](https://github.com/J535D165/recordlinkage), [cleanco](https://github.com/psolin/cleanco), [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers), [OpenCorporates API](https://api.opencorporates.com/documentation/API-Reference), [SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation), [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access), [OpenSanctions](https://github.com/OpenSanctions/opensanctions), [python-stdnum](https://github.com/arthurdejong/python-stdnum) | Normalization, public-registry boundaries, rights, and matching risk |
| Agents | [smolagents](https://github.com/huggingface/smolagents), [DSPy](https://github.com/stanfordnlp/dspy), [Haystack](https://github.com/deepset-ai/haystack), [LlamaIndex](https://github.com/run-llama/llama_index), [Semantic Kernel](https://github.com/microsoft/semantic-kernel), [Letta](https://github.com/letta-ai/letta), [Mem0](https://github.com/mem0ai/mem0), [Dify](https://github.com/langgenius/dify), [Flowise](https://github.com/FlowiseAI/Flowise), [Langflow](https://github.com/langflow-ai/langflow), [OpenHands](https://github.com/OpenHands/OpenHands), [LangChain](https://github.com/langchain-ai/langchain), [MetaGPT](https://github.com/geekan/MetaGPT), [AgentScope](https://github.com/modelscope/agentscope) | Tool/state/approval patterns, persistence, connectors, and autonomous-action risk |
| Local runtimes | [Ollama](https://github.com/ollama/ollama), [llama.cpp](https://github.com/ggml-org/llama.cpp), [vLLM](https://github.com/vllm-project/vllm), [LocalAI](https://github.com/mudler/LocalAI), [llamafile](https://github.com/mozilla-ai/llamafile), [LiteLLM](https://github.com/BerriAI/litellm), [Open WebUI](https://github.com/open-webui/open-webui), [Text Generation Inference](https://github.com/huggingface/text-generation-inference) | Local/provider path, model/license boundary, endpoint controls, and hidden compute |
| ETL/orchestration | [Airbyte](https://github.com/airbytehq/airbyte), [dlt](https://github.com/dlt-hub/dlt), [Meltano](https://github.com/meltano/meltano), [Singer Python](https://github.com/singer-io/singer-python), [Dagster](https://github.com/dagster-io/dagster), [Kestra](https://github.com/kestra-io/kestra), [Temporal](https://github.com/temporalio/temporal), [Prefect](https://github.com/PrefectHQ/prefect), [Airflow](https://github.com/apache/airflow) | Connector credentials, persistence, queues, retries, and idempotency |
| Intelligence/evidence | [GDELT](https://www.gdeltproject.org/data.html), [Common Crawl](https://commoncrawl.org/), [Internet Archive](https://archive.org/developers/), [MISP](https://github.com/MISP/MISP), [OpenCTI](https://github.com/OpenCTI-Platform/opencti), [OpenAlex](https://docs.openalex.org/) | Public data/service terms, source rights, and signal-to-account matching |
| Evaluation/observability | [MLflow](https://github.com/mlflow/mlflow), [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector), [OpenLLMetry](https://github.com/traceloop/openllmetry), [OpenInference](https://github.com/Arize-ai/openinference), [promptfoo](https://github.com/promptfoo/promptfoo), [DeepEval](https://github.com/confident-ai/deepeval), [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Redacted traces, evaluation, source receipt, and PII retention controls |
| CRM references | [SuiteCRM](https://github.com/SuiteCRM/SuiteCRM), [ERPNext](https://github.com/frappe/erpnext), [Dolibarr](https://github.com/dolibarr/dolibarr), [YetiForce](https://github.com/YetiForceCompany/YetiForce) | Schema comparison only; no migration or HubSpot mutation |

### 17.10 Expansion conclusion

The larger landscape confirms the original conclusion rather than replacing it: no end-to-end AI SDR runtime is adopted unchanged. The free-first path is a narrow local control plane—allowlisted collection, deterministic identity, append-only evidence, optional local model drafting, offline evaluation, and a proposal-only HubSpot adapter. Hosted free tiers, freemium products, paid APIs, mixed-license platforms, breach/security tooling, and autonomous browser/sending agents remain separately labeled and gated. Unknown license, rights, permission, DNC, identity, TEU, or cost remains an explicit block.

<details>
<summary>Superseded closeout material — retained for research traceability</summary>

> [!info] Superseded
> The current decision document is [[SheperD AI SDR Operating Blueprint - Ric]]. The following historical closeout sections are retained only so earlier research remains auditable.

## Appendix A. Superseded curated AI SDR shortlist

### 18.1 Selection rule

This closing shortlist is intentionally smaller than the 122-entry research catalog. A project remains here only if it is directly useful to AI SDR work or is an indispensable pipeline boundary, has an identifiable license, has a current activity signal in the 2026-08-10 snapshot, and can be wrapped in SheperD's proposal-only controls. Generic agent builders, stale examples, sending-first systems, and unrelated intelligence/security platforms stay in the catalog but are not recommendations.

### 18.2 Direct AI SDR/GTM repositories

| Repository | What is genuinely useful | Status for SheperD | Why it is not adopted unchanged |
|---|---|---|---|
| [OpenOutreach](https://github.com/eracle/OpenOutreach) | Closest complete AI SDR loop: lead discovery, qualification, enrichment, email, replies, follow-up, and local CRM | **Primary reference; quarantine runtime** | Autonomous mailbox effects, paid enrichment, and promotional/send paths |
| [YALC](https://github.com/Othmane-Khadri/YALC-the-GTM-operating-system) | GTM workflow structure, provider adapters, declarative actions, and HubSpot-oriented integration | **Primary architecture reference; borrow** | Auto-commit, email/LinkedIn actions, and broad secret/vendor surface |
| [SalesGPT](https://github.com/filip-michalsky/SalesGPT) | Stage-aware sales-agent state and conversation progression | **Borrow state/draft patterns** | Multichannel automation and payment/selling actions |
| [OneShot GTM](https://github.com/oneshot-agent/oneshot-gtm) | Prospecting queues, cadence concepts, receipts, and idempotency ideas | **Borrow receipt patterns** | Proprietary paid API and email/SMS/voice side effects |

These four are the only direct AI-SDR/GTM repositories worth deep-reading first. None is the SheperD runtime.

### 18.3 Minimal supporting stack

| Pipeline need | Repository | SheperD use | Status |
|---|---|---|---|
| Static scraping | [Scrapy](https://github.com/scrapy/scrapy) | Allowlisted HTTP collection and extraction | **Adopt** |
| Browser-assisted scraping | [Crawl4AI](https://github.com/unclecode/crawl4ai) | Conditional fallback for pages static HTTP cannot read | **Adopt conditionally** |
| Content extraction | [trafilatura](https://github.com/adbar/trafilatura) | Article text, metadata, and evidence normalization | **Adopt** |
| PDF/document extraction | [Docling](https://github.com/docling-project/docling) | Port, FMC, carrier, and regulatory documents | **Adopt** |
| Duplicate/alias candidates | [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | Domain/name similarity proposals before human review | **Adopt** |
| Typed proposal output | [PydanticAI](https://github.com/pydantic/pydantic-ai) | `ScoreProposal` and `OutreachDraft` schemas | **Borrow restricted profile** |
| Durable human interrupt | [LangGraph](https://github.com/langchain-ai/langgraph) | Add only when research needs checkpoints/resume | **Borrow, defer** |
| Local drafting model | [Ollama](https://github.com/ollama/ollama) | Local, no-tool explanation and draft generation | **Borrow** |
| CRM boundary | [HubSpot API Python SDK](https://github.com/HubSpot/hubspot-api-python) | Official client behind `HubSpotChangeProposal` | **Adopt proposal-only** |

The first implementation does not need LangFlow, Flowise, Dify, CrewAI, AutoGen, OpenHands, MetaGPT, a vector database, a second CRM, or a general-purpose automation platform.

### 18.4 The only architecture to carry forward

```text
Scrapy / Crawl4AI (conditional)
    -> trafilatura / Docling
    -> SourceRecord + EvidencePack
    -> RapidFuzz + deterministic identifiers
    -> AccountCandidate + ScoreProposal
    -> PydanticAI-shaped OutreachDraft via Ollama
    -> named human approval
    -> HubSpotChangeProposal via official SDK
```

No repo may send email, follow up, write HubSpot, automate LinkedIn, guess an address, or convert unknown evidence into a pass.

### 18.5 Explicitly not part of the final shortlist

- **Generic agent platforms:** LangFlow, Flowise, Dify, CrewAI, AutoGen, OpenHands, MetaGPT, and AgentScope. They add broad tool/runtime surface without solving SheperD's specific evidence and approval problem.
- **Stale or weak examples:** the LangGraph outreach example, Leadpoet, GTM prompt packages, and Whoogle. They are useful discovery context at most, not implementation foundations.
- **Sending/verification tools:** Mautic, listmonk, Reacher, email-sleuth, browser-use, and similar systems. Sending permission, identity, and DNC evidence remain unresolved.
- **Secondary infrastructure:** OpenRefine, Splink, libpostal, Miniflux, Dagster, Temporal, Langfuse, vector stores, and alternate CRMs. Keep them in the research catalog; add only after a measured requirement.

### 18.6 Final recommendation

Deep-read **OpenOutreach, YALC, SalesGPT, Scrapy, Crawl4AI, PydanticAI, and the HubSpot SDK**. Build SheperD from the supporting stack, but borrow the SDR repos' state and workflow ideas rather than deploying their autonomous actions. The meaningful conclusion is a small, governed AI-SDR pipeline—not a large collection of generic agent tools.

## Appendix B. Superseded technical AI SDR-to-HubSpot architecture

### 19.1 Responsibility split

The main AI SDR agent is an **orchestrator**, not an autonomous seller. It creates bounded jobs, passes typed objects between specialist workers, records receipts, and stops at policy gates. Deterministic code owns identity, deduplication, rights, D&D qualification gates, persistence, and HubSpot diffs. Models explain and draft; they do not grant themselves tools or authority.

| Plane | Owns | Does not do |
|---|---|---|
| Source plane | Approved public pages/RSS, government/regulator pages, and separately contracted trade/contact APIs | No arbitrary crawling, login, stealth, or source-rights assumption |
| Research plane | `SourceRecord`, `AccountCandidate`, `EvidencePack`, `SignalEvent`, and receipts in the research store | No HubSpot mutation, email, follow-up, or lifecycle movement |
| Agent plane | Bounded discovery, company, trade-volume, D&D-signal, contact-role, scoring, and drafting jobs | No unrestricted browser/code/tool execution; no guessed identity or permission |
| Decision plane | Hard gates, score rubric, approval queue, before/after diffs, and idempotency keys | No conversion of unknown into zero/pass; no autonomous approval |
| CRM plane | Read-only duplicate context and approved `HubSpotChangeProposal` application | No raw research dump or silent overwrite |
| Delivery plane | A separately authorized email adapter | Disabled in the research pilot; no autonomous send or follow-up |

### 19.2 Concrete execution flow

~~~mermaid
flowchart LR
    subgraph Sources["Approved source boundary"]
        GOV["Census, FMC, ports, terminals, rail, regulators"]
        WEB["Allowlisted public pages and publisher RSS"]
        TRADE["Contracted importer/trade-volume API"]
        CONTACT["Contracted contact-data API"]
    end

    subgraph Collect["Read-only collectors"]
        HTTP["Scrapy + trafilatura"]
        BROWSER["Crawl4AI conditional fallback"]
        DOCS["Docling PDF/document parser"]
        RECEIPT["SourceRecord + fetch receipt + content hash"]
    end

    subgraph Orchestrator["Main AI SDR orchestrator"]
        MAIN["Job scheduler/orchestrator\nPydanticAI-shaped contracts; LangGraph only for checkpoints"]
        DISC["Discovery worker\nfind candidate companies"]
        COMPANY["Company-research worker\nidentity, segment, footprint"]
        VOLUME["Trade-evidence worker\nTEU/volume + method + period"]
        DND["D&D-signal worker\ndetention/demurrage exposure"]
        ROLE["Contact-role worker\nCFO/COO/logistics/controller"]
        SCORE["Score worker\nhard gates + explanation"]
        DRAFT["Draft worker\napproved evidence only"]
    end

    subgraph State["Research state outside HubSpot"]
        AC["AccountCandidate\ndeterministic identity/dedupe"]
        EP["EvidencePack\nclaim-level lineage"]
        SIG["SignalEvent\nnews/regulatory/market trigger"]
        HYP["D&D ExposureHypothesis\nnot a loss fact"]
        SP["ScoreProposal"]
        OD["OutreachDraft\nunsent"]
        MATCH["AccountMatch"]
        WB["Weekly Brief"]
    end

    subgraph Human["Named human control"]
        REVIEW["Evidence, rights, identity, D&D, and DNC review"]
        APPROVE["Approve specific CRM diff and/or send draft"]
    end

    subgraph CRM["HubSpot operational boundary"]
        READ["Read-only HubSpot context\nIDs, domains, current fields"]
        HCP["HubSpotChangeProposal\nbefore/after + association + idempotency"]
        HS["HubSpot approved mutation"]
    end

    subgraph Delivery["Separate delivery boundary"]
        SEND["Email adapter"]
        FOLLOW["Follow-up scheduler"]
    end

    GOV --> HTTP
    WEB --> HTTP
    WEB --> BROWSER
    GOV --> DOCS
    TRADE --> VOLUME
    CONTACT --> ROLE
    HTTP --> RECEIPT
    BROWSER --> RECEIPT
    DOCS --> RECEIPT
    RECEIPT --> MAIN
    READ --> MAIN
    MAIN --> DISC
    MAIN --> COMPANY
    MAIN --> VOLUME
    MAIN --> DND
    MAIN --> ROLE
    DISC --> AC
    COMPANY --> AC
    VOLUME --> EP
    DND --> HYP
    ROLE --> EP
    AC --> EP
    EP --> SCORE
    HYP --> SCORE
    SCORE --> SP
    RECEIPT --> SIG
    SIG --> MATCH --> WB
    AC --> MATCH
    SP --> DRAFT --> OD
    EP --> REVIEW
    SP --> REVIEW
    OD --> REVIEW
    WB --> REVIEW
    REVIEW --> APPROVE
    APPROVE --> HCP
    READ --> HCP
    HCP -. "separate write authorization" .-> HS
    APPROVE -. "separate send authorization" .-> SEND
    SEND -. "only after explicit cadence approval" .-> FOLLOW
~~~

HubSpot appears twice deliberately: the research system may read current records for deduplication and stale-field detection; it may write only an approved, idempotent proposal. The research store remains the source of evidence. HubSpot remains the operational source of truth only for approved CRM state.

### 19.3 Sub-agent contracts and tool boundaries

Each worker receives a bounded input object and returns a typed object plus a receipt. Workers do not call one another ad hoc and do not share unrestricted credentials.

| Worker | Reads | Allowed tools | Returns | Hard stop |
|---|---|---|---|---|
| Discovery | Approved source definitions and search scope | Scrapy, trafilatura, restricted search/API adapters | Candidate URLs and `SourceRecord` proposals | No arbitrary domains or social-platform evasion |
| Company research | `SourceRecord`, public registries, candidate domain | HTTP/parser tools, SEC/Census/FMC/public registry adapters | Legal/display name, domain, address, industry, footprint evidence | No identity assertion without supporting identifiers |
| Trade evidence | Candidate identity and contracted provider response | Approved trade-data adapter | TEU/volume value, period, coverage, method, provider ID, uncertainty | Unknown volume is not zero; volume does not prove D&D loss |
| D&D signal | Evidence and dated market events | FMC/port/terminal/rail/news adapters, parser tools | `D&D ExposureHypothesis` with trigger, date, geography, evidence, confidence | No claim that the company lost money without direct evidence |
| Contact-role | Approved company identity and public/contracted contact response | Approved contact adapter, role classifier | Contact candidate, role evidence, permission state, DNC state, freshness | No guessed email, scraping evasion, or unknown permission treated as allowed |
| Score | `AccountCandidate`, `EvidencePack`, D&D hypothesis, CRM context | Deterministic rubric plus structured model explanation | `ScoreProposal` with gates, missingness, version, rationale | Model cannot change hard-gate results |
| Draft | Approved evidence, approved role, score rationale, outreach policy | Local Ollama call through typed schema | `OutreachDraft` with cited claims and prohibited-claim check | No send, follow-up, or unsupported “you lost money” claim |
| CRM proposal | Approved candidate, score, draft, current HubSpot read | Official HubSpot SDK in proposal mode | `HubSpotChangeProposal` diff and receipt | No direct write; no lifecycle-stage movement |

The main orchestrator may retry a failed read-only worker, but every retry has a run ID and idempotency key. A failed, partial, stale, or ambiguous result remains an exception; it is never silently promoted.

### 19.4 Detention and demurrage (D&D) qualification

“The importer moves enough containers” is a prioritization signal, not evidence that it incurred detention or demurrage. The system must represent D&D evidence separately:

| State | Meaning | Permitted use |
|---|---|---|
| `observed_loss` | A company filing, invoice/recovery record, public statement, or other approved primary evidence directly documents a cost or recovery issue | May support a human-reviewed problem hypothesis; never auto-send |
| `exposure_signal` | Time-bound evidence suggests risk: sustained dwell, port/terminal/rail disruption, carrier/fee change, facility footprint, or explicit logistics pain | May justify research and a cautious question in a draft; cannot state a loss as fact |
| `unknown` | No reliable company-level D&D evidence, conflicting evidence, or rights/identity uncertainty | Blocks qualification as a D&D opportunity and blocks outreach |

The minimum outreach gate is:

```text
importer_identity = pass
source_rights = pass
contact_identity = pass
permission_state = allowed
dnc_state = clear
dd_exposure_state in {observed_loss, exposure_signal}
evidence_freshness = pass
```

If only `exposure_signal` exists, the draft must ask an exploratory question grounded in the trigger. It may not say or imply that the company “lost money.” If D&D state is `unknown`, the system produces an internal research gap, not an outreach draft.

### 19.5 HubSpot integration point

The clean boundary is a **proposal adapter**, not an agent connected directly to HubSpot:

| Research object | HubSpot behavior |
|---|---|
| `AccountCandidate` | Read existing company by normalized domain/stable IDs; propose a new or updated importer company only after approval |
| `EvidencePack` | Retain in the research store; optionally attach a reviewed summary/note, never an uncontrolled raw dump |
| `D&D ExposureHypothesis` | Store as a proposed, sourced property or note with state, date, and evidence ID; never as an asserted loss amount without proof |
| Contact candidate | Propose contact creation/association only with role evidence, permission, DNC, source, and freshness fields |
| `ScoreProposal` | Propose priority/score fields with rubric version and missingness; score never changes lifecycle stage |
| `OutreachDraft` | Store as a human-review artifact or proposed note; it is not an email activity until separately authorized and sent |
| `SignalEvent` / `Weekly Brief` | Keep as intelligence evidence; optionally propose a reviewed note; never promote an account or opportunity |
| `HubSpotChangeProposal` | Contains portal, object type, stable ID, before/after diff, associations, expected current values, idempotency key, approval identity, and retry class |

The HubSpot adapter must use least-privilege scopes, stable IDs, normalized-domain deduplication, expected-version checks, safe retries, and current request-signature validation. No sub-agent receives a HubSpot write token.

### 19.6 Personalized-email lifecycle

1. A collector records a dated, rights-checked D&D trigger.
2. Company and contact workers resolve the importer and an evidenced decision-maker role.
3. The D&D worker produces an exposure hypothesis with citations and uncertainty.
4. The score worker checks ICP, source rights, identity, freshness, permission, DNC, and D&D gates.
5. The draft worker selects one or two approved facts, states the bounded hypothesis, asks a relevant question, and proposes a low-friction next step. It does not invent loss, savings, volume, or authority.
6. A named human reviews evidence, claims, recipient, permission, DNC, and tone.
7. Only after a separate send authorization may a delivery adapter send. Sending creates a receipt; it does not automatically trigger follow-up.
8. Any approved CRM update is a separate `HubSpotChangeProposal`; send approval and CRM-write approval are distinct decisions.

### 19.7 Recommended implementation boundary

Implement the control plane as a small application around typed domain contracts, not inside HubSpot and not inside a generic automation platform:

```text
domain/contracts/       SourceRecord, EvidencePack, ScoreProposal, OutreachDraft
research/collectors/    Scrapy, trafilatura, Crawl4AI conditional, Docling
research/workers/       discovery, company, trade, D&D, contact, score, draft
research/gates/         rights, identity, D&D, permission, DNC, freshness
research/store/         PostgreSQL or isolated SQLite + append-only receipts
orchestrator/           bounded jobs, retries, run IDs, idempotency
integrations/hubspot/   read context + proposal adapter only
delivery/email/         disabled until separately authorized
```

Start with ordinary bounded jobs and a local model endpoint. Add LangGraph only when checkpointed multi-step work is demonstrated; add queues, Dagster, or Temporal only when measured throughput/retry requirements justify them. The first useful milestone is not “send an email”; it is a reproducible, evidence-backed D&D prospect packet and a zero-side-effect HubSpot diff.

</details>
