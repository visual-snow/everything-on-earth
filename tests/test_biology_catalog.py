"""Tests for the biology catalog scaffold and assembly flow."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _load_biology_assembler():
    module_path = ROOT / "catalog" / "biology" / "assemble_catalog.py"
    spec = importlib.util.spec_from_file_location("biology_assemble_catalog", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_biology_config_has_expected_subdomains_and_wave_sweeps():
    config_path = ROOT / "catalog" / "biology" / "swarm-config.json"

    config = json.loads(config_path.read_text())
    subdomain_ids = [subdomain["id"] for subdomain in config["sub_domains"]]

    assert config["topic_slug"] == "biology"
    assert config["output_dir"] == "catalog/biology"
    assert config["discovery_dir"] == "catalog/biology/discovery"
    assert subdomain_ids[:27] == [
        "genomics",
        "transcriptomics",
        "proteomics",
        "metabolomics",
        "epigenomics",
        "metagenomics",
        "structural-biology",
        "bioinformatics-pipelines",
        "systems-biology",
        "phylogenetics",
        "computational-neuroscience",
        "cheminformatics",
        "ecology-conservation",
        "marine-biology",
        "climate-biology",
        "biodiversity-informatics",
        "biomedical-imaging",
        "clinical-genomics",
        "immunoinformatics",
        "synthetic-biology",
        "epidemiology-disease-modeling",
        "long-read-sequencing",
        "spatial-omics",
        "agricultural-biology-agtech",
        "protein-engineering-directed-evolution",
        "connectomics",
        "ancient-dna-paleogenomics",
    ]
    assert subdomain_ids[27:] == [
        "curated-lists-meta-sweep",
        "ecology-ocean-agtech-gap-sweep",
        "neuro-imaging-niche-gap-sweep",
    ]


def test_biology_enrichment_uses_primary_sub_domain_for_category():
    module = _load_biology_assembler()

    entry = {
        "repo_url": "https://github.com/broadinstitute/gatk",
        "name": "broadinstitute/gatk",
        "description": "Genome analysis toolkit for variant discovery and genotyping workflows.",
        "sub_domain": "clinical-genomics",
        "found_in_domains": ["genomics", "clinical-genomics"],
        "score": 10,
    }
    domain_name_by_id = {
        "genomics": "Genomics",
        "clinical-genomics": "Clinical Genomics",
    }

    enriched = module.enrich_entries([entry], domain_name_by_id)

    assert enriched[0]["category"] == "Clinical Genomics"
    assert enriched[0]["summary"]
    assert "genomics" in enriched[0]["tags"]


def test_biology_build_catalog_writes_expected_artifacts(tmp_path):
    module = _load_biology_assembler()

    config_path = tmp_path / "catalog" / "biology" / "swarm-config.json"
    discovery_dir = tmp_path / "catalog" / "biology" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "genomics.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/broadinstitute/gatk",
                    "name": "broadinstitute/gatk",
                    "description": "Genome analysis toolkit for variant discovery and genotyping.",
                    "sub_domain": "genomics",
                    "score": 10,
                    "score_rationale": "Canonical genomics toolkit.",
                    "stars": 5000,
                    "language": "Java",
                    "license": "BSD-3-Clause",
                    "last_activity": "2026-03-01",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Biology Test Catalog",
                "topic_slug": "biology",
                "output_dir": "catalog/biology",
                "discovery_dir": "catalog/biology/discovery",
                "sub_domains": [
                    {
                        "id": "genomics",
                        "name": "Genomics",
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

    output_dir = tmp_path / "catalog" / "biology"
    assert (output_dir / "raw-discovery.json").exists()
    assert (output_dir / "dedup.json").exists()
    assert (output_dir / "scored.json").exists()
    assert (output_dir / "enriched.json").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "RESULTS.md").exists()
    assert (output_dir / "explorer.html").exists()
    assert (output_dir / "broadinstitute-gatk" / "entry.json").exists()
