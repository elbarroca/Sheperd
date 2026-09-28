from __future__ import annotations

import argparse
import asyncio
import hashlib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

import sheperd_research.cli as cli_module
import sheperd_research.diagnostics as diagnostics_module
from sheperd_research.cli import (
    _audit_command,
    _best_repair_evidence,
    _context_version,
    _database,
    _history_repair_blocker,
    _parser,
    _repair_child_run_id,
    _run_command,
    _unresolved_repair_parents,
    _validate_command,
)
from sheperd_research.contracts import (
    ArticleDistillation,
    PeriodStatus,
    ResearchRunRequest,
    SourceCandidate,
    ValidationStatus,
)
from sheperd_research.db import MIGRATION_VERSION, InMemoryRepository
from sheperd_research.diagnostics import run_model_check, validate_database_url, validate_dev_branch
from sheperd_research.providers.errors import ProviderError
from sheperd_research.settings import (
    STRICT_OPENROUTER_MODEL,
    Settings,
    free_openrouter_policy_error,
    strict_openrouter_policy_error,
)


def test_settings_resolve_root_env_and_vault_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))
    settings = Settings()

    assert settings.repo_root == root
    assert settings.vault_root == root / "obsidian"
    assert settings.resolved_topics_path == root / "research-agents/config/topics.yml"
    assert (
        settings.resolved_source_catalog_path
        == root / "research-agents/config/source_catalog.yml"
    )
    assert settings.resolved_obsidian_output_dir == root / "obsidian/06_Research/Agent Runs"


def test_settings_exposes_ordered_tavily_key_slots() -> None:
    settings = Settings(
        tavily_api_key="primary-secret",
        tavily_api_key_2="secondary-secret",
        tavily_api_key_3="tertiary-secret",
    )

    assert settings.tavily_api_keys == (
        "primary-secret",
        "secondary-secret",
        "tertiary-secret",
    )
    assert settings.tavily_api_key_count == 3


def test_audit_database_reads_share_one_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class SnapshotRepository(InMemoryRepository):
        in_snapshot = False
        snapshot_entries = 0

        @contextmanager
        def read_snapshot(self) -> Iterator[None]:
            self.snapshot_entries += 1
            self.in_snapshot = True
            try:
                yield
            finally:
                self.in_snapshot = False

        def audit_summary(self) -> dict[str, object]:
            assert self.in_snapshot
            return {}

        def system_snapshot(self) -> dict[str, object]:
            assert self.in_snapshot
            return {}

        def close(self) -> None:
            return None

    repository = SnapshotRepository()
    quality_result: dict[str, object] = {
        "latest_strict_run": {"run_id": "strict-run", "current_status": "pass"},
        "current_status_counts": {"pass": 1},
        "blocking_reason_counts": {"incomplete_article_insights": 5},
    }

    def quality_audit(_: object) -> dict[str, object]:
        assert repository.in_snapshot
        return quality_result

    async def doctor(*_: object, **__: object) -> dict[str, object]:
        return {"status": "pass", "checks": {}}

    monkeypatch.setattr(cli_module, "_database", lambda _: repository)
    monkeypatch.setattr(cli_module, "_quality_audit", quality_audit)
    monkeypatch.setattr(cli_module, "run_doctor", doctor)
    printed: list[dict[str, object]] = []
    monkeypatch.setattr(cli_module, "_print_json", printed.append)

    result = _audit_command(
        argparse.Namespace(json=True, allow_free_fallbacks=False),
        Settings(_env_file=None),
    )

    assert result == 0
    assert repository.snapshot_entries == 1
    assert printed[0]["blockers"] == []

    quality_result["latest_strict_run"] = None
    printed.clear()
    result = _audit_command(
        argparse.Namespace(json=True, allow_free_fallbacks=False),
        Settings(_env_file=None),
    )

    assert result == 2
    assert repository.snapshot_entries == 2
    assert printed[0]["blockers"] == [
        {
            "check": "quality:latest_strict_run_missing",
            "status": "blocked",
            "message": "no active strict non-repair weekly run is available",
        }
    ]


