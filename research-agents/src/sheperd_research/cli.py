from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
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

from .blob import upload_private_pdf
from .contracts import (
    LaneDiscoveryResult,
    ResearchCadence,
    ResearchRunRequest,
    ReviewState,
    RunKind,
    RunResult,
    RunStatus,
    SourceCandidate,
    ValidationCheck,
    ValidationReport,
    ValidationStatus,
    is_free_model,
)
from .costs import estimate_run_cost
from .db import (
    MIGRATION_VERSION,
    PostgresRepository,
    _redact_audit_metadata,
    run_migrations,
    validation_profile_from_run,
)
from .diagnostics import (
    mcp_check,
    run_doctor,
    run_model_check,
    run_model_map,
    validate_database_url,
    validate_dev_branch,
)
from .exporters.obsidian import export_reviewed_brief, render_weekly_markdown
from .exporters.regional_indexes import generate_regional_indexes
from .progress import ProgressReporter
from .providers.capabilities import CapabilityReport, resolve_capabilities
from .providers.errors import ProviderError
from .providers.openai import (
    DEFAULT_OPENAI_MAX_CONCURRENT_REQUESTS,
    OpenAIProvider,
)
from .providers.tavily import TavilyProvider
from .settings import (
    STRICT_OPENROUTER_MODEL,
    Settings,
    free_openrouter_policy_error,
    strict_openrouter_policy_error,
)
from .source_catalog import REGIONS, load_source_catalog, validate_required_sources
from .system_report import render_system_report
from .topics import load_topic_configs
from .validation import (
    build_validation_report,
    provider_error_codes_from_run,
    source_quality_sources,
    validation_blocking_reasons,
)
from .validators import (
    content_hash,
    normalize_url,
    reader_source_contract_issues,
    validate_report_sections,
)
from .web import create_app
from .workflow import (
    STRICT_GLOBAL_GEOGRAPHIES,
    US_MEXICO_GEOGRAPHIES,
    ResearchWorkflow,
    checkpoint_serializer,
)

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
        "signal_events",
        "brief",
        "validation",
        "lane_statuses",
        "partial_reasons",
    }
)
TAVILY_RUNTIME_MIN_REQUEST_INTERVAL_SECONDS = 1.5
FULL_DISCOVERY_QUERY_LIMIT = 6
_CONTEXT_FILES = (
    "obsidian/context/Founder Brief.md",
    "obsidian/context/Founder Intelligence Knowledge Contract.md",
    "obsidian/06_Research/SheperD Deep Research - Control Note.md",
    "obsidian/06_Research/Market Evidence and Source Map.md",
    "research-agents/config/topics.yml",
    "research-agents/config/source_catalog.yml",
)


def _context_version(settings: Settings) -> str:
    manifest: list[str] = []
    for relative_path in _CONTEXT_FILES:
        path = settings.repo_root / relative_path
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append(f"{digest}  {relative_path}\n")
    manifest_hash = hashlib.sha256("".join(sorted(manifest)).encode()).hexdigest()
    return f"{_repository_commit(settings)}:{manifest_hash}"


def _repair_child_run_id(prefix: str, parent_run_id: str, round_number: int) -> str:
    parent_hash = hashlib.sha256(parent_run_id.encode()).hexdigest()[:12]
    return f"{prefix}-p{parent_hash}-r{round_number}"


def _repair_parent_issues(
    repository: PostgresRepository, run_id: str
) -> tuple[list[SourceCandidate], list[str]]:
    sources = repository.get_run_sources(run_id)
    known_urls = {normalize_url(source.url) for source in sources}
    source_hashes = repository.get_run_source_hashes(run_id)
    distillations = {
        normalize_url(item.source_url): item
        for item in repository.get_run_distillations(run_id)
    }
    issues: list[str] = []
    run = repository.get_run(run_id) or {}
    run_as_of = run.get("as_of")
    as_of = run_as_of if isinstance(run_as_of, datetime) else None
    if not sources:
        issues.append("missing_sources")
    for source in sources:
        url = normalize_url(source.url)
        if url not in source_hashes:
            issues.append(f"snapshot:{url}")
        distillation = distillations.get(url)
        for issue in reader_source_contract_issues(
            source,
            distillation,
            as_of=as_of,
        ):
            issues.append(f"reader_contract:{url}:{issue}")
    brief = repository.get_brief(run_id)
    if brief is None:
        issues.append("missing_brief")
    elif validate_report_sections(brief, known_urls):
        issues.append("incomplete_brief")
    return sources, sorted(set(issues))


def _repair_complete_source_count(
    repository: PostgresRepository,
    run_id: str,
    sources: list[SourceCandidate],
    *,
    as_of: datetime,
) -> int:
    source_hashes = repository.get_run_source_hashes(run_id)
    distillations = {
        normalize_url(item.source_url): item
        for item in repository.get_run_distillations(run_id)
    }
    return sum(
        url in source_hashes
        and not reader_source_contract_issues(
            source,
            distillations.get(url),
            as_of=as_of,
        )
        for source in sources
        for url in [normalize_url(source.url)]
    )


def _best_repair_evidence(
    repository: PostgresRepository,
    parent_run_id: str,
    parent_sources: list[SourceCandidate],
    *,
    as_of: datetime,
) -> tuple[str, list[SourceCandidate]]:
    expected_urls = {normalize_url(source.url) for source in parent_sources}
    best_run_id = parent_run_id
    best_sources = parent_sources
    best_count = _repair_complete_source_count(
        repository,
        parent_run_id,
        parent_sources,
        as_of=as_of,
    )
    for run in repository.list_runs(include_repairs=True, limit=1000):
        if (
            run.get("run_kind") != RunKind.REPAIR.value
            or run.get("parent_run_id") != parent_run_id
        ):
            continue
        candidate_run_id = str(run["run_id"])
        candidate_sources = repository.get_run_sources(candidate_run_id)
        if {
            normalize_url(source.parent_navigation_url or source.url)
            for source in candidate_sources
        } != expected_urls:
            continue
        complete_count = _repair_complete_source_count(
            repository,
            candidate_run_id,
            candidate_sources,
            as_of=as_of,
        )
        if complete_count > best_count:
            best_run_id = candidate_run_id
            best_sources = candidate_sources
            best_count = complete_count
    return best_run_id, best_sources


