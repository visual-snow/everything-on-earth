"""Tests for the massive-crawl deterministic pipeline."""

import json
import subprocess
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup, run_score, run_finalize, run_explorer


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


def test_score_removes_empty_url():
    entries = [
        {"repo_url": "", "name": "bad", "description": "No URL", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "good", "description": "Has URL", "score": 5},
    ]
    result, _ = run_score(entries)
    assert len(result) == 1
    assert result[0]["name"] == "good"


def test_score_removes_empty_description():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "no-desc", "description": "", "score": 5},
        {"repo_url": "https://github.com/c/d", "name": "has-desc", "description": "A real tool", "score": 5},
    ]
    result, _ = run_score(entries)
    assert len(result) == 1
    assert result[0]["name"] == "has-desc"


def test_score_attaches_quality_score():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool", "score": 8, "stars": 5000},
    ]
    result, _ = run_score(entries)
    assert len(result) == 1
    assert "quality_score" in result[0]
    assert result[0]["quality_score"] > 0


def test_score_higher_stars_higher_score():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "few", "description": "Few stars", "score": 5, "stars": 10},
        {"repo_url": "https://github.com/c/d", "name": "many", "description": "Many stars", "score": 5, "stars": 10000},
    ]
    result, _ = run_score(entries)
    assert result[1]["quality_score"] > result[0]["quality_score"]


def test_score_logs_removals():
    entries = [
        {"repo_url": "", "name": "no-url", "description": "Missing", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "ok", "description": "OK", "score": 5},
    ]
    _, removed_log = run_score(entries)
    assert len(removed_log) == 1
    assert any("no_url" in log["reason"] for log in removed_log)


# --- Finalize tests ---


def test_finalize_produces_catalog_and_results_only(tmp_path):
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
    assert (tmp_path / "RESULTS.md").exists()
    assert not (tmp_path / "explorer.html").exists()

    catalog = json.loads((tmp_path / "catalog.json").read_text())
    assert len(catalog) == 2
    assert catalog[0]["quality_score"] >= catalog[1]["quality_score"]


def test_explorer_merges_domains(tmp_path):
    """run_explorer scans catalog/*/catalog.json and produces catalog/explorer.html."""
    domain_a = tmp_path / "alpha"
    domain_a.mkdir()
    domain_a_catalog = [
        {
            "repo_url": "https://github.com/a/one",
            "name": "one",
            "description": "Tool 1",
            "quality_score": 80,
            "score": 8,
            "stars": 1000,
            "sub_domain": "sub1",
            "found_in_domains": ["sub1"],
            "tags": ["tag1"],
        },
    ]
    (domain_a / "catalog.json").write_text(json.dumps(domain_a_catalog))

    domain_b = tmp_path / "beta"
    domain_b.mkdir()
    domain_b_catalog = [
        {
            "repo_url": "https://github.com/b/two",
            "name": "two",
            "description": "Tool 2",
            "quality_score": 60,
            "score": 6,
            "stars": 500,
            "sub_domain": "sub2",
            "found_in_domains": ["sub2"],
            "tags": ["tag2"],
        },
    ]
    (domain_b / "catalog.json").write_text(json.dumps(domain_b_catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    explorer_path = tmp_path / "explorer.html"
    assert explorer_path.exists()
    content = explorer_path.read_text()
    assert "alpha" in content
    assert "beta" in content
    assert "one" in content
    assert "two" in content


def test_explorer_injects_domain_field(tmp_path):
    """Each entry gets a 'domain' field matching its folder name."""
    domain = tmp_path / "cybersecurity"
    domain.mkdir()
    catalog = [
        {
            "repo_url": "https://github.com/a/b",
            "name": "tool",
            "description": "A tool",
            "quality_score": 70,
            "score": 7,
            "stars": 100,
            "sub_domain": "sub",
            "found_in_domains": ["sub"],
            "tags": [],
        },
    ]
    (domain / "catalog.json").write_text(json.dumps(catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    assert '"domain":"cybersecurity"' in content or '"domain": "cybersecurity"' in content


def test_explorer_skips_non_catalog_dirs(tmp_path):
    """Directories without catalog.json are silently skipped."""
    empty_dir = tmp_path / "empty-domain"
    empty_dir.mkdir()

    real = tmp_path / "real"
    real.mkdir()
    (real / "catalog.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/x/y",
                    "name": "y",
                    "description": "Y",
                    "quality_score": 50,
                    "score": 5,
                    "stars": 10,
                    "sub_domain": "s",
                    "found_in_domains": ["s"],
                    "tags": [],
                },
            ]
        )
    )

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    assert (tmp_path / "explorer.html").exists()


def test_explorer_sorts_by_quality_score(tmp_path):
    """Merged entries are sorted by quality_score descending."""
    domain = tmp_path / "test"
    domain.mkdir()
    catalog = [
        {
            "repo_url": "https://github.com/a/low",
            "name": "low",
            "description": "Low",
            "quality_score": 20,
            "score": 2,
            "stars": 10,
            "sub_domain": "s",
            "found_in_domains": ["s"],
            "tags": [],
        },
        {
            "repo_url": "https://github.com/a/high",
            "name": "high",
            "description": "High",
            "quality_score": 90,
            "score": 9,
            "stars": 10000,
            "sub_domain": "s",
            "found_in_domains": ["s"],
            "tags": [],
        },
    ]
    (domain / "catalog.json").write_text(json.dumps(catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    assert content.index("high") < content.index("low")


def test_cli_explorer_stage(tmp_path):
    """The --stage explorer --catalog-root flag works end-to-end."""
    domain = tmp_path / "testdomain"
    domain.mkdir()
    (domain / "catalog.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/a/b",
                    "name": "tool",
                    "description": "A tool",
                    "quality_score": 70,
                    "score": 7,
                    "stars": 100,
                    "sub_domain": "sub",
                    "found_in_domains": ["sub"],
                    "tags": ["test"],
                },
            ]
        )
    )

    pipeline_path = Path(__file__).parent.parent / "pipeline" / "pipeline.py"
    result = subprocess.run(
        [sys.executable, str(pipeline_path), "--stage", "explorer", "--catalog-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (tmp_path / "explorer.html").exists()