def test_draft_commands_require_explicit_run_identity_and_as_of() -> None:
    parser = _parser()

    for command in ("run", "e2e", "repair"):
        with pytest.raises(SystemExit):
            parser.parse_args([command])


def test_context_version_hashes_only_the_six_controlled_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    relative_paths = (
        "obsidian/context/Founder Brief.md",
        "obsidian/context/Founder Intelligence Knowledge Contract.md",
        "obsidian/06_Research/SheperD Deep Research - Control Note.md",
        "obsidian/06_Research/Market Evidence and Source Map.md",
        "research-agents/config/topics.yml",
        "research-agents/config/source_catalog.yml",
    )
    for index, relative_path in enumerate(relative_paths):
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"controlled-{index}", encoding="utf-8")
    monkeypatch.setattr(cli_module, "_repository_commit", lambda _: "commit-1")
    settings = Settings(repo_root=tmp_path)

    first = _context_version(settings)
    manifest = "".join(
        sorted(
            f"{hashlib.sha256((tmp_path / relative_path).read_bytes()).hexdigest()}"
            f"  {relative_path}\n"
            for relative_path in relative_paths
        )
    )
    assert first == f"commit-1:{hashlib.sha256(manifest.encode()).hexdigest()}"
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")
    assert _context_version(settings) == first
    (tmp_path / relative_paths[0]).write_text("changed", encoding="utf-8")

    assert _context_version(settings) != first
    assert first.startswith("commit-1:")


def test_repair_child_ids_are_deterministic_and_parent_scoped() -> None:
    first = _repair_child_run_id("batch", "parent-a", 1)

    assert first == _repair_child_run_id("batch", "parent-a", 1)
    assert first != _repair_child_run_id("batch", "parent-b", 1)
    assert first != _repair_child_run_id("batch", "parent-a", 2)
    assert first.startswith("batch-p")
    assert first.endswith("-r1")


def test_repair_inventory_targets_only_enrolled_sourceful_incomplete_packets() -> None:
    repository = InMemoryRepository()
    repository.create_run("raw-only", ResearchRunRequest(topic_set="dnd-port"))
    repository.create_run("repairable", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/incomplete")
    repository.record_source(source, run_id="repairable")
    repository.record_distillation(
        "repairable",
        ArticleDistillation(
            source_url=source.url,
            summary="Legacy incomplete packet.",
        ),
    )
    repository.create_run(
        "prior-repair",
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind="repair",
            parent_run_id="repairable",
            repair_round=1,
        ),
    )

    parents = _unresolved_repair_parents(repository)  # type: ignore[arg-type]

    assert [parent[0] for parent in parents] == ["repairable"]


def test_repair_reuses_the_most_complete_prior_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    source = SourceCandidate(url="https://example.com/source")
    repository.record_source(source, run_id="parent")
    repository.create_run(
        "prior-child",
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind="repair",
            parent_run_id="parent",
            repair_round=1,
        ),
    )
    repository.record_source(source, run_id="prior-child")
    repository.record_snapshot("prior-child", source, "captured evidence")
    repository.record_distillation(
        "prior-child",
        ArticleDistillation(source_url=source.url, summary="Complete packet."),
    )
    monkeypatch.setattr(
        cli_module,
        "reader_source_contract_issues",
        lambda *_args, **_kwargs: [],
    )

    evidence_run_id, evidence_sources = _best_repair_evidence(
        repository,  # type: ignore[arg-type]
        "parent",
        repository.get_run_sources("parent"),
        as_of=ResearchRunRequest(topic_set="dnd-port").as_of,
    )

    assert evidence_run_id == "prior-child"
    assert [item.url for item in evidence_sources] == [source.url]


