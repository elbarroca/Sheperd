---
title: Knowledge Retrieval Contract
type: system
status: active
owner: Michael
updated: 2026-07-15
evidence_status: policy
confidentiality: internal
tags:
  - sheperd/system
  - sheperd/ai
---

# Knowledge Retrieval Contract

## Goal

Give humans and AI the smallest trustworthy context pack for a question while preventing claims from outrunning evidence.

## Retrieval priority

1. Canonical topic note.
2. [[01_Company/Claims and Evidence Register]].
3. Current primary-source note in `10_Sources/`.
4. Internal proposals and de-identified observations.
5. Inference only when explicitly labeled.

## Response contract

Every AI answer using this vault must return:

```text
Answer: <direct answer>
Evidence: <wikilinks and source URLs>
Evidence status: verified | company-claim | internal-proposal | internal-observation | internal-data | internal-decision | inference | unverified | mixed | policy
Confidence: high | medium | low
Missing: <material unanswered question or "none">
```

## Hard rules

- Do not turn `company-claim`, `internal-proposal`, or `inference` into fact.
- Do not use a numerical claim externally unless its register row is `approved` for that use.
- “Three years” means the specific complaint limitation described in [[02_Domain/D&D and OSRA Primer]], not guaranteed refund eligibility.
- Do not give regulatory or legal conclusions; retrieve sources and route to the named reviewer.
- Do not infer current product capability from website language alone.
- Never retrieve or store raw customer data in this vault.
- When sources conflict, state the conflict and stop at `mixed` or `unknown`.

## Context packs

| Question | Minimum pack |
|---|---|
| What is SheperD? | [[01_Company/Company Brief]] + [[01_Company/Claims and Evidence Register]] |
| What can the product do today? | [[01_Company/Product and Business Model]] + [[01_Company/Open Questions and Diligence]] |
| Is a D&D claim recoverable? | [[02_Domain/D&D and OSRA Primer]] + approved case evidence outside Obsidian + human reviewer |
| Who should Michael target? | [[03_GTM/ICP and Stakeholder Personas]] + CRM cohort data |
| What should Michael do this week? | [[03_GTM/16-Week Operating Plan]] + current scorecard |
| Can this copy be published? | [[01_Company/Claims and Evidence Register]] + [[03_GTM/Website and Content Audit]] + human approval |
| Which AI workflow is safe? | [[05_AI/AI Enablement Roadmap]] + [[05_AI/Human Approval Policy]] |

## Vector-friendly writing standard

- One subject per note; one claim per claim-register row.
- Use stable, descriptive headings.
- Put the answer before background.
- Prefer short sections over long narratives.
- Link canonical notes instead of repeating definitions.
- Preserve exact dates, actors, and evidence status.
- Split notes when retrieval would regularly need only one section.
