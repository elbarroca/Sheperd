from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import yaml
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
)
from pydantic import ValidationError

from .contracts import (
    LaneDiscoveryResult,
    ResearchCadence,
    ResearchRunRequest,
    ReviewState,
    RunResult,
    RunStatus,
    ValidationStatus,
)
from .db import PostgresRepository, _redact_audit_metadata, run_migrations
from .diagnostics import (
    mcp_check,
    run_doctor,
    run_model_check,
    validate_database_url,
    validate_dev_branch,
)
from .exporters.obsidian import export_reviewed_brief
from .exporters.regional_indexes import generate_regional_indexes
from .progress import ProgressReporter
from .providers.capabilities import CapabilityReport, resolve_capabilities
from .providers.errors import ProviderError
from .providers.openrouter import OpenRouterProvider
from .providers.tavily import TavilyProvider
from .settings import (
    STRICT_OPENROUTER_MODEL,
    Settings,
    free_openrouter_policy_error,
    strict_openrouter_policy_error,
)
from .source_catalog import REGIONS, load_source_catalog, validate_required_sources
from .topics import load_topic_configs
from .validation import build_validation_report
from .web import create_app
from .workflow import ResearchWorkflow, checkpoint_serializer

_CHECKPOINT_ALLOWED_CHANNELS = frozenset(
    {
        "run_id",
        "request",
        "topic",
        "retained_sources",
        "retained_distillations",
        "sources",
        "source_hashes",
        "distillations",
        "claims",
        "signals",
        "brief",
        "validation",
        "lane_statuses",
        "partial_reasons",
    }
)


def _redact_checkpoint(checkpoint: Checkpoint) -> Checkpoint:
    redacted = checkpoint.copy()
    channel_values = redacted.get("channel_values", {})
    redacted["channel_values"] = {
        channel: value
        for channel, value in channel_values.items()
        if channel in _CHECKPOINT_ALLOWED_CHANNELS
    }
    return redacted


def _redact_checkpoint_metadata(metadata: CheckpointMetadata) -> CheckpointMetadata:
    return cast(
        CheckpointMetadata,
        _redact_audit_metadata(dict(metadata)),
    )


def _redact_checkpoint_writes(
    writes: Sequence[tuple[str, Any]],
) -> list[tuple[str, Any]]:
    redacted: list[tuple[str, Any]] = []
    for channel, value in writes:
        if channel == "content":
            redacted.append((channel, {}))
        elif channel == "messages":
            redacted.append((channel, []))
        elif channel in _CHECKPOINT_ALLOWED_CHANNELS:
            redacted.append((channel, value))
    return redacted


@asynccontextmanager
async def _checkpoint_saver(
    database_url: str,
) -> AsyncIterator[BaseCheckpointSaver[str]]:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg import AsyncConnection
    from psycopg.rows import DictRow, dict_row
    from psycopg_pool import AsyncConnectionPool

    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
        database_url,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        min_size=1,
        max_size=4,
        max_lifetime=300,
        max_idle=60,
        open=False,
    )
    class RedactingAsyncPostgresSaver(AsyncPostgresSaver):
        async def aput(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions,
        ) -> RunnableConfig:
            return await super().aput(
                config,
                _redact_checkpoint(checkpoint),
                _redact_checkpoint_metadata(metadata),
                new_versions,
            )

        async def aput_writes(
            self,
            config: RunnableConfig,
            writes: Sequence[tuple[str, Any]],
            task_id: str,
            task_path: str = "",
        ) -> None:
            await super().aput_writes(
                config,
                _redact_checkpoint_writes(writes),
                task_id,
                task_path,
            )

    async with pool:
        checkpointer = RedactingAsyncPostgresSaver(
            conn=pool,
            serde=checkpoint_serializer(),
        )
        await checkpointer.setup()
        yield cast(BaseCheckpointSaver[str], checkpointer)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(UTC)


def _database(settings: Settings) -> PostgresRepository:
    branch_error = validate_dev_branch(settings.neon_branch_id)
    if branch_error:
        raise RuntimeError(f"BLOCKED: {branch_error}")
    url_error = validate_database_url(settings.database_url, pooled=True)
    if url_error:
        raise RuntimeError(f"BLOCKED: DATABASE_URL: {url_error}")
    assert settings.database_url is not None
    try:
        return PostgresRepository.from_url(settings.database_url, settings.neon_branch_id)
    except Exception as error:
        raise RuntimeError(
            f"BLOCKED: DATABASE_URL connection failed: {error.__class__.__name__}"
        ) from error