def _unresolved_repair_parents(
    repository: PostgresRepository,
    unresolved_parent_ids: set[str] | None = None,
) -> list[tuple[str, str, list[SourceCandidate], list[str]]]:
    if unresolved_parent_ids is None:
        history = repository.audit_summary().get("history_quality", {})
        unresolved_parent_ids = (
            {str(value) for value in history.get("unresolved_parent_ids", [])}
            if isinstance(history, dict)
            else set()
        )
    all_runs = repository.list_runs(include_repairs=True, limit=1000)
    parents: list[tuple[str, str, list[SourceCandidate], list[str]]] = []
    for run in all_runs:
        if run.get("run_kind", "research") != "research":
            continue
        run_id = str(run["run_id"])
        if run_id not in unresolved_parent_ids:
            continue
        sources, issues = _repair_parent_issues(repository, run_id)
        is_repair_candidate = bool(sources) and bool(issues)
        if is_repair_candidate:
            parents.append((run_id, str(run.get("topic_set") or "dnd-port"), sources, issues))
    return sorted(parents, key=lambda item: item[0])


def _history_repair_blocker(repository: PostgresRepository) -> str | None:
    history = repository.audit_summary().get("history_quality", {})
    count = history.get("unresolved_parent_count", 0) if isinstance(history, dict) else 0
    if isinstance(count, int) and count > 0:
        return f"{count} historical repair parent(s) remain unresolved"
    return None


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


def _require_autonomous_draft(args: argparse.Namespace, settings: Settings) -> int | None:
    if settings.run_mode != "autonomous-draft":
        return _blocked(args, "set RUN_MODE=autonomous-draft for draft writes")
    return None


def _run_error_code(error: str | None) -> str | None:
    if not error:
        return None
    normalized = error.lower()
    for marker, code in (
        ("rate", "rate_limit"),
        ("429", "rate_limit"),
        ("timeout", "timeout"),
        ("extract", "extraction_failed"),
        ("distill", "distillation_failed"),
        ("insight", "incomplete_article_insights"),
        ("synthesis", "synthesis_failed"),
        ("validation", "validation_failed"),
        ("evidence", "missing_evidence"),
    ):
        if marker in normalized:
            return code
    return "workflow_error"


def _capability_report(
    settings: Settings,
    models: tuple[str, ...],
    *,
    require_tools: bool,
    allow_cached: bool = True,
) -> CapabilityReport:
    if settings.openai_api_key is None:
        raise ProviderError("OPENAI_API_KEY is not configured")
    return asyncio.run(
        resolve_capabilities(
            settings.openai_api_key.get_secret_value(),
            models,
            settings.openrouter_capabilities_cache,
            require_tools=require_tools,
            allow_cached=allow_cached,
        )
    )


def _run_command(args: argparse.Namespace, settings: Settings) -> int:
    mode_block = _require_autonomous_draft(args, settings)
    if mode_block is not None:
        return mode_block
    progress = ProgressReporter(enabled=bool(getattr(args, "verbose", False)))
    allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))
    if not getattr(args, "strict", True) and not allow_free_fallbacks:
        return _blocked(args, "run requires --strict or --allow-free-fallbacks")
    if settings.legacy_provider_explicit:
        legacy_policy_error = strict_openrouter_policy_error(
            settings.openrouter_model,
            settings.openrouter_fallback_model_list,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
        if legacy_policy_error is not None:
            return _blocked(args, legacy_policy_error)
    if not settings.has_database_credentials:
        return _blocked(args, "set pooled DATABASE_URL in the repository-root .env.local")
    if not settings.has_live_provider_credentials:
        return _blocked(
            args,
            "set Tavily and OpenAI keys in the repository-root .env.local",
        )
    requested_model = args.model or settings.openai_model
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
            research_scope=args.scope,
            new_findings_only=args.new_only,
            cadence=ResearchCadence(getattr(args, "cadence", "weekly")),
            as_of=_parse_datetime(args.as_of) or datetime.now(UTC),
            since=_parse_datetime(args.since),
            max_sources=args.max_sources,
            model=requested_model,
            seed_urls=args.seed_url,
            context_version=_context_version(settings),
            research_timezone=settings.research_timezone,
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
        return _blocked(
            args,
            "configured OpenAI model does not support discovery tools and structured output",
        )
    try:
        repository = _database(settings)
    except RuntimeError as error:
        return _blocked(args, str(error))
    try:
        history_blocker = _history_repair_blocker(repository)
        if history_blocker is not None:
            return _blocked(args, history_blocker)
        openai_key = settings.openai_api_key
        if not settings.tavily_api_keys or openai_key is None:
            return _blocked(args, "provider credentials are incomplete")

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        settings.tavily_api_keys,
                        settings.tavily_project_id,
                        timeout_seconds=15 if getattr(args, "profile", "full") == "canary" else 45,
                        min_request_interval_seconds=TAVILY_RUNTIME_MIN_REQUEST_INTERVAL_SECONDS,
                        progress=progress,
                    ),
                    OpenAIProvider(
                        openai_key.get_secret_value(),
                        request.model,
                        fallback_models=tuple(
                            model
                            for model in fallback_models
                            if model != request.model
                        ),
                        allow_free_fallbacks=allow_free_fallbacks,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_report=capabilities,
                        max_concurrent_requests=DEFAULT_OPENAI_MAX_CONCURRENT_REQUESTS,
                        progress=progress,
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=settings.llm_max_calls,
                    max_llm_input_chars=settings.llm_max_input_chars,
                    max_run_seconds=settings.max_run_seconds,
                    discovery_query_limit=(
                        1
                        if getattr(args, "profile", "full") == "canary"
                        else FULL_DISCOVERY_QUERY_LIMIT
                    ),
                    progress=progress,
                    research_timezone=settings.research_timezone,
                )
                return await workflow.run(request, run_id=args.run_id)

        result = asyncio.run(execute())
        _print_json(result.model_dump(mode="json"))
        return 0 if result.validation_status is ValidationStatus.PASS else 2
    finally:
        repository.close()


