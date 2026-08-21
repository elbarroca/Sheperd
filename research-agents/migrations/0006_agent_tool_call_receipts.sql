CREATE TABLE IF NOT EXISTS agent_tool_calls (
    tool_call_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    agent_step_id BIGINT REFERENCES agent_steps(step_id) ON DELETE RESTRICT,
    agent_name TEXT NOT NULL,
    lane TEXT NOT NULL DEFAULT 'system',
    attempt INTEGER NOT NULL,
    call_index INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    query TEXT,
    urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    input_hash TEXT NOT NULL,
    result_hash TEXT,
    result_count INTEGER,
    latency_ms INTEGER,
    status TEXT NOT NULL,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, agent_name, attempt, call_index)
);

CREATE INDEX IF NOT EXISTS agent_tool_calls_run_idx
    ON agent_tool_calls (run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS agent_tool_calls_tool_idx
    ON agent_tool_calls (run_id, tool_name, status);
CREATE INDEX IF NOT EXISTS agent_tool_calls_attempt_idx
    ON agent_tool_calls (agent_name, attempt, created_at DESC);

ALTER TABLE agent_steps
    ADD COLUMN IF NOT EXISTS capability_manifest_hash TEXT,
    ADD COLUMN IF NOT EXISTS required_tools JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS agent_steps_capability_manifest_idx
    ON agent_steps (capability_manifest_hash, created_at DESC);

ALTER TABLE article_distillations
    ADD COLUMN IF NOT EXISTS entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS signals JSONB NOT NULL DEFAULT '[]'::jsonb;
