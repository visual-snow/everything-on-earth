# Coding Conventions

**Analysis Date:** 2026-03-27

## Naming Conventions

### Files and Directories

**Pipeline scripts:** `snake_case.py` under `pipeline/`
- `pipeline.py`, `utils.py`, `build_capability_graph.py`, `generate_capabilities.py`, `sync_catalog_layout.py`, `discover_candidates.py`

**Catalog assembler scripts:** `assemble_catalog.py` placed directly inside `catalog/<domain>/`
- `catalog/biology/assemble_catalog.py`, `catalog/fintech/assemble_catalog.py`, etc.

**Per-domain config:** `swarm-config.json` — always this exact name, inside `catalog/<domain>/`

**Template files:** `snake_case` with Jinja2 extension for Markdown, `.html` for HTML
- `results.md.jinja`, `explorer.html`, `detail.html`, `base.html`, `landing.html`

**Skill wrappers:** `SKILL.md` (uppercase) at the root of each skill directory under `adapters/<platform>/skills/<skill-name>/`

**Workflow artifacts:** `manifest.json`, `runtime.json`, `contract.md` under `workflows/<workflow>/`

**Hook scripts:** named by function in `kebab-case` with `.sh` or `.py` extension
- `session-context.sh`, `compact-restore.sh`, `route-query.py`

**Test files:** `test_<module_name>.py` in `tests/`

**Fixture files:** stored in `tests/fixtures/`, named by content (`raw-discovery.json`, `swarm-config-test.json`)

### Directories

- Domain directories under `catalog/`: `kebab-case` plural nouns (`telecoms`, `cybersecurity`, `gaming`, `biology`, `fintech`)
- Per-entry slug directories under `catalog/<domain>/`: `<owner>-<repo>` slug format (`intel-flexran`, `broadinstitute-gatk`)
- Skill directories under `adapters/claude/skills/`: `kebab-case` matching workflow name (`massive-crawl`, `map-capabilities`, `capability-router`, `supercharge`)
- Hook directories under `adapters/claude/hooks/`: `kebab-case` matching the trigger/context (`supercharge/`)

### Slugs

Slug generation is centralized in `pipeline/utils.py`:
1. Lowercase the raw name string
2. Replace any run of non-alphanumeric characters with a single `-`
3. Strip leading and trailing `-`
4. Append `-2`, `-3`, etc. to resolve collisions within the same catalog

```python
# pipeline/utils.py
def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s
```

Capability IDs use the same logic via `slugify_capability()` in `pipeline/build_capability_graph.py`.

## Catalog Entry Schema Conventions

### entry.json (per-slug directory)

**Common fields (all domains):**
- `repo_url` — lowercase normalized GitHub URL, no trailing slash, no `.git`
- `name` — `"owner/RepoName"` format (preserves original casing)
- `description` — plain-text, single paragraph
- `sub_domain` — kebab-case string matching a `sub_domains[].id` from the domain's `swarm-config.json`
- `score` — integer 1-10 from discovery agent
- `score_rationale` — one-sentence explanation
- `stars` — integer from GitHub API
- `language` — primary language string or `null`
- `license` — SPDX identifier string or `null`
- `last_activity` — ISO 8601 date string (`YYYY-MM-DD`) or `null`
- `slug` — generated, always present after `load_catalog()` or `sync_catalog_layout`
- `found_in_domains` — list of `sub_domain` strings where this repo appeared
- `quality_score` — float 0-100, composite of agent score + log-scaled stars
- `tags` — list of kebab-case strings (enriched by `assemble_catalog.py`)
- `category` — human-readable string derived from primary `sub_domain`
- `summary` — one-line string, max ~120 chars

**Telecoms-specific additional fields in entry.json:**
- `domain` — primary domain (equivalent to `sub_domain` in other catalogs)
- `secondary_domains` — list of strings
- `protocols` — list of protocol name strings
- `provides` — list of kebab-case capability IDs (used by capability graph)
- `needs` — list of kebab-case dependency strings
- `docker_support` — object: `{has_dockerfile, has_compose, docker_hub_image, compose_services_count, docker_evidence}`
- `github_metrics` — object: `{stars, last_commit, language, license}`
- `eval_potential_score` — float 1-10 (telecoms scale; pipeline normalizes to 0-100 by multiplying by 10)
- `eval_notes` — prose string
- `related_repos` — list of URL strings
- `_sources` — list of relative discovery file paths (internal provenance tracking)
- `use_cases` — list of kebab-case strings (derived from `domain` + `secondary_domains`)

### factsheet.json (telecoms only, per-slug directory)

Detailed technical profile. All keys are lowercase snake_case:
- `slug`, `name`, `what_it_is` — string
- `components` — list of strings, format `"<component-name> — <description>"`
- `protocols` — list of strings
- `measurement` — list of strings
- `configuration` — list of strings
- `fault_injection` — list of strings (may be empty)
- `modes` — list of strings
- `constraints` — list of strings
- `docker_services` — list of strings
- `notable_absences` — list of strings

### capability.md (per-slug directory)

Prose-only Markdown document. No YAML frontmatter. Structure:
- First paragraph: one-sentence description of the tool and its role
- Sections using `##` headers named by capability area (e.g., `## Signal Processing`, `## Constraints`)
- Bullet lists under each section; no nested sublists
- Present tense; no marketing language

