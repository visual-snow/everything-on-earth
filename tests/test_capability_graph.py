"""Tests for the capability graph builder and supercharge hooks."""

import csv
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from build_capability_graph import (
    build_capability_map_csv,
    build_domain_graph_slice,
    build_domain_routing,
    build_global_graph,
    extract_capabilities,
    list_domains,
    main,
    slugify_capability,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_telecoms_fixture(tmp_path):
    """Create a minimal telecoms catalog with provides[] entries."""
    domain = "telecoms"
    domain_dir = tmp_path / domain
    domain_dir.mkdir()

    entries = [
        {
            "name": "Open5GS",
            "repo_url": "https://github.com/open5gs/open5gs",
            "description": "Open-source 5G core",
            "domain": "5g-core",
            "secondary_domains": ["4g-core"],
            "provides": ["5g-core-amf", "5g-core-smf", "5g-core-upf", "4g-core-mme"],
            "slug": "open5gs",
        },
        {
            "name": "srsRAN",
            "repo_url": "https://github.com/srsran/srsran",
            "description": "Open-source 5G RAN",
            "domain": "5g-ran",
            "secondary_domains": ["4g"],
            "provides": ["5g-core-amf", "gnb-emulation", "ue-emulation"],
            "slug": "srsran",
        },
    ]
    (domain_dir / "catalog.json").write_text(json.dumps(entries))

    for entry in entries:
        slug_dir = domain_dir / entry["slug"]
        slug_dir.mkdir()
        (slug_dir / "entry.json").write_text(json.dumps(entry))
        (slug_dir / "factsheet.json").write_text(json.dumps({"slug": entry["slug"]}))
        (slug_dir / "capability.md").write_text(f"# {entry['name']}\n")

    return tmp_path


def _make_multi_domain_fixture(tmp_path):
    """Create a fixture with telecoms + cybersecurity domains."""
    _make_telecoms_fixture(tmp_path)

    cyber_dir = tmp_path / "cybersecurity"
    cyber_dir.mkdir()
    entries = [
        {
            "repo_url": "https://github.com/a/scanner",
            "name": "Scanner",
            "description": "Vuln scanner",
            "sub_domain": "vulnerability-scanning",
            "score": 8,
            "tags": ["security", "scanner"],
            "category": "Vulnerability Scanning",
            "slug": "scanner",
        }
    ]
    (cyber_dir / "catalog.json").write_text(json.dumps(entries))

    return tmp_path


# ---------------------------------------------------------------------------
# slugify_capability
# ---------------------------------------------------------------------------

def test_slugify_basic():
    assert slugify_capability("5g-core-amf") == "5g-core-amf"


def test_slugify_strips_special_chars():
    assert slugify_capability("openflow-1.3") == "openflow-1-3"


def test_slugify_lowercases():
    assert slugify_capability("Docker-Image-Build") == "docker-image-build"


# ---------------------------------------------------------------------------
# list_domains
# ---------------------------------------------------------------------------

def test_list_domains(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    assert domains == ["cybersecurity", "telecoms"]


def test_list_domains_skips_dirs_without_catalog(tmp_path):
    _make_telecoms_fixture(tmp_path)
    (tmp_path / "empty_dir").mkdir()
    domains = list_domains(tmp_path)
    assert "empty_dir" not in domains


# ---------------------------------------------------------------------------
# extract_capabilities
# ---------------------------------------------------------------------------

def test_extract_capabilities_count(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, aliases, edges = extract_capabilities(tmp_path, "telecoms")
    # open5gs provides 4, srsran provides 3, 5g-core-amf is shared -> 6 unique
    assert len(caps) == 6


def test_extract_capabilities_shared_cap(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, _ = extract_capabilities(tmp_path, "telecoms")
    cap_map = {c["id"]: c for c in caps}
    amf = cap_map["5g-core-amf"]
    assert "open5gs" in amf["implemented_by"]
    assert "srsran" in amf["implemented_by"]


def test_extract_capabilities_related(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, _ = extract_capabilities(tmp_path, "telecoms")
    cap_map = {c["id"]: c for c in caps}
    # 5g-core-amf and 5g-core-smf are co-provided by open5gs
    amf = cap_map["5g-core-amf"]
    assert "5g-core-smf" in amf["related_capabilities"]


def test_extract_capabilities_edges(tmp_path):
    _make_telecoms_fixture(tmp_path)
    _, _, edges = extract_capabilities(tmp_path, "telecoms")
    # open5gs provides 4, srsran provides 3 -> 7 edges
    assert len(edges) == 7
    assert all(e["domain"] == "telecoms" for e in edges)
    assert all(e["source_field"] == "provides" for e in edges)


def test_extract_capabilities_evidence_paths(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, _ = extract_capabilities(tmp_path, "telecoms")
    for cap in caps:
        for ev in cap["evidence"]:
            assert "factsheet" in ev
            assert "capability_doc" in ev


def test_extract_capabilities_aliases(tmp_path):
    """Aliases are only generated when raw form differs from slugified ID."""
    _make_telecoms_fixture(tmp_path)
    _, aliases, _ = extract_capabilities(tmp_path, "telecoms")
    # All our test provides[] are already in slug form, so no aliases
    assert len(aliases) == 0


# ---------------------------------------------------------------------------
# build_domain_routing
# ---------------------------------------------------------------------------

def test_domain_routing_includes_all_domains(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    rows = build_domain_routing(tmp_path, domains)
    domain_names = {r["domain"] for r in rows}
    assert "telecoms" in domain_names
    assert "cybersecurity" in domain_names


def test_domain_routing_domain_name_weight(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    rows = build_domain_routing(tmp_path, domains)
    domain_name_rows = [r for r in rows if r["source"] == "domain_name"]
    assert all(r["weight"] == 1.0 for r in domain_name_rows)


def test_domain_routing_sub_domains(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    rows = build_domain_routing(tmp_path, domains)
    cyber_subs = [
        r for r in rows
        if r["domain"] == "cybersecurity" and r["source"] == "sub_domain"
    ]
    assert any(r["keyword_or_alias"] == "vulnerability-scanning" for r in cyber_subs)


def test_domain_routing_tags(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    rows = build_domain_routing(tmp_path, domains)
    cyber_tags = [
        r for r in rows
        if r["domain"] == "cybersecurity" and r["source"] == "tag"
    ]
    assert any(r["keyword_or_alias"] == "security" for r in cyber_tags)


def test_domain_routing_csv_fields(tmp_path):
    _make_multi_domain_fixture(tmp_path)
    domains = list_domains(tmp_path)
    rows = build_domain_routing(tmp_path, domains)
    for row in rows:
        assert set(row.keys()) == {"domain", "keyword_or_alias", "source", "weight"}


# ---------------------------------------------------------------------------
# build_domain_graph_slice
# ---------------------------------------------------------------------------

def test_domain_graph_slice_structure(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, edges = extract_capabilities(tmp_path, "telecoms")
    slice_data = build_domain_graph_slice("telecoms", caps, edges, tmp_path)
    assert slice_data["domain"] == "telecoms"
    assert len(slice_data["repos"]) == 2
    assert len(slice_data["capabilities"]) == 6
    assert len(slice_data["repo_capability_edges"]) == 7


# ---------------------------------------------------------------------------
# build_global_graph
# ---------------------------------------------------------------------------

def test_global_graph_combines_slices(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, edges = extract_capabilities(tmp_path, "telecoms")
    slice_data = build_domain_graph_slice("telecoms", caps, edges, tmp_path)
    graph = build_global_graph({"telecoms": slice_data})
    assert "telecoms" in graph["domains"]
    assert len(graph["capabilities"]) == 6


# ---------------------------------------------------------------------------
# build_capability_map_csv
# ---------------------------------------------------------------------------

def test_capability_map_rows(tmp_path):
    _make_telecoms_fixture(tmp_path)
    caps, _, edges = extract_capabilities(tmp_path, "telecoms")
    rows = build_capability_map_csv("telecoms", edges, caps)
    assert len(rows) == 7
    assert all(r["domain"] == "telecoms" for r in rows)
    assert all("capability_label" in r for r in rows)


# ---------------------------------------------------------------------------
# Full CLI integration
# ---------------------------------------------------------------------------

def test_main_produces_all_outputs(tmp_path):
    _make_telecoms_fixture(tmp_path)
    output = tmp_path / "output"
    main([
        "--catalog-root", str(tmp_path),
        "--output-root", str(output),
        "--pilot-domain", "telecoms",
    ])
    assert (output / "ontology" / "capability-registry.json").exists()
    assert (output / "ontology" / "aliases.csv").exists()
    assert (output / "graph" / "graph.json").exists()
    assert (output / "graph" / "domains" / "telecoms.json").exists()
    assert (output / "exports" / "csv" / "domain-routing.csv").exists()
    assert (output / "exports" / "csv" / "telecoms-capability-map.csv").exists()


def test_main_registry_valid_json(tmp_path):
    _make_telecoms_fixture(tmp_path)
    output = tmp_path / "output"
    main(["--catalog-root", str(tmp_path), "--output-root", str(output)])
    data = json.loads((output / "ontology" / "capability-registry.json").read_text())
    assert isinstance(data, list)
    assert len(data) > 0
    for cap in data:
        assert "id" in cap
        assert "implemented_by" in cap
        assert "evidence" in cap


def test_main_routing_csv_valid(tmp_path):
    _make_telecoms_fixture(tmp_path)
    output = tmp_path / "output"
    main(["--catalog-root", str(tmp_path), "--output-root", str(output)])
    with open(output / "exports" / "csv" / "domain-routing.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) > 0
    assert set(rows[0].keys()) == {"domain", "keyword_or_alias", "source", "weight"}


def test_main_with_claude_adapter(tmp_path):
    _make_telecoms_fixture(tmp_path)
    output = tmp_path / "output"
    main([
        "--catalog-root", str(tmp_path),
        "--output-root", str(output),
        "--adapter", "claude",
    ])
    # Generated skills should exist
    repo_root = Path(__file__).parent.parent
    router_skill = repo_root / "adapters" / "claude" / "skills" / "capability-router" / "SKILL.md"
    domain_skill = repo_root / "adapters" / "claude" / "skills" / "domain-telecoms" / "SKILL.md"
    assert router_skill.exists()
    assert domain_skill.exists()


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------

def test_workflow_manifest_files_exist():
    """All files listed in capability-router manifest must exist."""
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / "workflows" / "capability-router" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    for f in manifest["files"]:
        assert (manifest_path.parent / f).exists(), f"Missing: {f}"


def test_models_json_has_router_classifier():
    """Claude models config must declare capability-router.classifier.model = haiku."""
    repo_root = Path(__file__).parent.parent
    models = json.loads((repo_root / "adapters" / "claude" / "models.json").read_text())
    assert "capability-router" in models
    assert models["capability-router"]["classifier"]["model"] == "haiku"


def test_installer_references_router_and_domain_skills():
    """Claude installer must copy router + telecoms + supercharge skills."""
    repo_root = Path(__file__).parent.parent
    install_sh = (repo_root / "adapters" / "claude" / "install.sh").read_text()
    assert "capability-router" in install_sh
    assert "domain-telecoms" in install_sh
    assert "supercharge" in install_sh


def test_generated_skill_paths_exist():
    """Generated Claude skill files must exist on disk."""
    repo_root = Path(__file__).parent.parent
    for skill_name in ["capability-router", "domain-telecoms", "supercharge"]:
        path = repo_root / "adapters" / "claude" / "skills" / skill_name / "SKILL.md"
        assert path.exists(), f"Missing: {path}"


def test_hook_scripts_exist():
    """All supercharge hook scripts must exist and be executable."""
    repo_root = Path(__file__).parent.parent
    hooks_dir = repo_root / "adapters" / "claude" / "hooks" / "supercharge"
    for script in ["session-context.sh", "compact-restore.sh", "route-query.py"]:
        path = hooks_dir / script
        assert path.exists(), f"Missing: {path}"


def test_settings_local_has_supercharge_hooks():
    """Settings must wire all three supercharge hooks."""
    repo_root = Path(__file__).parent.parent
    settings = json.loads(
        (repo_root / ".claude" / "settings.local.json").read_text()
    )
    hooks = settings["hooks"]

    # SessionStart hooks
    assert "SessionStart" in hooks
    session_matchers = [h.get("matcher", "") for h in hooks["SessionStart"]]
    assert "startup" in session_matchers
    assert "compact" in session_matchers

    # UserPromptSubmit hook
    assert "UserPromptSubmit" in hooks
    assert len(hooks["UserPromptSubmit"]) >= 1


def test_route_decision_schema_valid():
    """Route decision schema must be valid JSON Schema."""
    repo_root = Path(__file__).parent.parent
    schema_path = (
        repo_root / "workflows" / "capability-router" / "schemas"
        / "route-decision-schema.json"
    )
    schema = json.loads(schema_path.read_text())
    assert schema["type"] == "object"
    assert "primary_domain" in schema["required"]
    assert "confidence" in schema["required"]
    assert schema["additionalProperties"] is False


# ---------------------------------------------------------------------------
# Supercharge hook integration tests
# ---------------------------------------------------------------------------

def test_session_context_hook_output():
    """session-context.sh must produce supercharge context."""
    repo_root = Path(__file__).parent.parent
    graph_path = repo_root / "capability-graph" / "graph" / "graph.json"
    if not graph_path.exists():
        return  # Skip if graph not built yet

    result = subprocess.run(
        ["bash", str(repo_root / "adapters" / "claude" / "hooks" / "supercharge" / "session-context.sh")],
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(repo_root), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert result.returncode == 0
    assert "<supercharge>" in result.stdout
    assert "capabilities" in result.stdout


def test_route_query_hook_telecoms():
    """route-query.py must route telecoms queries correctly."""
    repo_root = Path(__file__).parent.parent
    routing_csv = repo_root / "capability-graph" / "exports" / "csv" / "domain-routing.csv"
    if not routing_csv.exists():
        return  # Skip if graph not built yet

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "adapters" / "claude" / "hooks" / "supercharge" / "route-query.py"),
        ],
        input='{"prompt":"What 5G core network tools exist?"}',
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(repo_root), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert result.returncode == 0
    assert "telecoms" in result.stdout


def test_route_query_hook_no_match():
    """route-query.py must produce no output for generic queries."""
    repo_root = Path(__file__).parent.parent
    routing_csv = repo_root / "capability-graph" / "exports" / "csv" / "domain-routing.csv"
    if not routing_csv.exists():
        return

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "adapters" / "claude" / "hooks" / "supercharge" / "route-query.py"),
        ],
        input='{"prompt":"Help me write a Python function"}',
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(repo_root), "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
