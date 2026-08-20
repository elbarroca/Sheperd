CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT PRIMARY KEY,
    topic_set TEXT NOT NULL,
    request JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'succeeded', 'partial', 'failed')),
    as_of TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    neon_branch_id TEXT,
    migration_version TEXT NOT NULL DEFAULT '0001_initial',
    error TEXT
);

CREATE TABLE IF NOT EXISTS agent_steps (
    step_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS agent_steps_run_agent_idx
    ON agent_steps (run_id, agent_name);
CREATE INDEX IF NOT EXISTS agent_steps_run_idx ON agent_steps (run_id, created_at);

CREATE TABLE IF NOT EXISTS sources (
    normalized_url TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    retrieved_at TIMESTAMPTZ NOT NULL,
    source_kind TEXT NOT NULL,
    snippet TEXT NOT NULL DEFAULT '',
    topics TEXT[] NOT NULL DEFAULT '{}',
    geographies TEXT[] NOT NULL DEFAULT '{}',
    is_seed BOOLEAN NOT NULL DEFAULT FALSE,
    evidence_status TEXT NOT NULL DEFAULT 'unverified',
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'english'::regconfig,
            coalesce(title, '') || ' ' || coalesce(publisher, '') || ' ' ||
            coalesce(snippet, '')
        )
    ) STORED
);

CREATE INDEX IF NOT EXISTS sources_search_idx ON sources USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS sources_published_idx ON sources (published_at DESC);
CREATE INDEX IF NOT EXISTS sources_retrieved_idx ON sources (retrieved_at DESC);

CREATE TABLE IF NOT EXISTS source_snapshots (
    snapshot_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    normalized_url TEXT NOT NULL REFERENCES sources(normalized_url) ON DELETE RESTRICT,
    content_hash TEXT NOT NULL,
    content_length INTEGER NOT NULL DEFAULT 0,
    retrieved_at TIMESTAMPTZ NOT NULL,
    UNIQUE (run_id, normalized_url)
);

CREATE TABLE IF NOT EXISTS article_distillations (
    distillation_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    normalized_url TEXT NOT NULL REFERENCES sources(normalized_url) ON DELETE RESTRICT,
    summary TEXT NOT NULL,
    key_points JSONB NOT NULL DEFAULT '[]'::jsonb,
    limitations JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, normalized_url)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    claim_hash TEXT NOT NULL,
    claim_text TEXT NOT NULL,
    evidence_status TEXT NOT NULL DEFAULT 'unverified',
    confidence TEXT NOT NULL DEFAULT 'low',
    source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    support_locator TEXT,
    conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS claims_run_hash_idx ON claims (run_id, claim_hash);
CREATE INDEX IF NOT EXISTS claims_run_idx ON claims (run_id, created_at);

CREATE TABLE IF NOT EXISTS signal_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    geographies TEXT[] NOT NULL DEFAULT '{}',
    ports TEXT[] NOT NULL DEFAULT '{}',
    carriers TEXT[] NOT NULL DEFAULT '{}',
    event_at TIMESTAMPTZ,
    source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_status TEXT NOT NULL DEFAULT 'unverified',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS weekly_briefs (
    brief_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    covered_from TIMESTAMPTZ NOT NULL,
    covered_until TIMESTAMPTZ NOT NULL,
    summary TEXT NOT NULL,
    signal_event_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    limitations JSONB NOT NULL DEFAULT '[]'::jsonb,
    review_state TEXT NOT NULL DEFAULT 'draft',
    evidence_status TEXT NOT NULL DEFAULT 'mixed',
    model_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    content_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS review_decisions (
    decision_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    decision TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS review_decisions_run_idx ON review_decisions (run_id, created_at);