def _repair_command(args: argparse.Namespace, settings: Settings) -> int:
    mode_block = _require_autonomous_draft(args, settings)
    if mode_block is not None:
        return mode_block
    if not settings.has_database_credentials:
        return _blocked(args, "set pooled DATABASE_URL in the repository-root .env.local")
    if not settings.has_live_provider_credentials:
        return _blocked(
            args,
            "set Tavily and OpenAI keys in the repository-root .env.local",
        )
    allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))
    model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
    fallback_models = model_chain[1:]
    policy_error = (
        free_openrouter_policy_error(
            settings.openai_model,
            fallback_models,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
        if allow_free_fallbacks
        else strict_openrouter_policy_error(
            settings.openai_model,
            settings.openrouter_fallback_model_list,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
    )
    if policy_error is not None:
        return _blocked(args, policy_error)
    try:
        capabilities = _capability_report(
            settings,
            (settings.openai_model, *fallback_models),
            require_tools=True,
            allow_cached=False,
        )
        repository = _database(settings)
        history_quality = repository.audit_summary().get("history_quality", {})
        unresolved_parent_ids = (
            {
                str(value)
                for value in history_quality.get("unresolved_parent_ids", [])
            }
            if isinstance(history_quality, dict)
            else set()
        )
        parents = _unresolved_repair_parents(repository, unresolved_parent_ids)
        as_of = _parse_datetime(args.as_of)
        if as_of is None:
            raise ValueError("repair requires an explicit UTC --as-of")
        context_version = _context_version(settings)
        openai_key = settings.openai_api_key
        if not settings.tavily_api_keys or openai_key is None:
            return _blocked(args, "provider credentials are incomplete")
        progress = ProgressReporter(enabled=bool(getattr(args, "verbose", False)))

        async def execute() -> tuple[list[dict[str, object]], str | None]:
            outcomes: list[dict[str, object]] = []
            stop_failure: str | None = None
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        settings.tavily_api_keys,
                        settings.tavily_project_id,
                        min_request_interval_seconds=TAVILY_RUNTIME_MIN_REQUEST_INTERVAL_SECONDS,
                        progress=progress,
                    ),
                    OpenAIProvider(
                        openai_key.get_secret_value(),
                        settings.openai_model,
                        fallback_models=fallback_models,
                        allow_free_fallbacks=allow_free_fallbacks,
                        capability_report=capabilities,
                        progress=progress,
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=settings.llm_max_calls,
                    max_llm_input_chars=settings.llm_max_input_chars,
                    max_run_seconds=settings.max_run_seconds,
                    progress=progress,
                    research_timezone=settings.research_timezone,
                )
                for parent_run_id, topic_set, sources, legacy_issues in parents:
                    evidence_run_id, repair_sources = _best_repair_evidence(
                        repository,
                        parent_run_id,
                        sources,
                        as_of=as_of,
                    )
                    prior_fingerprint: str | None = None
                    parent_attempts: list[dict[str, object]] = []
                    resolved = False
                    for round_number in range(1, 4):
                        child_run_id = _repair_child_run_id(
                            args.run_id, parent_run_id, round_number
                        )
                        if repository.get_run(child_run_id) is not None:
                            blockers = ["repair_child_run_exists"]
                            result = None
                        else:
                            request = ResearchRunRequest(
                                topic_set=topic_set,
                                cadence=ResearchCadence.WEEKLY,
                                as_of=as_of,
                                max_sources=args.max_sources,
                                model=settings.openai_model,
                                include_topic_seeds=False,
                                validation_profile="repair",
                                context_version=context_version,
                                research_timezone=settings.research_timezone,
                                run_kind=RunKind.REPAIR,
                                parent_run_id=parent_run_id,
                                repair_round=round_number,
                            )
                            result = await workflow.repair(
                                request,
                                repair_sources,
                                child_run_id,
                                evidence_run_id=evidence_run_id,
                            )
                            validation = repository.get_validation(child_run_id)
                            blockers = (
                                validation_blocking_reasons(validation)
                                if validation is not None
                                else [
                                    result.error_code
                                    or _run_error_code(result.error)
                                    or "repair_failed"
                                ]
                            )
                        fingerprint = hashlib.sha256(
                            json.dumps(sorted(blockers)).encode()
                        ).hexdigest()
                        parent_attempts.append(
                            {
                                "run_id": child_run_id,
                                "round": round_number,
                                "status": (
                                    result.status.value if result is not None else "blocked"
                                ),
                                "blocking_reasons": blockers,
                                "blocker_fingerprint": fingerprint,
                            }
                        )
                        if (
                            result is not None
                            and result.status is RunStatus.SUCCEEDED
                            and result.validation_status is ValidationStatus.PASS
                        ):
                            resolved = True
                            break
                        stop_text = " ".join(blockers).casefold()
                        if any(
                            marker in stop_text
                            for marker in (
                                "authentication",
                                "credential",
                                "quota",
                                "rate_limit",
                                "provider",
                                "timeout",
                                "extraction",
                                "source_access",
                            )
                        ):
                            stop_failure = f"{parent_run_id}:{blockers[0]}"
                            break
                        if prior_fingerprint == fingerprint:
                            break
                        prior_fingerprint = fingerprint
                        candidate_sources = repository.get_run_sources(child_run_id)
                        if {
                            normalize_url(source.parent_navigation_url or source.url)
                            for source in candidate_sources
                        } == {
                            normalize_url(source.parent_navigation_url or source.url)
                            for source in repair_sources
                        } and _repair_complete_source_count(
                            repository,
                            child_run_id,
                            candidate_sources,
                            as_of=as_of,
                        ) >= _repair_complete_source_count(
                            repository,
                            evidence_run_id,
                            repair_sources,
                            as_of=as_of,
                        ):
                            evidence_run_id = child_run_id
                            repair_sources = candidate_sources
                    outcomes.append(
                        {
                            "parent_run_id": parent_run_id,
                            "legacy_issues": legacy_issues,
                            "source_count": len(sources),
                            "resolved": resolved,
                            "attempts": parent_attempts,
                        }
                    )
                    if stop_failure is not None:
                        break
            return outcomes, stop_failure

        outcomes, stop_failure = asyncio.run(execute())
        unresolved = [
            str(item["parent_run_id"])
            for item in outcomes
            if item.get("resolved") is not True
        ]
        if stop_failure is not None:
            unattempted = {
                parent_run_id for parent_run_id, _, _, _ in parents
            } - {str(item["parent_run_id"]) for item in outcomes}
            unresolved.extend(sorted(unattempted))
        status = "pass" if not unresolved and stop_failure is None else "blocked"
        _print_json(
            {
                "status": status,
                "batch_prefix": args.run_id,
                "as_of": as_of.isoformat(),
                "context_version": context_version,
                "raw_legacy_parent_count": (
                    history_quality.get("raw_defect_parent_count", 0)
                    if isinstance(history_quality, dict)
                    else 0
                ),
                "repair_parent_count": len(parents),
                "unresolved_parent_count": len(set(unresolved)),
                "unresolved_parent_ids": sorted(set(unresolved)),
                "stop_failure": stop_failure,
                "parents": outcomes,
            }
        )
        return 0 if status == "pass" else 2
    except (ProviderError, RuntimeError, ValueError) as error:
        return _blocked(args, str(error))
    finally:
        if "repository" in locals():
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
        with repository.read_snapshot():
            summary = repository.audit_summary()
            quality = _quality_audit(repository)
            snapshot = repository.system_snapshot()
        snapshot_steps = snapshot.get("agent_steps", [])
        snapshot_tools = snapshot.get("tool_calls", [])
        cost = estimate_run_cost(
            snapshot_steps if isinstance(snapshot_steps, list) else [],
            snapshot_tools if isinstance(snapshot_tools, list) else [],
        )
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
        history_quality = summary.get("history_quality")
        if isinstance(history_quality, dict):
            unresolved_parent_count = history_quality.get(
                "unresolved_parent_count", 0
            )
            if (
                isinstance(unresolved_parent_count, int)
                and unresolved_parent_count > 0
            ):
                blockers.append(
                    {
                        "check": "quality:unresolved_repair_parents",
                        "status": "failed",
                        "message": (
                            f"{unresolved_parent_count} historical parent run(s) "
                            "remain unresolved"
                        ),
                    }
                )
        latest_strict = quality.get("latest_strict_run")
        if not isinstance(latest_strict, dict):
            blockers.append(
                {
                    "check": "quality:latest_strict_run_missing",
                    "status": "blocked",
                    "message": "no active strict non-repair weekly run is available",
                }
            )
        elif latest_strict.get("current_status") != "pass":
            blockers.append(
                {
                    "check": "quality:latest_strict_run",
                    "status": "failed",
                    "message": (
                        "latest strict non-repair weekly run is "
                        f"{latest_strict.get('current_status', 'blocked')}"
                    ),
                }
            )
        table_counts = snapshot.get("table_counts")
        period_counts = snapshot.get("period_counts")
        run_source_count = (
            table_counts.get("run_sources", 0)
            if isinstance(table_counts, dict)
            else 0
        )
        in_period_count = (
            period_counts.get("in_period", 0)
            if isinstance(period_counts, dict)
            else 0
        )
        if (
            isinstance(run_source_count, int)
            and run_source_count > 0
            and isinstance(in_period_count, int)
            and in_period_count == 0
        ):
            blockers.append(
                {
                    "check": "period:eligible_weekly_sources",
                    "status": "blocked",
                    "message": (
                        "no persisted source has a publication date inside its "
                        "weekly window"
                    ),
                }
            )
        status = (
            "pass"
            if diagnostics.get("status") == "pass" and not blockers
            else "blocked"
        )
        _print_json(
            {
                "status": status,
                "database": summary,
                "quality": quality,
                "system": snapshot,
                "cost_estimate": cost,
                "diagnostics": diagnostics,
                "blockers": blockers,
            }
        )
        return 0 if status == "pass" else 2
    except Exception as error:
        return _blocked(args, f"audit failed: {error.__class__.__name__}")
    finally:
        repository.close()


def _repository_commit(settings: Settings) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=settings.repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "not recorded"
    commit = result.stdout.strip()
    return commit or "not recorded"


def _repository_dirty(settings: Settings) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=settings.repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
    return bool(result.stdout.strip())


def _system_report_command(args: argparse.Namespace, settings: Settings) -> int:
    try:
        repository = _database(settings)
    except RuntimeError as error:
        return _blocked(args, str(error))
    try:
        audit = repository.audit_summary()
        snapshot = repository.system_snapshot()
        try:
            diagnostics = asyncio.run(
                run_doctor(settings, allow_free_fallbacks=False)
            )
        except Exception as error:
            diagnostics = {
                "status": "blocked",
                "checks": {
                    "providers": {
                        "status": "blocked",
                        "error_code": error.__class__.__name__,
                    }
                },
            }
        health = repository.health()
        output = (
            Path(args.output).expanduser().resolve()
            if args.output
            else settings.vault_root / "06_Research" / "SheperD Technical and Operations Report.md"
        )
        vault_root = settings.vault_root.resolve()
        if vault_root not in output.parents:
            return _blocked(args, "system reports are limited to the obsidian vault")
        report = render_system_report(
            snapshot=snapshot,
            audit=audit,
            diagnostics=diagnostics,
            branch_id=str(health.get("branch_id") or settings.neon_branch_id),
            migration_version=str(health.get("migration_version") or MIGRATION_VERSION),
            repository_commit=_repository_commit(settings),
            repository_dirty=_repository_dirty(settings),
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        table_counts = snapshot.get("table_counts")
        period_counts = snapshot.get("period_counts")
        temporal_blocked = (
            isinstance(table_counts, dict)
            and isinstance(period_counts, dict)
            and isinstance(table_counts.get("run_sources"), int)
            and table_counts["run_sources"] > 0
            and period_counts.get("in_period", 0) == 0
        )
        quality = audit.get("quality")
        quality_blocked = (
            isinstance(quality, dict)
            and (
                quality.get("distillations_incomplete", 0) > 0
                or quality.get("briefs_with_complete_sections", 0)
                < quality.get("briefs_total", 0)
            )
        )
        readiness_blocked = temporal_blocked or quality_blocked
        payload = {
            "status": (
                "pass"
                if diagnostics.get("status") == "pass"
                and health.get("status") == "pass"
                and not readiness_blocked
                else "blocked"
            ),
            "output": str(output),
            "migration_version": health.get("migration_version"),
            "branch_id": health.get("branch_id") or settings.neon_branch_id,
            "table_count": len(table_counts) if isinstance(table_counts, dict) else 0,
            "readiness_status": "not_production_ready" if readiness_blocked else "ready",
        }
        _print_json(payload)
        return 0 if payload["status"] == "pass" else 2
    except (OSError, RuntimeError, ValueError) as error:
        return _blocked(args, f"system report failed: {error.__class__.__name__}")
    finally:
        repository.close()


def _e2e_command(args: argparse.Namespace, settings: Settings) -> int:
    mode_block = _require_autonomous_draft(args, settings)
    if mode_block is not None:
        return mode_block
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
        stage("environment", "blocked", message="Tavily and OpenAI credentials are required")
        _print_json({"status": "blocked", "stages": stages})
        return 2
    model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
    fallback_models = model_chain[1:]
    policy_error = (
        free_openrouter_policy_error(
            settings.openai_model,
            fallback_models,
            raw_fallback_config=settings.openrouter_fallback_models,
        )
        if allow_free_fallbacks
        else strict_openrouter_policy_error(
            settings.openai_model,
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
        stage(
            "environment",
            "blocked",
            message="configured OpenAI model is not eligible for discovery",
        )
        _print_json({"status": "blocked", "stages": stages})
        return 2
    stage(
        "environment",
        "pass",
        model=settings.openai_model,
        fallback_models=list(capabilities.eligible_models[1:]),
        eligible_models=list(capabilities.eligible_models),
        skipped_models=list(capabilities.skipped_models),
        capability_manifest_hash=capabilities.manifest_hash,
        branch_id=settings.neon_branch_id,
    )
    try:
        request = ResearchRunRequest(
            topic_set="dnd-port",
            research_scope=args.scope,
            new_findings_only=args.new_only,
            as_of=_parse_datetime(args.as_of) or datetime.now(UTC),
            max_sources=3 if args.profile == "canary" else 30,
            model=settings.openai_model,
            include_topic_seeds=False,
            validation_profile=args.profile,
            context_version=_context_version(settings),
            research_timezone=settings.research_timezone,
        )
        repository = _database(settings)
        health = repository.health()
        migration_version = health.get("migration_version")
        if health.get("status") != "pass" or migration_version != MIGRATION_VERSION:
            stage(
                "database",
                "blocked",
                error_code="schema_migration_stale",
                migration_version=migration_version,
                expected_migration_version=MIGRATION_VERSION,
            )
            repository.close()
            _print_json({"status": "blocked", "stages": stages})
            return 2
        stage("database", "pass", migration_version=migration_version)
        history_blocker = _history_repair_blocker(repository)
        if history_blocker is not None:
            stage("history", "blocked", message=history_blocker)
            repository.close()
            _print_json({"status": "blocked", "stages": stages})
            return 2
        stage("history", "pass", unresolved_parent_count=0)
    except (RuntimeError, ValueError) as error:
        stage("database", "blocked", message=error.__class__.__name__)
        _print_json({"status": "blocked", "stages": stages})
        return 2

    try:
        openai_key = settings.openai_api_key
        assert settings.tavily_api_keys and openai_key is not None

        async def execute() -> RunResult:
            async with _checkpoint_saver(settings.database_url or "") as checkpointer:
                workflow = ResearchWorkflow(
                    repository,
                    TavilyProvider(
                        settings.tavily_api_keys,
                        settings.tavily_project_id,
                        min_request_interval_seconds=TAVILY_RUNTIME_MIN_REQUEST_INTERVAL_SECONDS,
                        progress=progress,
                    ),
                    OpenAIProvider(
                        openai_key.get_secret_value(),
                        request.model,
                        fallback_models=fallback_models,
                        allow_free_fallbacks=allow_free_fallbacks,
                        max_output_tokens=settings.llm_max_output_tokens,
                        capability_report=capabilities,
                        max_concurrent_requests=DEFAULT_OPENAI_MAX_CONCURRENT_REQUESTS,
                        progress=progress,
                    ),
                    load_topic_configs(settings.resolved_topics_path),
                    checkpointer=checkpointer,
                    max_llm_calls=min(
                        settings.llm_max_calls,
                        16 if args.profile == "canary" else 48,
                    ),
                    max_llm_input_chars=min(
                        settings.llm_max_input_chars,
                        60_000 if args.profile == "canary" else 350_000,
                    ),
                    max_run_seconds=min(
                        settings.max_run_seconds,
                        420 if args.profile == "canary" else 900,
                    ),
                    discovery_query_limit=(
                        1 if args.profile == "canary" else FULL_DISCOVERY_QUERY_LIMIT
                    ),
                    progress=progress,
                    research_timezone=settings.research_timezone,
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
            error_code=_run_error_code(result.error),
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
    if not settings.tavily_api_key or not settings.openai_api_key:
        _print_json(
            {
                "status": "blocked",
                "message": "Tavily and OpenAI credentials are required",
            }
        )
        return 2
    provider: OpenAIProvider | None = None
    capabilities: CapabilityReport | None = None
    try:
        allow_free_fallbacks = bool(getattr(args, "allow_free_fallbacks", False))
        model_chain = settings.model_chain(allow_free_fallbacks=allow_free_fallbacks)
        fallback_models = model_chain[1:]
        policy_error = (
            free_openrouter_policy_error(
                settings.openai_model,
                fallback_models,
                raw_fallback_config=settings.openrouter_fallback_models,
            )
            if allow_free_fallbacks
            else strict_openrouter_policy_error(
                settings.openai_model,
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
            raise ProviderError(
                "configured OpenAI model does not support discovery tools and structured output"
            )
        topic = load_topic_configs(settings.resolved_topics_path)["dnd-port"]
        as_of = _parse_datetime(args.as_of) or datetime.now(UTC)
        since = as_of - timedelta(days=topic.lookback_days)
        provider = OpenAIProvider(
            settings.openai_api_key.get_secret_value(),
            settings.openai_model,
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
        eligible_models = set(capabilities.eligible_models)

        def resolved_model_matches_configured(model: str) -> bool:
            return any(
                model == eligible or model.startswith(f"{eligible}-")
                for eligible in eligible_models
            )

        checks = {
            "create_agent": True,
            "chat_openai": True,
            "tavily_search": "tavily_search" in tool_names,
            "tavily_extract": "tavily_extract" in tool_names,
            "structured_output": bool(result.packet.source_urls),
            "resolved_models_configured": all(
                resolved_model_matches_configured(model) for model in resolved_models
            ),
            "strict_resolved_model": len(resolved_models) == 1
            and resolved_model_matches_configured(resolved_models[0]),
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
                "message": (
                    getattr(error, "error_code", None)
                    or ("invalid_output" if isinstance(error, ValueError) else "provider_error")
                ),
                "error_code": getattr(error, "error_code", None) or attempt_error_code,
                "capabilities": capabilities.as_dict() if capabilities else None,
                "attempts": provider.call_history if provider else [],
            }
        )
        return 2


def _build_persisted_validation(
    repository: PostgresRepository, run_id: str
) -> ValidationReport:
    run = repository.get_run(run_id)
    if run is None:
        raise KeyError(f"run not found: {run_id}")
    request_value = run.get("request")
    if not isinstance(request_value, dict):
        raise ValueError("run request metadata is unavailable")
    raw_model = request_value.get("model")
    validation_model = raw_model if isinstance(raw_model, str) else STRICT_OPENROUTER_MODEL
    normalized_request = dict(request_value)
    # Legacy runs may contain the retired openrouter/free router identifier.
    # Normalize only invalid historical values; retain the original model for
    # the deterministic model-policy validation check.
    normalized_request["model"] = (
        raw_model
        if isinstance(raw_model, str) and is_free_model(raw_model)
        else STRICT_OPENROUTER_MODEL
    )
    request = ResearchRunRequest.model_validate(normalized_request)
    sources = repository.get_run_sources(run_id)
    claims = repository.get_run_claims(run_id)
    get_distillations = getattr(repository, "get_run_distillations", None)
    distillations = get_distillations(run_id) if callable(get_distillations) else None
    get_signal_events = getattr(repository, "get_run_signal_events", None)
    signal_events = get_signal_events(run_id) if callable(get_signal_events) else None
    get_brief = getattr(repository, "get_brief", None)
    brief = get_brief(run_id) if callable(get_brief) else None
    strict_profile = request.validation_profile in {"full", "global-canary"}
    repair_mode = request.validation_profile == "repair"
    quality_source_count = len(source_quality_sources(sources))
    eligible_weekly_source_count = (
        sum(source.eligible_for_weekly for source in sources)
        if request.cadence is ResearchCadence.WEEKLY
        else None
    )
    minimum_eligible_sources = (
        10
        if request.cadence is ResearchCadence.WEEKLY
        and request.validation_profile in {"full", "global-canary"}
        else None
    )
    scoped_geographies = (
        US_MEXICO_GEOGRAPHIES
        if request.research_scope == "us-mexico"
        else STRICT_GLOBAL_GEOGRAPHIES
    )
    scoped_regions = (
        {"us", "mexico"}
        if request.research_scope == "us-mexico"
        else set(REGIONS) - {"global"}
    )
    return build_validation_report(
        run_id,
        sources,
        claims,
        request.as_of,
        validation_model,
        repository.get_run_lane_statuses(run_id),
        repository.get_run_snapshot_hashes(run_id),
        minimum_sources=(
            quality_source_count
            if repair_mode
            else 1
            if request.validation_profile in {"canary", "global-canary"}
            else 10
        ),
        minimum_claims=(
            quality_source_count
            if repair_mode
            else 1
            if request.validation_profile in {"canary", "global-canary"}
            else 5
        ),
        required_source_hash_count=quality_source_count if repair_mode else None,
        tool_call_count=(
            None
            if repair_mode
            else sum(
                1
                for call in repository.get_run_tool_calls(run_id)
                if call.get("status") == "succeeded"
            )
        ),
        required_tool_lanes={
            lane: {"tavily_search", "tavily_extract"}.issubset(
                {
                    str(call.get("tool_name"))
                    for call in repository.get_run_tool_calls(run_id)
                    if call.get("lane") == lane and call.get("status") == "succeeded"
                }
            )
            for lane in ("regulatory", "us-ports", "mexico")
        }
        if not repair_mode
        else None,
        distillations=distillations,
        signal_events=signal_events if repair_mode else None,
        required_geographies=set(scoped_geographies) if strict_profile else set(),
        required_regions=scoped_regions if strict_profile else set(),
        required_lanes=set() if repair_mode else None,
        brief=brief,
        provider_error_codes=provider_error_codes_from_run(
            sources=sources,
            steps=repository.get_run_steps(run_id),
            tool_calls=repository.get_run_tool_calls(run_id),
        ),
        eligible_weekly_source_count=eligible_weekly_source_count,
        minimum_eligible_sources=minimum_eligible_sources,
        require_reader_contract=(
            repair_mode
            or run.get("migration_version") == MIGRATION_VERSION
            or str(run.get("prompt_version") or "").startswith("workflow-v4-reader")
        ),
    )


def _iter_run_ids(repository: PostgresRepository) -> list[str]:
    run_ids: list[str] = []
    offset = 0
    while True:
        rows = repository.list_runs(limit=1000, offset=offset)
        if not rows:
            break
        run_ids.extend(
            str(row["run_id"])
            for row in rows
            if isinstance(row.get("run_id"), str)
        )
        if len(rows) < 1000:
            break
        offset += len(rows)
    return run_ids


def _quality_audit(repository: PostgresRepository) -> dict[str, object]:
    observations: list[dict[str, object]] = []
    for run_id in _iter_run_ids(repository):
        run = repository.get_run(run_id)
        if run is None or run.get("archived_at") is not None:
            continue
        stored = repository.get_validation(run_id)
        try:
            current = _build_persisted_validation(repository, run_id)
            observations.append(
                {
                    "run_id": run_id,
                    "as_of": run.get("as_of"),
                    "validation_profile": validation_profile_from_run(run),
                    "stored_status": stored.status.value if stored else "missing",
                    "current_status": current.status.value,
                    "blocking_reasons": validation_blocking_reasons(current),
                    "article_insight_completeness": next(
                        (
                            check.observed
                            for check in current.checks
                            if check.name == "article_insight_completeness"
                        ),
                        None,
                    ),
                    "report_section_status": next(
                        (
                            check.status.value
                            for check in current.checks
                            if check.name == "report_sections"
                        ),
                        "not_recorded",
                    ),
                    "stale_validation": stored is None
                    or stored.content_hash != current.content_hash
                    or stored.status is not current.status,
                }
            )
        except (KeyError, TypeError, ValueError) as error:
            observations.append(
                {
                    "run_id": run_id,
                    "as_of": run.get("as_of"),
                    "validation_profile": validation_profile_from_run(run),
                    "stored_status": stored.status.value if stored else "missing",
                    "current_status": "blocked",
                    "blocking_reasons": ["stale_validation"],
                    "error": error.__class__.__name__,
                    "stale_validation": True,
                }
            )
    strict_observations = [
        item for item in observations if item.get("validation_profile") == "full"
    ]
    def observation_as_of(item: dict[str, object]) -> datetime:
        value = item.get("as_of")
        return value if isinstance(value, datetime) else datetime.min.replace(tzinfo=UTC)

    latest_strict = max(strict_observations, key=observation_as_of, default=None)
    current_statuses = (
        [str(latest_strict["current_status"])] if latest_strict is not None else []
    )
    reason_counts: dict[str, int] = {}
    for observation in observations:
        raw_reasons = observation.get("blocking_reasons", [])
        reasons = raw_reasons if isinstance(raw_reasons, list) else []
        for reason in reasons:
            if isinstance(reason, str):
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
    return {
        "active_runs_checked": len(observations),
        "latest_strict_run": latest_strict,
        "current_status_counts": {
            status: current_statuses.count(status)
            for status in sorted(set(current_statuses))
        },
        "stale_validation_count": sum(
            bool(item.get("stale_validation")) for item in observations
        ),
        "raw_active_defect_reason_counts": dict(sorted(reason_counts.items())),
        "reports": observations,
    }


def _validate_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    try:
        try:
            report = _build_persisted_validation(repository, args.run_id)
        except KeyError:
            print(f"ERROR: run not found: {args.run_id}")
            return 2
        except (TypeError, ValueError) as error:
            print(f"BLOCKED: {error}")
            return 2
        repository.record_validation(report)
        _print_json(
            report.model_dump(mode="json")
            | {"blocking_reasons": validation_blocking_reasons(report)}
        )
        return 0 if report.status is ValidationStatus.PASS else 2
    finally:
        repository.close()


def _revalidate_command(args: argparse.Namespace, settings: Settings) -> int:
    if not _require_database(settings):
        return 2
    repository = _database(settings)
    results: list[dict[str, object]] = []
    try:
        for run_id in _iter_run_ids(repository):
            run = repository.get_run(run_id)
            if run is None:
                continue
            if args.scope == "active" and run.get("archived_at") is not None:
                continue
            try:
                report = _build_persisted_validation(repository, run_id)
                repository.record_validation(report)
                results.append(
                    {
                        "run_id": run_id,
                        "status": report.status.value,
                        "blocking_reasons": validation_blocking_reasons(report),
                    }
                )
            except (TypeError, ValueError, KeyError) as error:
                blocked = ValidationReport(
                    run_id=run_id,
                    status=ValidationStatus.BLOCKED,
                    checks=[
                        ValidationCheck(
                            name="revalidation",
                            status=ValidationStatus.BLOCKED,
                            message=error.__class__.__name__,
                        )
                    ],
                    blocking_reasons=["stale_validation"],
                    content_hash=content_hash(
                        f"revalidation:{run_id}:{error.__class__.__name__}"
                    ),
                )
                repository.record_validation(blocked)
                results.append(
                    {
                        "run_id": run_id,
                        "status": "blocked",
                        "blocking_reasons": ["stale_validation"],
                        "error": error.__class__.__name__,
                    }
                )
        counts: dict[str, int] = {}
        for result in results:
            status = str(result["status"])
            counts[status] = counts.get(status, 0) + 1
        payload = {
            "status": (
                "pass"
                if counts.get("failed", 0) == 0 and counts.get("blocked", 0) == 0
                else "failed"
            ),
            "scope": args.scope,
            "checked": len(results),
            "counts": dict(sorted(counts.items())),
            "runs": results,
        }
        _print_json(payload)
        return 0 if payload["status"] == "pass" else 2
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
            try:
                validation = _build_persisted_validation(repository, args.run_id)
            except (KeyError, TypeError, ValueError) as error:
                print(
                    "BLOCKED: current validation could not be computed: "
                    f"{error.__class__.__name__}"
                )
                return 2
            if validation.status is not ValidationStatus.PASS:
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
        run = repository.get_run(args.run_id)
        if run is None or run.get("status") != "succeeded":
            print("BLOCKED: only a succeeded run may be exported")
            return 2
        try:
            validation = _build_persisted_validation(repository, args.run_id)
        except (KeyError, TypeError, ValueError) as error:
            print(
                "BLOCKED: current validation could not be computed: "
                f"{error.__class__.__name__}"
            )
            return 2
        if brief.review_state is not ReviewState.APPROVED:
            print("BLOCKED: only reviewed briefs may be exported")
            return 2
        if validation.status is not ValidationStatus.PASS:
            print("BLOCKED: only briefs with passing validation may be exported")
            return 2
        export_format = getattr(args, "format", "md")
        requested_destination = (
            Path(args.output).resolve()
            if args.output
            else settings.resolved_obsidian_output_dir
            / f"{brief.covered_until.date()} - {brief.title}.md"
        )
        if export_format == "pdf":
            markdown_destination = requested_destination.with_suffix(".md")
            pdf_destination = requested_destination.with_suffix(".pdf")
        else:
            markdown_destination = requested_destination.with_suffix(".md")
            pdf_destination = requested_destination.with_suffix(".pdf")
        output_root = settings.resolved_obsidian_output_dir.resolve()
        destinations = [markdown_destination] if export_format == "md" else [pdf_destination]
        if export_format == "both":
            destinations = [markdown_destination, pdf_destination]
        if any(output_root not in destination.parents for destination in destinations):
            print("BLOCKED: exports are limited to obsidian/06_Research/Agent Runs/")
            return 2
        sources = repository.get_run_sources(args.run_id)
        distillations = repository.get_run_distillations(args.run_id)
        claims = repository.get_run_claims(args.run_id)
        source_hashes = repository.get_run_source_hashes(args.run_id)
        signals = repository.get_run_signal_events(args.run_id)
        steps = repository.get_run_steps(args.run_id)
        tool_calls = repository.get_run_tool_calls(args.run_id)
        markdown = render_weekly_markdown(
            brief,
            validation=validation,
            sources=sources,
            distillations=distillations,
            claims=claims,
            source_hashes=source_hashes,
            signals=signals,
            steps=steps,
            tool_calls=tool_calls,
            run=run,
            status="approved",
        )
        if export_format in {"md", "both"}:
            export_reviewed_brief(
                brief,
                markdown_destination,
                validation=validation,
                sources=sources,
                distillations=distillations,
                claims=claims,
                source_hashes=source_hashes,
                signals=signals,
                steps=steps,
                tool_calls=tool_calls,
                run=run,
            )
        output_paths: list[str] = [str(markdown_destination)] if export_format != "pdf" else []
        if export_format in {"pdf", "both"}:
            if settings.blob_read_write_token is None:
                print("BLOCKED: BLOB_READ_WRITE_TOKEN is required for PDF export")
                return 2
            from .pdf import render_pdf

            render_pdf(markdown, pdf_destination)
            artifact = upload_private_pdf(
                pdf_destination,
                f"reports/{args.run_id}.pdf",
                settings.blob_read_write_token.get_secret_value(),
            )
            repository.record_pdf_artifact(
                args.run_id,
                blob_path=artifact["pathname"],
                blob_url=artifact["url"],
                content_hash=hashlib.sha256(pdf_destination.read_bytes()).hexdigest(),
            )
            output_paths.append(str(pdf_destination))
        print("\n".join(output_paths))
        return 0
    except (PermissionError, RuntimeError, OSError) as error:
        print(f"BLOCKED: {error}")
        return 2
    finally:
        repository.close()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sheperd-research")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--topic-set", default="dnd-port")
    run.add_argument("--scope", choices=["global", "us-mexico"], default="global")
    run.add_argument("--new-only", action="store_true")
    run.add_argument("--cadence", choices=["daily", "weekly"], default="weekly")
    run.add_argument("--strict", action="store_true")
    run.add_argument("--allow-free-fallbacks", action="store_true")
    run.add_argument("--json", action="store_true")
    run.add_argument("--verbose", action="store_true")
    run.add_argument("--run-id", required=True)
    run.add_argument("--since")
    run.add_argument("--as-of", required=True)
    run.add_argument("--max-sources", type=int, default=25)
    run.add_argument("--model")
    run.add_argument("--seed-url", action="append", default=[])

    e2e = subparsers.add_parser("e2e")
    e2e.add_argument(
        "--profile", choices=["canary", "global-canary", "full"], default="canary"
    )
    e2e.add_argument("--scope", choices=["global", "us-mexico"], default="global")
    e2e.add_argument("--new-only", action="store_true")
    e2e.add_argument("--strict", action="store_true")
    e2e.add_argument("--allow-free-fallbacks", action="store_true")
    e2e.add_argument("--run-id", required=True)
    e2e.add_argument("--as-of", required=True)
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
    model_map = subparsers.add_parser("model-map")
    model_map.add_argument("--json", action="store_true")
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

    system_report = subparsers.add_parser("system-report")
    system_report.add_argument("--output")
    system_report.add_argument("--json", action="store_true")

    repair = subparsers.add_parser("repair")
    repair.add_argument("--source-scope", choices=["incomplete"], default="incomplete")
    repair.add_argument("--run-id", required=True)
    repair.add_argument("--as-of", required=True)
    repair.add_argument("--max-sources", type=int, default=25)
    repair.add_argument("--allow-free-fallbacks", action="store_true")
    repair.add_argument("--verbose", action="store_true")
    repair.add_argument("--json", action="store_true")

    validate = subparsers.add_parser("validate")
    validate.add_argument("--run-id", required=True)

    revalidate = subparsers.add_parser("revalidate")
    revalidate.add_argument("--scope", choices=["active", "all"], default="active")
    revalidate.add_argument("--json", action="store_true")

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
    export.add_argument("--format", choices=["md", "pdf", "both"], default="md")
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
    if args.command == "system-report":
        return _system_report_command(args, settings)
    if args.command == "repair":
        return _repair_command(args, settings)
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
    if args.command == "model-map":
        result = asyncio.run(run_model_map(settings))
        _print_json(result)
        return 0 if result["status"] == "pass" else 2
    if args.command == "source-map":
        return _source_map_command(args, settings)
    if args.command == "index":
        return _index_command(args, settings)
    if args.command == "validate":
        return _validate_command(args, settings)
    if args.command == "revalidate":
        return _revalidate_command(args, settings)
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

        uvicorn.run(
            create_app(repository, settings=settings),
            host=settings.host,
            port=settings.port,
        )
        return 0
    print("Unknown command", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
