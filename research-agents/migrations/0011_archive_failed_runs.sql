BEGIN;

ALTER TABLE research_runs
    ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS archive_reason TEXT;

UPDATE research_runs
SET archived_at = COALESCE(archived_at, now()),
    archive_reason = COALESCE(archive_reason, CASE
        WHEN validation_status = 'failed' THEN 'validation_failed'
        ELSE 'run_failed'
    END)
WHERE archived_at IS NULL
  AND (status = 'failed' OR validation_status = 'failed');

CREATE INDEX IF NOT EXISTS research_runs_active_reports_idx
    ON research_runs (as_of DESC, run_id)
    WHERE archived_at IS NULL;

CREATE INDEX IF NOT EXISTS research_runs_archived_reports_idx
    ON research_runs (archived_at DESC, as_of DESC, run_id)
    WHERE archived_at IS NOT NULL;

COMMIT;
