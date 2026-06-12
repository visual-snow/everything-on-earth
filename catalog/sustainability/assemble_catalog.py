#!/usr/bin/env python3
"""Build the sustainability catalog from per-domain discovery outputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))

from catalog_assembler import (  # type: ignore  # noqa: E402
    CatalogSpec,
    build_catalog as _build_catalog,
    enrich_entries as _enrich_entries,
    extract_tags as _extract_tags,
    run_cli,
)


STOPWORDS = {
    "analysis",
    "analytics",
    "app",
    "dashboard",
    "data",
    "github",
    "open",
    "opensource",
    "platform",
    "software",
    "source",
    "sustainability",
    "sustainable",
    "system",
    "systems",
    "tool",
    "tooling",
    "tools",
}

KEYWORDS = {
    "air-quality",
    "biodiversity",
    "bioacoustics",
    "camera-trap",
    "carbon-accounting",
    "carbon-credit",
    "carbon-footprint",
    "carbon-risk",
    "circular-economy",
    "climate-finance",
    "climate-risk",
    "cmip",
    "csrd",
    "demand-response",
    "downscaling",
    "embodied-carbon",
    "energy-modeling",
    "energyplus",
    "environmental-justice",
    "era5",
    "esg",
    "ghg",
    "green-building",
    "hydrology",
    "issb",
    "lca",
    "land-cover",
    "life-cycle",
    "microgrid",
    "ndvi",
    "ocean-climate",
    "renewable-energy",
    "remote-sensing",
    "scope-3",
    "sdg",
    "smart-grid",
    "soil-carbon",
    "supply-chain",
    "tcfd",
    "transport",
    "water-quality",
    "watershed",
}

DOMAIN_TAG_HINTS = {
    "carbon-accounting-ghg": ["carbon-accounting", "ghg", "scope-3", "carbon-footprint"],
    "energy-modeling-simulation": ["energy-modeling", "energyplus", "grid-simulation", "building-energy"],
    "climate-data-analysis": ["climate-data", "cmip", "era5", "downscaling"],
    "life-cycle-assessment": ["lca", "life-cycle", "environmental-impact", "embodied-carbon"],
    "remote-sensing-land-use": ["remote-sensing", "land-cover", "deforestation", "ndvi"],
    "renewable-energy-optimization": ["renewable-energy", "microgrid", "storage-optimization", "energy-planning"],
    "biodiversity-monitoring": ["biodiversity", "camera-trap", "bioacoustics", "species-monitoring"],
    "water-resource-management": ["hydrology", "watershed", "water-quality", "water-modeling"],
    "circular-economy-waste": ["circular-economy", "material-flow", "recycling", "waste-tracking"],
    "esg-reporting-compliance": ["esg", "csrd", "tcfd", "issb"],
    "smart-grid-demand-response": ["smart-grid", "demand-response", "load-forecasting", "ev-charging"],
    "supply-chain-sustainability": ["supply-chain", "traceability", "scope-3", "deforestation"],
    "air-quality-emissions": ["air-quality", "emissions", "dispersion-modeling", "inventory"],
    "sustainable-agriculture": ["precision-agriculture", "soil-carbon", "crop-modeling", "regenerative-agriculture"],
    "ocean-climate": ["ocean-climate", "blue-carbon", "marine-carbon", "ocean-acidification"],
    "sustainable-transport": ["transport", "ev-routing", "public-transit", "mobility"],
    "green-building-certification": ["green-building", "leed", "breeam", "embodied-carbon"],
    "environmental-justice": ["environmental-justice", "equity", "exposure-mapping", "community-impact"],
    "climate-finance": ["climate-finance", "green-bonds", "carbon-credit", "climate-risk"],
    "sustainability-dashboards-viz": ["sdg", "kpi-dashboard", "data-portal", "climate-visualization"],
}

TAG_ALIASES = {
    "breeam": "breeam",
    "carboncredit": "carbon-credit",
    "carboncredits": "carbon-credit",
    "cmip6": "cmip",
    "co2": "ghg",
    "csrd": "csrd",
    "ebird": "biodiversity",
    "energyplus": "energyplus",
    "era5": "era5",
    "esg": "esg",
    "ghg": "ghg",
    "inaturalist": "biodiversity",
    "issb": "issb",
    "kpi": "kpi-dashboard",
    "lca": "lca",
    "leed": "leed",
    "ndvi": "ndvi",
    "scope3": "scope-3",
    "sdg": "sdg",
    "tcfd": "tcfd",
}


SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    tag_aliases=TAG_ALIASES,
)


def enrich_entries(entries: list[dict], domain_name_by_id: dict[str, str]) -> list[dict]:
    return _enrich_entries(entries, domain_name_by_id, SPEC)


def extract_tags(entry: dict) -> list[str]:
    return _extract_tags(entry, SPEC)


def build_catalog(
    config_path: Path,
    batch_size: int,
    repo_root: Path | None = None,
    sync_site: bool = False,
) -> Path:
    return _build_catalog(config_path, batch_size, SPEC, repo_root=repo_root, sync_site=sync_site)


def main() -> None:
    run_cli(SPEC, domain="sustainability")


if __name__ == "__main__":
    main()
