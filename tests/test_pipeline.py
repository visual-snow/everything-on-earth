"""Tests for the massive-crawl deterministic pipeline."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup, run_score, run_enrich, strip_code_fences, run_finalize


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


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_removes_empty_url(MockClient, mock_fetch):
    entries = [
        {"repo_url": "", "name": "bad", "description": "No URL", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "good", "description": "Has URL", "score": 5},
    ]
    mock_fetch.return_value = _mock_signals()
    result, removed_log = run_score(entries)
    assert len(result) == 1
    assert result[0]["name"] == "good"


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_removes_empty_description(MockClient, mock_fetch):
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "no-desc", "description": "", "score": 5},
        {"repo_url": "https://github.com/c/d", "name": "has-desc", "description": "A real tool", "score": 5},
    ]
    mock_fetch.return_value = _mock_signals()
    result, removed_log = run_score(entries)
    assert len(result) == 1
    assert result[0]["name"] == "has-desc"


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_removes_404_repos(MockClient, mock_fetch):
    entries = [
        {"repo_url": "https://github.com/a/deleted", "name": "gone", "description": "Deleted repo", "score": 5},
        {"repo_url": "https://github.com/c/d", "name": "alive", "description": "Active repo", "score": 5},
    ]
    mock_fetch.side_effect = [None, _mock_signals()]
    result, removed_log = run_score(entries)
    assert len(result) == 1
    assert result[0]["name"] == "alive"
    assert any("github_404" in log["reason"] for log in removed_log)


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_removes_blank_repos(MockClient, mock_fetch):
    entries = [
        {"repo_url": "https://github.com/a/blank", "name": "blank", "description": "Blank repo", "score": 5},
    ]
    mock_fetch.return_value = _mock_signals(has_readme=False, size_kb=5)
    result, removed_log = run_score(entries)
    assert len(result) == 0
    assert any("blank_repo" in log["reason"] for log in removed_log)


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_removes_unmodified_forks(MockClient, mock_fetch):
    entries = [
        {"repo_url": "https://github.com/a/fork", "name": "fork", "description": "A fork", "score": 5},
    ]
    mock_fetch.return_value = _mock_signals(is_fork=True, stars=0, forks=0)
    result, removed_log = run_score(entries)
    assert len(result) == 0
    assert any("unmodified_fork" in log["reason"] for log in removed_log)


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_attaches_quality_score(MockClient, mock_fetch):
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool", "score": 8},
    ]
    mock_fetch.return_value = _mock_signals(stars=5000)
    result, _ = run_score(entries)
    assert len(result) == 1
    assert "quality_score" in result[0]
    assert "discovery_score" in result[0]
    assert result[0]["discovery_score"] == 8
    assert 0 <= result[0]["quality_score"] <= 100


@patch("github_signals.fetch_signals")
@patch("github_signals.GitHubClient")
def test_score_logs_removals(MockClient, mock_fetch):
    entries = [
        {"repo_url": "", "name": "no-url", "description": "Missing", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "ok", "description": "OK", "score": 5},
    ]
    mock_fetch.return_value = _mock_signals()
    _, removed_log = run_score(entries)
    assert len(removed_log) == 1
    assert any("no_url" in log["reason"] for log in removed_log)


def _mock_signals(**overrides) -> dict:
    defaults = {
        "stars": 100, "forks": 20, "open_issues": 10, "subscribers": 30,
        "contributors": 5, "releases": 3, "last_push": "2025-06-01T00:00:00Z",
        "license_spdx": "MIT", "has_readme": True, "has_wiki": False,
        "has_pages": False, "is_fork": False, "size_kb": 5000,
        "archived": False, "created_at": "2022-01-01T00:00:00Z", "commit_count": None,
    }
    defaults.update(overrides)
    return defaults


# --- Enrich tests ---


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
            "sub_domain": "scanning", "score": 9, "quality_score": 85.2, "discovery_score": 9,
            "stars": 1000, "language": "Go",
            "license": "MIT", "last_activity": "2025-01-01", "tags": ["security"],
            "category": "Scanning", "summary": "A scanning tool", "found_in_domains": ["scanning"]
        },
        {
            "repo_url": "https://github.com/c/d", "name": "c/d", "description": "Tool B",
            "sub_domain": "policy", "score": 7, "quality_score": 52.1, "discovery_score": 7,
            "stars": 500, "language": "Python",
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
    assert catalog[0]["quality_score"] >= catalog[1]["quality_score"]  # sorted descending
