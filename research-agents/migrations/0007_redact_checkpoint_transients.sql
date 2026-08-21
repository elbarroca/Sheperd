-- Article bodies, prompts, and arbitrary channels are transient execution state.
-- The checkpoint tables are created by the LangGraph saver after the ordered set,
-- so each cleanup is guarded for fresh databases and remains idempotent.
DO $$
BEGIN
    IF to_regclass('public.checkpoints') IS NOT NULL THEN
        UPDATE checkpoints SET metadata = '{}'::jsonb;
        UPDATE checkpoints
        SET checkpoint = jsonb_set(
            jsonb_set(checkpoint, '{channel_values,content}', '{}'::jsonb, true),
            '{channel_values,messages}', '[]'::jsonb, true
        )
        WHERE checkpoint ? 'channel_values';
    END IF;

    IF to_regclass('public.checkpoint_blobs') IS NOT NULL THEN
        UPDATE checkpoint_blobs
        SET type = 'msgpack',
            blob = decode('80', 'hex')
        WHERE channel = 'content';

        UPDATE checkpoint_blobs
        SET type = 'msgpack',
            blob = decode('90', 'hex')
        WHERE channel = 'messages';
    END IF;

    IF to_regclass('public.checkpoint_writes') IS NOT NULL THEN
        UPDATE checkpoint_writes
        SET type = 'msgpack',
            blob = decode('80', 'hex')
        WHERE channel = 'content';

        UPDATE checkpoint_writes
        SET type = 'msgpack',
            blob = decode('90', 'hex')
        WHERE channel = 'messages';
    END IF;
END $$;
