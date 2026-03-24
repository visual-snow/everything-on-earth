"""Tests for the massive-crawl deterministic pipeline."""

import json
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup, run_score, run_finalize, compute_edges, run_site


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
    by_name = {r["name"]: r for r in result}
    assert by_name["many"]["quality_score"] > by_name["few"]["quality_score"]


def test_score_logs_removals():
    entries = [
        {"repo_url": "", "name": "no-url", "description": "Missing", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "ok", "description": "OK", "score": 5},
    ]
    _, removed_log = run_score(entries)
    assert len(removed_log) == 1
    assert any("no_url" in log["reason"] for log in removed_log)


# --- Finalize tests ---


def test_finalize_produces_catalog_and_results(tmp_path):
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


# --- Edge computation tests ---


def test_compute_edges_shared_subdomain():
    entries = [
        {"slug": "a", "found_in_domains": ["network"], "tags": ["x"]},
        {"slug": "b", "found_in_domains": ["network"], "tags": ["y"]},
        {"slug": "c", "found_in_domains": ["web"], "tags": ["z"]},
    ]
    edges = compute_edges(entries)
    pairs = {frozenset((e["source"], e["target"])) for e in edges}
    assert frozenset(("a", "b")) in pairs
    assert frozenset(("a", "c")) not in pairs


def test_compute_edges_shared_tags():
    entries = [
        {"slug": "a", "found_in_domains": ["d1"], "tags": ["x", "y"]},
        {"slug": "b", "found_in_domains": ["d2"], "tags": ["x", "y"]},
        {"slug": "c", "found_in_domains": ["d3"], "tags": ["x"]},
    ]
    edges = compute_edges(entries)
    pairs = {frozenset((e["source"], e["target"])) for e in edges}
    assert frozenset(("a", "b")) in pairs
    assert frozenset(("a", "c")) not in pairs


def test_compute_edges_dedup():
    entries = [
        {"slug": "a", "found_in_domains": ["net"], "tags": ["x", "y"]},
        {"slug": "b", "found_in_domains": ["net"], "tags": ["x", "y"]},
    ]
    edges = compute_edges(entries)
    assert len(edges) == 1


def test_compute_edges_empty():
    assert compute_edges([]) == []


# --- Site generation tests ---


def _make_catalog(tmp_path, domain, entries):
    """Helper: write a catalog.json for testing."""
    domain_dir = tmp_path / "catalog" / domain
    domain_dir.mkdir(parents=True)
    (domain_dir / "catalog.json").write_text(json.dumps(entries))
    return domain_dir


SAMPLE_ENTRIES = [
    {
        "repo_url": "https://github.com/a/tool1", "name": "a/tool1",
        "description": "First tool", "sub_domain": "scan",
        "score": 9, "quality_score": 85, "stars": 1000,
        "language": "Go", "license": "MIT", "tags": ["sec", "scan"],
        "found_in_domains": ["scan"],
    },
    {
        "repo_url": "https://github.com/b/tool2", "name": "b/tool2",
        "description": "Second tool", "sub_domain": "scan",
        "score": 7, "quality_score": 55, "stars": 500,
        "language": "Python", "license": "Apache-2.0", "tags": ["sec", "scan"],
        "found_in_domains": ["scan"],
    },
]


def test_site_generates_landing(tmp_path):
    _make_catalog(tmp_path, "test-domain", SAMPLE_ENTRIES)
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir)

    landing = tmp_path / "index.html"
    assert landing.exists()
    content = landing.read_text()
    assert "Everything on Earth" in content
    assert "Test Domain" in content


def test_site_generates_graph_page(tmp_path):
    _make_catalog(tmp_path, "mydom", SAMPLE_ENTRIES)
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir)

    graph = tmp_path / "catalog" / "mydom" / "index.html"
    assert graph.exists()
    content = graph.read_text()
    assert "force-graph" in content
    assert "EDGES" in content


def test_site_generates_detail_pages(tmp_path):
    _make_catalog(tmp_path, "mydom", SAMPLE_ENTRIES)
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir)

    detail_dir = tmp_path / "catalog" / "mydom" / "detail"
    assert detail_dir.exists()
    files = list(detail_dir.glob("*.html"))
    assert len(files) == 2


def test_site_reads_capability_md(tmp_path):
    _make_catalog(tmp_path, "mydom", SAMPLE_ENTRIES[:1])
    cap_dir = tmp_path / "caps" / "mydom" / "a-tool1"
    cap_dir.mkdir(parents=True)
    (cap_dir / "capability.md").write_text("# Tool1 Capabilities\n\nDoes great things.")

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir, capability_root=tmp_path / "caps")

    detail = (tmp_path / "catalog" / "mydom" / "detail" / "a-tool1.html").read_text()
    assert "capability-md" in detail
    assert "Tool1 Capabilities" in detail


def test_site_fallback_no_capability(tmp_path):
    _make_catalog(tmp_path, "mydom", SAMPLE_ENTRIES[:1])
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir)

    detail = (tmp_path / "catalog" / "mydom" / "detail" / "a-tool1.html").read_text()
    assert "First tool" in detail
    assert "capability-md" not in detail
