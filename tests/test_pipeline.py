"""Tests for the everything-on-earth deterministic pipeline."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup


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
