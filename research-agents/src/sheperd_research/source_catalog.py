from __future__ import annotations

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .contracts import SourceCandidate
from .validators import (
    MANDATORY_EXCLUDED_DOMAINS,
    can_extract_url,
    deduplicate_sources,
    matches_domain,
    normalize_url,
    url_policy_error,
)

DEFAULT_SOURCE_CATALOG_PATH = Path(__file__).resolve().parents[2] / "config/source_catalog.yml"
CATALOG_WEIGHT_TARGETS = {
    "us": 0.6,
    "mexico": 0.2,
    "europe": 0.15,
    "global": 0.05,
}
REGIONS = frozenset(CATALOG_WEIGHT_TARGETS)
JURISDICTIONS = frozenset(
    {
        "us-federal",
        "us-federal-courts",
        "west-coast",
        "east-coast",
        "gulf",
        "mexico-federal",
        "mexico-pacific",
        "mexico-gulf",
        "eu",
        "europe-port",
        "global",
        "public-trade",
    }
)
AUTHORITY_TIERS = frozenset({"primary", "reference", "trade-press"})
SOURCE_TYPES = frozenset(
    {
        "regulator",
        "court",
        "public-records",
        "port-authority",
        "customs",
        "intergovernmental",
        "economic-data",
        "trade-media",
    }
)
SIGNAL_TYPES = frozenset(
    {
        "regulatory",
        "enforcement",
        "court-opinion",
        "port-operations",
        "terminal-operations",
        "trade-flow",
        "macro",
        "market-commentary",
    }
)
ACCESS_TYPES = frozenset({"public-html", "public-dataset"})
REFRESH_CADENCES = frozenset({"daily", "weekly", "monthly"})
AUTHORITATIVE_SOURCE_TYPES = frozenset(
    {
        "regulator",
        "court",
        "port-authority",
        "customs",
        "intergovernmental",
        "economic-data",
    }
)
DISCOVERY_GEOGRAPHIES_BY_JURISDICTION: dict[str, tuple[str, ...]] = {
    "us-federal": ("Regulatory", "United States"),
    "us-federal-courts": ("Regulatory", "United States"),
    "west-coast": ("West Coast",),
    "east-coast": ("East Coast",),
    "gulf": ("Gulf",),
    "mexico-federal": ("Mexico",),
    "mexico-pacific": ("Mexico",),
    "mexico-gulf": ("Mexico",),
}


def _approx_equal(left: float, right: float) -> bool:
    return abs(left - right) <= 1e-9


def _normalize_domain(value: str) -> str:
    stripped = value.strip().lower()
    parsed = urlsplit(stripped if "://" in stripped else f"https://{stripped}")
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if not host or "." not in host:
        raise ValueError("domain must be a valid hostname")
    return host


def _host(url: str) -> str:
    return (urlsplit(normalize_url(url)).hostname or "").lower().removeprefix("www.")


def _matches_domain(host: str, domain: str) -> bool:
    return matches_domain(host, domain)


