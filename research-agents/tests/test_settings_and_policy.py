from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import pytest

import sheperd_research.cli as cli_module
import sheperd_research.diagnostics as diagnostics_module
from sheperd_research.cli import _database, _run_command, _validate_command
from sheperd_research.contracts import ResearchRunRequest, SourceCandidate, ValidationStatus
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
    )

    assert settings.tavily_api_keys == ("primary-secret", "secondary-secret")
    assert settings.tavily_api_key_count == 2


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
            return {"request": request.model_dump(mode="json")}

        def get_run_sources(self, _: str) -> list[SourceCandidate]:
            return [
                SourceCandidate(
                    url="https://example.com/source",
                    extraction_status="failed",
                    extraction_error_code="provider_unavailable",
                )
            ]

        def get_run_claims(self, _: str) -> list[object]:
            return []

        def get_run_lane_statuses(self, _: str) -> dict[str, str]:
            return {"regulatory": "succeeded", "us-ports": "succeeded", "mexico": "succeeded"}

        def get_run_snapshot_hashes(self, _: str) -> list[str]:
            return []

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
