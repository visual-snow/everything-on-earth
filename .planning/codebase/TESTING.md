# Testing Patterns

**Analysis Date:** 2026-03-27

## Test Framework

**Runner:** pytest 9.0.2 (Python 3.14)

**Config:** No `pytest.ini`, `setup.cfg`, or `pyproject.toml`. pytest discovers tests automatically from the `tests/` directory.

**Dependencies:** pytest is the only test dependency. All tests use stdlib assertions (`assert`). No third-party assertion libraries, no coverage tooling configured.

**Run commands:**
```bash
python3 -m pytest                   # Run all tests
python3 -m pytest tests/test_pipeline.py   # Run one module
python3 -m pytest -k test_dedup     # Run tests matching a name pattern
python3 -m pytest --collect-only    # List all collected tests without running
```

**Total tests collected:** 111 as of 2026-03-27.

## Test File Locations and Naming

All test files live in `tests/` at the project root. No co-located tests alongside source files.

**Naming convention:** `test_<module_or_domain_name>.py`

| Test file | What it covers |
|---|---|
| `tests/test_pipeline.py` | `pipeline/pipeline.py` — dedup, score, finalize, compute_edges, run_site |
| `tests/test_capability_graph.py` | `pipeline/build_capability_graph.py` + contract/adapter integration |
| `tests/test_generate_capabilities.py` | `pipeline/generate_capabilities.py` — slugify, slug_dir, load_catalog, progress |
| `tests/test_discover_candidates.py` | `pipeline/discover_candidates.py` — URL normalization, scoring, entry building |
| `tests/test_sync_catalog_layout.py` | `pipeline/sync_catalog_layout.py` — layout sync, slug collision resolution |
| `tests/test_repo_contracts.py` | Cross-cutting contracts: workflow files, adapter hooks, installers, settings |
| `tests/test_biology_catalog.py` | `catalog/biology/assemble_catalog.py` |
| `tests/test_fintech_catalog.py` | `catalog/fintech/assemble_catalog.py` |
| `tests/test_education_catalog.py` | `catalog/education/assemble_catalog.py` (inferred from collection) |
| `tests/test_healthcare_assemble_catalog.py` | `catalog/healthcare/assemble_catalog.py` |
| `tests/test_legal_catalog.py` | `catalog/legal/assemble_catalog.py` |
| `tests/test_sustainability_catalog.py` | `catalog/sustainability/assemble_catalog.py` |

**Fixtures directory:** `tests/fixtures/` contains static JSON files used as test data inputs (`raw-discovery.json`, `swarm-config-test.json`).

## Import Pattern for Pipeline Modules

Pipeline modules are not installed packages. Every test file that imports from `pipeline/` uses `sys.path.insert`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from pipeline import run_dedup, run_score
```

For catalog assemblers, either the same pattern is used against `catalog/<domain>/`, or the module is loaded dynamically via `importlib.util`:

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "biology_assemble_catalog",
    ROOT / "catalog" / "biology" / "assemble_catalog.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

## Test Structure Patterns

**Pure function tests:** simple `assert` calls, inline data construction, no fixtures:
```python
def test_normalize_url_lowercase():
    assert normalize_url("https://github.com/Aqua/Trivy") == "https://github.com/aqua/trivy"
```

**File system tests:** use `tmp_path` (pytest builtin) for isolated directories:
```python
def test_finalize_produces_catalog_and_results(tmp_path):
    run_finalize(entries, topic="Test Topic", output_dir=tmp_path, template_dir=template_dir)
    assert (tmp_path / "catalog.json").exists()
```

**Contract tests:** read actual repo files and assert on their structure:
```python
def test_massive_crawl_runtime_contract_matches_current_workflow():
    runtime = json.loads((ROOT / "workflows" / "massive-crawl" / "runtime.json").read_text())
    assert runtime["stages"] == ["brainstorm", "discover", "dedup", "score", "enrich", "finalize", "gap_review"]
