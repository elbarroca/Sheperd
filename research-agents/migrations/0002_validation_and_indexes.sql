ALTER TABLE research_runs
    ADD COLUMN IF NOT EXISTS model_id TEXT NOT NULL DEFAULT 'google/gemma-4-26b-a4b-it:free',
    ADD COLUMN IF NOT EXISTS prompt_version TEXT NOT NULL DEFAULT 'workflow-v2',
    ADD COLUMN IF NOT EXISTS citation_coverage NUMERIC(6, 5) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS validation_status TEXT NOT NULL DEFAULT 'blocked',
    ADD COLUMN IF NOT EXISTS validation_content_hash TEXT;

ALTER TABLE agent_steps
    ADD COLUMN IF NOT EXISTS lane TEXT NOT NULL DEFAULT 'system',
    ADD COLUMN IF NOT EXISTS attempt INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS duration_ms INTEGER,
    ADD COLUMN IF NOT EXISTS input_hash TEXT,
    ADD COLUMN IF NOT EXISTS output_hash TEXT,
    ADD COLUMN IF NOT EXISTS error_code TEXT;

DROP INDEX IF EXISTS agent_steps_run_agent_idx;
CREATE UNIQUE INDEX IF NOT EXISTS agent_steps_run_agent_attempt_idx
    ON agent_steps (run_id, agent_name, attempt);

ALTER TABLE sources
    ADD COLUMN IF NOT EXISTS lane TEXT NOT NULL DEFAULT 'unassigned';

ALTER TABLE article_distillations
    ADD COLUMN IF NOT EXISTS content_hash TEXT,
    ADD COLUMN IF NOT EXISTS evidence_status TEXT NOT NULL DEFAULT 'mixed';

ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS supersedes_claim_id BIGINT REFERENCES claims(claim_id) ON DELETE RESTRICT;

ALTER TABLE weekly_briefs
    ADD COLUMN IF NOT EXISTS search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'english'::regconfig,
            coalesce(title, '') || ' ' || coalesce(summary, '')
        )
    ) STORED;

ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english'::regconfig, coalesce(claim_text, ''))
    ) STORED;

CREATE INDEX IF NOT EXISTS research_runs_status_idx ON research_runs (status, started_at DESC);
CREATE INDEX IF NOT EXISTS research_runs_as_of_idx ON research_runs (as_of DESC);
CREATE INDEX IF NOT EXISTS agent_steps_lane_idx ON agent_steps (run_id, lane, status);
CREATE INDEX IF NOT EXISTS sources_lane_idx ON sources (lane, published_at DESC);
CREATE INDEX IF NOT EXISTS sources_geographies_idx ON sources USING GIN (geographies);
CREATE INDEX IF NOT EXISTS claims_search_idx ON claims USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS claims_evidence_idx ON claims (evidence_status, created_at DESC);
CREATE INDEX IF NOT EXISTS weekly_briefs_search_idx ON weekly_briefs USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS weekly_briefs_review_idx ON weekly_briefs (review_state, covered_until DESC);

CREATE TABLE IF NOT EXISTS validation_checks (
    validation_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE REFERENCES research_runs(run_id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK (status IN ('pass', 'partial', 'blocked', 'failed')),
    source_count INTEGER NOT NULL DEFAULT 0,
    unique_source_count INTEGER NOT NULL DEFAULT 0,
    claim_count INTEGER NOT NULL DEFAULT 0,
    cited_claim_count INTEGER NOT NULL DEFAULT 0,
    citation_coverage NUMERIC(6, 5) NOT NULL DEFAULT 0,
    lane_coverage TEXT[] NOT NULL DEFAULT '{}',
    checks JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    as_of TIMESTAMPTZ,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS validation_checks_status_idx
    ON validation_checks (status, created_at DESC);
