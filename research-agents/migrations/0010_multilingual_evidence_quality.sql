BEGIN;

ALTER TABLE sources
    ADD COLUMN IF NOT EXISTS region TEXT NOT NULL DEFAULT 'global',
    ADD COLUMN IF NOT EXISTS language_code TEXT NOT NULL DEFAULT 'und',
    ADD COLUMN IF NOT EXISTS language_confidence NUMERIC(4, 3) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS authority_tier TEXT NOT NULL DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS catalog_source_id TEXT,
    ADD COLUMN IF NOT EXISTS source_type TEXT NOT NULL DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS freshness_status TEXT NOT NULL DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS freshness_days INTEGER,
    ADD COLUMN IF NOT EXISTS extraction_status TEXT NOT NULL DEFAULT 'not_attempted',
    ADD COLUMN IF NOT EXISTS extraction_error_code TEXT,
    ADD COLUMN IF NOT EXISTS normalized_title_en TEXT,
    ADD COLUMN IF NOT EXISTS normalized_snippet_en TEXT;

DROP INDEX IF EXISTS sources_search_idx;
ALTER TABLE sources DROP COLUMN IF EXISTS search_vector;
ALTER TABLE sources
    ADD COLUMN search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'english'::regconfig,
            coalesce(title, '') || ' ' || coalesce(publisher, '') || ' ' ||
            coalesce(snippet, '') || ' ' || coalesce(normalized_title_en, '') || ' ' ||
            coalesce(normalized_snippet_en, '')
        )
    ) STORED;
CREATE INDEX IF NOT EXISTS sources_search_idx ON sources USING GIN (search_vector);

ALTER TABLE article_distillations
    ADD COLUMN IF NOT EXISTS source_language TEXT NOT NULL DEFAULT 'und',
    ADD COLUMN IF NOT EXISTS summary_original TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS key_points_original JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS translation_status TEXT NOT NULL DEFAULT 'not_needed',
    ADD COLUMN IF NOT EXISTS evidence_excerpts JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS evidence_locators JSONB NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS original_claim TEXT,
    ADD COLUMN IF NOT EXISTS evidence_excerpt TEXT,
    ADD COLUMN IF NOT EXISTS independent_source_count INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS citation_status TEXT NOT NULL DEFAULT 'uncited',
    ADD COLUMN IF NOT EXISTS verification_basis TEXT;

DROP INDEX IF EXISTS claims_search_idx;
ALTER TABLE claims DROP COLUMN IF EXISTS search_vector;
ALTER TABLE claims
    ADD COLUMN search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'english'::regconfig,
            coalesce(claim_text, '') || ' ' || coalesce(original_claim, '') || ' ' ||
            coalesce(evidence_excerpt, '')
        )
    ) STORED;
CREATE INDEX IF NOT EXISTS claims_search_idx ON claims USING GIN (search_vector);

UPDATE claims
SET
    citation_status = CASE
        WHEN jsonb_typeof(source_urls) = 'array' AND jsonb_array_length(source_urls) > 0
            THEN 'cited'
        ELSE 'uncited'
    END,
    independent_source_count = CASE
        WHEN jsonb_typeof(source_urls) = 'array' AND jsonb_array_length(source_urls) > 0
            THEN 1
        ELSE 0
    END
WHERE citation_status = 'uncited' OR independent_source_count = 0;

UPDATE claims
SET
    evidence_status = 'partially-supported',
    verification_basis = 'legacy-single-source'
WHERE evidence_status = 'verified'
  AND (
      jsonb_typeof(source_urls) <> 'array'
      OR jsonb_array_length(source_urls) < 2
  );

CREATE INDEX IF NOT EXISTS sources_region_idx
    ON sources (region, published_at DESC);
CREATE INDEX IF NOT EXISTS sources_language_idx
    ON sources (language_code, retrieved_at DESC);
CREATE INDEX IF NOT EXISTS sources_freshness_idx
    ON sources (freshness_status, published_at DESC);
CREATE INDEX IF NOT EXISTS sources_authority_type_idx
    ON sources (authority_tier, source_type, retrieved_at DESC);
CREATE INDEX IF NOT EXISTS sources_extraction_idx
    ON sources (extraction_status, retrieved_at DESC);
CREATE INDEX IF NOT EXISTS claims_verification_basis_idx
    ON claims (verification_basis, independent_source_count, created_at DESC);
CREATE INDEX IF NOT EXISTS article_distillations_language_idx
    ON article_distillations (source_language, translation_status, created_at DESC);
CREATE INDEX IF NOT EXISTS article_distillations_translation_idx
    ON article_distillations (translation_status, created_at DESC);

COMMIT;
