"""Tests for the everything-on-earth deterministic pipeline."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup, run_prune, run_enrich, strip_code_fences, run_finalize


def test_normalize_url_lowercase():
    assert normalize_url("https://github.com/Aqua/Trivy") == "https://github.com/aqua/trivy"


def test_normalize_url_strip_trailing_slash():
    assert normalize_url("https://github.com/falco/falco/") == "https://github.com/falco/falco"


def test_normalize_url_strip_git_suffix():
    assert normalize_url("https://github.com/owner/repo.git") == "https://github.com/owner/repo"


def test_normalize_url_all_at_once():
    assert normalize_url("https://github.com/Owner/Repo.git/") == "https://github.com/owner/repo"


def test_dedup_keeps_highest_score():
    entries = [
        {"repo_url": "https://github.com/owner/repo", "name": "a", "score": 5, "sub_domain": "d1"},
        {"repo_url": "https://github.com/Owner/Repo", "name": "b", "score": 9, "sub_domain": "d2"},
        {"repo_url": "https://github.com/owner/repo.git", "name": "c", "score": 3, "sub_domain": "d3"},
    ]
    result = run_dedup(entries)
    assert len(result) == 1
    assert result[0]["score"] == 9
    assert result[0]["found_in_domains"] == ["d1", "d2", "d3"]


def test_dedup_output_not_larger_than_input():
    entries = [
        {"repo_url": f"https://github.com/owner/repo{i}", "name": f"r{i}", "score": i, "sub_domain": "d1"}
        for i in range(10)
    ]
    result = run_dedup(entries)
    assert len(result) <= len(entries)


def test_dedup_preserves_non_duplicates():
    entries = [
        {"repo_url": "https://github.com/a/one", "name": "one", "score": 5, "sub_domain": "d1"},
        {"repo_url": "https://github.com/b/two", "name": "two", "score": 7, "sub_domain": "d2"},
    ]
    result = run_dedup(entries)
    assert len(result) == 2


def test_prune_removes_empty_url():
    entries = [
        {"repo_url": "", "name": "bad", "description": "No URL", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "good", "description": "Has URL", "score": 5},
    ]
    result, pruned_log = run_prune(entries)
    assert len(result) == 1
    assert result[0]["name"] == "good"


def test_prune_removes_empty_description():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "no-desc", "description": "", "score": 5},
        {"repo_url": "https://github.com/c/d", "name": "has-desc", "description": "A real tool", "score": 5},
    ]
    result, pruned_log = run_prune(entries)
    assert len(result) == 1
    assert result[0]["name"] == "has-desc"


def test_prune_min_score():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "low", "description": "Low score", "score": 2},
        {"repo_url": "https://github.com/c/d", "name": "high", "description": "High score", "score": 8},
    ]
    result, _ = run_prune(entries, min_score=5)
    assert len(result) == 1
    assert result[0]["name"] == "high"


def test_prune_min_stars():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "few", "description": "Few stars", "score": 5, "stars": 10},
        {"repo_url": "https://github.com/c/d", "name": "many", "description": "Many stars", "score": 5, "stars": 500},
    ]
    result, _ = run_prune(entries, min_stars=100)
    assert len(result) == 1
    assert result[0]["name"] == "many"


def test_prune_active_since():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "old", "description": "Old repo", "score": 5, "last_activity": "2020-01-01"},
        {"repo_url": "https://github.com/c/d", "name": "new", "description": "New repo", "score": 5, "last_activity": "2025-06-01"},
    ]
    result, _ = run_prune(entries, active_since="2023-01-01")
    assert len(result) == 1
    assert result[0]["name"] == "new"


def test_prune_logs_what_was_removed():
    entries = [
        {"repo_url": "", "name": "no-url", "description": "Missing", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "low-score", "description": "OK", "score": 1},
    ]
    _, pruned_log = run_prune(entries, min_score=3)
    assert len(pruned_log) == 2
    assert any("no_url" in log["reason"] for log in pruned_log)
    assert any("min_score" in log["reason"] for log in pruned_log)


# --- Enrich tests ---

from unittest.mock import patch, MagicMock


def test_strip_code_fences_json():
    raw = '```json\n{"tags": ["security"]}\n```'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_strip_code_fences_plain():
    raw = '```\n{"tags": ["security"]}\n```'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_strip_code_fences_no_fences():
    raw = '{"tags": ["security"]}'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_enrich_preserves_count():
    """Enrichment must NEVER drop entries -- len(output) == len(input)."""
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "tool-a", "description": "A security tool", "score": 8},
        {"repo_url": "https://github.com/c/d", "name": "tool-b", "description": "Another tool", "score": 7},
    ]
    mock_response = {
        "tags": ["kubernetes", "security"],
        "category": "Security Scanning",
        "summary": "A Kubernetes security scanning tool"
    }

    with patch("pipeline.enrich_single") as mock_enrich:
        mock_enrich.return_value = mock_response
        result = run_enrich(entries, topic="K8s Security", max_tokens=1024)

    assert len(result) == len(entries), f"Enrichment dropped entries: {len(result)} != {len(entries)}"
    assert result[0]["tags"] == ["kubernetes", "security"]
    assert result[0]["category"] == "Security Scanning"


# --- Finalize tests ---


def test_finalize_produces_three_outputs(tmp_path):
    entries = [
        {
            "repo_url": "https://github.com/a/b", "name": "a/b", "description": "Tool A",
            "sub_domain": "scanning", "score": 9, "stars": 1000, "language": "Go",
            "license": "MIT", "last_activity": "2025-01-01", "tags": ["security"],
            "category": "Scanning", "summary": "A scanning tool", "found_in_domains": ["scanning"]
        },
        {
            "repo_url": "https://github.com/c/d", "name": "c/d", "description": "Tool B",
            "sub_domain": "policy", "score": 7, "stars": 500, "language": "Python",
            "license": "Apache-2.0", "last_activity": "2025-06-01", "tags": ["policy"],
            "category": "Policy", "summary": "A policy tool", "found_in_domains": ["policy"]
        },
    ]
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_finalize(entries, topic="Test Topic", output_dir=tmp_path, template_dir=template_dir)

    assert (tmp_path / "catalog.json").exists()
    assert (tmp_path / "explorer.html").exists()
    assert (tmp_path / "RESULTS.md").exists()

    catalog = json.loads((tmp_path / "catalog.json").read_text())
    assert len(catalog) == 2
    assert catalog[0]["score"] >= catalog[1]["score"]  # sorted descending
