from __future__ import annotations

import os
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

STRICT_OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"
DEFAULT_FREE_FALLBACK_MODELS = (
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "z-ai/glm-5.2:free",
)
_FREE_MODEL_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*:free$"
)


def is_free_openrouter_model(value: str) -> bool:
    return bool(_FREE_MODEL_PATTERN.fullmatch(value))


def parse_openrouter_fallback_models(value: str) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            item.strip()
            for item in value.split(",")
            if item.strip()
        )
    )


def has_raw_openrouter_fallback_config(value: str | Sequence[str]) -> bool:
    if isinstance(value, str):
        return value != ""
    return any(isinstance(item, str) and item != "" for item in value)


def strict_openrouter_policy_error(
    model: str,
    fallback_models: Sequence[str],
    *,
    raw_fallback_config: str | Sequence[str] | None = None,
) -> str | None:
    if model != STRICT_OPENROUTER_MODEL:
        return f"OPENROUTER_MODEL must be {STRICT_OPENROUTER_MODEL}"
    if raw_fallback_config is not None and has_raw_openrouter_fallback_config(
        raw_fallback_config
    ):
        return "OPENROUTER_FALLBACK_MODELS must be empty"
    if fallback_models:
        return "OPENROUTER_FALLBACK_MODELS must be empty"
    return None


def free_openrouter_policy_error(
    model: str,
    fallback_models: Sequence[str],
    *,
    raw_fallback_config: str | Sequence[str] | None = None,
) -> str | None:
    if model != STRICT_OPENROUTER_MODEL:
        return f"OPENROUTER_MODEL must remain {STRICT_OPENROUTER_MODEL}"
    if (
        raw_fallback_config is not None
        and isinstance(raw_fallback_config, str)
        and raw_fallback_config.strip()
        and not fallback_models
    ):
        return "OPENROUTER_FALLBACK_MODELS contains no valid free models"
    for fallback in fallback_models:
        if not is_free_openrouter_model(fallback):
            return f"fallback model must be a valid OpenRouter :free model: {fallback}"
    return None


def discover_repo_root(start: Path | None = None) -> Path:
    override = os.environ.get("SHEPERD_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if not root.exists():
            raise RuntimeError("SHEPERD_ROOT does not exist")
        return root

    candidates = [start or Path.cwd(), Path(__file__).resolve()]
    for candidate in candidates:
        for directory in (candidate, *candidate.parents):
            if (directory / ".git").exists() and (directory / "obsidian").exists():
                return directory
    raise RuntimeError("unable to discover the SheperD repository root")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repo_root: Path = Field(default_factory=discover_repo_root, exclude=True)
    database_url: str | None = None
    direct_database_url: str | None = None
    neon_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("NEON_PG_API_KEY", "NEON_API_KEY"),
    )
    neon_project_id: str | None = None
    neon_project_name: str = "sheperd-research"
    neon_branch_id: str = "main"
    tavily_api_key: SecretStr | None = None
    tavily_project_id: str | None = None
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = STRICT_OPENROUTER_MODEL
    openrouter_fallback_models: str = ""
    research_timezone: str = "Europe/Lisbon"
    topics_path: Path = Path("config/topics.yml")
    source_catalog_path: Path = Path("config/source_catalog.yml")
    obsidian_output_dir: Path = Path("06_Research/Agent Runs")
    host: str = "127.0.0.1"
    port: int = 8787
    llm_max_calls: int = 48
    llm_max_input_chars: int = 350_000
    llm_max_output_tokens: int = 3_000
    max_run_seconds: int = 900

    def __init__(self, **values: Any) -> None:
        root = discover_repo_root()
        values.setdefault("_env_file", root / ".env.local")
        super().__init__(**values)

    @property
    def vault_root(self) -> Path:
        return self.repo_root / "obsidian"

    @property
    def research_agents_root(self) -> Path:
        return self.repo_root / "research-agents"

    @property
    def resolved_topics_path(self) -> Path:
        if self.topics_path.is_absolute():
            return self.topics_path
        return self.research_agents_root / self.topics_path

    @property
    def resolved_source_catalog_path(self) -> Path:
        if self.source_catalog_path.is_absolute():
            return self.source_catalog_path
        return self.research_agents_root / self.source_catalog_path

    @property
    def resolved_obsidian_output_dir(self) -> Path:
        if self.obsidian_output_dir.is_absolute():
            return self.obsidian_output_dir
        return (self.vault_root / self.obsidian_output_dir).resolve()

    @property
    def openrouter_capabilities_cache(self) -> Path:
        return self.research_agents_root / ".cache" / "openrouter-capabilities.json"

    @property
    def has_live_provider_credentials(self) -> bool:
        return bool(self.tavily_api_key and self.openrouter_api_key)

    @property
    def has_database_credentials(self) -> bool:
        return bool(self.database_url)

    @property
    def has_direct_database_credentials(self) -> bool:
        return bool(self.direct_database_url)

    @property
    def has_neon_management_credentials(self) -> bool:
        return bool(self.neon_api_key)

    @property
    def openrouter_model_chain(self) -> tuple[str, ...]:
        configured = [self.openrouter_model, *self.openrouter_fallback_model_list]
        return tuple(dict.fromkeys(configured))

    def model_chain(self, *, allow_free_fallbacks: bool) -> tuple[str, ...]:
        if not allow_free_fallbacks:
            return (self.openrouter_model,)
        configured = self.openrouter_fallback_model_list
        fallbacks = configured or DEFAULT_FREE_FALLBACK_MODELS
        return tuple(dict.fromkeys((self.openrouter_model, *fallbacks)))

    @property
    def openrouter_fallback_model_list(self) -> tuple[str, ...]:
        return parse_openrouter_fallback_models(self.openrouter_fallback_models)

    @property
    def strict_openrouter_policy_error(self) -> str | None:
        return strict_openrouter_policy_error(
            self.openrouter_model,
            self.openrouter_fallback_model_list,
            raw_fallback_config=self.openrouter_fallback_models,
        )
