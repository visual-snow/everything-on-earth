"""Tests for syncing domain catalogs into folder-per-framework layout."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from sync_catalog_layout import sync_repo_catalogs


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def test_sync_repo_catalogs_imports_telecom_and_keeps_use_cases_in_json(tmp_path):
    repo_root = tmp_path / "repo"
    task_designer_root = tmp_path / "task-designer"

    telecom_catalog = [
        {
            "name": "Containerlab",
            "repo_url": "https://github.com/srl-labs/containerlab",
            "description": "Network lab orchestration",
            "domain": "network-lab-orchestration",
            "secondary_domains": ["multi-vendor-nos", "topology-management"],
            "protocols": ["BGP"],
            "provides": ["network-lab-orchestration"],
            "needs": ["docker-engine"],
            "docker_support": {"has_dockerfile": True, "has_compose": False},
            "github_metrics": {"stars": 2500},
            "eval_potential_score": 9,
            "eval_notes": "Useful for telecom labs",
            "related_repos": [],
            "_sources": ["discovery/labs.json"],
        }
    ]
    write_json(task_designer_root / "data" / "catalog.json", telecom_catalog)
    source_slug_dir = task_designer_root / "data" / "sandbox_capabilities" / "containerlab"
    write_json(source_slug_dir / "entry.json", telecom_catalog[0])
    write_json(source_slug_dir / "factsheet.json", {"what_it_is": "Container-based network labs"})
    source_slug_dir.mkdir(parents=True, exist_ok=True)
    (source_slug_dir / "capability.md").write_text("# Containerlab\n")

    write_json(repo_root / "catalog" / "gaming" / "catalog.json", [])
    write_json(repo_root / "catalog" / "cybersecurity" / "catalog.json", [])

    sync_repo_catalogs(repo_root=repo_root, task_designer_root=task_designer_root)

    telecom_catalog_path = repo_root / "catalog" / "telecoms" / "catalog.json"
    assert telecom_catalog_path.exists()

    synced_catalog = json.loads(telecom_catalog_path.read_text())
    assert synced_catalog[0]["slug"] == "containerlab"
    assert synced_catalog[0]["use_cases"] == [
        "network-lab-orchestration",
        "multi-vendor-nos",
        "topology-management",
    ]

    telecom_framework_dir = repo_root / "catalog" / "telecoms" / "containerlab"
    assert (telecom_framework_dir / "entry.json").exists()
    assert (telecom_framework_dir / "factsheet.json").exists()
    assert (telecom_framework_dir / "capability.md").exists()
    assert not (repo_root / "catalog" / "telecoms" / "network-lab-orchestration").exists()


def test_sync_repo_catalogs_seeds_entry_json_for_existing_domains_and_preserves_other_files(tmp_path):
    repo_root = tmp_path / "repo"
    task_designer_root = tmp_path / "task-designer"

    write_json(task_designer_root / "data" / "catalog.json", [])

    gaming_entry = {
        "name": "Godot",
        "repo_url": "https://github.com/godotengine/godot",
        "description": "Game engine",
        "sub_domain": "game-engines-3d",
        "score": 10,
    }
    write_json(repo_root / "catalog" / "gaming" / "catalog.json", [gaming_entry])
    discovery_file = repo_root / "catalog" / "gaming" / "discovery" / "game-engines-3d.json"
    discovery_file.parent.mkdir(parents=True, exist_ok=True)
    discovery_file.write_text("{}")
    write_json(repo_root / "catalog" / "cybersecurity" / "catalog.json", [])

    sync_repo_catalogs(repo_root=repo_root, task_designer_root=task_designer_root)

    seeded_entry_path = repo_root / "catalog" / "gaming" / "godot" / "entry.json"
    assert seeded_entry_path.exists()
    seeded_entry = json.loads(seeded_entry_path.read_text())
    assert seeded_entry["name"] == "Godot"
    assert seeded_entry["slug"] == "godot"
    assert discovery_file.exists()

    gaming_catalog = json.loads((repo_root / "catalog" / "gaming" / "catalog.json").read_text())
    assert gaming_catalog[0]["slug"] == "godot"


def test_sync_repo_catalogs_resolves_slug_collisions_with_numeric_suffixes(tmp_path):
    repo_root = tmp_path / "repo"
    task_designer_root = tmp_path / "task-designer"

    write_json(task_designer_root / "data" / "catalog.json", [])
    duplicate_entries = [
        {
            "name": "InQuest/awesome-yara",
            "repo_url": "https://github.com/InQuest/awesome-yara",
            "description": "YARA resources",
            "sub_domain": "yara",
            "score": 9,
        },
        {
            "name": "InQuest/awesome-yara",
            "repo_url": "https://github.com/InQuest/awesome-yara-2",
            "description": "Another YARA resource entry",
            "sub_domain": "yara",
            "score": 8,
        },
    ]
    write_json(repo_root / "catalog" / "cybersecurity" / "catalog.json", duplicate_entries)
    write_json(repo_root / "catalog" / "gaming" / "catalog.json", [])

    sync_repo_catalogs(repo_root=repo_root, task_designer_root=task_designer_root)

    synced_catalog = json.loads((repo_root / "catalog" / "cybersecurity" / "catalog.json").read_text())
    assert [entry["slug"] for entry in synced_catalog] == [
        "inquest-awesome-yara",
        "inquest-awesome-yara-2",
    ]
    assert (repo_root / "catalog" / "cybersecurity" / "inquest-awesome-yara" / "entry.json").exists()
    assert (repo_root / "catalog" / "cybersecurity" / "inquest-awesome-yara-2" / "entry.json").exists()
