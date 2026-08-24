from __future__ import annotations

from urllib.parse import urlsplit

from .contracts import SourceCandidate, ValidationStatus
from .providers.capabilities import resolve_capabilities
from .providers.errors import ProviderError
from .providers.openai import OpenAIProvider
from .providers.tavily import TavilyProvider
from .settings import (
    Settings,
    free_openrouter_policy_error,
    strict_openrouter_policy_error,
)

FMC_SMOKE_URL = "https://www.fmc.gov/articles/final-rule-on-demurrage-detention-cleared-to-take-full-effect-may-28"


def _status(ok: bool, message: str, **details: object) -> dict[str, object]:
    return {"status": "pass" if ok else "blocked", "message": message, **details}


def validate_database_url(url: str | None, *, pooled: bool) -> str | None:
    if not url or not url.strip():
        return "database URL is not configured"
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname or ""
        port = parsed.port
    except ValueError:
        return "database URL is malformed"
    if parsed.scheme not in {"postgres", "postgresql"} or not hostname:
        return "database URL must be a PostgreSQL URL"
    if port is not None and not 1 <= port <= 65535:
        return "database URL has an invalid port"
    has_pooler = "-pooler" in hostname.lower()
    if pooled != has_pooler:
        expected = "pooled" if pooled else "direct"
        return f"database URL must be {expected}"
    return None


def validate_dev_branch(branch_id: str) -> str | None:
    if not branch_id.strip():
        return "NEON_BRANCH_ID is not configured"
    return None


def _env_check(settings: Settings) -> dict[str, object]:
    fields = {
        "TAVILY_API_KEY": bool(settings.tavily_api_key),
        "TAVILY_API_KEY_2": bool(settings.tavily_api_key_2),
        "TAVILY_API_KEY_COUNT": settings.tavily_api_key_count,
        "TAVILY_PROJECT_ID": bool(settings.tavily_project_id),
        "OPENAI_API_KEY": bool(settings.openai_api_key),
        "DATABASE_URL": bool(settings.database_url),
        "DIRECT_DATABASE_URL": bool(settings.direct_database_url),
        "OPENAI_MODEL": settings.openai_model,
        "OPENAI_FALLBACK_MODELS": [],
    }
    required = (
        "TAVILY_API_KEY",
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "DIRECT_DATABASE_URL",
    )
    return {
        "status": "pass" if all(fields[key] for key in required) else "blocked",
        "fields": fields,
        "env_file": str(settings.repo_root / ".env.local"),
    }


def _model_check(
    settings: Settings, *, allow_free_fallbacks: bool = False
) -> dict[str, object]:
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
    return _status(
        policy_error is None,
        "OpenAI model policy",
        requested_models=list(model_chain),
        required_model=settings.openai_model,
        allow_free_fallbacks=allow_free_fallbacks,
        policy_error=policy_error,
    )


def _database_check(url: str | None, *, pooled: bool, label: str) -> dict[str, object]:
    url_error = validate_database_url(url, pooled=pooled)
    if url_error:
        return _status(False, f"{label}: {url_error}")
    assert url is not None
    try:
        import psycopg

        with psycopg.connect(url, connect_timeout=10) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user")
            identity = cursor.fetchone()
            if identity is None:
                raise RuntimeError("database identity query returned no row")
            database, user = identity
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'research_runs')"
            )
            schema_row = cursor.fetchone()
            if schema_row is None:
                raise RuntimeError("database schema query returned no row")
            has_schema = bool(schema_row[0])
            migration_version: str | None = None
            if has_schema:
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = 'schema_migrations')"
                )
                migrations_row = cursor.fetchone()
                if migrations_row is None:
                    raise RuntimeError("migration table query returned no row")
                if migrations_row[0]:
                    cursor.execute("SELECT max(version) FROM schema_migrations")
                    version_row = cursor.fetchone()
                    if version_row is None:
                        raise RuntimeError("migration version query returned no row")
                    migration_version = version_row[0]
        return _status(
            True,
            f"{label} connection succeeded",
            database=database,
            user=user,
            research_schema=has_schema,
            migration_version=migration_version or "not_applied",
        )
    except Exception as error:
        return _status(False, f"{label} connection failed: {error.__class__.__name__}")