def _require_database(settings: Settings) -> bool:
    try:
        branch_error = validate_dev_branch(settings.neon_branch_id)
        url_error = validate_database_url(settings.database_url, pooled=True)
    except Exception:
        branch_error = None
        url_error = "database URL is malformed"
    if branch_error:
        print(f"BLOCKED: {branch_error}")
        return False
    if url_error:
        print(f"BLOCKED: DATABASE_URL: {url_error}")
        return False
    return True


def _print_json(value: object) -> None:
    print(json.dumps(value, default=str, sort_keys=True))


def _blocked(args: argparse.Namespace, message: str) -> int:
    if getattr(args, "json", False):
        _print_json({"status": "blocked", "error": message})
    else:
        print(message if message.startswith("BLOCKED:") else f"BLOCKED: {message}")
    return 2


def _capability_report(
    settings: Settings,
    models: tuple[str, ...],
    *,
    require_tools: bool,
    allow_cached: bool = True,
) -> CapabilityReport:
    if settings.openrouter_api_key is None:
        raise ProviderError("OPENROUTER_API_KEY is not configured")
    return asyncio.run(
        resolve_capabilities(
            settings.openrouter_api_key.get_secret_value(),
            models,
            settings.openrouter_capabilities_cache,
            require_tools=require_tools,
            allow_cached=allow_cached,
        )
    )


