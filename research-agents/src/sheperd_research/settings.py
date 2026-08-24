from __future__ import annotations

import os
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Self

from pydantic import Field, PrivateAttr, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_OPENAI_MODEL = "gpt-5.6-luna"
STRICT_OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"  # legacy persisted-run identifier
DEFAULT_FREE_FALLBACK_MODELS = (
    "z-ai/glm-5.2:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-20b:free",
    "dots-studio/dots-3-note-preview:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "liquid/lfm-2.5-2.6b:free",
)
_FREE_MODEL_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*:free$"
)
_OPENAI_MODEL_PATTERN = re.compile(r"^(?:gpt|o\d|chatgpt)-[a-z0-9][a-z0-9._-]*$")


def is_free_openrouter_model(value: str) -> bool:
    return bool(_FREE_MODEL_PATTERN.fullmatch(value))


def is_openai_model(value: str) -> bool:
    return bool(_OPENAI_MODEL_PATTERN.fullmatch(value))


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
    if is_openai_model(model):
        if model != DEFAULT_OPENAI_MODEL:
            return f"OPENAI_MODEL must be {DEFAULT_OPENAI_MODEL}"
        if fallback_models or (
            isinstance(raw_fallback_config, str) and raw_fallback_config.strip()
        ):
            return "OpenAI model fallbacks must be empty"
        return None
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
    if is_openai_model(model):
        if model != DEFAULT_OPENAI_MODEL:
            return f"OPENAI_MODEL must be {DEFAULT_OPENAI_MODEL}"
        if fallback_models or (
            isinstance(raw_fallback_config, str) and raw_fallback_config.strip()
        ):
            return "OpenAI model fallbacks are not supported"
        return None
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
    neon_project_id: str | None = None
    neon_project_name: str = "sheperd-research"
    neon_branch_id: str = "main"
    tavily_api_key: SecretStr | None = None
    tavily_api_key_2: SecretStr | None = None
    tavily_project_id: str | None = None
    openai_api_key: SecretStr | None = None
    openai_model: str = DEFAULT_OPENAI_MODEL
    # Compatibility fields are ignored for runtime selection and retained only
    # so older persisted requests/tests can still be deserialized.
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
    llm_max_output_tokens: int = 6_000
    max_run_seconds: int = 2_400
    _legacy_provider_explicit: bool = PrivateAttr(default=False)

    def __init__(self, **values: Any) -> None:
        root = discover_repo_root()
        legacy_provider_explicit = (
            "openrouter_api_key" in values and "openai_api_key" not in values
        )
        values.setdefault("_env_file", root / ".env.local")
        super().__init__(**values)
        self._legacy_provider_explicit = legacy_provider_explicit

    @model_validator(mode="after")
    def select_openai_provider(self) -> Self:
        # Keep legacy fields readable for old persisted requests/tests, but
        # mirror the new provider only when OpenAI is explicitly configured.
        if self.openai_api_key is not None or self.openai_model != DEFAULT_OPENAI_MODEL:
            self.openrouter_api_key = self.openai_api_key
            self.openrouter_model = self.openai_model
            self.openrouter_fallback_models = ""
        return self

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
        return bool(self.tavily_api_key and self.openai_api_key)

    @property
    def legacy_provider_explicit(self) -> bool:
        return self._legacy_provider_explicit

    @property
    def tavily_api_keys(self) -> tuple[str, ...]:
        return tuple(
            secret.get_secret_value()
            for secret in (self.tavily_api_key, self.tavily_api_key_2)
            if secret is not None and secret.get_secret_value().strip()
        )

    @property
    def tavily_api_key_count(self) -> int:
        return len(self.tavily_api_keys)

    @property
    def has_database_credentials(self) -> bool:
        return bool(self.database_url)

    @property
    def has_direct_database_credentials(self) -> bool:
        return bool(self.direct_database_url)

    @property
    def openrouter_model_chain(self) -> tuple[str, ...]:
        return (self.openai_model,)

    def model_chain(self, *, allow_free_fallbacks: bool) -> tuple[str, ...]:
        del allow_free_fallbacks
        return (self.openai_model,)

    @property
    def openrouter_fallback_model_list(self) -> tuple[str, ...]:
        return ()

    @property
    def strict_openrouter_policy_error(self) -> str | None:
        return strict_openrouter_policy_error(
            self.openai_model,
            (),
        )
