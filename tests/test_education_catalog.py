"""Tests for the education catalog scaffold and assembly flow."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _load_education_assembler():
    module_path = ROOT / "education" / "assemble_catalog.py"
    spec = importlib.util.spec_from_file_location("education_assemble_catalog", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_education_config_has_20_subdomains():
    config_path = ROOT / "education" / "swarm-config.json"

    config = json.loads(config_path.read_text())
    subdomain_ids = [subdomain["id"] for subdomain in config["sub_domains"]]

    assert config["topic_slug"] == "education"
    assert config["output_dir"] == "catalog/education"
    assert config["discovery_dir"] == "education/discovery"
    assert subdomain_ids == [
        "lms",
        "adaptive-learning",
        "assessment-testing",
        "interactive-coding-education",
        "k12-stem",
        "video-lecture-platforms",
        "collaborative-learning",
        "curriculum-authoring",
        "sis",
        "gamification-engagement",
        "language-learning",
        "accessibility-inclusive-education",
        "analytics-learning-dashboards",
        "virtual-labs-simulations",
        "classroom-management",
        "research-academic-publishing",
        "special-education-therapy",
        "credentialing-certification",
        "edtech-infrastructure",
        "ai-teaching-assistants",
    ]


def test_education_enrichment_adds_category_summary_and_tags():
    module = _load_education_assembler()

    enriched = module.enrich_entries(
        [
            {
                "repo_url": "https://github.com/moodle/moodle",
                "name": "moodle/moodle",
                "description": "Open-source learning management system for courses, grading, plugins, and online classrooms.",
                "sub_domain": "lms",
                "found_in_domains": ["lms", "edtech-infrastructure"],
                "score": 10,
                "stars": 1000,
                "language": "PHP",
                "license": "GPL-3.0",
                "last_activity": "2026-01-10"
            }
        ],
        {
            "lms": "Learning Management Systems",
            "edtech-infrastructure": "EdTech Infrastructure"
        },
    )

    entry = enriched[0]
    assert entry["category"] == "Learning Management Systems"
    assert entry["summary"]
    assert "learning" in entry["summary"].lower()
    assert "lms" in entry["tags"]


def test_education_build_catalog_writes_expected_artifacts(tmp_path):
    module = _load_education_assembler()

    config_path = tmp_path / "education" / "swarm-config.json"
    discovery_dir = tmp_path / "education" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "lms.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/moodle/moodle",
                    "name": "moodle/moodle",
                    "description": "Open-source learning management system for courses and grading.",
                    "sub_domain": "lms",
                    "score": 10,
                    "score_rationale": "Canonical OSS LMS.",
                    "stars": 1000,
                    "language": "PHP",
                    "license": "GPL-3.0",
                    "last_activity": "2026-01-10",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Education Test Catalog",
                "topic_slug": "education",
                "output_dir": "catalog/education",
                "discovery_dir": "education/discovery",
                "sub_domains": [
                    {
                        "id": "lms",
                        "name": "Learning Management Systems",
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
        catalog_root=tmp_path / "catalog",
    )

    output_dir = tmp_path / "catalog" / "education"
    assert (output_dir / "raw-discovery.json").exists()
    assert (output_dir / "dedup.json").exists()
    assert (output_dir / "scored.json").exists()
    assert (output_dir / "enriched.json").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "RESULTS.md").exists()
    assert (output_dir / "explorer.html").exists()
    assert (output_dir / "moodle-moodle" / "entry.json").exists()