def _run_command(args: argparse.Namespace, settings: Settings) -> int:
    progress = ProgressReporter(enabled=bool(getattr(args, "verbose", False)))
    allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))
    if not getattr(args, "strict", True) and not allow_free_fallbacks:
        return _blocked(args, "run requires --strict or --allow-free-fallbacks")
    if not settings.has_database_credentials:
        return _blocked(args, "set pooled DATABASE_URL in the repository-root .env.local")
    if not settings.has_live_provider_credentials:
        return _blocked(
            args,
            "set replacement Tavily and OpenRouter keys in the repository-root .env.local",
        )
    requested_model = args.model or settings.openrouter_model
    model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
    fallback_models = model_chain[1:]
    policy_error = (
        free_openrouter_policy_error(
            requested_model,
            fallback_models,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
        if allow_free_fallbacks
        else strict_openrouter_policy_error(
            requested_model,
            settings.openrouter_fallback_model_list,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
    )
    if policy_error is not None:
        return _blocked(args, policy_error)
    try:
        request = ResearchRunRequest(
            topic_set=args.topic_set,
            cadence=ResearchCadence(getattr(args, "cadence", "weekly")),
            as_of=_parse_datetime(args.as_of) or datetime.now(UTC),
            since=_parse_datetime(args.since),
            max_sources=args.max_sources,
            model=requested_model,
            seed_urls=args.seed_url,
        )
    except ValueError as error:
        return _blocked(args, str(error))
    try:
        capabilities = _capability_report(
            settings,
            (request.model, *fallback_models),
            require_tools=True,
            allow_cached=False,
        )
    except ProviderError as error:
        return _blocked(args, str(error))
    if not capabilities.eligible_models:
        return _blocked(args, "no free model supports discovery tools and structured output")
    try:
        repository = _database(settings)
    except RuntimeError as error:
        return _blocked(args, str(error))
    try:
        openrouter_key = settings.openrouter_api_key
        if not settings.tavily_api_keys or openrouter_key is None:
            return _blocked(args, "provider credentials are incomplete")

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        settings.tavily_api_keys,
                        settings.tavily_project_id,
                        timeout_seconds=15 if getattr(args, "profile", "full") == "canary" else 45,
                        progress=progress,
                    ),
                    OpenRouterProvider(
                        openrouter_key.get_secret_value(),
                        request.model,
                        fallback_models=tuple(
                            model
                            for model in fallback_models
                            if model != request.model
                        ),
                        allow_free_fallbacks=allow_free_fallbacks,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_report=capabilities,
                        max_concurrent_requests=(
                            1
                            if allow_free_fallbacks
                            else (
                                2
                                if getattr(args, "profile", "full") == "canary"
                                else 1
                            )
                        ),
                        progress=progress,
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=settings.llm_max_calls,
                    max_llm_input_chars=settings.llm_max_input_chars,
                    max_run_seconds=settings.max_run_seconds,
                    progress=progress,
                )
                return await workflow.run(request, run_id=args.run_id)

        result = asyncio.run(execute())
        _print_json(result.model_dump(mode="json"))
        return 0 if result.validation_status is ValidationStatus.PASS else 2
    finally:
        repository.close()


def _rollup_command(args: argparse.Namespace, settings: Settings) -> int:
    try:
        month = datetime.strptime(args.month, "%Y-%m").replace(tzinfo=UTC)
        if month.strftime("%Y-%m") != args.month:
            raise ValueError
    except ValueError:
        return _blocked(args, "--month must use YYYY-MM")
    next_month = (
        datetime(month.year + 1, 1, 1, tzinfo=UTC)
        if month.month == 12
        else datetime(month.year, month.month + 1, 1, tzinfo=UTC)
    )
    try:
        repository = _database(settings)
    except RuntimeError as error:
        return _blocked(args, str(error))
    try:
        rollups = repository.monthly_rollup(
            since=month,
            until=next_month - timedelta(microseconds=1),
        )
        _print_json({"status": "pass", "month": args.month, "rollups": rollups})
        return 0
    except Exception as error:
        return _blocked(args, f"monthly rollup failed: {error.__class__.__name__}")
    finally:
        repository.close()


def _audit_command(args: argparse.Namespace, settings: Settings) -> int:
    try:
        repository = _database(settings)
    except RuntimeError as error:
        return _blocked(args, str(error))
    try:
        summary = repository.audit_summary()
        diagnostics = asyncio.run(
            run_doctor(
                settings,
                allow_free_fallbacks=bool(getattr(args, "allow_free_fallbacks", False)),
            )
        )
        blockers: list[dict[str, object]] = []
        checks = diagnostics.get("checks", {})
        if isinstance(checks, dict):
            for name, value in checks.items():
                if (
                    name != "providers"
                    and
                    isinstance(value, dict)
                    and value.get("status") not in {"pass", "not_configured"}
                ):
                    blockers.append(
                        {
                            "check": name,
                            "status": value.get("status"),
                            "message": value.get("message"),
                        }
                    )
                if name == "providers" and isinstance(value, dict):
                    for provider, provider_check in value.items():
                        if (
                            isinstance(provider_check, dict)
                            and provider_check.get("status") not in {"pass", "not_configured"}
                        ):
                            blockers.append(
                                {
                                    "check": f"provider:{provider}",
                                    "status": provider_check.get("status"),
                                    "message": provider_check.get("message"),
                                }
                            )
        status = "pass" if diagnostics.get("status") == "pass" else "blocked"
        _print_json(
            {
                "status": status,
                "database": summary,
                "diagnostics": diagnostics,
                "blockers": blockers,
            }
        )
        return 0 if status == "pass" else 2
    except Exception as error:
        return _blocked(args, f"audit failed: {error.__class__.__name__}")
    finally:
        repository.close()


def _e2e_command(args: argparse.Namespace, settings: Settings) -> int:
    progress = ProgressReporter(enabled=bool(getattr(args, "verbose", False)))
    stages: dict[str, dict[str, object]] = {}
    allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))

    def stage(name: str, status: str, **details: object) -> None:
        stages[name] = {"status": status, **details}

    if not settings.has_database_credentials or not settings.has_direct_database_credentials:
        stage("environment", "blocked", message="pooled and direct database URLs are required")
        _print_json({"status": "blocked", "stages": stages})
        return 2
    if not settings.has_live_provider_credentials:
        stage("environment", "blocked", message="Tavily and OpenRouter credentials are required")
        _print_json({"status": "blocked", "stages": stages})
        return 2
    model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
    fallback_models = model_chain[1:]
    policy_error = (
        free_openrouter_policy_error(
            settings.openrouter_model,
            fallback_models,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
        if allow_free_fallbacks
        else strict_openrouter_policy_error(
            settings.openrouter_model,
            settings.openrouter_fallback_model_list,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
    )
    if policy_error is not None:
        stage("environment", "blocked", message=policy_error)
        _print_json({"status": "blocked", "stages": stages})
        return 2
    try:
        capabilities = _capability_report(
            settings,
            model_chain,
            require_tools=True,
            allow_cached=False,
        )
    except ProviderError as error:
        stage("environment", "blocked", message=str(error))
        _print_json({"status": "blocked", "stages": stages})
        return 2
    if not capabilities.eligible_models:
        stage("environment", "blocked", message="no eligible free discovery model")
        _print_json({"status": "blocked", "stages": stages})
        return 2
    stage(
        "environment",
        "pass",
        model=settings.openrouter_model,
        fallback_models=list(capabilities.eligible_models[1:]),
        eligible_models=list(capabilities.eligible_models),
        skipped_models=list(capabilities.skipped_models),
        capability_manifest_hash=capabilities.manifest_hash,
        branch_id=settings.neon_branch_id,
    )
    try:
        request = ResearchRunRequest(
            topic_set="dnd-port",
            as_of=_parse_datetime(args.as_of) or datetime.now(UTC),
            max_sources=3 if args.profile == "canary" else 30,
            model=settings.openrouter_model,
            include_topic_seeds=False,
            validation_profile=args.profile,
        )
        repository = _database(settings)
        health = repository.health()
        stage("database", "pass", migration_version=health.get("migration_version"))
    except (RuntimeError, ValueError) as error:
        stage("database", "blocked", message=error.__class__.__name__)
        _print_json({"status": "blocked", "stages": stages})
        return 2

    try:
        openrouter_key = settings.openrouter_api_key
        assert settings.tavily_api_keys and openrouter_key is not None

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        settings.tavily_api_keys,
                        settings.tavily_project_id,
                        progress=progress,
                    ),
                    OpenRouterProvider(
                        openrouter_key.get_secret_value(),
                        request.model,
                        fallback_models=fallback_models,
                        allow_free_fallbacks=allow_free_fallbacks,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_report=capabilities,
                        max_concurrent_requests=(
                            1
                            if allow_free_fallbacks
                            else (2 if args.profile == "canary" else 1)
                        ),
                        progress=progress,
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=min(
                        settings.llm_max_calls,
                        5 if args.profile == "canary" else 48,
                    ),
                    max_llm_input_chars=min(
                        settings.llm_max_input_chars,
                        60_000 if args.profile == "canary" else 350_000,
                    ),
                    max_run_seconds=min(
                        settings.max_run_seconds,
                        420 if args.profile == "canary" else 900,
                    ),
                    discovery_query_limit=1 if args.profile == "canary" else None,
                    progress=progress,
                )
                return await workflow.run(request, run_id=args.run_id)

        result = asyncio.run(execute())
        steps = repository.get_run_steps(args.run_id)
        sources = repository.get_run_sources(args.run_id)
        brief = repository.get_brief(args.run_id)
        validation = repository.get_validation(args.run_id)
        tool_calls = repository.get_run_tool_calls(args.run_id)
        distillations = repository.get_run_distillations(args.run_id)
        tool_counts = {
            tool_name: sum(1 for call in tool_calls if call.get("tool_name") == tool_name)
            for tool_name in ("tavily_search", "tavily_extract")
        }
        lane_counts = {
            lane: sum(1 for source in sources if source.lane == lane)
            for lane in ("regulatory", "us-ports", "mexico")
        }
        resolved_models = sorted(
            {
                str(model)
                for model in [
                    *(step.get("resolved_model") for step in steps),
                    brief.model_id if brief else None,
                ]
                if model
            }
        )
        stage(
            "workflow",
            result.status.value,
            run_id=args.run_id,
            source_count=len(sources),
            distillation_count=len(distillations),
            claim_count=result.claim_count,
            tool_call_count=len(tool_calls),
            tool_counts=tool_counts,
            lane_counts=lane_counts,
            resolved_models=resolved_models,
            error=result.error,
        )
        stage(
            "persistence",
            "pass" if repository.get_run(args.run_id) is not None else "failed",
            brief_written=brief is not None,
            validation_written=validation is not None,
            checkpoint_steps=len(steps),
            source_count=len(sources),
            distillation_count=len(distillations),
            claim_count=result.claim_count,
            tool_call_count=len(tool_calls),
        )

        from fastapi.testclient import TestClient

        client = TestClient(create_app(repository))
        weekly_response = client.get(f"/api/reports/weekly/{args.run_id}")
        monthly_response = client.get("/api/reports/monthly")
        api_passed = weekly_response.status_code == 200 and monthly_response.status_code == 200
        weekly_payload = weekly_response.json() if weekly_response.status_code == 200 else {}
        required_sections = {
            "brief",
            "validation",
            "lane_coverage",
            "models",
            "steps",
            "as_of",
            "covered_from",
            "covered_until",
        }
        ui_passed = api_passed and required_sections.issubset(weekly_payload)
        api_status = "pass" if api_passed else "failed"
        ui_status = "pass" if ui_passed else "failed"
        stage("api", api_status, weekly_status=weekly_response.status_code)
        stage("ui_contract", ui_status, sections=sorted(required_sections))
        lane_passed = all(lane_counts[lane] > 0 for lane in lane_counts)
        step_names = {str(step.get("agent_name")) for step in steps}
        required_steps = {"distillation", "critic", "synthesis", "validation"}
        accepted = (
            result.status.value == "succeeded"
            and brief is not None
            and validation is not None
            and validation.status is ValidationStatus.PASS
            and lane_passed
            and required_steps.issubset(step_names)
            and api_passed
            and ui_passed
        )
        status = "pass" if accepted else "failed"
        _print_json(
            {
                "status": status,
                "run_id": args.run_id,
                "validation_status": validation.status.value if validation else "missing",
                "resolved_models": resolved_models,
                "stages": stages,
            }
        )
        return 0 if accepted else 2
    except Exception as error:
        stage("workflow", "failed", message=error.__class__.__name__)
        _print_json({"status": "failed", "run_id": args.run_id, "stages": stages})
        return 2
    finally:
        repository.close()


def _agent_check_command(args: argparse.Namespace, settings: Settings) -> int:
    progress = ProgressReporter(enabled=bool(getattr(args, "verbose", False)))
    if not settings.tavily_api_key or not settings.openrouter_api_key:
        _print_json(
            {
                "status": "blocked",
                "message": "Tavily and OpenRouter credentials are required",
            }
        )
        return 2
    provider: OpenRouterProvider | None = None
    capabilities: CapabilityReport | None = None
    try:
        allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))
        model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
        fallback_models = model_chain[1:]
        policy_error = (
            free_openrouter_policy_error(
                settings.openrouter_model,
                fallback_models,
                raw_fallback_config=settings.openrouter_fallback_models,
            )
            if allow_free_fallbacks
            else strict_openrouter_policy_error(
                settings.openrouter_model,
                settings.openrouter_fallback_model_list,
                raw_fallback_config=settings.openrouter_fallback_models,
            )
        )
        if policy_error is not None:
            raise ProviderError(policy_error)
        capabilities = _capability_report(
            settings,
            model_chain,
            require_tools=True,
            allow_cached=False,
        )
        if not capabilities.eligible_models:
            raise ProviderError("no free model supports discovery tools and structured output")
        topic = load_topic_configs(settings.resolved_topics_path)["dnd-port"]
        as_of = _parse_datetime(args.as_of) or datetime.now(UTC)
        since = as_of - timedelta(days=topic.lookback_days)
        provider = OpenRouterProvider(
            settings.openrouter_api_key.get_secret_value(),
            settings.openrouter_model,
            fallback_models=fallback_models,
            allow_free_fallbacks=allow_free_fallbacks,
            capability_report=capabilities,
            timeout_seconds=15,
            progress=progress,
        )
        tavily = TavilyProvider(
            settings.tavily_api_keys,
            settings.tavily_project_id,
            timeout_seconds=20,
            progress=progress,
        )

        async def execute() -> LaneDiscoveryResult:
            return await provider.discover_lane(
                "regulatory",
                [topic.queries[0]],
                ("Regulatory", "United States"),
                since=since,
                until=as_of,
                include_domains=topic.include_domains,
                exclude_domains=topic.exclude_domains,
                max_results=3,
                tavily=tavily,
            )

        result = asyncio.run(execute())
        attempts = result.metadata.get("attempts", [])
        if not isinstance(attempts, list):
            attempts = []
        receipts: list[dict[str, object]] = []
        for attempt in attempts:
            raw_receipts = attempt.get("tool_call_receipts") if isinstance(attempt, dict) else None
            if isinstance(raw_receipts, list):
                receipts.extend(item for item in raw_receipts if isinstance(item, dict))
        tool_names = {str(receipt.get("tool_name")) for receipt in receipts}
        resolved_models = sorted(
            {
                str(item.get("resolved_model"))
                for item in attempts
                if isinstance(item, dict) and item.get("resolved_model")
            }
        )
        checks = {
            "create_agent": True,
            "chat_openrouter": True,
            "tavily_search": "tavily_search" in tool_names,
            "tavily_extract": "tavily_extract" in tool_names,
            "structured_output": bool(result.packet.source_urls),
            "resolved_models_free": all(
                model in set(capabilities.eligible_models) for model in resolved_models
            ),
            "strict_resolved_model": (
                resolved_models == [STRICT_OPENROUTER_MODEL]
                if not allow_free_fallbacks
                else True
            ),
        }
        passed = all(checks.values()) and bool(receipts)
        _print_json(
            {
                "status": "pass" if passed else "partial",
                "checks": checks,
                "source_count": len(result.sources),
                "extracted_count": len(result.content),
                "tool_calls": len(receipts),
                "resolved_models": resolved_models,
                "capability_manifest_hash": capabilities.manifest_hash,
                "attempts": attempts,
            }
        )
        return 0 if passed else 2
    except (ProviderError, ValueError) as error:
        attempt_error_code = next(
            (
                str(attempt.get("error_code"))
                for attempt in reversed(provider.call_history if provider else [])
                if isinstance(attempt, dict) and attempt.get("error_code")
            ),
            None,
        )
        _print_json(
            {
                "status": "partial",
                "message": str(error),
                "error_code": getattr(error, "error_code", None) or attempt_error_code,
                "capabilities": capabilities.as_dict() if capabilities else None,
                "attempts": provider.call_history if provider else [],
            }
        )
        return 2