### swarm-config.json

Top-level keys:
- `topic` — human-readable string
- `topic_slug` — kebab-case, matches the `catalog/<domain>` directory name
- `output_dir` — relative path `"catalog/<domain>"`
- `discovery_dir` — relative path `"catalog/<domain>/discovery"`
- `sub_domains` — list of objects with:
  - `id` — kebab-case, becomes the `sub_domain` field on entries
  - `name` — human-readable string; often `"<Area> — <subtitle>"`
  - `queries` — list of search strings
- `orchestration` (optional) — `{wave_count, parallel_agents_per_wave}`
- `waves` (optional) — list of `{id, subdomains}` objects for wave scheduling
- `constraints` (optional) — object with boolean flags

## HTML Template Patterns

Templates live in `pipeline/templates/`. Rendered with Jinja2 (`Environment(loader=FileSystemLoader(...))`).

**Base template:** `base.html` — provides page shell; child templates extend it.

**Detail page** (`detail.html`): receives `entry`, `domain_name`, `domain_slug`, `capability_md`, `nearby_repos`. Conditionally renders a `div.capability-md` section only when `capability_md` is non-empty; falls back to a static placeholder section with `"Capability mapping has not been generated"`.

**Explorer** (`explorer.html`): receives `title`, `total`, `catalog_count`, `catalog_json` (inline JSON string of all entries). Renders a search/filter UI.

**Results** (`results.md.jinja`): Jinja2 Markdown template. Renders a summary table with columns `| Sub-domain | Repos | Avg Discovery Score |`. References `See \`explorer.html\` to browse interactively.` at the end.

## Python Code Style

**All pipeline Python is stdlib + jinja2 only** (`pipeline/requirements.txt` declares only `jinja2>=3.1.0`).

**Module-level constants** are UPPER_SNAKE_CASE sets or dicts:
```python
STOPWORDS = {"analysis", "biology", ...}
KEYWORDS = {"16s", "acmg", ...}
WAVE_SIZE = 15
```

**Path handling:** always use `pathlib.Path`. Never `os.path.join`.

**File I/O pattern:** read with `path.read_text()`, write with `path.write_text(...)`. JSON written with `json.dumps(payload, indent=2)` (plus trailing newline in `sync_catalog_layout.py`).

**Function signatures:** type-annotated with stdlib types. Use `list[dict]` and `dict[str, str]` (Python 3.10+ style lowercase generics). Use `Path | None` for optional paths.

**Docstrings:** single-line for simple functions, multi-line module docstring at the top of each file. No class docstrings (no classes used in pipeline code). No inline comments explaining obvious logic.

**Print conventions:** pipeline print statements are prefixed with the stage name in brackets:
```python
print(f"[dedup] Input: {len(raw)} entries")
print(f"[score] Kept: {len(result)}, Removed: {len(removed_log)}")
print(f"[site] Wrote {explorer_path} ({total_repos} entries, {len(domain_catalogs)} domains)")
```

**Assertions:** used for invariant checks inside pipeline functions, not for input validation:
```python
assert len(result) <= len(entries), f"Dedup expanded data: {len(result)} > {len(entries)}"
```

**Error exit pattern:** `print("Error: ...", file=sys.stderr); sys.exit(1)` — used in `main()` only.

**sys.path manipulation for imports:** test files and catalog assemblers add their module directory to `sys.path` at the top:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
```
Catalog assemblers reference `REPO_ROOT = Path(__file__).resolve().parents[2]`.

**No classes:** all pipeline and assembler code is purely functional. No OOP.

**Naming:** functions use `snake_case`. All module-level identifiers are `snake_case` except constants. No abbreviations except established conventions (`e` for entry in tight loops, `d` for domain in tight loops).

## Hook and Skill Naming

**Skill file naming:** always `SKILL.md` at the root of the skill directory. No other variant.

**Skill YAML frontmatter fields:**
- `name` — kebab-case, matches directory name
- `description` — folded block scalar (`>-`) starting with trigger phrases; tested by `test_repo_contracts.py`
- `disable-model-invocation` — always `true` for adapter wrappers
- `context` — always `fork` for adapter wrappers
- `allowed-tools` — explicit list (no wildcard)

**Hook script placement:** `adapters/claude/hooks/<context-name>/<script-name>`. Must be referenced in `.claude/settings.local.json` using the `adapters/claude/hooks/` prefix path. Paths are validated by `test_repo_contracts.py`.

**Workflow directories:** each workflow under `workflows/<workflow-name>/` contains:
- `manifest.json` — declares all files in the workflow directory (`files` key, list of relative paths)
- `runtime.json` — declares `stages`, `roles`, `artifacts`, and `invariants`
- `contract.md` — prose contract document
- `prompts/` — shared, platform-neutral prompt templates
- `schemas/` — JSON Schema files

**Workflow prompts:** must be platform-neutral. Must not contain `TaskList(`, `TaskUpdate(`, `TeamCreate(` or any Claude-specific API calls. Validated by `test_repo_contracts.py::test_shared_massive_crawl_prompt_stays_platform_neutral`.

---

*Convention analysis: 2026-03-27*
