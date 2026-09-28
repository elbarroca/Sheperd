BEGIN;

ALTER TABLE run_sources
    ADD COLUMN IF NOT EXISTS period_status TEXT NOT NULL DEFAULT 'undated'
        CHECK (period_status IN ('in_period', 'background', 'undated', 'future', 'excluded')),
    ADD COLUMN IF NOT EXISTS period_basis TEXT NOT NULL DEFAULT 'unknown'
        CHECK (period_basis IN ('published_at', 'retrieved_at', 'run_as_of', 'unknown')),
    ADD COLUMN IF NOT EXISTS eligible_for_weekly BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS run_sources_period_idx
    ON run_sources (period_status, eligible_for_weekly, run_id);
CREATE INDEX IF NOT EXISTS run_sources_weekly_eligible_idx
    ON run_sources (run_id, eligible_for_weekly, period_status);

UPDATE run_sources rs
SET period_status = CASE
        WHEN s.published_at IS NULL THEN 'undated'
        WHEN s.published_at > rr.as_of THEN 'future'
        WHEN s.published_at >= COALESCE(wb.covered_from, rr.as_of - INTERVAL '7 days')
             AND s.published_at < COALESCE(wb.covered_until, rr.as_of)
            THEN 'in_period'
        ELSE 'background'
    END,
    period_basis = CASE
        WHEN s.published_at IS NULL THEN 'unknown'
        ELSE 'published_at'
    END,
    eligible_for_weekly = (
        s.published_at IS NOT NULL
        AND s.published_at <= rr.as_of
        AND s.published_at >= COALESCE(wb.covered_from, rr.as_of - INTERVAL '7 days')
        AND s.published_at < COALESCE(wb.covered_until, rr.as_of)
    )
FROM sources s
JOIN research_runs rr ON TRUE
LEFT JOIN weekly_briefs wb ON wb.run_id = rr.run_id
WHERE s.normalized_url = rs.normalized_url
  AND rr.run_id = rs.run_id;

COMMIT;
