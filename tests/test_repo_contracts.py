"""Repository-level contract tests for workflow/adapters layout."""

import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_massive_crawl_runtime_contract_matches_current_workflow():
    runtime_path = ROOT / "workflows" / "massive-crawl" / "runtime.json"
    runtime = json.loads(runtime_path.read_text())

    assert runtime["stages"] == [
        "brainstorm",
        "discover",
        "dedup",
        "score",
        "enrich",
        "finalize",
        "gap_review",
    ]
    assert runtime["roles"] == ["scout", "discoverer", "enricher"]
    assert runtime["artifacts"]["scored"] == "scored.json"
    assert runtime["artifacts"]["enriched"] == "enriched.json"
    assert runtime["invariants"]["enrichment_preserves_count"] is True
    assert runtime["invariants"]["enrichment_preserves_order"] is True


def test_workflow_manifests_only_reference_existing_files():
    workflow_dirs = [ROOT / "workflows" / "massive-crawl", ROOT / "workflows" / "map-capabilities"]

    for workflow_dir in workflow_dirs:
        manifest = json.loads((workflow_dir / "manifest.json").read_text())
        for rel_path in manifest["files"]:
            assert (workflow_dir / rel_path).exists(), f"missing {workflow_dir / rel_path}"


def test_codex_enricher_default_mapping_is_declared():
    models_path = ROOT / "adapters" / "codex" / "models.json"
    models = json.loads(models_path.read_text())

    enricher = models["massive-crawl"]["enricher"]
    assert enricher["model"] == "gpt-5.4-mini"
    assert enricher["reasoning_effort"] == "medium"
    assert enricher["allow_override"] is True
