---
title: SheperD Context Layer
type: context-index
status: active-internal
owner: Ricardo
updated: 2026-07-15
evidence_status: internal-decision
confidentiality: internal
tags:
  - sheperd/context
  - sheperd/founder-intelligence
---

# SheperD Context Layer

## Purpose

This folder is the curated control layer between the canonical research vault and the founder intelligence dashboard. It does not duplicate the numbered vault folders. It explains what enters the dashboard, how facts differ from interpretation, and which decisions remain blocked.

## Repository surfaces

| Surface | Purpose | Source of truth |
|---|---|---|
| Root numbered folders | Canonical company, domain, GTM, operations, AI, research, source, and template notes | Yes |
| `website/` | Public marketing website | Public-surface implementation only |
| `founder-intelligence/` | Private, Vercel-ready founder briefing and retrieval dashboard | Generated views; never canonical |
| `context/` | Curated founder brief, Ricardo interpretation, and knowledge contract | Yes for interpretation and dashboard boundaries |

## Current entry points

- [[Founder Brief]] — shortest founder-level state and next decision.
- [[Ricardo - Strategic Interpretation]] — Ricardo's analysis of Avi's 16-week proposal and Michael's operating implications.
- [[Founder Intelligence Knowledge Contract]] — ingestion, vectorization, provenance, privacy, and promotion rules.
- [[../03_GTM/SheperD GTM Validation and Optimization - Control Note]] — GTM control state.
- [[../06_Research/SheperD Deep Research - Control Note]] — research frontier.
- [[../07_Founder_Operating_System/README]] — local query prototype retained as a fail-closed reference implementation.

## Update order

1. Update the canonical Markdown or CSV artifact.
2. Update Ricardo's interpretation only if the conclusion changes.
3. Run `pnpm index:build` in `founder-intelligence/`.
4. Run lint, typecheck, tests, build, and browser verification.
5. Review the generated dashboard diff before sharing.

No dashboard edit silently changes canonical truth.
