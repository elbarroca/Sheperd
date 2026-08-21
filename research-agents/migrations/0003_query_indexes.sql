CREATE INDEX IF NOT EXISTS research_runs_topic_status_as_of_idx
    ON research_runs (topic_set, status, as_of DESC);

CREATE INDEX IF NOT EXISTS agent_steps_run_status_idx
    ON agent_steps (run_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS source_snapshots_run_url_idx
    ON source_snapshots (run_id, normalized_url);

CREATE INDEX IF NOT EXISTS article_distillations_run_idx
    ON article_distillations (run_id, created_at DESC);

CREATE INDEX IF NOT EXISTS sources_evidence_published_idx
    ON sources (evidence_status, published_at DESC);

CREATE INDEX IF NOT EXISTS signal_events_run_event_idx
    ON signal_events (run_id, event_at DESC, created_at DESC);

CREATE INDEX IF NOT EXISTS weekly_briefs_period_idx
    ON weekly_briefs (covered_from DESC, covered_until DESC);
