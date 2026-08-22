BEGIN;

ALTER TABLE article_distillations
    ADD COLUMN IF NOT EXISTS insight_packet JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS quality_status TEXT NOT NULL DEFAULT 'incomplete',
    ADD COLUMN IF NOT EXISTS quality_issues JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS article_distillations_quality_idx
    ON article_distillations (quality_status, run_id, created_at DESC);

CREATE INDEX IF NOT EXISTS article_distillations_run_quality_idx
    ON article_distillations (run_id, quality_status);

CREATE INDEX IF NOT EXISTS article_distillations_insight_packet_idx
    ON article_distillations USING GIN (insight_packet);

COMMIT;
