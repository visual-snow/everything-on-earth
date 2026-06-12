# Codebase Concerns

**Analysis Date:** 2026-03-27

---

## Broken Navigation: All 3,635 Detail Pages Link to Deleted Index Files

**Issue:** Every detail page renders a breadcrumb with `<a href="../index.html">` (e.g., "Back to graph") and a search input that redirects to `../index.html?q=...`. The per-domain `index.html` files have been deleted for all 11 domains. The global explorer moved to the root `index.html`, but the detail templates were not updated to match.

**Files affected:**
- `catalog/cybersecurity/detail/*.html` — 397 pages
- `catalog/gaming/detail/*.html` — 336 pages
- `catalog/telecoms/detail/*.html` — 166 pages
- `catalog/biology/detail/*.html` — 565 pages
- `catalog/education/detail/*.html` — 283 pages
- `catalog/fintech/detail/*.html` — 311 pages
- `catalog/geopolitics/detail/*.html` — 236 pages
- `catalog/healthcare/detail/*.html` — 348 pages
- `catalog/legal/detail/*.html` — 383 pages
- `catalog/sustainability/detail/*.html` — 381 pages
- `catalog/trading/detail/*.html` — 229 pages

**Deleted files (confirmed absent):**
- `catalog/cybersecurity/index.html` (deleted, still tracked by git)
- `catalog/gaming/index.html` (deleted, still tracked by git)
- `catalog/telecoms/index.html` (deleted, still tracked by git)
- `catalog/explorer.html` (deleted, still tracked by git)

**Impact:** Clicking "Back to graph" or submitting the search input from any detail page returns a 404. All 3,635 detail pages are navigationally broken.

**Fix approach:** Update `pipeline/templates/detail.html` to set the breadcrumb domain link to `../../../index.html` (the global root explorer) instead of `../index.html`. Regenerate all detail pages by running the pipeline's `run_site()` function across all domain catalogs.

---

## Capability Graph Covers Only Telecoms

**Issue:** The capability graph at `capability-graph/` has domain-level data for only one domain. `capability-graph/graph/graph.json` declares `"domains": ["telecoms"]`. `capability-graph/graph/domains/` contains only `telecoms.json`. The `capability-router` skill (`adapters/claude/skills/capability-router/SKILL.md`) explicitly lists only `telecoms` as a domain with a generated skill, and notes that deep routing is unavailable for all other domains.

**Files:**
- `capability-graph/graph/graph.json` — single-domain graph
- `capability-graph/graph/domains/telecoms.json` — only domain file
- `capability-graph/exports/csv/telecoms-capability-map.csv` — only domain export
- `adapters/claude/skills/capability-router/SKILL.md` — hardcoded to telecoms
- `adapters/claude/skills/domain-telecoms/` — only domain-level skill

**Impact:** The routing CSV (`capability-graph/exports/csv/domain-routing.csv`) covers all 11 domains for keyword matching, but once routed, only telecoms has any deep capability context. 10 of 11 domains return a stub response from the router.

**Fix approach:** Run `pipeline/build_capability_graph.py` for each domain catalog. Generate domain skill files under `adapters/claude/skills/domain-{slug}/` and update `SKILL.md` to register them.

---

## Schema Divergence: Telecoms vs All Other Domains

**Issue:** The telecoms catalog uses a different field schema than every other domain. Telecoms entries have `eval_potential_score` (integer, 1-10 scale), `domain`, `secondary_domains`, `github_metrics.stars`, and no `quality_score` field at the catalog level. All other domains use `quality_score` (float, 0-100), `score`, `sub_domain`, `found_in_domains`, and top-level `stars`.

`pipeline/pipeline.py`'s `normalize_entry()` function bridges this at render time, but the telecoms `catalog.json` on disk remains in the non-standard format.

**Files:**
- `catalog/telecoms/catalog.json` — divergent schema
- `pipeline/pipeline.py:31-55` — `normalize_entry()` compensates at runtime

