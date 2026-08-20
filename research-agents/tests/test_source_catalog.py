from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import sheperd_research.cli as cli_module
from sheperd_research.cli import _source_map_command
from sheperd_research.contracts import SourceCandidate
from sheperd_research.settings import Settings
from sheperd_research.source_catalog import (
    authoritative_geography_domain_catalog,
    load_source_catalog,
    validate_required_sources,
)


def _catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config/source_catalog.yml"


def test_source_catalog_validates_coverage_and_redacts_urls() -> None:
    catalog = load_source_catalog(_catalog_path())

    assert catalog.coverage_weights.as_dict() == {
        "us": 0.6,
        "mexico": 0.2,
        "europe": 0.15,
        "global": 0.05,
    }
    redacted = catalog.redacted_rows()
    sample = next(row for row in redacted if row["source_id"] == "us-fmc")

    assert "url" not in sample
    assert sample["domain"] == "fmc.gov"
    assert sample["coverage"] == {"region": "us", "weight": 0.6}
    assert sample["last_validation_status"] == "not-checked"


def test_authoritative_domain_catalog_excludes_trade_media() -> None:
    catalog = authoritative_geography_domain_catalog(_catalog_path())

    assert catalog["fmc.gov"] == ("Regulatory", "United States")
    assert catalog["gaports.com"] == ("East Coast",)
    assert "gcaptain.com" not in catalog


def test_validate_required_sources_deduplicates_and_matches_domains() -> None:
    class TavilyStub:
        async def search(
            self,
            query: str,
            *,
            include_domains: list[str] | None = None,
            exclude_domains: list[str] | None = None,
            max_results: int = 5,
        ) -> list[SourceCandidate]:
            del query, exclude_domains, max_results
            assert include_domains is not None
            domain = include_domains[0]
            return [
                SourceCandidate(
                    url=f"https://www.{domain}/article?utm_source=test",
                    publisher=domain,
                    published_at=datetime(2026, 8, 20, tzinfo=UTC),
                ),
                SourceCandidate(
                    url=f"https://www.{domain}/article",
                    publisher=domain,
                    published_at=datetime(2026, 8, 20, tzinfo=UTC),
                ),
            ]

    observations = asyncio.run(
        validate_required_sources(load_source_catalog(_catalog_path()), TavilyStub())
    )

    assert observations
    assert all(observation.status == "pass" for observation in observations)


def test_source_map_command_redacts_urls_and_requires_strict_pass(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))

    class TavilyStub:
        def __init__(self, *_: object, **__: object) -> None:
            return None

        async def search(
            self,
            query: str,
            *,
            include_domains: list[str] | None = None,
            exclude_domains: list[str] | None = None,
            max_results: int = 5,
        ) -> list[SourceCandidate]:
            del query, exclude_domains, max_results
            assert include_domains is not None
            domain = include_domains[0]
            return [
                SourceCandidate(
                    url=f"https://www.{domain}/validated",
                    publisher=domain,
                    published_at=datetime(2026, 8, 20, tzinfo=UTC),
                )
            ]

    monkeypatch.setattr(cli_module, "TavilyProvider", TavilyStub)

    result = _source_map_command(
        argparse.Namespace(check=True, strict=True, json=True),
        Settings(tavily_api_key="secret"),
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["required_failures"] == []
    assert all("url" not in row for row in payload["sources"])
    assert all(
        row["last_validation_status"] in {"pass", "not-checked"} for row in payload["sources"]
    )


def test_source_map_command_fails_strict_when_required_domain_cannot_validate(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).resolve().parents[2]
    monkeypatch.setenv("SHEPERD_ROOT", str(root))

    class TavilyStub:
        def __init__(self, *_: object, **__: object) -> None:
            return None

        async def search(
            self,
            query: str,
            *,
            include_domains: list[str] | None = None,
            exclude_domains: list[str] | None = None,
            max_results: int = 5,
        ) -> list[SourceCandidate]:
            del query, exclude_domains, max_results
            assert include_domains is not None
            if include_domains[0] == "fmc.gov":
                return []
            return [
                SourceCandidate(
                    url=f"https://www.{include_domains[0]}/validated",
                    publisher=include_domains[0],
                    published_at=datetime(2026, 8, 20, tzinfo=UTC),
                )
            ]

    monkeypatch.setattr(cli_module, "TavilyProvider", TavilyStub)

    result = _source_map_command(
        argparse.Namespace(check=True, strict=True, json=True),
        Settings(tavily_api_key="secret"),
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 2
    assert payload["status"] == "failed"
    assert "us-fmc" in payload["summary"]["required_failures"]
