ALTER TABLE research_runs
    ADD COLUMN IF NOT EXISTS run_kind TEXT NOT NULL DEFAULT 'research'
        CHECK (run_kind IN ('research', 'repair')),
    ADD COLUMN IF NOT EXISTS parent_run_id TEXT REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS repair_round SMALLINT
        CHECK (repair_round BETWEEN 1 AND 3);

ALTER TABLE research_runs
    ADD CONSTRAINT research_runs_repair_lineage_check CHECK (
        (run_kind = 'research' AND parent_run_id IS NULL AND repair_round IS NULL)
        OR
        (run_kind = 'repair' AND parent_run_id IS NOT NULL AND repair_round BETWEEN 1 AND 3)
    );

CREATE INDEX IF NOT EXISTS research_runs_lineage_idx
    ON research_runs (parent_run_id, repair_round, started_at DESC);
CREATE INDEX IF NOT EXISTS research_runs_kind_idx
    ON research_runs (run_kind, started_at DESC);

ALTER TABLE run_sources
    ADD COLUMN IF NOT EXISTS source_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(source_snapshot) = 'object'),
    ADD COLUMN IF NOT EXISTS published_at_snapshot TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS retrieved_at_snapshot TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS snapshot_basis TEXT NOT NULL DEFAULT 'legacy_backfill'
        CHECK (snapshot_basis IN ('captured', 'legacy_backfill'));

UPDATE run_sources rs
SET source_snapshot = jsonb_strip_nulls(jsonb_build_object(
        'url', s.url,
        'title', s.title,
        'publisher', s.publisher,
        'published_at', s.published_at,
        'retrieved_at', s.retrieved_at,
        'source_kind', s.source_kind,
        'snippet', s.snippet,
        'topics', to_jsonb(s.topics),
        'geographies', to_jsonb(s.geographies),
        'lane', s.lane,
        'is_seed', s.is_seed,
        'evidence_status', s.evidence_status,
        'region', s.region,
        'language_code', s.language_code,
        'language_confidence', s.language_confidence,
        'authority_tier', s.authority_tier,
        'catalog_source_id', s.catalog_source_id,
        'source_type', s.source_type,
        'freshness_status', s.freshness_status,
        'freshness_days', s.freshness_days,
        'extraction_status', rs.extraction_status,
        'extraction_error_code', rs.extraction_error_code,
        'normalized_title_en', s.normalized_title_en,
        'normalized_snippet_en', s.normalized_snippet_en,
        'period_status', rs.period_status,
        'period_basis', rs.period_basis,
        'eligible_for_weekly', rs.eligible_for_weekly
    )),
    published_at_snapshot = s.published_at,
    retrieved_at_snapshot = s.retrieved_at,
    snapshot_basis = 'legacy_backfill'
FROM sources s
WHERE s.normalized_url = rs.normalized_url
  AND rs.source_snapshot = '{}'::jsonb;

ALTER TABLE run_sources
    ALTER COLUMN snapshot_basis SET DEFAULT 'captured';

ALTER TABLE run_sources
    DROP CONSTRAINT IF EXISTS run_sources_period_basis_check;
ALTER TABLE run_sources
    ADD CONSTRAINT run_sources_period_basis_check CHECK (
        period_basis IN ('published_at', 'event_at', 'retrieved_at', 'run_as_of', 'unknown')
    );

CREATE INDEX IF NOT EXISTS run_sources_snapshot_basis_idx
    ON run_sources (run_id, snapshot_basis, normalized_url);
CREATE INDEX IF NOT EXISTS run_sources_publication_snapshot_idx
    ON run_sources (run_id, published_at_snapshot DESC);

CREATE OR REPLACE FUNCTION enforce_finished_run_source_snapshot_immutability()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF ROW(
        NEW.source_snapshot,
        NEW.published_at_snapshot,
        NEW.retrieved_at_snapshot,
        NEW.snapshot_basis
    ) IS DISTINCT FROM ROW(
        OLD.source_snapshot,
        OLD.published_at_snapshot,
        OLD.retrieved_at_snapshot,
        OLD.snapshot_basis
    ) AND EXISTS (
        SELECT 1
        FROM research_runs rr
        WHERE rr.run_id = OLD.run_id
          AND rr.status <> 'running'
    ) THEN
        RAISE EXCEPTION 'run source snapshots are immutable after run completion';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS run_sources_snapshot_immutability ON run_sources;
CREATE TRIGGER run_sources_snapshot_immutability
BEFORE UPDATE OF source_snapshot, published_at_snapshot, retrieved_at_snapshot, snapshot_basis
ON run_sources
FOR EACH ROW
EXECUTE FUNCTION enforce_finished_run_source_snapshot_immutability();

ALTER TABLE signal_events
    ADD COLUMN IF NOT EXISTS headline TEXT,
    ADD COLUMN IF NOT EXISTS what_changed TEXT,
    ADD COLUMN IF NOT EXISTS published_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS retrieved_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS period_status TEXT
        CHECK (period_status IN ('in_period', 'background', 'undated', 'future', 'excluded')),
    ADD COLUMN IF NOT EXISTS period_basis TEXT
        CHECK (period_basis IN ('published_at', 'event_at', 'retrieved_at', 'run_as_of', 'unknown')),
    ADD COLUMN IF NOT EXISTS eligible_for_weekly BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS region TEXT,
    ADD COLUMN IF NOT EXISTS lane TEXT,
    ADD COLUMN IF NOT EXISTS evidence_locator TEXT,
    ADD COLUMN IF NOT EXISTS impact TEXT,
    ADD COLUMN IF NOT EXISTS risk TEXT,
    ADD COLUMN IF NOT EXISTS opportunity TEXT,
    ADD COLUMN IF NOT EXISTS next_step TEXT,
    ADD COLUMN IF NOT EXISTS limitations JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS signal_events_timeline_idx
    ON signal_events (run_id, eligible_for_weekly, event_at, published_at);
CREATE INDEX IF NOT EXISTS signal_events_lane_region_idx
    ON signal_events (run_id, lane, region);
