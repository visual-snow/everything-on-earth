# Architecture

**Analysis Date:** 2026-03-27

## Pattern Overview

**Overall:** Multi-workflow agentic pipeline with a deterministic Python core.

The system has two distinct concerns wired together:

1. **Catalog production** — discover, score, enrich, and publish open-source repositories organized by domain.
2. **Capability graph** — extract structured capability data from catalogs, build a routing index, and serve AI agents navigating the landscape.

LLM agents handle subjective tasks (discovery, enrichment, capability authoring). All merge, dedup, scoring formula, and HTML generation steps are deterministic Python with no LLM involvement.

**Key Characteristics:**
- Workflows are platform-agnostic contracts; adapters wrap them for Claude or Codex.
- Every stage reads one file and writes one file; no shared mutable state between stages.
- The static site (`index.html`, `catalog/<domain>/detail/*.html`) is a build artifact produced by `pipeline/pipeline.py --stage site`.

## Layers

**Workflow Contracts:**
- Purpose: Platform-agnostic source of truth for agent behavior, schemas, prompts, and invariants.
- Location: `workflows/<workflow>/`
- Contains: `contract.md`, `manifest.json`, `runtime.json`, `schemas/`, `prompts/`, `examples/`
- Depends on: Nothing (authoritative source)
- Used by: `adapters/claude/skills/`, `adapters/codex/skills/`

**Adapter Skills:**
- Purpose: Wrap workflow contracts with platform-specific configuration (model selection, tool permissions, hook wiring).
- Location: `adapters/claude/skills/<skill>/SKILL.md`, `adapters/codex/skills/<skill>/`
- Contains: YAML front-matter (model, allowed-tools, context mode) + behavior instructions that reference, not duplicate, the shared contract.
- Depends on: `workflows/<workflow>/contract.md`
- Used by: Claude Code or Codex at runtime as agent instructions.

**Python Pipeline:**
- Purpose: Deterministic data transformation — dedup, score, finalize, site generation, capability graph construction.
- Location: `pipeline/`
- Key scripts: `pipeline.py`, `build_capability_graph.py`, `discover_candidates.py`, `generate_capabilities.py`, `sync_catalog_layout.py`, `utils.py`
- Depends on: `catalog/*/catalog.json`, Jinja2 templates in `pipeline/templates/`
- Used by: Claude agents (via Bash tool) and human operators.

**Catalog Store:**
- Purpose: Persistent artifact store; one directory per domain, one subdirectory per repository slug.
- Location: `catalog/<domain>/`
- Contains: `catalog.json` (domain-wide flat list), `<slug>/entry.json`, optionally `<slug>/factsheet.json` and `<slug>/capability.md`.
- Depends on: Pipeline and map-capabilities workflow outputs.
- Used by: Site generator, capability graph builder, capability-router skill.

**Capability Graph:**
- Purpose: Pre-compiled structured knowledge for AI navigation; not derived at query time.
- Location: `capability-graph/`
- Contains: `ontology/capability-registry.json`, `ontology/aliases.csv`, `graph/graph.json`, `graph/domains/<domain>.json`, `exports/csv/domain-routing.csv`, `exports/csv/<domain>-capability-map.csv`.
- Depends on: `catalog/<domain>/` entry data (`provides[]` field in `entry.json`).
- Used by: `adapters/claude/skills/capability-router/SKILL.md`, `adapters/claude/skills/domain-telecoms/SKILL.md`.

**Static Site:**
- Purpose: Human-facing HTML explorer, generated as a build artifact.
- Key outputs: `index.html` (unified explorer, all domains), `catalog/<domain>/detail/<slug>.html` (per-repo detail pages).
- Depends on: `pipeline/templates/`, `catalog/*/catalog.json`, `catalog/<domain>/<slug>/capability.md`.

## Data Flow

**Catalog Production (massive-crawl workflow):**

1. Scout subagents brainstorm sub-domains; user approves `swarm-config.json`.
2. Discoverer agents run Firecrawl searches per sub-domain, call GitHub API via `gh` CLI, write `discovery/<sub-domain>.json`.
3. All discovery files are concatenated into `raw-discovery.json` (no LLM synthesis).
4. `pipeline.py --stage dedup` normalizes URLs and deduplicates; writes `dedup.json`.
5. `pipeline.py --stage score` applies formula (agent relevance × 6 + log-scaled stars × 40); writes `scored.json`.
6. Enricher agents (haiku-class) attach `tags`, `category`, `summary` to each entry; writes `enriched.json`.
7. `pipeline.py --stage finalize` sorts by `quality_score`, writes `catalog.json` and `RESULTS.md`.

**Site Generation:**

1. `pipeline.py --stage site` reads all `catalog/*/catalog.json` files.
2. Normalizes schema differences (telecoms uses `domain`/`secondary_domains`; others use `sub_domain`/`found_in_domains`).
3. Computes per-domain edges: entries linked by shared sub-domain or ≥2 shared tags.
4. Renders `index.html` (unified explorer, all entries as JSON blob) and `catalog/<domain>/detail/<slug>.html` using Jinja2 templates.
5. Each detail page inlines `capability.md` content if available.

