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

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
)

from .contracts import (
    LaneDiscoveryResult,
    ResearchRunRequest,
    ReviewState,
    RunResult,
    RunStatus,
    ValidationStatus,
    is_free_model,
)
from .db import PostgresRepository, run_migrations
from .diagnostics import (
    mcp_check,
    run_doctor,
    run_model_check,
    validate_database_url,
    validate_dev_branch,
)
from .exporters.obsidian import export_reviewed_brief
from .providers.capabilities import CapabilityReport, resolve_capabilities
from .providers.errors import ProviderError
from .providers.openrouter import OpenRouterProvider
from .providers.tavily import TavilyProvider
from .settings import STRICT_OPENROUTER_MODEL, Settings, strict_openrouter_policy_error
from .topics import load_topic_configs
from .validation import build_validation_report
from .web import create_app
from .workflow import ResearchWorkflow, checkpoint_serializer


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
        @staticmethod
        def _redact_checkpoint(checkpoint: Checkpoint) -> Checkpoint:
            redacted = checkpoint.copy()
            channel_values = dict(redacted["channel_values"])
            channel_values.pop("content", None)
            channel_values.pop("messages", None)
            redacted["channel_values"] = channel_values
            return redacted

        async def aput(
            self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions,
        ) -> RunnableConfig:
            return await super().aput(
                config,
                self._redact_checkpoint(checkpoint),
                metadata,
                new_versions,
            )

        async def aput_writes(
            self,
            config: RunnableConfig,
            writes: Sequence[tuple[str, Any]],
            task_id: str,
            task_path: str = "",
        ) -> None:
            redacted_writes = [
                (
                    channel,
                    []
                    if channel == "messages"
                    else {} if channel == "content" else value,
                )
                for channel, value in writes
            ]
            await super().aput_writes(config, redacted_writes, task_id, task_path)

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
    if not settings.has_database_credentials:
        print("BLOCKED: set pooled DATABASE_URL in the repository-root .env.local")
        return 2
    if not settings.has_live_provider_credentials:
        print(
            "BLOCKED: set replacement Tavily and OpenRouter keys "
            "in the repository-root .env.local"
        )
        return 2
    requested_model = args.model or settings.openrouter_model
    policy_error = strict_openrouter_policy_error(
        requested_model,
        settings.openrouter_fallback_model_list,
    )
    if policy_error is not None:
        print(f"BLOCKED: {policy_error}")
        return 2
    try:
        request = ResearchRunRequest(
            topic_set=args.topic_set,
            as_of=_parse_datetime(args.as_of) or datetime.now(UTC),
            since=_parse_datetime(args.since),
            max_sources=args.max_sources,
            model=requested_model,
            seed_urls=args.seed_url,
        )
    except ValueError as error:
        print(f"BLOCKED: {error}")
        return 2
    try:
        capabilities = _capability_report(
            settings,
            (request.model,),
            require_tools=True,
            allow_cached=False,
        )
    except ProviderError as error:
        print(f"BLOCKED: {error}")
        return 2
    if not capabilities.eligible_models:
        print("BLOCKED: no free model supports discovery tools and structured output")
        return 2
    try:
        repository = _database(settings)
    except RuntimeError as error:
        print(str(error))
        return 2
    try:
        tavily_key = settings.tavily_api_key
        openrouter_key = settings.openrouter_api_key
        if tavily_key is None or openrouter_key is None:
            print("BLOCKED: provider credentials are incomplete")
            return 2

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        tavily_key.get_secret_value(),
                        settings.tavily_project_id,
                        timeout_seconds=15 if getattr(args, "profile", "full") == "canary" else 45,
                        max_retries=1 if getattr(args, "profile", "full") == "canary" else 2,
                    ),
                    OpenRouterProvider(
                        openrouter_key.get_secret_value(),
                        request.model,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_manifest_hash=capabilities.manifest_hash,
                        max_concurrent_requests=(
                            2 if getattr(args, "profile", "full") == "canary" else 1
                        ),
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=settings.llm_max_calls,
                    max_llm_input_chars=settings.llm_max_input_chars,
                    max_run_seconds=settings.max_run_seconds,
                )
                return await workflow.run(request, run_id=args.run_id)

        result = asyncio.run(execute())
        _print_json(result.model_dump(mode="json"))
        return 0 if result.validation_status is ValidationStatus.PASS else 2
    finally:
        repository.close()