def _validate_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    try:
        run = repository.get_run(args.run_id)
        if run is None:
            print(f"ERROR: run not found: {args.run_id}")
            return 2
        request_value = run.get("request")
        if not isinstance(request_value, dict):
            print("BLOCKED: run request metadata is unavailable")
            return 2
        request = ResearchRunRequest.model_validate(request_value)
        sources = repository.get_run_sources(args.run_id)
        claims = repository.get_run_claims(args.run_id)
        get_distillations = getattr(repository, "get_run_distillations", None)
        distillations = get_distillations(args.run_id) if callable(get_distillations) else None
        strict_profile = request.validation_profile in {"full", "global-canary"}
        report = build_validation_report(
            args.run_id,
            sources,
            claims,
            request.as_of,
            request.model,
            repository.get_run_lane_statuses(args.run_id),
            repository.get_run_snapshot_hashes(args.run_id),
            minimum_sources=1 if request.validation_profile in {"canary", "global-canary"} else 10,
            minimum_claims=1 if request.validation_profile in {"canary", "global-canary"} else 5,
            tool_call_count=sum(
                1
                for call in repository.get_run_tool_calls(args.run_id)
                if call.get("status") == "succeeded"
            ),
            required_tool_lanes={
                lane: {
                    "tavily_search",
                    "tavily_extract",
                }.issubset(
                    {
                        str(call.get("tool_name"))
                        for call in repository.get_run_tool_calls(args.run_id)
                        if call.get("lane") == lane
                        and call.get("status") == "succeeded"
                    }
                )
                for lane in ("regulatory", "us-ports", "mexico")
            },
            distillations=distillations,
            required_geographies=(
                {
                    "Regulatory",
                    "United States",
                    "West Coast",
                    "East Coast",
                    "Gulf",
                    "Canada",
                    "Mexico",
                    "Europe",
                    "South America",
                    "Middle East",
                }
                if strict_profile
                else set()
            ),
            required_regions=(set(REGIONS) - {"global"} if strict_profile else set()),
        )
        repository.record_validation(report)
        _print_json(report.model_dump(mode="json"))
        return 0 if report.status is ValidationStatus.PASS else 2
    finally:
        repository.close()


