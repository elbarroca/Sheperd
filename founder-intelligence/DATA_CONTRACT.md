# Founder Intelligence Data Contract

## Canonical flow

```text
Root Markdown and CSV
        ↓ validated local ingestion
context/ interpretation contract
        ↓ deterministic section chunking
committed TF-IDF sparse index + dashboard JSON
        ↓ read-only server DTOs
Founder Intelligence UI
```

## Corpus

Admitted roots are declared in `scripts/build-knowledge-index.mjs`. `website/`, archives, recovery files, environment files, binaries, and generated build output are excluded.

## Retrieval fields

Every indexed chunk contains:

- Stable hash ID
- Repository-relative path
- Title and section
- Knowledge layer
- Evidence status
- Confidentiality
- Tags
- Bounded source text
- Normalized sparse vector

The search API accepts 2–160 characters, returns at most 12 results, and exposes only the safe result DTO.

## Interpretation separation

- `Fact` means sourced content with its recorded evidence state.
- `Ricardo interpretation` means analysis or recommendation.
- `Founder decision` requires an explicit owner, date, scope, and revisit condition.
- A search score or priority score cannot promote evidence or execution state.

## Future semantic embeddings

Do not connect an embedding model or vector database until hosting, model provider, data-processing terms, retention, region, subprocessors, deletion, authentication, authorization, evaluation, and rollback are approved.