```

**Helper pattern:** private helpers prefixed with `_` at module scope for fixture construction:
```python
def _make_catalog(tmp_path, domain, entries):
    """Helper: write a catalog.json for testing."""
    ...

SAMPLE_ENTRIES = [...]  # module-level constant reused across tests
```

**Monkeypatching:** used in `test_discover_candidates.py` to stub out external calls (GitHub API, subprocess):
```python
monkeypatch.setattr("discover_candidates.gather_candidates", lambda **_: fake_candidates)
monkeypatch.setattr("discover_candidates.search_query", lambda query, per_query_limit: [...])
monkeypatch.setattr("discover_candidates.fetch_repo_meta", lambda repo_url: ...)
```

**Subprocess integration tests:** `test_capability_graph.py` spawns real hook scripts via `subprocess.run` with a sanitized `PATH` and `CLAUDE_PROJECT_DIR`. These skip gracefully when capability graph artifacts have not been built yet:
```python
def test_session_context_hook_output():
    graph_path = repo_root / "capability-graph" / "graph" / "graph.json"
    if not graph_path.exists():
        return  # Skip if graph not built yet
    result = subprocess.run(...)
    assert result.returncode == 0
```

## What Is Tested

### Pipeline stages (`test_pipeline.py` — 36 tests)
- `normalize_url`: lowercase, trailing slash strip, `.git` suffix strip, combined normalization
- `run_dedup`: keeps highest-scoring duplicate, merges `found_in_domains`, output not larger than input, preserves non-duplicates
- `run_score`: removes entries without URL, removes entries without description (empty string and `null`), attaches `quality_score`, higher stars yield higher score, logs removals
- `run_finalize`: writes `catalog.json` and `RESULTS.md`, sorts by score descending, subdomain table format in RESULTS
- `compute_edges`: edges from shared subdomain, edges from shared tags (threshold 2), deduplication of edges, empty input
- `run_site`: generates `index.html`, generates per-domain `detail/` directory, generates correct number of detail pages, reads `capability.md` when present, falls back to placeholder when absent, prefers `telecoms` over legacy `telecom`

### Capability graph builder (`test_capability_graph.py` — 38 tests)
- `slugify_capability`: basic pass-through, special char stripping, lowercasing
- `list_domains`: returns sorted list, skips dirs without `catalog.json`
- `extract_capabilities`: correct unique capability count, shared capabilities include all implementors, related capabilities via co-provision, edge count and fields, evidence paths include `factsheet` and `capability_doc`, aliases only generated when slug differs from raw
- `build_domain_routing`: all domains included, domain name rows have weight 1.0, sub-domain rows present, tag rows present, CSV fields correct
- `build_domain_graph_slice`: correct structure keys and counts
- `build_global_graph`: combines slices correctly
- `build_capability_map_csv`: correct row count and fields
- `main()` CLI: produces all expected output files, registry is valid JSON with required keys, routing CSV fields correct, `--adapter claude` generates skill files
- Contract tests: workflow manifest files exist, `models.json` has router classifier, installer references required skills, generated skill paths on disk, hook scripts exist, settings has supercharge hooks, route-decision schema is valid JSON Schema
- Hook integration tests: `session-context.sh` produces `<supercharge>` block, `route-query.py` routes telecoms queries, `route-query.py` emits no output for generic queries (all three skip if graph not built)

### Discovery candidates (`test_discover_candidates.py` — 10 tests)
- `normalize_github_repo_url`: strips subpaths, rejects topics/search/non-GitHub URLs
- `extract_repo_urls`: filters non-repo URLs, deduplicates normalized URLs
- `build_entry_from_github_meta`: correct field mapping, handles missing optionals (null license, null last_activity)
- `score_candidate`: rewards domain overlap and multi-query hits, penalizes off-topic matches
- `build_discovery_entries`: output contract shape (exact field set and score range)
- `gather_candidates`: skips repos with missing metadata
- `run_json_command`: treats "No results found" stdout as empty payload

### Catalog layout sync (`test_sync_catalog_layout.py` — 3 tests)
- Imports telecom catalog, writes `use_cases` field, creates per-slug directories with `entry.json`, `factsheet.json`, `capability.md`
- Seeds `entry.json` for existing domains, preserves unrelated files, writes `slug` into `catalog.json`
- Resolves slug collisions with numeric suffixes (`inquest-awesome-yara`, `inquest-awesome-yara-2`)

### Generate capabilities utilities (`test_generate_capabilities.py` — 7 tests)
- `slugify`: basic, special chars, edge stripping
- `slug_dir`: creates directory, idempotent
- `load_catalog`: adds slugs from name, resolves collisions with `-2` suffix
- Progress round-trip (save then load), default empty progress structure

### Repo contracts (`test_repo_contracts.py` — 12 tests)
- `runtime.json` stage and role arrays match expected values
- Workflow manifests only reference files that exist on disk
- Codex `models.json` enricher declaration
- Claude hook config present, paths use `adapters/claude/hooks/` prefix, referenced files exist on disk
- `map-capabilities` skill has `disable-model-invocation: true` and `context: fork`
- Skill descriptions include required trigger phrases (tested via regex on YAML `description:` block)
- Shared massive-crawl prompt has no platform-specific API calls
- `contract.md` preserves toolless researcher requirement
- Codex installer exists; root installer exposes `--claude` and `--codex` flags
- Installer scripts are executable (`st_mode & 0o111`)
- `.gitignore` has `!.claude/` and `!.claude/settings.local.json` exceptions

### Domain catalog assemblers (3 tests each per domain)
Pattern is identical across `biology`, `fintech`, `education`, `healthcare`, `legal`, `sustainability`:
1. Config file has expected `sub_domains` list and correct top-level paths
2. `enrich_entries()` uses primary `sub_domain` for `category` field (not secondary domains)
3. `build_catalog()` produces the full artifact set: `raw-discovery.json`, `dedup.json`, `scored.json`, `enriched.json`, `catalog.json`, `RESULTS.md`, `explorer.html`, plus per-entry `entry.json` under slug directory

Additional tests for fintech:
- `passes_relevance_gate()` returns `True` for relevant entries, `False` for off-topic
- `build_catalog()` excludes entries with score below threshold

## Coverage Gaps

**Untested areas:**

**`pipeline/pipeline.py` — `normalize_entry()`:** field normalization for cross-domain schema compatibility (sub_domain alias, eval_potential_score scaling, stars from github_metrics) has no direct unit tests.

**`catalog/*/assemble_catalog.py` — config validation:** tests assert that specific sub-domain IDs are present in the config but do not test config loading failures, missing `discovery_dir`, or malformed JSON.

**`pipeline/sync_catalog_layout.py` — telecom import error paths:** `FileNotFoundError` raised for missing slug directories in the telecom source is not tested.

**`pipeline/discover_candidates.py` — `run_json_command` with real subprocess:** the live Firecrawl CLI path is not tested (requires external tool); only the "No results found" stub is covered.

**`pipeline/build_capability_graph.py` — multi-domain graph with `provides[]` from non-telecoms domains:** all capability extraction tests use only the telecoms fixture. No test exercises cybersecurity or other domains with `provides[]` data.

**Hook scripts — error paths:** `route-query.py` and `session-context.sh` are tested only for the happy path. Malformed input, missing routing CSV, and invalid JSON are not tested.

**HTML templates:** no snapshot or DOM tests for `base.html`, `explorer.html`, or `detail.html`. Integration is tested only by checking for string presence in `run_site` output.

**`education/assemble_catalog.py`:** has its own test file (`test_education_catalog.py`) but lives outside `catalog/` at `education/assemble_catalog.py` — this anomalous location is not tested as a structural contract.

---

*Testing analysis: 2026-03-27*