def test_history_repair_blocker_uses_unresolved_enrolled_parents() -> None:
    repository = InMemoryRepository()
    repository.create_run("parent", ResearchRunRequest(topic_set="dnd-port"))
    repository.record_source(
        SourceCandidate(url="https://example.com/incomplete"),
        run_id="parent",
    )
    repository.create_run(
        "repair-child",
        ResearchRunRequest(
            topic_set="dnd-port",
            validation_profile="repair",
            run_kind="repair",
            parent_run_id="parent",
            repair_round=1,
        ),
    )

    assert _history_repair_blocker(repository) == (
        "1 historical repair parent(s) remain unresolved"
    )


def test_run_command_blocks_read_only_mode_before_provider_checks(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[object] = []

    def fail_capability_report(*_: object, **__: object) -> object:
        calls.append(object())
        raise AssertionError("capability resolution should not run")

    monkeypatch.setattr(cli_module, "_capability_report", fail_capability_report)
    settings = Settings(
        run_mode="read-only",
        database_url="postgresql://ep-example-pooler.eu-central-1.aws.neon.tech/neondb",
        tavily_api_key="secret",
        openai_api_key="secret",
    )

    result = _run_command(
        argparse.Namespace(
            topic_set="dnd-port",
            cadence="weekly",
            strict=True,
            allow_free_fallbacks=False,
            verbose=False,
            run_id="canary-20260826T225937Z",
            as_of="2026-08-26T22:59:37Z",
            since=None,
            max_sources=3,
            model=None,
            seed_url=[],
        ),
        settings,
    )

    assert result == 2
    assert "RUN_MODE=autonomous-draft" in capsys.readouterr().out
    assert calls == []


def test_research_request_rejects_paid_models() -> None:
    with pytest.raises(ValueError, match=STRICT_OPENROUTER_MODEL):
        ResearchRunRequest(topic_set="dnd-port", model="openrouter/some-paid-model")
    with pytest.raises(ValueError, match=STRICT_OPENROUTER_MODEL):
        ResearchRunRequest(topic_set="dnd-port", model="malformed:free")


def test_strict_openrouter_policy_rejects_router_model_and_fallbacks() -> None:
    assert (
        strict_openrouter_policy_error("openrouter/free", ())
        == f"OPENROUTER_MODEL must be {STRICT_OPENROUTER_MODEL}"
    )


def test_free_fallback_policy_keeps_gemma_primary() -> None:
    assert free_openrouter_policy_error("nvidia/nemotron-3-super-120b-a12b:free", ()) == (
        f"OPENROUTER_MODEL must remain {STRICT_OPENROUTER_MODEL}"
    )
    assert free_openrouter_policy_error(
        STRICT_OPENROUTER_MODEL,
        ("openai/gpt-4o",),
    ) == "fallback model must be a valid OpenRouter :free model: openai/gpt-4o"
    assert (
        strict_openrouter_policy_error(
            STRICT_OPENROUTER_MODEL,
            ("nvidia/nemotron-3-super-120b-a12b:free",),
        )
        == "OPENROUTER_FALLBACK_MODELS must be empty"
    )
    assert (
        strict_openrouter_policy_error(
            STRICT_OPENROUTER_MODEL,
            (),
            raw_fallback_config=" , ",
        )
        == "OPENROUTER_FALLBACK_MODELS must be empty"
    )


def test_run_command_rejects_raw_fallback_config_before_capability_check(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))
    calls: list[object] = []

    def fail_capability_report(*_: object, **__: object) -> object:
        calls.append(object())
        raise AssertionError("capability resolution should not run")

    monkeypatch.setattr(cli_module, "_capability_report", fail_capability_report)
    settings = Settings(
        run_mode="autonomous-draft",
        database_url="postgresql://ep-example-pooler.eu-central-1.aws.neon.tech/neondb",
        tavily_api_key="secret",
        openrouter_api_key="secret",
        openrouter_fallback_models=",",
    )

    result = _run_command(
        argparse.Namespace(
            topic_set="dnd-port",
            as_of=None,
            since=None,
            max_sources=1,
            model=None,
            seed_url=[],
        ),
        settings,
    )

    assert result == 2
    assert "OPENROUTER_FALLBACK_MODELS must be empty" in capsys.readouterr().out
    assert calls == []