**Impact:** Any new tooling that reads `catalog.json` directly (tests, future scripts, external consumers) must re-implement the same normalization logic or produce incorrect results. The normalization is a runtime shim, not a canonical fix.

**Fix approach:** Migrate `catalog/telecoms/catalog.json` to the standard schema fields (`quality_score`, `sub_domain`, `found_in_domains`, `stars`) and update the sync script if applicable.

---

## 8 Domains Have No Per-Domain `index.html` and Were Never Fully Generated

**Issue:** The following 8 domains were added as new catalog directories with detail pages but have no corresponding `index.html` or equivalent landing page under their directory, and several lack complete pipeline outputs:

| Domain | `index.html` | `explorer.html` | `assemble_catalog.py` | `swarm-config.json` | `RESULTS.md` |
|---|---|---|---|---|---|
| `biology` | missing | present | present | present | present |
| `education` | missing | present | missing | missing | present |
| `fintech` | missing | present | present | present | present |
| `geopolitics` | missing | missing | missing | present | present |
| `healthcare` | missing | missing | present | present | present |
| `legal` | missing | present | present | present | present |
| `sustainability` | missing | present | present | present | present |
| `trading` | missing | missing | missing | present | present |

**Files affected:** All of `catalog/{domain}/` for the eight domains above.

**Impact:** There is no navigable entry point for these domains at the domain level. Users reaching `catalog/biology/` get a directory listing or 404 depending on server configuration.

---

## Large Untracked Pipeline Artifact Files Not Gitignored

**Issue:** Every domain directory contains `enrich-batch-N.json` and `enriched-batch-N.json` files from enrichment runs. These 222 files are not committed but also not listed in `.gitignore`. They will appear as untracked noise on every `git status`. `scored.json`, `RESULTS.md`, and `GAP-FILL-WAVE.md` files under domain directories are also untracked.

`.gitignore` covers `enriched.json` (singular) but not `enrich-batch-*.json`, `enriched-batch-*.json`, `scored.json`, or `RESULTS.md`.

**Files:**
- `.gitignore` — missing patterns
- 222 `enrich-batch-*.json` / `enriched-batch-*.json` files across all catalog domains

**Fix approach:** Add to `.gitignore`:
```
enrich-batch-*.json
enriched-batch-*.json
scored.json
RESULTS.md
GAP-FILL-WAVE.md
```

---

## `node_modules/` (52 MB) Not Gitignored

**Issue:** `node_modules/` is present at the repo root (52 MB) and is untracked but not listed in `.gitignore`. The project uses no Node.js build step; `package.json` is metadata-only (install scripts, keywords). Node is listed only as a peer engine requirement (`>=18`). There is no `package-lock.json` or `yarn.lock`.

**Files:**
- `.gitignore` — missing `node_modules/` entry
- `package.json` — no `dependencies` or `devDependencies` declared

**Fix approach:** Add `node_modules/` to `.gitignore`. If `node_modules/` was installed by accident, delete it.

---

## `pipeline/templates/graph.html` Deleted With No Replacement Confirmed

**Issue:** `pipeline/templates/graph.html` is staged for deletion (tracked by git, removed from disk). This template previously rendered per-domain graph views. The pipeline code does not reference it by name in any remaining `.py` file, and the new `explorer.html` template appears to absorb this function. However, the telecoms `index.html` that was also deleted had been generated by this template and linked from detail pages.

**Files:**
- `pipeline/templates/graph.html` — deleted, not replaced with equivalent output path

**Impact:** If any external link or bookmark pointed to `catalog/telecoms/index.html`, it is now broken. The deletion appears intentional but the downstream breakage in detail pages (see broken navigation concern above) was not resolved at the same time.

---

## Prompt Injection Hardening Plan Not Implemented

