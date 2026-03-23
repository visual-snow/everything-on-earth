"""Tests for generate_capabilities.py wave orchestration utilities."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from generate_capabilities import slugify, slug_dir, load_catalog, load_progress, save_progress


def test_slugify_basic():
    assert slugify("Containerlab") == "containerlab"


def test_slugify_special_chars():
    assert slugify("Open5GS (Docker)") == "open5gs-docker"


def test_slugify_strips_edges():
    assert slugify("  --hello--  ") == "hello"


def test_slug_dir_creates_directory(tmp_path):
    d = slug_dir(tmp_path, "akvorado")
    assert d == tmp_path / "akvorado"
    assert d.is_dir()


def test_slug_dir_idempotent(tmp_path):
    slug_dir(tmp_path, "akvorado")
    d = slug_dir(tmp_path, "akvorado")
    assert d.is_dir()


def test_load_catalog_adds_slugs(tmp_path):
    catalog = [{"name": "Containerlab"}, {"name": "FAUCET"}]
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))
    entries = load_catalog(catalog_path)
    assert entries[0]["slug"] == "containerlab"
    assert entries[1]["slug"] == "faucet"


def test_load_catalog_resolves_collisions(tmp_path):
    catalog = [{"name": "Tool"}, {"name": "Tool"}]
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))
    entries = load_catalog(catalog_path)
    assert entries[0]["slug"] == "tool"
    assert entries[1]["slug"] == "tool-2"


def test_progress_round_trip(tmp_path):
    progress = {"completed": ["a"], "failed": {"b": "reason"}, "in_progress": ["c"]}
    save_progress(tmp_path, progress)
    loaded = load_progress(tmp_path)
    assert loaded == progress


def test_progress_default(tmp_path):
    loaded = load_progress(tmp_path)
    assert loaded == {"completed": [], "failed": {}, "in_progress": []}