def test_validate_command_counts_only_succeeded_tool_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    request = ResearchRunRequest(topic_set="dnd-port", validation_profile="canary")

    class RepositoryStub:
        def get_run(self, _: str) -> dict[str, object]:
            return {
                "request": request.model_dump(mode="json"),
                "migration_version": MIGRATION_VERSION,
                "prompt_version": "workflow-v2",
            }

        def get_run_sources(self, _: str) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://example.com/source",
                    extraction_status="failed",
                    extraction_error_code="provider_unavailable",
                    period_status=PeriodStatus.IN_PERIOD,
                    eligible_for_weekly=True,
                ),
                SourceCandidate(
                    url="https://example.com/in-period-but-ineligible",
                    extraction_status="succeeded",
                    period_status=PeriodStatus.IN_PERIOD,
                    eligible_for_weekly=False,
                )
            ]

        def get_run_claims(self, _: str) -> list[object]:
            return []

        def get_run_lane_statuses(self, _: str) -> dict[str, str]:
            return {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"}

        def get_run_snapshot_hashes(self, _: str) -> list[str]:
            return []

        def get_run_period_counts(self, _: str) -> dict[str, int]:
            return {"in_period": 2}

        def get_run_tool_calls(self, _: str) -> list[dict[str, object]]:
            return [
                {
                    "lane": lane,
                    "tool_name": tool,
                    "status": "failed",
                    "error_code": "timeout" if lane == "regulatory" else None,
                }
                for lane in ("regulatory", "us-ports", "mexico")
                for tool in ("tavily_search", "tavily_extract")
            ]

        def get_run_steps(self, _: str) -> list[dict[str, object]]:
            return [
                {
                    "agent_name": "discovery:regulatory",
                    "status": "failed",
                    "error_code": "rate_limit",
                }
            ]

        def record_validation(self, _: object) -> None:
            return None

        def close(self) -> None:
            return None

    class ReportStub:
        status = ValidationStatus.PASS

        def model_dump(self, **_: object) -> dict[str, object]:
            return {}

    def build_report(*_: object, **kwargs: object) -> ReportStub:
        captured.update(kwargs)
        return ReportStub()

    monkeypatch.setattr(cli_module, "_require_database", lambda _: True)
    monkeypatch.setattr(cli_module, "_database", lambda _: RepositoryStub())
    monkeypatch.setattr(cli_module, "build_validation_report", build_report)

    result = _validate_command(argparse.Namespace(run_id="run-1"), Settings())

    assert result == 0
    assert captured["tool_call_count"] == 0
    assert captured["eligible_weekly_source_count"] == 1
    assert captured["require_reader_contract"] is True
    assert captured["required_tool_lanes"] == {
        "regulatory": False,
        "us-ports": False,
        "mexico": False,
    }
    assert captured["provider_error_codes"] == [
        "extraction_failed",
        "provider_unavailable",
        "rate_limit",
        "timeout",
    ]


def test_validate_command_uses_the_persisted_repair_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    request = ResearchRunRequest(
        topic_set="dnd-port",
        validation_profile="repair",
        run_kind="repair",
        parent_run_id="parent",
        repair_round=1,
    )
    sources = [
        SourceCandidate(
            url=f"https://example.com/source-{index}",
            source_kind="repair",
            extraction_status="succeeded",
        )
        for index in range(2)
    ]
    events = [object(), object()]

    class RepositoryStub:
        def get_run(self, _: str) -> dict[str, object]:
            return {"request": request.model_dump(mode="json")}

        def get_run_sources(self, _: str) -> list[SourceCandidate]:
            return sources

        def get_run_claims(self, _: str) -> list[object]:
            return [object(), object()]

        def get_run_distillations(self, _: str) -> list[object]:
            return [object(), object()]

        def get_run_signal_events(self, _: str) -> list[object]:
            return events

        def get_brief(self, _: str) -> None:
            return None

        def get_run_lane_statuses(self, _: str) -> dict[str, str]:
            return {}

        def get_run_snapshot_hashes(self, _: str) -> list[str]:
            return ["a" * 64, "b" * 64]

        def get_run_tool_calls(self, _: str) -> list[dict[str, object]]:
            return []

        def get_run_steps(self, _: str) -> list[dict[str, object]]:
            return []

        def get_run_period_counts(self, _: str) -> dict[str, int]:
            return {}

        def record_validation(self, _: object) -> None:
            return None

        def close(self) -> None:
            return None

    class ReportStub:
        status = ValidationStatus.PASS

        def model_dump(self, **_: object) -> dict[str, object]:
            return {}

    def build_report(*_: object, **kwargs: object) -> ReportStub:
        captured.update(kwargs)
        return ReportStub()

    monkeypatch.setattr(cli_module, "_require_database", lambda _: True)
    monkeypatch.setattr(cli_module, "_database", lambda _: RepositoryStub())
    monkeypatch.setattr(cli_module, "build_validation_report", build_report)

    result = _validate_command(argparse.Namespace(run_id="repair-run"), Settings())

    assert result == 0
    assert captured["minimum_sources"] == 2
    assert captured["minimum_claims"] == 2
    assert captured["required_source_hash_count"] == 2
    assert captured["tool_call_count"] is None
    assert captured["required_tool_lanes"] is None
    assert captured["required_lanes"] == set()
    assert captured["signal_events"] == events


def test_database_url_policy_distinguishes_pooled_and_direct_connections() -> None:
    pooled = "postgresql://ep-example-pooler.eu-central-1.aws.neon.tech/neondb"
    direct = "postgresql://ep-example.eu-central-1.aws.neon.tech/neondb"

    assert validate_database_url(pooled, pooled=True) is None
    assert validate_database_url(direct, pooled=False) is None
    assert validate_database_url(direct, pooled=True) is not None
    assert validate_database_url("not-a-dsn", pooled=False) is not None


def test_database_constructor_rejects_malformed_runtime_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))
    settings = Settings(database_url="not-a-dsn")

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        _database(settings)