def _validation_request_key(
    query: str,
    include_domains: list[str],
    exclude_domains: list[str],
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    return (
        query.strip().casefold(),
        tuple(sorted(_normalize_domain(domain) for domain in include_domains)),
        tuple(sorted(_normalize_domain(domain) for domain in exclude_domains)),
    )


class CoverageWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    us: float
    mexico: float
    europe: float
    global_: float = Field(alias="global")

    @model_validator(mode="after")
    def validate_targets(self) -> CoverageWeights:
        observed = {
            "us": self.us,
            "mexico": self.mexico,
            "europe": self.europe,
            "global": self.global_,
        }
        for key, expected in CATALOG_WEIGHT_TARGETS.items():
            if not _approx_equal(observed[key], expected):
                raise ValueError(f"coverage_weights.{key} must be {expected}")
        if not _approx_equal(sum(observed.values()), 1.0):
            raise ValueError("coverage weights must sum to 1.0")
        return self

    def as_dict(self) -> dict[str, float]:
        return {
            "us": self.us,
            "mexico": self.mexico,
            "europe": self.europe,
            "global": self.global_,
        }


class CatalogSource(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_id: str = Field(pattern=r"^[a-z0-9-]+$")
    region: str
    jurisdiction: str
    authority_tier: str
    domain: str
    url: str
    source_type: str
    signal_types: list[str] = Field(min_length=1)
    access: str
    enabled: bool = True
    required: bool = False
    refresh_cadence: str

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        if value not in REGIONS:
            raise ValueError(f"region must be one of {sorted(REGIONS)}")
        return value

    @field_validator("jurisdiction")
    @classmethod
    def validate_jurisdiction(cls, value: str) -> str:
        if value not in JURISDICTIONS:
            raise ValueError(f"jurisdiction must be one of {sorted(JURISDICTIONS)}")
        return value

    @field_validator("authority_tier")
    @classmethod
    def validate_authority_tier(cls, value: str) -> str:
        if value not in AUTHORITY_TIERS:
            raise ValueError(f"authority_tier must be one of {sorted(AUTHORITY_TIERS)}")
        return value

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str) -> str:
        return _normalize_domain(value)

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        if value not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {sorted(SOURCE_TYPES)}")
        return value

    @field_validator("signal_types")
    @classmethod
    def validate_signal_types(cls, value: list[str]) -> list[str]:
        unknown = [item for item in value if item not in SIGNAL_TYPES]
        if unknown:
            raise ValueError(f"signal_types contain unknown values: {sorted(set(unknown))}")
        return value

    @field_validator("access")
    @classmethod
    def validate_access(cls, value: str) -> str:
        if value not in ACCESS_TYPES:
            raise ValueError(f"access must be one of {sorted(ACCESS_TYPES)}")
        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        normalized = normalize_url(value)
        if url_policy_error(normalized) is not None:
            raise ValueError("catalog URLs must exclude LinkedIn and paywall markers")
        return normalized

    @field_validator("refresh_cadence")
    @classmethod
    def validate_refresh_cadence(cls, value: str) -> str:
        if value not in REFRESH_CADENCES:
            raise ValueError(f"refresh_cadence must be one of {sorted(REFRESH_CADENCES)}")
        return value

    @model_validator(mode="after")
    def validate_url_host(self) -> CatalogSource:
        if _host(self.url) != self.domain:
            raise ValueError("catalog URL host must match the declared domain")
        if self.required and not self.enabled:
            raise ValueError("required sources must be enabled")
        return self

    @property
    def discovery_geographies(self) -> tuple[str, ...]:
        if self.source_type not in AUTHORITATIVE_SOURCE_TYPES:
            return ()
        return DISCOVERY_GEOGRAPHIES_BY_JURISDICTION.get(self.jurisdiction, ())


class SourceCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coverage_weights: CoverageWeights
    sources: list[CatalogSource] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_uniqueness(self) -> SourceCatalog:
        source_ids: set[str] = set()
        domains: set[str] = set()
        enabled_regions = {source.region for source in self.sources if source.enabled}
        required_domains: set[str] = set()
        for source in self.sources:
            if source.source_id in source_ids:
                raise ValueError(f"duplicate source_id: {source.source_id}")
            if source.domain in domains:
                raise ValueError(f"duplicate domain: {source.domain}")
            source_ids.add(source.source_id)
            domains.add(source.domain)
            if source.enabled and source.required:
                required_domains.add(source.domain)
        missing_regions = set(CATALOG_WEIGHT_TARGETS) - enabled_regions
        if missing_regions:
            raise ValueError(
                "catalog must include at least one enabled source for every coverage region"
            )
        if not required_domains:
            raise ValueError("catalog must define a non-empty required-domain set")
        return self

    def enabled_sources(self) -> list[CatalogSource]:
        return [source for source in self.sources if source.enabled]

    def required_sources(self) -> list[CatalogSource]:
        return [source for source in self.enabled_sources() if source.required]

    def authoritative_domain_geographies(self) -> dict[str, tuple[str, ...]]:
        return {
            source.domain: source.discovery_geographies
            for source in self.enabled_sources()
            if source.discovery_geographies
        }

    def redacted_rows(
        self,
        statuses: dict[str, str] | None = None,
    ) -> list[dict[str, object]]:
        observed = statuses or {}
        coverage = self.coverage_weights.as_dict()
        return [
            {
                "source_id": source.source_id,
                "domain": source.domain,
                "access": source.access,
                "coverage": {
                    "region": source.region,
                    "weight": coverage[source.region],
                },
                "authority": {
                    "tier": source.authority_tier,
                    "type": source.source_type,
                },
                "last_validation_status": observed.get(source.source_id, "not-checked"),
            }
            for source in self.sources
        ]


class CatalogValidationObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    status: str
    matched_domains: list[str] = Field(default_factory=list)


class CatalogSearchProvider(Protocol):
    async def search(
        self,
        query: str,
        *,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        max_results: int = 5,
    ) -> list[SourceCandidate]: ...


def source_catalog_path(path: Path | None = None) -> Path:
    return (path or DEFAULT_SOURCE_CATALOG_PATH).resolve()


@lru_cache(maxsize=8)
def _load_source_catalog_cached(path_value: str) -> SourceCatalog:
    path = Path(path_value)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return SourceCatalog.model_validate(raw)


def load_source_catalog(path: Path | None = None) -> SourceCatalog:
    resolved = source_catalog_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"source catalog not found: {resolved}")
    return _load_source_catalog_cached(str(resolved))


def authoritative_geography_domain_catalog(path: Path | None = None) -> dict[str, tuple[str, ...]]:
    return load_source_catalog(path).authoritative_domain_geographies()


async def validate_required_sources(
    catalog: SourceCatalog,
    tavily: CatalogSearchProvider,
) -> list[CatalogValidationObservation]:
    required_sources = catalog.required_sources()
    if not required_sources:
        raise ValueError("catalog must define a non-empty required-domain set")

    async def validate(
        key: tuple[str, tuple[str, ...], tuple[str, ...]],
        sources: list[CatalogSource],
    ) -> list[CatalogValidationObservation]:
        query, include_domains, exclude_domains = key
        results = await tavily.search(
            query,
            include_domains=list(include_domains),
            exclude_domains=list(exclude_domains),
            max_results=3,
        )
        deduped = deduplicate_sources(results)
        matched = sorted(
            {
                _host(candidate.url)
                for candidate in deduped
                if can_extract_url(candidate.url)
                and any(
                    _matches_domain(_host(candidate.url), domain)
                    for domain in include_domains
                )
            }
        )
        status = "pass" if matched else "unknown"
        return [
            CatalogValidationObservation(
                source_id=source.source_id,
                status=status,
                matched_domains=matched,
            )
            for source in sources
        ]

    grouped_requests: dict[
        tuple[str, tuple[str, ...], tuple[str, ...]],
        list[CatalogSource],
    ] = {}
    for source in required_sources:
        key = _validation_request_key(
            source.domain,
            [source.domain],
            list(MANDATORY_EXCLUDED_DOMAINS),
        )
        grouped_requests.setdefault(key, []).append(source)

    results = await asyncio.gather(
        *(validate(key, sources) for key, sources in grouped_requests.items())
    )
    observations = [item for group in results for item in group]
    required_ids = {source.source_id for source in required_sources}
    observed_ids = {observation.source_id for observation in observations}
    if observed_ids != required_ids:
        raise ValueError("required-domain validation missing observations")
    return observations
