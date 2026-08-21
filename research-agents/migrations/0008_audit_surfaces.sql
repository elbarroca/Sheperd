-- Task 4: retain only structured, sanitized audit arguments and query receipts.
ALTER TABLE agent_tool_calls
    ADD COLUMN IF NOT EXISTS sanitized_args JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS agent_tool_calls_run_lane_idx
    ON agent_tool_calls (run_id, lane, created_at DESC);

CREATE INDEX IF NOT EXISTS source_snapshots_run_hash_idx
    ON source_snapshots (run_id, content_hash);

CREATE INDEX IF NOT EXISTS article_distillations_run_evidence_idx
    ON article_distillations (run_id, evidence_status, created_at DESC);

CREATE INDEX IF NOT EXISTS claims_run_evidence_idx
    ON claims (run_id, evidence_status, created_at DESC);

CREATE INDEX IF NOT EXISTS signal_events_run_evidence_idx
    ON signal_events (run_id, evidence_status, event_at DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS agent_steps_run_stage_idx
    ON agent_steps (run_id, agent_name, status, created_at DESC);

CREATE INDEX IF NOT EXISTS research_runs_validation_as_of_idx
    ON research_runs (validation_status, as_of DESC);
