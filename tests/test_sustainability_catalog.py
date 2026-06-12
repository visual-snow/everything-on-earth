"""Tests for the sustainability catalog scaffold and assembly flow."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _load_sustainability_assembler():
    module_path = ROOT / "catalog" / "sustainability" / "assemble_catalog.py"
    spec = importlib.util.spec_from_file_location("sustainability_assemble_catalog", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_sustainability_config_has_expected_subdomains_and_waves():
    config_path = ROOT / "catalog" / "sustainability" / "swarm-config.json"

    config = json.loads(config_path.read_text())
    subdomain_ids = [subdomain["id"] for subdomain in config["sub_domains"]]
    wave_ids = [wave["id"] for wave in config["waves"]]

    assert config["topic_slug"] == "sustainability"
    assert config["output_dir"] == "catalog/sustainability"
    assert config["discovery_dir"] == "catalog/sustainability/discovery"
    assert subdomain_ids == [
        "carbon-accounting-ghg",
        "energy-modeling-simulation",
        "climate-data-analysis",
        "life-cycle-assessment",
        "remote-sensing-land-use",
        "renewable-energy-optimization",
        "biodiversity-monitoring",
        "water-resource-management",
        "circular-economy-waste",
        "esg-reporting-compliance",
        "smart-grid-demand-response",
        "supply-chain-sustainability",
        "air-quality-emissions",
        "sustainable-agriculture",
        "ocean-climate",
        "sustainable-transport",
        "green-building-certification",
        "environmental-justice",
        "climate-finance",
        "sustainability-dashboards-viz",
    ]
    assert wave_ids == ["wave-1", "wave-2", "wave-3", "wave-4"]
    assert all(len(wave["subdomains"]) == 5 for wave in config["waves"])


def test_sustainability_enrichment_uses_primary_sub_domain_for_category():
    module = _load_sustainability_assembler()

    entry = {
        "repo_url": "https://github.com/mlco2/codecarbon",
        "name": "mlco2/codecarbon",
        "description": "Track emissions from compute workloads and estimate their impact.",
        "sub_domain": "carbon-accounting-ghg",
        "found_in_domains": ["carbon-accounting-ghg", "climate-finance"],
        "score": 10,
    }
    domain_name_by_id = {
        "carbon-accounting-ghg": "Carbon Accounting / GHG",
        "climate-finance": "Climate Finance",
    }

    enriched = module.enrich_entries([entry], domain_name_by_id)

    assert enriched[0]["category"] == "Carbon Accounting / GHG"
    assert enriched[0]["summary"]
    assert "carbon-accounting" in enriched[0]["tags"]


def test_sustainability_build_catalog_writes_expected_artifacts(tmp_path):
    module = _load_sustainability_assembler()

    config_path = tmp_path / "catalog" / "sustainability" / "swarm-config.json"
    discovery_dir = tmp_path / "catalog" / "sustainability" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "carbon-accounting-ghg.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/mlco2/codecarbon",
                    "name": "mlco2/codecarbon",
                    "description": "Track emissions from compute workloads and estimate their impact.",
                    "sub_domain": "carbon-accounting-ghg",
                    "score": 10,
                    "score_rationale": "Canonical emissions tracking toolkit.",
                    "stars": 1700,
                    "language": "Python",
                    "license": "MIT",
                    "last_activity": "2026-03-24",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Sustainability Test Catalog",
                "topic_slug": "sustainability",
                "output_dir": "catalog/sustainability",
                "discovery_dir": "catalog/sustainability/discovery",
                "sub_domains": [
                    {
                        "id": "carbon-accounting-ghg",
                        "name": "Carbon Accounting / GHG",
                        "queries": [],
                    }
                ],
            }
        )
    )

    module.build_catalog(
        config_path=config_path,
        batch_size=10,
        repo_root=tmp_path,
        sync_site=False,
    )

    output_dir = tmp_path / "catalog" / "sustainability"
    assert (output_dir / "raw-discovery.json").exists()
    assert (output_dir / "dedup.json").exists()
    assert (output_dir / "scored.json").exists()
    assert (output_dir / "enriched.json").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "RESULTS.md").exists()
    assert (output_dir / "explorer.html").exists()
    assert (output_dir / "mlco2-codecarbon" / "entry.json").exists()
