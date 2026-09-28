BEGIN;

ALTER TABLE weekly_briefs
    ADD COLUMN IF NOT EXISTS pdf_blob_path TEXT,
    ADD COLUMN IF NOT EXISTS pdf_blob_url TEXT,
    ADD COLUMN IF NOT EXISTS pdf_content_hash TEXT,
    ADD COLUMN IF NOT EXISTS pdf_uploaded_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS weekly_briefs_pdf_artifact_idx
    ON weekly_briefs (pdf_blob_path, pdf_uploaded_at DESC);

COMMIT;