def _e2e_command(args: argparse.Namespace, settings: Settings) -> int:
    stages: dict[str, dict[str, object]] = {}

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
    if settings.strict_openrouter_policy_error is not None:
        stage("environment", "blocked", message=settings.strict_openrouter_policy_error)
        _print_json({"status": "blocked", "stages": stages})
        return 2
    try:
        capabilities = _capability_report(
            settings,
            settings.openrouter_model_chain,
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
        model=STRICT_OPENROUTER_MODEL,
        fallback_models=[],
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
        tavily_key = settings.tavily_api_key
        openrouter_key = settings.openrouter_api_key
        assert tavily_key is not None and openrouter_key is not None

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(tavily_key.get_secret_value(), settings.tavily_project_id),
                    OpenRouterProvider(
                        openrouter_key.get_secret_value(),
                        request.model,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_manifest_hash=capabilities.manifest_hash,
                        max_concurrent_requests=2 if args.profile == "canary" else 1,
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
        expected_missing_report = (
            result.status.value == "partial"
            and brief is None
            and weekly_response.status_code == 404
            and monthly_response.status_code == 200
        )
        api_status = "pass" if api_passed else "partial" if expected_missing_report else "failed"
        ui_status = "pass" if ui_passed else "partial" if expected_missing_report else "failed"
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
        status = "pass" if accepted else "partial" if result.status.value == "partial" else "failed"
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
        if settings.strict_openrouter_policy_error is not None:
            raise ProviderError(settings.strict_openrouter_policy_error)
        capabilities = _capability_report(
            settings,
            settings.openrouter_model_chain,
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
            capability_manifest_hash=capabilities.manifest_hash,
            timeout_seconds=15,
        )
        tavily = TavilyProvider(
            settings.tavily_api_key.get_secret_value(),
            settings.tavily_project_id,
            timeout_seconds=20,
            max_retries=1,
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
        receipts: list[dict[str, object]] = []
        for attempt in provider.call_history:
            raw_receipts = attempt.get("tool_call_receipts")
            if isinstance(raw_receipts, list):
                receipts.extend(item for item in raw_receipts if isinstance(item, dict))
        tool_names = {str(receipt.get("tool_name")) for receipt in receipts}
        checks = {
            "create_agent": True,
            "chat_openrouter": True,
            "tavily_search": "tavily_search" in tool_names,
            "tavily_extract": "tavily_extract" in tool_names,
            "structured_output": bool(result.packet.source_urls),
            "free_resolved_model": all(
                is_free_model(str(item.get("resolved_model")))
                for item in provider.call_history
                if item.get("resolved_model")
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
                "resolved_models": sorted(
                    {
                        str(item.get("resolved_model"))
                        for item in provider.call_history
                        if item.get("resolved_model")
                    }
                ),
                "capability_manifest_hash": capabilities.manifest_hash,
                "attempts": provider.call_history,
            }
        )
        return 0 if passed else 2
    except (ProviderError, ValueError) as error:
        _print_json(
            {
                "status": "partial",
                "message": error.__class__.__name__,
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
        report = build_validation_report(
            args.run_id,
            sources,
            claims,
            request.as_of,
            request.model,
            repository.get_run_lane_statuses(args.run_id),
            repository.get_run_snapshot_hashes(args.run_id),
            minimum_sources=1 if request.validation_profile == "canary" else 10,
            minimum_claims=1 if request.validation_profile == "canary" else 5,
            tool_call_count=len(repository.get_run_tool_calls(args.run_id)),
            required_tool_lanes={
                lane: {
                    "tavily_search",
                    "tavily_extract",
                }.issubset(
                    {
                        str(call.get("tool_name"))
                        for call in repository.get_run_tool_calls(args.run_id)
                        if call.get("lane") == lane
                    }
                )
                for lane in ("regulatory", "us-ports", "mexico")
            },
        )
        repository.record_validation(report)
        _print_json(report.model_dump(mode="json"))
        return 0 if report.status is ValidationStatus.PASS else 2
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
    run.add_argument("--run-id")
    run.add_argument("--since")
    run.add_argument("--as-of")
    run.add_argument("--max-sources", type=int, default=25)
    run.add_argument("--model")
    run.add_argument("--seed-url", action="append", default=[])

    e2e = subparsers.add_parser("e2e")
    e2e.add_argument("--profile", choices=["canary", "full"], default="canary")
    e2e.add_argument("--run-id", required=True)
    e2e.add_argument("--as-of")
    e2e.add_argument("--json", action="store_true")

    agent_check = subparsers.add_parser("agent-check")
    agent_check.add_argument("--as-of")
    agent_check.add_argument("--json", action="store_true")

    subparsers.add_parser("doctor").add_argument("--json", action="store_true")
    subparsers.add_parser("mcp-check").add_argument("--json", action="store_true")
    subparsers.add_parser("model-check").add_argument("--json", action="store_true")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("migrate")

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
    if args.command == "e2e":
        return _e2e_command(args, settings)
    if args.command == "agent-check":
        return _agent_check_command(args, settings)
    if args.command == "doctor":
        result = asyncio.run(run_doctor(settings))
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "mcp-check":
        result = mcp_check()
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "model-check":
        result = asyncio.run(run_model_check(settings))
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
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
