ALTER TABLE agent_steps
    ADD COLUMN IF NOT EXISTS model_index INTEGER,
    ADD COLUMN IF NOT EXISTS fallback_reason TEXT,
    ADD COLUMN IF NOT EXISTS tool_calls INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS agent_steps_attempt_idx
    ON agent_steps (run_id, agent_name, attempt, created_at);
CREATE INDEX IF NOT EXISTS agent_steps_model_attempt_idx
    ON agent_steps (resolved_model, attempt, created_at DESC);
CREATE INDEX IF NOT EXISTS agent_steps_error_idx
    ON agent_steps (error_code, created_at DESC);
