---
title: Human Approval Policy
type: policy
status: proposed
owner: Avi
updated: 2026-07-15
evidence_status: policy
confidentiality: internal
tags:
  - sheperd/ai
  - sheperd/policy
---

# Human Approval Policy

## AI may assist

- Retrieve cited internal knowledge.
- Draft meeting briefs, notes, tasks, and CRM updates.
- Flag missing CRM fields, stale actions, or SLA risk.
- Draft outreach, objections, FAQs, and content from approved facts.
- Compare cohorts and summarize descriptive metrics with sample sizes.
- Draft missing-item requests from deterministic checklists.

## AI may not decide or execute autonomously

- Regulatory interpretation, legal advice, or case eligibility.
- Refund/recovery value, probability, or guarantee.
- Pricing, contract, or commercial-model approval.
- Customer-data acceptance/rejection or security decisions.
- External email, LinkedIn outreach, publishing, or dispute filing.
- Final qualification, CRM stage, partner rating, hiring, or funding.
- Irreversible deletion or record changes.

## Approval matrix

| Action | Required approver |
|---|---|
| External sales message | Michael; Avi for new claim/message version |
| Regulatory statement | Named domain/legal reviewer |
| Recovery estimate | Product/data owner plus approved methodology |
| Customer content/case study | Customer permission + Avi + legal/privacy as needed |
| Customer-data workflow | Legal/privacy + product/security owner |
| Stage/qualification change | Michael or opportunity owner |
| Pricing/contract term | Avi and authorized legal/commercial owner |

## Output labels

Every AI draft must visibly state `DRAFT — HUMAN REVIEW REQUIRED`, list its sources, and flag missing evidence. No system should remove that label before approval.

## Incident rule

If AI exposes sensitive data, invents a regulatory claim, sends externally without approval, or changes a material record incorrectly: stop the workflow, preserve logs, notify the owner, assess impact, correct records, and document the learning before restart.