**Capability Mapping (map-capabilities workflow):**

1. Operator loads a catalog and initializes or resumes `wave-progress.json` via `generate_capabilities.py`.
2. Per wave of 15 slugs: researcher subagent reads prefetched `entry.json` + `readme-raw.md`, produces `factsheet.json`.
3. Writer subagent reads `factsheet.json`, produces `capability.md`.
4. Judge subagent reviews the wave; failures are marked in `wave-progress.json` for retry.

**Capability Graph Construction:**

1. `build_capability_graph.py` reads all `catalog/<domain>/catalog.json` and per-slug `entry.json` files.
2. Extracts `provides[]` arrays from entry.json (currently only telecoms has this data — designated "pilot domain").
3. Slugifies capability strings, resolves aliases by co-occurrence, links repos to capabilities.
4. Builds co-occurrence-based `related_capabilities` relationships.
5. Writes ontology, per-domain graph slices, global graph, and CSV exports.
6. If `--adapter claude`, generates `adapters/claude/skills/capability-router/SKILL.md` and `adapters/claude/skills/domain-telecoms/SKILL.md`.

**Capability Routing (runtime, at agent query time):**

1. `capability-router` skill (haiku classifier) reads `capability-graph/exports/csv/domain-routing.csv`.
2. Classifies user query against routing index (domain names, sub-domains, tags, categories as candidates).
3. Routes to the matching domain skill if a generated `adapters/claude/skills/domain-<name>/SKILL.md` exists; otherwise falls back to general catalog search.

## Key Abstractions

**Entry:**
- The canonical data unit. Fields: `repo_url`, `name`, `description`, `sub_domain`, `score`, `stars`, `language`, `license`, `last_activity`, `found_in_domains`, `quality_score`, `tags`, `category`, `summary`, `slug`.
- Telecoms entries extend the schema with `domain`, `secondary_domains`, `protocols`, `provides[]`, `needs[]`, `docker_support`, `github_metrics`, `eval_potential_score`.
- Normalization function `normalize_entry()` in `pipeline/pipeline.py` reconciles the two schemas at site-generation time.

**Slug:**
- A filesystem-safe identifier derived from `entry["name"]` via `slugify()` in `pipeline/utils.py`.
- Used as directory name under `catalog/<domain>/`, as HTML filename under `detail/`, and as node ID in the capability graph.

**Capability:**
- A normalized string from a repo's `provides[]` list.
- Stored with: `id` (slugified), `label` (title-cased), `aliases`, `related_capabilities` (co-occurrence), `implemented_by` (repo slugs), `evidence` (paths to factsheet/capability.md).

**Workflow vs. Adapter:**
- A workflow (`workflows/<name>/`) defines WHAT an agent does: contract, schemas, invariants, role boundaries.
- An adapter (`adapters/<platform>/skills/<name>/SKILL.md`) defines HOW a specific platform executes it: model tier, tool list, context forking.

## Entry Points

**Site rebuild:**
- Invocation: `python pipeline/pipeline.py --catalog-root catalog --stage site`
- Triggers: After any catalog update; generates/overwrites `index.html` and all `detail/*.html` files.

**Capability graph rebuild:**
- Invocation: `python pipeline/build_capability_graph.py --adapter claude`
- Triggers: After catalog entries gain new `provides[]` data; regenerates all `capability-graph/` artifacts and updates Claude skill files.

**New domain catalog:**
- Invocation: Run massive-crawl skill via Claude Code; pipeline stages follow.
- Outputs land in `catalog/<domain>/` and get incorporated on next site rebuild.

## Error Handling

**Strategy:** Fail fast with descriptive messages; no silent data loss.

**Patterns:**
- `pipeline.py` uses `assert len(result) <= len(entries)` to catch dedup expansion bugs.
- `run_score` writes a `removed_log` listing every dropped entry with its reason (`no_url`, `no_description`).
- `sync_catalog_layout.py` raises `FileNotFoundError` if a telecom slug directory is absent from the source.
- `generate_capabilities.py` marks slugs as failed in `wave-progress.json` rather than silently skipping.
- `build_capability_graph.py` exits with error if catalog root is missing or empty.

## Cross-Cutting Concerns

**Logging:** `print()` statements with `[stage]` prefixes; no structured logging framework.
**Validation:** Schema conformance is enforced by contracts and tests, not runtime validators.
**Authentication:** GitHub API access via `gh` CLI (ambient token). Firecrawl via `firecrawl` CLI. No auth code in pipeline.
**Determinism:** All pipeline stages (dedup, score, finalize, graph build) must be reproducible from the same inputs; this is enforced by tests and contract invariants.

---

*Architecture analysis: 2026-03-27*
