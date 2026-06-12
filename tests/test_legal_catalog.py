"""Tests for the legal catalog scaffold and assembly flow."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _load_legal_assembler():
    module_path = ROOT / "catalog" / "legal" / "assemble_catalog.py"
    spec = importlib.util.spec_from_file_location("legal_assemble_catalog", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_legal_config_has_expected_subdomains_and_waves():
    config_path = ROOT / "catalog" / "legal" / "swarm-config.json"

    config = json.loads(config_path.read_text())
    subdomain_ids = [subdomain["id"] for subdomain in config["sub_domains"]]
    wave_ids = [wave["id"] for wave in config["waves"]]

    assert config["topic_slug"] == "legal"
    assert config["output_dir"] == "catalog/legal"
    assert config["discovery_dir"] == "catalog/legal/discovery"
    assert subdomain_ids == [
        "legal-ai-nlp",
        "privacy-data-protection",
        "compliance-regulatory-automation",
        "smart-contracts-legal",
        "contract-analysis-clm",
        "e-discovery-document-review",
        "aml-kyc-identity",
        "legal-research-case-law",
        "legal-document-automation",
        "legal-analytics-prediction",
        "corporate-governance-entity-mgmt",
        "court-case-management",
        "access-to-justice-civic-tech",
        "ip-patent-trademark",
        "legal-knowledge-ontologies",
        "digital-forensics-litigation",
        "tax-compliance-automation",
        "immigration-visa-processing",
        "alternative-dispute-resolution",
        "legal-practice-management",
        "curated-lists-meta-sweep",
    ]
    assert wave_ids == ["wave-1", "wave-2", "wave-3"]
    assert all(len(wave["subdomains"]) == 7 for wave in config["waves"])


def test_legal_enrichment_uses_primary_sub_domain_for_category():
    module = _load_legal_assembler()

    entry = {
        "repo_url": "https://github.com/jhpyle/docassemble",
        "name": "jhpyle/docassemble",
        "description": "Open-source platform for guided interviews, form assembly, and legal workflow automation.",
        "sub_domain": "legal-document-automation",
        "found_in_domains": ["legal-document-automation", "access-to-justice-civic-tech"],
        "score": 10,
    }
    domain_name_by_id = {
        "legal-document-automation": "Legal Document Automation",
        "access-to-justice-civic-tech": "Access to Justice / Civic Tech",
    }

    enriched = module.enrich_entries([entry], domain_name_by_id)

    assert enriched[0]["category"] == "Legal Document Automation"
    assert enriched[0]["summary"]
    assert "document-automation" in enriched[0]["tags"]


def test_legal_build_catalog_writes_expected_artifacts(tmp_path):
    module = _load_legal_assembler()

    config_path = tmp_path / "catalog" / "legal" / "swarm-config.json"
    discovery_dir = tmp_path / "catalog" / "legal" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "legal-document-automation.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/jhpyle/docassemble",
                    "name": "jhpyle/docassemble",
                    "description": "Open-source platform for guided interviews and legal form assembly.",
                    "sub_domain": "legal-document-automation",
                    "score": 10,
                    "score_rationale": "Canonical legal document automation framework.",
                    "stars": 1900,
                    "language": "Python",
                    "license": "MIT",
                    "last_activity": "2026-03-25",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Legal Test Catalog",
                "topic_slug": "legal",
                "output_dir": "catalog/legal",
                "discovery_dir": "catalog/legal/discovery",
                "sub_domains": [
                    {
                        "id": "legal-document-automation",
                        "name": "Legal Document Automation",
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

    output_dir = tmp_path / "catalog" / "legal"
    assert (output_dir / "raw-discovery.json").exists()
    assert (output_dir / "dedup.json").exists()
    assert (output_dir / "scored.json").exists()
    assert (output_dir / "enriched.json").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "RESULTS.md").exists()
    assert (output_dir / "explorer.html").exists()
    assert (output_dir / "jhpyle-docassemble" / "entry.json").exists()
