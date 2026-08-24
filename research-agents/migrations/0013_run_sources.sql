BEGIN;

CREATE TABLE IF NOT EXISTS run_sources (
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    normalized_url TEXT NOT NULL REFERENCES sources(normalized_url) ON DELETE RESTRICT,
    extraction_status TEXT NOT NULL DEFAULT 'not_attempted'
        CHECK (extraction_status IN ('succeeded', 'failed', 'not_attempted')),
    extraction_error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (run_id, normalized_url)
);

INSERT INTO run_sources (
    run_id, normalized_url, extraction_status, extraction_error_code, created_at, updated_at
)
SELECT
    run_id, normalized_url, 'succeeded', NULL, retrieved_at, retrieved_at
FROM source_snapshots
ON CONFLICT (run_id, normalized_url) DO NOTHING;

CREATE INDEX IF NOT EXISTS run_sources_url_idx
    ON run_sources (normalized_url, run_id);
CREATE INDEX IF NOT EXISTS run_sources_extraction_idx
    ON run_sources (run_id, extraction_status);

COMMIT;