**Issue:** `docs/plans/2026-03-23-prompt-injection-hardening-plan.md` describes moving external content scraping (firecrawl) from Researcher sub-agents to the orchestrator, so Researcher agents receive only pre-scraped content with no live tool access. This is a security architecture change to prevent README-based prompt injection.

The plan was not applied. `adapters/claude/skills/map-capabilities/SKILL.md` does not include the scrape phase described in the plan. Researcher agents in the enrichment workflow still have access to external tools when run.

**Files:**
- `docs/plans/2026-03-23-prompt-injection-hardening-plan.md` — plan only, not implemented
- `adapters/claude/skills/map-capabilities/SKILL.md` — unchanged from pre-plan state

**Impact:** Malicious content in a cataloged repo's README could potentially manipulate enrichment output for that entry.

---

## Duplicate/Parallel `education/` Directory at Repo Root

**Issue:** A second `education/` directory exists at the repo root alongside `catalog/education/`. The root `education/` contains `assemble_catalog.py`, `swarm-config.json`, and a `discovery/` subdirectory. Its `swarm-config.json` sets `"output_dir": "catalog/education"`, indicating it is a staging/configuration area for driving the pipeline into `catalog/education/`.

This creates two locations associated with the education domain, which is not the pattern for any other domain (all other domain configurations live inside `catalog/{domain}/`).

**Files:**
- `education/` — root-level staging directory
- `catalog/education/` — actual catalog output

**Fix approach:** Determine whether `education/`'s files should be absorbed into `catalog/education/` (matching the pattern of domains like biology and fintech, which have `assemble_catalog.py` and `swarm-config.json` inside `catalog/{domain}/`) and consolidate.

---

## Design System Defines a Light Theme Conflicting With the Actual Dark Theme

**Issue:** `design-system/everything-on-earth/MASTER.md` defines a light color palette (`#F8FAFC` background, `#1E293B` text). The site uses a dark theme throughout (`#0d1117` background, `#c9d1d9` text, matching GitHub's dark mode palette).

The design system document was likely generated by a tool from a template without updating to match the actual implementation.

**Files:**
- `design-system/everything-on-earth/MASTER.md` — stale/incorrect color palette
- `index.html`, `pipeline/templates/explorer.html`, `pipeline/templates/detail.html` — actual dark theme

**Impact:** Any developer using the design system as a reference will apply wrong colors.

---

## Test Coverage Gaps

**Domains without catalog-specific tests:**
- `catalog/cybersecurity/` — no `tests/test_cybersecurity_catalog.py`
- `catalog/gaming/` — no `tests/test_gaming_catalog.py`
- `catalog/geopolitics/` — no `tests/test_geopolitics_catalog.py`
- `catalog/telecoms/` — no `tests/test_telecoms_catalog.py`
- `catalog/trading/` — no `tests/test_trading_catalog.py`

Covered domains: biology, education, fintech, healthcare, legal, sustainability (each has a corresponding test file in `tests/`).

**Other gaps:**
- No tests for `pipeline/build_capability_graph.py` (the file that produces `capability-graph/graph/`) — `tests/test_capability_graph.py` exists but verify scope.
- No test verifies that detail page breadcrumb links resolve to existing files (i.e., the broken navigation issue would not be caught by the current test suite).

---

## `training-stack/` Untracked and Undocumented

**Issue:** A `training-stack/` directory exists at the repo root with subdirectories `anatomy-viewer/`, `medagentsim/`, `nginx/`, `opanex/`, `triage-trainer/`, and a `docker-compose.yml`. This appears to be a separate application stack (medical/training domain), unrelated to the catalog pipeline and not referenced anywhere in `CLAUDE.md`, `README.md`, or any workflow file. It is fully untracked by git.

**Files:**
- `training-stack/` — untracked, no documentation or CLAUDE.md context

**Fix approach:** Either add documentation explaining its relationship to this repo and commit it, or move it to a separate repository.

---

*Concerns audit: 2026-03-27*