async def _provider_check(
    settings: Settings, *, allow_free_fallbacks: bool = False
) -> dict[str, object]:
    checks: dict[str, object] = {}
    tavily: TavilyProvider | None = None
    openai: OpenAIProvider | None = None

    def key_slots() -> list[int]:
        if tavily is None:
            return []
        slots: list[int] = []
        for attempt in tavily.call_history:
            slot = attempt.get("key_slot")
            if isinstance(slot, int) and not isinstance(slot, bool):
                slots.append(slot)
        return sorted(set(slots))

    def successful_key_slot() -> int | None:
        if tavily is None:
            return None
        for attempt in reversed(tavily.call_history):
            slot = attempt.get("key_slot")
            if (
                attempt.get("status") == "succeeded"
                and isinstance(slot, int)
                and not isinstance(slot, bool)
            ):
                return slot
        return None

    if settings.tavily_api_keys:
        try:
            tavily = TavilyProvider(settings.tavily_api_keys, settings.tavily_project_id)
            search_results = await tavily.search(
                "latest FMC demurrage detention enforcement",
                include_domains=["fmc.gov"],
                exclude_domains=["linkedin.com"],
                max_results=1,
            )
            extracted = await tavily.extract(
                [SourceCandidate(url=FMC_SMOKE_URL, source_kind="doctor-smoke")]
            )
            checks["tavily"] = _status(
                bool(search_results) and bool(extracted),
                "Tavily Search and Extract completed",
                search_results=len(search_results),
                extracted_sources=len(extracted),
                key_slots_attempted=key_slots(),
                successful_key_slot=successful_key_slot(),
            )
        except (ProviderError, ValueError) as error:
            checks["tavily"] = _status(
                False,
                f"Tavily check failed: {error}",
                key_slots_attempted=key_slots(),
            )
    else:
        checks["tavily"] = _status(False, "TAVILY_API_KEY is not configured")

    if settings.openai_api_key:
        try:
            model_chain = settings.model_chain(
                allow_free_fallbacks=allow_free_fallbacks
            )
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
            capabilities = await resolve_capabilities(
                settings.openai_api_key.get_secret_value(),
                model_chain,
                settings.openrouter_capabilities_cache,
                require_tools=True,
                allow_cached=False,
            )
            if not capabilities.eligible_models:
                raise ProviderError(
                    "configured OpenAI model does not support discovery tools and structured output"
                )
            openai = OpenAIProvider(
                settings.openai_api_key.get_secret_value(),
                settings.openai_model,
                fallback_models=fallback_models,
                allow_free_fallbacks=allow_free_fallbacks,
                capability_report=capabilities,
            )
            model = await openai.health_check()
            checks["openai"] = _status(
                True,
                "OpenAI structured output completed",
                model=model,
                capabilities=capabilities.as_dict(),
                attempts=openai.call_history,
            )
        except (ProviderError, ValueError) as error:
            checks["openai"] = _status(
                False,
                f"OpenAI check failed: {error}",
                error_code=getattr(error, "error_code", None),
                attempts=(
                    openai.call_history
                    if openai is not None
                    else getattr(error, "attempts", [])
                ),
            )
    else:
        checks["openai"] = _status(
            False,
            "OpenAI key is not configured",
        )
    return checks


def _neon_check() -> dict[str, object]:
    return {
        "status": "not_configured",
        "message": (
            "Neon management uses host-controlled MCP OAuth; "
            "DATABASE_URL is runtime access and DIRECT_DATABASE_URL is migration access"
        ),
    }


async def run_doctor(
    settings: Settings, *, allow_free_fallbacks: bool = False
) -> dict[str, object]:
    provider_checks = await _provider_check(
        settings, allow_free_fallbacks=allow_free_fallbacks
    )
    checks: dict[str, object] = {
        "environment": _env_check(settings),
        "model_policy": _model_check(
            settings, allow_free_fallbacks=allow_free_fallbacks
        ),
        "providers": provider_checks,
        "neon_management": _neon_check(),
        "database_pooled": _database_check(
            settings.database_url, pooled=True, label="DATABASE_URL"
        ),
        "database_direct": _database_check(
            settings.direct_database_url,
            pooled=False,
            label="DIRECT_DATABASE_URL",
        ),
    }
    statuses: list[object] = []
    for key, value in checks.items():
        if key == "neon_management":
            continue
        if isinstance(value, dict) and isinstance(value.get("status"), str):
            statuses.append(value["status"])
        if key == "providers" and isinstance(value, dict):
            statuses.extend(
                nested.get("status")
                for nested in value.values()
                if isinstance(nested, dict)
            )
    overall = "pass" if statuses and all(status == "pass" for status in statuses) else "blocked"
    return {"status": overall, "root": str(settings.repo_root), "checks": checks}