def _source_map_command(args: argparse.Namespace, settings: Settings) -> int:
    del args.json
    if args.strict and not args.check:
        _print_json(
            {
                "status": "blocked",
                "error_code": "source_map_check_required",
                "message": "source-map --strict requires --check",
            }
        )
        return 2
    try:
        catalog = load_source_catalog(settings.resolved_source_catalog_path)
    except FileNotFoundError:
        _print_json(
            {
                "status": "blocked",
                "error_code": "source_catalog_missing",
                "message": "source catalog not found",
            }
        )
        return 2
    except (ValidationError, ValueError, yaml.YAMLError):
        _print_json(
            {
                "status": "blocked",
                "error_code": "source_catalog_invalid",
                "message": "source catalog failed validation",
            }
        )
        return 2

    statuses: dict[str, str] = {}
    validation_error_code: str | None = None
    validation_message: str | None = None
    if args.check:
        if settings.tavily_api_key is None:
            _print_json(
                {
                    "status": "blocked",
                    "error_code": "source_map_credentials_required",
                    "message": "Tavily credentials are required for source-map --check",
                }
            )
            return 2
        tavily = TavilyProvider(
            settings.tavily_api_keys,
            settings.tavily_project_id,
            timeout_seconds=15,
        )
        try:
            observations = asyncio.run(validate_required_sources(catalog, tavily))
            statuses = {
                observation.source_id: observation.status
                for observation in observations
            }
        except ProviderError:
            validation_error_code = "source_map_check_failed"
            validation_message = "required-domain validation failed"
        except ValueError:
            validation_error_code = "source_map_check_incomplete"
            validation_message = "required-domain validation missing observations"

    required_ids = {source.source_id for source in catalog.required_sources()}
    missing_observations = sorted(required_ids - set(statuses))
    if args.check and missing_observations and validation_error_code is None:
        validation_error_code = "source_map_check_incomplete"
        validation_message = "required-domain validation missing observations"
    failing_required = sorted(
        source.source_id
        for source in catalog.required_sources()
        if statuses.get(source.source_id) != "pass"
    )
    observed_regions = {source.region for source in catalog.enabled_sources()}
    missing_regions = sorted(set(REGIONS) - observed_regions)
    status = "pass"
    if validation_message is not None or (
        args.check and (missing_observations or failing_required or missing_regions)
    ):
        status = "failed" if args.strict else "partial"

    _print_json(
        {
            "status": status,
            "summary": {
                "sources": len(catalog.sources),
                "enabled": len(catalog.enabled_sources()),
                "required": len(catalog.required_sources()),
                "coverage_weights": catalog.coverage_weights.as_dict(),
                "required_failures": failing_required,
                "missing_observations": missing_observations,
                "missing_regions": missing_regions,
                "validation_error_code": validation_error_code,
                "validation_message": validation_message,
            },
            "sources": catalog.redacted_rows(statuses),
        }
    )
    return 0 if status == "pass" or (status == "partial" and not args.strict) else 2


