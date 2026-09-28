from __future__ import annotations

import os
from collections.abc import Callable
from threading import Lock
from typing import cast

from fastapi import FastAPI

from sheperd_research.db import PostgresRepository, RepositoryProtocol
from sheperd_research.diagnostics import validate_database_url
from sheperd_research.settings import Settings
from sheperd_research.web import create_app


def _runtime_database_config() -> tuple[str | None, str]:
    try:
        settings = Settings()
    except RuntimeError:
        return os.environ.get("DATABASE_URL"), os.environ.get("NEON_BRANCH_ID", "main")
    return settings.database_url, settings.neon_branch_id


def _runtime_settings() -> Settings | None:
    try:
        return Settings()
    except RuntimeError:
        return None


def _connect_repository() -> PostgresRepository:
    database_url, branch_id = _runtime_database_config()
    url_error = validate_database_url(database_url, pooled=True)
    if url_error or database_url is None:
        raise RuntimeError("runtime DATABASE_URL is blocked")
    if not branch_id.strip():
        raise RuntimeError("runtime NEON_BRANCH_ID is blocked")
    try:
        return PostgresRepository.from_url(database_url, branch_id)
    except Exception as error:
        raise RuntimeError("runtime database connection failed") from error


class _LazyRepository:
    def __init__(self) -> None:
        self._repository: RepositoryProtocol | None = None
        self._error: RuntimeError | None = None
        self._lock = Lock()

    def _load(self) -> RepositoryProtocol:
        if self._error is not None:
            raise self._error
        if self._repository is not None:
            return self._repository
        with self._lock:
            if self._error is not None:
                raise self._error
            if self._repository is None:
                try:
                    self._repository = _connect_repository()
                except RuntimeError as error:
                    self._error = error
                    raise
            return self._repository

    def __getattr__(self, name: str) -> Callable[..., object]:
        return cast(Callable[..., object], getattr(self._load(), name))


app: FastAPI = create_app(
    cast(RepositoryProtocol, _LazyRepository()),
    settings=_runtime_settings(),
)
