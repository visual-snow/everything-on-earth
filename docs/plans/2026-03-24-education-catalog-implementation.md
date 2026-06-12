# Education Catalog Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new `education` domain catalog with 20 education sub-domains, per-subdomain discovery outputs, deterministic assembly artifacts, and generated site pages under `catalog/education`.

**Architecture:** Follow the existing domain pattern used by `healthcare`: keep discovery inputs in `education/discovery/`, define the crawl scope in `education/swarm-config.json`, assemble deterministic artifacts with a domain-specific `education/assemble_catalog.py`, and then regenerate the global site via the shared pipeline. For discovery, use four waves of five discoverer agents that search and scrape with Firecrawl, then write schema-compatible JSON directly to `education/discovery/<subdomain>.json`; do not depend on `pipeline/discover_candidates.py` for final discovery output because it is GitHub-only and does not emit `score` or `score_rationale`.

**Tech Stack:** Python 3, pytest, existing Firecrawl CLI integration, existing GitHub CLI metadata lookup, shared Jinja pipeline templates.

---

### Task 1: Add Education Domain Scaffold

**Files:**
- Create: `education/swarm-config.json`
- Create: `education/discovery/.gitkeep`
- Test: `tests/test_education_catalog.py`

- [ ] **Step 1: Write the failing test**

```python
def test_education_config_has_20_subdomains():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_config_has_20_subdomains -v`
Expected: FAIL because the config file does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `education/swarm-config.json` with:
- `topic`, `topic_slug`, `output_dir`, `discovery_dir`
- exactly 20 `sub_domains`
- stable ids matching the approved scope
- 4-6 Firecrawl search queries per subdomain
- education-first scope rules suitable for adjacent infrastructure filtering
- assert the exact 20-id set used by the four discovery waves

Create `education/discovery/.gitkeep`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_config_has_20_subdomains -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add education/swarm-config.json education/discovery/.gitkeep tests/test_education_catalog.py
git commit -m "feat: add education crawl scope"
```

### Task 2: Add Deterministic Education Assembler

**Files:**
- Create: `education/assemble_catalog.py`
- Modify: `tests/test_education_catalog.py`

- [ ] **Step 1: Write the failing test**

```python
def test_education_enrichment_adds_category_summary_and_tags():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_enrichment_adds_category_summary_and_tags -v`
Expected: FAIL because the assembler module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Implement `education/assemble_catalog.py` by adapting the existing healthcare assembler pattern:
- load discovery outputs from `education/discovery/*.json`
- normalize entries
- run shared `run_dedup`, `run_score`, `run_finalize`, `run_site`
- add education-specific tag extraction and category naming
- emit `raw-discovery.json`, `dedup.json`, `scored.json`, `enrich-batch-*.json`, `enriched-batch-*.json`, `enriched.json`, `catalog.json`, `RESULTS.md`, `explorer.html`
- sync per-entry `entry.json` files under `catalog/education/<slug>/`
- expose injectable `repo_root` / `catalog_root` parameters so tests can build against temporary fixtures without depending on the workspace root

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_enrichment_adds_category_summary_and_tags -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add education/assemble_catalog.py tests/test_education_catalog.py
git commit -m "feat: add education catalog assembler"
```

### Task 3: Add Assembly Smoke Coverage

**Files:**
- Modify: `tests/test_education_catalog.py`

- [ ] **Step 1: Write the failing test**

```python
def test_education_build_catalog_writes_expected_artifacts(tmp_path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_build_catalog_writes_expected_artifacts -v`
Expected: FAIL because the build path is not implemented or not writing all expected files.

- [ ] **Step 3: Write minimal implementation**

Adjust `education/assemble_catalog.py` so the test fixture can:
- point at a temporary config/discovery location via injectable roots
- build the deterministic output set without mutating unrelated real workspace files
- preserve enrichment count and order

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_education_catalog.py::test_education_build_catalog_writes_expected_artifacts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add education/assemble_catalog.py tests/test_education_catalog.py
git commit -m "test: cover education catalog assembly"
```

### Task 4: Run Discovery Waves And Build Catalog

**Files:**
- Generate: `education/discovery/*.json`
- Generate: `catalog/education/*`
- Generate: global site files rewritten by `run_site`, including root `index.html` and per-domain pages under `catalog/*/`

- [ ] **Step 1: Execute four waves of five discoverer agents**

Wave layout:
- Wave 1: `lms`, `adaptive-learning`, `assessment-testing`, `interactive-coding-education`, `k12-stem`
- Wave 2: `video-lecture-platforms`, `collaborative-learning`, `curriculum-authoring`, `sis`, `gamification-engagement`
- Wave 3: `language-learning`, `accessibility-inclusive-education`, `analytics-learning-dashboards`, `virtual-labs-simulations`, `classroom-management`
- Wave 4: `research-academic-publishing`, `special-education-therapy`, `credentialing-certification`, `edtech-infrastructure`, `ai-teaching-assistants`

Each discoverer must:
- use Firecrawl search/scrape inputs directly
- write one `education/discovery/<subdomain>.json`
- keep only canonical GitHub/GitLab repo URLs
- attach discovery score and rationale
- attach stars, language, license, and last_activity using repo metadata lookups
- write output that already matches the shared `massive-crawl` discovery schema

- [ ] **Step 2: Verify discovery outputs exist for all 20 subdomains**

Run: `find education/discovery -name '*.json' | wc -l`
Expected: `20`

- [ ] **Step 3: Build the catalog**

Run: `python3 education/assemble_catalog.py --config education/swarm-config.json`
Expected: catalog artifacts written under `catalog/education/` and global site pages regenerated

- [ ] **Step 4: Verify the end-to-end outputs**

Run: `python3 -m pytest tests/test_education_catalog.py tests/test_pipeline.py tests/test_discover_candidates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add education catalog/education index.html catalog/*/index.html catalog/*/detail
git commit -m "feat: publish education catalog"
```
