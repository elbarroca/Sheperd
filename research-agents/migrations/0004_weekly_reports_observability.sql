ALTER TABLE weekly_briefs
    ADD COLUMN IF NOT EXISTS executive_bullets JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS developments JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS risks JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS opportunities JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS uncertainties JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS follow_up_questions JSONB NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE agent_steps
    ADD COLUMN IF NOT EXISTS requested_model TEXT,
    ADD COLUMN IF NOT EXISTS resolved_model TEXT,
    ADD COLUMN IF NOT EXISTS prompt_version TEXT,
    ADD COLUMN IF NOT EXISTS request_id TEXT,
    ADD COLUMN IF NOT EXISTS input_tokens INTEGER,
    ADD COLUMN IF NOT EXISTS output_tokens INTEGER,
    ADD COLUMN IF NOT EXISTS total_tokens INTEGER,
    ADD COLUMN IF NOT EXISTS wall_clock_ms INTEGER;

CREATE INDEX IF NOT EXISTS weekly_briefs_report_period_idx
    ON weekly_briefs (covered_from DESC, covered_until DESC, review_state);
CREATE INDEX IF NOT EXISTS weekly_briefs_model_idx
    ON weekly_briefs (model_id, covered_until DESC);
CREATE INDEX IF NOT EXISTS agent_steps_resolved_model_idx
    ON agent_steps (resolved_model, created_at DESC);
CREATE INDEX IF NOT EXISTS agent_steps_status_idx
    ON agent_steps (run_id, status, created_at DESC);
