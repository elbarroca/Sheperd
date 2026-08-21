---
title: Founder Intelligence Knowledge Contract
type: knowledge-contract
status: active-internal
owner: Ricardo
updated: 2026-07-15
evidence_status: internal-decision
confidentiality: internal
tags:
  - sheperd/context
  - sheperd/knowledge
  - sheperd/security
---

# Founder Intelligence Knowledge Contract

## Layer contract

| Layer | Meaning | Dashboard treatment |
|---|---|---|
| Fact | Sourced statement with its recorded evidence state | Shows source, status, confidence, and limits |
| Ricardo interpretation | Analysis or recommendation by Ricardo | Visibly labeled; cannot promote a fact |
| Founder decision | Explicit owner-approved operating decision | Shows owner, date, scope, and revisit condition |
| Unknown/blocker | Required evidence is absent or contradicted | Remains visible; ranking cannot remove it |

## Admitted corpus

The local index may ingest Markdown and CSV files from `00_System/`, `01_Company/`, `02_Domain/`, `03_GTM/`, `04_Operations/`, `05_AI/`, `06_Goals/`, `06_Research/`, `07_Founder_Operating_System/data/`, `10_Sources/`, `90_Templates/`, and `context/`.

It excludes `website/`, archives, recovery bundles, credentials, environment files, binaries, customer records, and generated build output.

## Vectorization

Version 1 uses deterministic local TF-IDF sparse vectors over section-level chunks. It provides reproducible similarity retrieval without an external embedding service, secret, connector, or network call. It is lexical retrieval, not human-level semantic understanding.

A later embedding/pgvector adapter requires:

- Approved hosting and model providers.
- Data-processing, retention, region, subprocessor, and deletion review.
- Authentication and resource-level authorization.
- Evaluation against a fixed retrieval question set.
- A rollback path to the committed local index.

## Provenance requirements

Every chunk carries a stable ID, source path, title, section, knowledge layer, evidence status, confidentiality, tags, and normalized vector. Search score never changes evidence status.

## Deployment boundary

- The committed dashboard contains D0/D1 internal research only.
- Vercel Preview Deployment Protection is required before founder sharing.
- Production remains private until authentication, authorization, logging, and privacy controls are approved.
- D2 belongs in an approved CRM. D3 remains outside the repository, index, browser bundle, and AI systems.
