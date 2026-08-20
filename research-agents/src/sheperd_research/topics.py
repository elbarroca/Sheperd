from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import TopicConfig


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
            lookback_days=14,
        )
    }


def load_topic_configs(path: Path) -> dict[str, TopicConfig]:
    if not path.exists():
        return default_topic_configs()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    topics = raw.get("topics", {})
    return {name: TopicConfig(name=name, **definition) for name, definition in topics.items()}
