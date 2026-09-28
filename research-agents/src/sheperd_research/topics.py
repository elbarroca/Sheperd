from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import RegionQueryPack, TopicConfig
from .validators import MANDATORY_EXCLUDED_DOMAINS

DND_PORT_INCLUDE_DOMAINS = [
    "fmc.gov",
    "ecfr.gov",
    "federalregister.gov",
    "cadc.uscourts.gov",
    "courtlistener.com",
    "justice.gov",
    "ftc.gov",
    "portoflosangeles.org",
    "polb.com",
    "oaklandca.gov",
    "nwseaportalliance.com",
    "portseattle.org",
    "portoftacoma.com",
    "gaports.com",
    "scspa.com",
    "panynj.gov",
    "portofvirginia.com",
    "porthouston.com",
    "puertomanzanillo.com.mx",
    "puertolazarocardenas.com.mx",
    "puertodeveracruz.com.mx",
    "puertoaltamira.com.mx",
    "anam.gob.mx",
    "gob.mx",
    "transport.ec.europa.eu",
    "emsa.europa.eu",
    "ec.europa.eu",
    "portofrotterdam.com",
    "portofantwerpbruges.com",
    "hamburg-port-authority.de",
    "valenciaport.com",
    "portdebarcelona.cat",
    "portoffelixstowe.co.uk",
    "peelports.com",
    "imo.org",
    "unctad.org",
    "worldbank.org",
    "portwatch.imf.org",
    "wto.org",
    "gcaptain.com",
    "container-news.com",
    "theloadstar.com",
    "splash247.com",
]


def default_region_packs() -> dict[str, RegionQueryPack]:
    language_hints = {
        "us": ["en"],
        "canada": ["en", "fr"],
        "mexico": ["es", "en"],
        "europe": ["en", "fr", "de", "es"],
        "south-america": ["pt", "es", "en"],
        "middle-east": ["ar", "en"],
        "global": ["en", "fr", "es", "pt", "de", "ar"],
    }
    definitions = {
        "us": ("United States", ["Los Angeles", "Long Beach", "Savannah", "Houston"]),
        "canada": ("Canada", ["Vancouver", "Prince Rupert", "Montreal", "Halifax"]),
        "mexico": ("Mexico", ["Manzanillo", "Lázaro Cárdenas", "Veracruz", "Altamira"]),
        "europe": ("Europe", ["Rotterdam", "Antwerp", "Hamburg", "Valencia", "Felixstowe"]),
        "south-america": ("South America", ["Santos", "San Antonio", "Buenos Aires", "Callao"]),
        "middle-east": ("Middle East", ["Abu Dhabi", "Jeddah", "Salalah", "Hamad Port"]),
        "global": ("Global", []),
    }
    authority_domains = {
        "canada": [
            "tc.canada.ca",
            "portvancouver.com",
            "rupertport.com",
            "port-montreal.com",
            "porthalifax.ca",
        ],
        "south-america": ["gov.br", "antaq.gov.br", "portodesantos.com.br", "puertosanantonio.com"],
        "middle-east": ["adports.ae", "ports.gov.sa", "motc.gov.om", "mwani.gov.qa"],
    }
    query_templates = [
        "{region} maritime D&D demurrage detention fees regulation enforcement",
        "{region} container port congestion dwell time closure TEU carrier terminal",
        "{region} shipping line importer freight fluidity court trade update",
    ]
    return {
        key: RegionQueryPack(
            region=key,
            countries=[country],
            ports=ports,
            signal_types=["regulatory", "port-operations", "trade-flow", "fees"],
            query_families=[template.format(region=country) for template in query_templates],
            language_hints=language_hints[key],
            required=key != "global",
            freshness_days=14,
            authority_domains=authority_domains.get(key, []),
            allow_open_discovery=True,
        )
        for key, (country, ports) in definitions.items()
    }


def default_topic_configs() -> dict[str, TopicConfig]:
    return {
        "dnd-port": TopicConfig(
            name="dnd-port",
            description="D&D, port, carrier, terminal, and regulatory intelligence.",
            queries=[
                "latest United States maritime port regulation enforcement shipping update",
                "latest United States container port operations carrier terminal update",
                "latest East Coast Gulf U.S. port congestion terminal carrier update",
                "latest Mexico container port Manzanillo Veracruz trade shipping update",
                "latest Europe Rotterdam Antwerp Hamburg Valencia "
                "Barcelona Felixstowe port shipping update",
            ],
            geographies=[
                "Regulatory",
                "United States",
                "West Coast",
                "East Coast",
                "Gulf",
                "Canada",
                "Mexico",
                "Europe",
                "South America",
                "Middle East",
                "Global",
            ],
            include_domains=DND_PORT_INCLUDE_DOMAINS,
            exclude_domains=["linkedin.com"],
            lookback_days=14,
            region_packs=default_region_packs(),
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
    loaded: dict[str, TopicConfig] = {}
    for name, definition in topics.items():
        topic = TopicConfig(name=name, **definition)
        if not topic.region_packs and name == "dnd-port":
            topic = topic.model_copy(update={"region_packs": default_region_packs()})
        loaded[name] = _validate_topic_config(topic)
    return loaded
