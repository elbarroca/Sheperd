from pathlib import Path


def test_archive_migration_is_append_safe_and_backfills_failed_runs() -> None:
    migration = (
        Path(__file__).parents[1] / "migrations" / "0011_archive_failed_runs.sql"
    ).read_text()

    assert "archived_at" in migration
    assert "archive_reason" in migration
    assert "validation_status = 'failed'" in migration
    assert "status = 'failed'" in migration
    assert "DELETE" not in migration.upper()
