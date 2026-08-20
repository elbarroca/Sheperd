from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import TopicConfig
from .validators import MANDATORY_EXCLUDED_DOMAINS

DND_PORT_INCLUDE_DOMAINS = [
    "fmc.gov",
    "ecfr.gov",
    "portoflosangeles.org",
    "polb.com",
    "oaklandca.gov",
    "nwseaportalliance.com",
    "gaports.com",
    "scspa.com",
    "panynj.gov",
    "porthouston.com",
    "puertomanzanillo.com.mx",
]


def default_topic_configs() -> dict[str, TopicConfig]:
    return {
        "dnd-port": TopicConfig(
            name="dnd-port",
            description="D&D, port, carrier, terminal, and regulatory intelligence.",
            queries=[
                "latest U.S. demurrage detention FMC court carrier terminal update",
                "latest West Coast U.S. port congestion dwell time container update",
                "latest East Coast Gulf U.S. port congestion terminal carrier update",
                "latest Mexico container port Manzanillo Veracruz trade shipping update",
            ],
            geographies=["West Coast", "East Coast", "Gulf", "Mexico"],
            include_domains=DND_PORT_INCLUDE_DOMAINS,
            exclude_domains=["linkedin.com"],
            lookback_days=14,
        )
    }


def _validate_topic_config(topic: TopicConfig) -> TopicConfig:
    if not topic.geographies:
        raise ValueError(f"topic {topic.name} must define non-empty geographies")
    if not topic.include_domains:
        raise ValueError(
            f"topic {topic.name} must define a non-empty include_domains allowlist"
        )
    observed_exclusions = {
        domain.lower().removeprefix("www.") for domain in topic.exclude_domains
    }
    missing_exclusions = {
        domain for domain in MANDATORY_EXCLUDED_DOMAINS if domain not in observed_exclusions
    }
    if not topic.exclude_domains or missing_exclusions:
        raise ValueError(
            f"topic {topic.name} must define non-empty exclude_domains including "
            f"mandatory exclusions: {sorted(MANDATORY_EXCLUDED_DOMAINS)}"
        )
    return topic


def load_topic_configs(path: Path) -> dict[str, TopicConfig]:
    if not path.exists():
        return {
            name: _validate_topic_config(topic)
            for name, topic in default_topic_configs().items()
        }
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    topics = raw.get("topics", {})
    return {
        name: _validate_topic_config(TopicConfig(name=name, **definition))
        for name, definition in topics.items()
    }
