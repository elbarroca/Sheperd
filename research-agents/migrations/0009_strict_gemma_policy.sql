ALTER TABLE research_runs
    ALTER COLUMN model_id SET DEFAULT 'google/gemma-4-26b-a4b-it:free';

UPDATE research_runs
SET model_id = 'google/gemma-4-26b-a4b-it:free'
WHERE model_id IS DISTINCT FROM 'google/gemma-4-26b-a4b-it:free';