async def run_model_check(
    settings: Settings, *, allow_free_fallbacks: bool = False
) -> dict[str, object]:
    policy = _model_check(settings, allow_free_fallbacks=allow_free_fallbacks)
    if policy.get("status") != "pass":
        return {"status": "blocked", "policy": policy}
    if not settings.openai_api_key:
        if settings.legacy_provider_explicit and settings.openrouter_api_key:
            try:
                await resolve_capabilities(
                    settings.openrouter_api_key.get_secret_value(),
                    (settings.openrouter_model,),
                    settings.openrouter_capabilities_cache,
                    require_tools=True,
                    allow_cached=False,
                )
            except ProviderError as error:
                return {
                    "status": "blocked",
                    "policy": policy,
                    "message": str(error),
                }
            return {
                "status": "blocked",
                "policy": policy,
                "message": "legacy OpenRouter credentials cannot authorize new runs",
            }
        return {
            "status": "blocked",
            "policy": policy,
            "message": "OPENAI_API_KEY is not configured",
        }


    capabilities = None
    provider: OpenAIProvider | None = None
    try:
        model_chain = settings.model_chain(
            allow_free_fallbacks=allow_free_fallbacks
        )
        capabilities = await resolve_capabilities(
            settings.openai_api_key.get_secret_value(),
            model_chain,
            settings.openrouter_capabilities_cache,
            require_tools=True,
            allow_cached=False,
        )
        if not capabilities.eligible_models:
            return {
                "status": "blocked",
                "policy": policy,
                "capabilities": capabilities.as_dict(),
                "message": (
                    "configured OpenAI model does not support discovery tools "
                    "and structured output"
                ),
            }
        provider = OpenAIProvider(
            settings.openai_api_key.get_secret_value(),
            settings.openai_model,
            fallback_models=model_chain[1:],
            allow_free_fallbacks=allow_free_fallbacks,
            capability_report=capabilities,
        )
        resolved_model = await provider.health_check()
        return {
            "status": "pass",
            "policy": policy,
            "requested_models": list(model_chain),
            "capabilities": capabilities.as_dict(),
            "resolved_model": resolved_model,
            "attempts": provider.call_history,
        }
    except (ProviderError, ValueError) as error:
        return {
            "status": "blocked",
            "policy": policy,
            "requested_models": list(model_chain),
            "message": str(error),
            "error_code": getattr(error, "error_code", None),
            "capabilities": capabilities.as_dict() if capabilities else None,
            "attempts": (
                provider.call_history
                if provider
                else getattr(error, "attempts", [])
            ),
        }


async def run_model_map(settings: Settings) -> dict[str, object]:
    if not settings.openai_api_key:
        return {
            "status": "blocked",
            "message": "OPENAI_API_KEY is not configured",
        }
    try:
        return {
            "status": "pass",
            "catalog": {
                "provider": "openai",
                "models": [
                    {
                        "model": settings.openai_model,
                        "status": "configured",
                        "supports_tools": True,
                        "supports_structured_outputs": True,
                    }
                ],
                "recommended_cascade": [settings.openai_model],
            },
        }
    except ProviderError as error:
        return {
            "status": "blocked",
            "message": str(error),
        }


def mcp_check() -> dict[str, object]:
    return {
        "status": ValidationStatus.BLOCKED.value,
        "message": (
            "MCP connectors are host-controlled and are not available "
            "inside the service process."
        ),
        "checks": {
            "tavily": "Run a read-only Tavily MCP Search and Extract smoke test in the host.",
            "neon": "Run a read-only Neon MCP project/branch/SQL smoke test in the host.",
            "openai": (
                "No OpenAI MCP connector is required; validate "
                "the LangChain adapter directly."
            ),
        },
    }