def _index_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    try:
        requested = args.region.strip().lower()
        regions = "all" if requested == "all" else [requested]
        result = generate_regional_indexes(
            repository,
            settings.vault_root / "06_Research" / "Research Index",
            run_id=args.run_id,
            regions=regions,
        )
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    except (RuntimeError, ValueError, OSError) as error:
        return _blocked(args, f"regional index generation failed: {error.__class__.__name__}")
    finally:
        repository.close()


def _review_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    try:
        decision = {
            "approve": ReviewState.APPROVED,
            "reject": ReviewState.REJECTED,
            "needs-review": ReviewState.NEEDS_REVIEW,
        }[args.decision]
        if decision is ReviewState.APPROVED:
            run = repository.get_run(args.run_id)
            if run is None or run.get("status") != RunStatus.SUCCEEDED.value:
                print("BLOCKED: only a succeeded run may be approved")
                return 2
            validation = repository.get_validation(args.run_id)
            if validation is None or validation.status is not ValidationStatus.PASS:
                print("BLOCKED: only a fully passing validation may be approved")
                return 2
        repository.review_brief(args.run_id, decision, args.reviewer, args.notes)
        print(f"Recorded {decision.value} for {args.run_id}.")
        return 0
    finally:
        repository.close()


def _export_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    try:
        brief = repository.get_brief(args.run_id)
        if brief is None:
            print(f"ERROR: brief not found: {args.run_id}")
            return 2
        if repository.get_validation(args.run_id) is None:
            print("BLOCKED: run has no validation report")
            return 2
        run = repository.get_run(args.run_id)
        if run is None or run.get("status") != "succeeded":
            print("BLOCKED: only a succeeded run may be exported")
            return 2
        destination = (
            Path(args.output).resolve()
            if args.output
            else settings.resolved_obsidian_output_dir
            / f"{brief.covered_until.date()} - {brief.title}.md"
        )
        output_root = settings.resolved_obsidian_output_dir.resolve()
        if output_root not in destination.parents and destination != output_root:
            print("BLOCKED: exports are limited to obsidian/06_Research/Agent Runs/")
            return 2
        export_reviewed_brief(
            brief,
            destination,
            validation=repository.get_validation(args.run_id),
            sources=repository.get_run_sources(args.run_id),
            distillations=repository.get_run_distillations(args.run_id),
            claims=repository.get_run_claims(args.run_id),
            source_hashes=repository.get_run_source_hashes(args.run_id),
            signals=repository.get_run_signal_events(args.run_id),
            steps=repository.get_run_steps(args.run_id),
            tool_calls=repository.get_run_tool_calls(args.run_id),
            run=run,
        )
        print(destination)
        return 0
    except PermissionError as error:
        print(f"BLOCKED: {error}")
        return 2
    finally:
        repository.close()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sheperd-research")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--topic-set", default="dnd-port")
    run.add_argument("--cadence", choices=["daily", "weekly"], default="weekly")
    run.add_argument("--strict", action="store_true")
    run.add_argument("--allow-free-fallbacks", action="store_true")
    run.add_argument("--json", action="store_true")
    run.add_argument("--verbose", action="store_true")
    run.add_argument("--run-id")
    run.add_argument("--since")
    run.add_argument("--as-of")
    run.add_argument("--max-sources", type=int, default=25)
    run.add_argument("--model")
    run.add_argument("--seed-url", action="append", default=[])

    e2e = subparsers.add_parser("e2e")
    e2e.add_argument(
        "--profile", choices=["canary", "global-canary", "full"], default="canary"
    )
    e2e.add_argument("--strict", action="store_true")
    e2e.add_argument("--allow-free-fallbacks", action="store_true")
    e2e.add_argument("--run-id", required=True)
    e2e.add_argument("--as-of")
    e2e.add_argument("--json", action="store_true")
    e2e.add_argument("--verbose", action="store_true")

    agent_check = subparsers.add_parser("agent-check")
    agent_check.add_argument("--strict", action="store_true")
    agent_check.add_argument("--allow-free-fallbacks", action="store_true")
    agent_check.add_argument("--as-of")
    agent_check.add_argument("--json", action="store_true")
    agent_check.add_argument("--verbose", action="store_true")

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--strict", action="store_true")
    doctor.add_argument("--allow-free-fallbacks", action="store_true")
    doctor.add_argument("--json", action="store_true")
    mcp_check_parser = subparsers.add_parser("mcp-check")
    mcp_check_parser.add_argument("--strict", action="store_true")
    mcp_check_parser.add_argument("--json", action="store_true")
    model_check = subparsers.add_parser("model-check")
    model_check.add_argument("--strict", action="store_true")
    model_check.add_argument("--allow-free-fallbacks", action="store_true")
    model_check.add_argument("--json", action="store_true")
    source_map = subparsers.add_parser("source-map")
    source_map.add_argument("--check", action="store_true")
    source_map.add_argument("--strict", action="store_true")
    source_map.add_argument("--json", action="store_true")
    index = subparsers.add_parser("index")
    index.add_argument("--region", default="all")
    index.add_argument("--run-id", required=True)
    index.add_argument("--json", action="store_true")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("migrate")

    rollup = subparsers.add_parser("rollup")
    rollup.add_argument("--month", required=True)
    rollup.add_argument("--json", action="store_true")

    audit = subparsers.add_parser("audit")
    audit.add_argument("--allow-free-fallbacks", action="store_true")
    audit.add_argument("--json", action="store_true")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--run-id", required=True)

    review = subparsers.add_parser("review")
    review.add_argument("--run-id", required=True)
    review.add_argument(
        "--decision", choices=["approve", "reject", "needs-review"], required=True
    )
    review.add_argument("--reviewer", default="local-reviewer")
    review.add_argument("--notes", default="")

    export = subparsers.add_parser("export")
    export.add_argument("--run-id", required=True)
    export.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    settings = Settings()
    if args.command == "run":
        return _run_command(args, settings)
    if args.command == "rollup":
        return _rollup_command(args, settings)
    if args.command == "audit":
        return _audit_command(args, settings)
    if args.command == "e2e":
        return _e2e_command(args, settings)
    if args.command == "agent-check":
        return _agent_check_command(args, settings)
    if args.command == "doctor":
        result = asyncio.run(
            run_doctor(settings, allow_free_fallbacks=args.allow_free_fallbacks)
        )
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "mcp-check":
        result = mcp_check()
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "model-check":
        result = asyncio.run(
            run_model_check(
                settings, allow_free_fallbacks=args.allow_free_fallbacks
            )
        )
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "source-map":
        return _source_map_command(args, settings)
    if args.command == "index":
        return _index_command(args, settings)
    if args.command == "validate":
        return _validate_command(args, settings)
    if args.command == "review":
        return _review_command(args, settings)
    if args.command == "export":
        return _export_command(args, settings)
    if args.command == "migrate":
        branch_error = validate_dev_branch(settings.neon_branch_id)
        if branch_error:
            print(f"BLOCKED: {branch_error}")
            return 2
        url_error = validate_database_url(settings.direct_database_url, pooled=False)
        if url_error:
            print(f"BLOCKED: DIRECT_DATABASE_URL: {url_error}")
            return 2
        assert settings.direct_database_url is not None
        try:
            names = run_migrations(
                settings.direct_database_url,
                settings.research_agents_root / "migrations",
            )
        except Exception as error:
            print(f"BLOCKED: migration failed: {error.__class__.__name__}")
            return 2
        print(
            f"Applied {', '.join(names)}."
            if names
            else "No migrations applied; database is current."
        )
        return 0
    if args.command == "dashboard":
        if not _require_database(settings):
            return 2
        try:
            repository = _database(settings)
        except RuntimeError as error:
            print(str(error))
            return 2
        import uvicorn

        uvicorn.run(create_app(repository), host=settings.host, port=settings.port)
        return 0
    print("Unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