def test_configured_main_branch_is_allowed() -> None:
    assert validate_dev_branch("main") is None
    assert validate_dev_branch("production") is None
    assert validate_dev_branch("dev") is None


def test_run_model_check_blocks_when_live_capabilities_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).resolve().parents[3]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))

    async def fail_capabilities(*_: object, **__: object) -> object:
        raise ProviderError("OpenRouter live capability manifest unavailable")

    monkeypatch.setattr(diagnostics_module, "resolve_capabilities", fail_capabilities)
    result = asyncio.run(run_model_check(Settings(openrouter_api_key="secret")))

    assert result["status"] == "blocked"
    assert result["message"] == "OpenRouter live capability manifest unavailable"


def test_model_check_strict_gate_allows_explicit_free_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    observed: dict[str, object] = {}

    class SettingsStub:
        pass

    async def fake_model_check(
        settings: object, *, allow_free_fallbacks: bool
    ) -> dict[str, object]:
        observed["settings"] = settings
        observed["allow_free_fallbacks"] = allow_free_fallbacks
        return {"status": "pass"}

    monkeypatch.setattr(cli_module, "Settings", SettingsStub)
    monkeypatch.setattr(cli_module, "run_model_check", fake_model_check)

    assert (
        cli_module.main(
            ["model-check", "--allow-free-fallbacks", "--strict", "--json"]
        )
        == 0
    )
    assert observed["allow_free_fallbacks"] is True
    assert capsys.readouterr().out.strip() == '{"status": "pass"}'
