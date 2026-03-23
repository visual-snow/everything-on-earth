# Folder-per-slug Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure map-capabilities output from flat `{slug}_file` to nested `{slug}/file` directories.

**Architecture:** Add a `slug_dir()` path helper in `generate_capabilities.py`, update 3 save-path references in `SKILL.md`, update description in SKILL.md frontmatter. No changes to progress tracking format — `wave-progress.json` stays at the output-dir root and only tracks slug strings.

**Tech Stack:** Python 3, SKILL.md (Claude Code skill markup)

**Design doc:** `docs/plans/2026-03-23-folder-per-slug-design.md`

---

### Task 1: Add `slug_dir` helper and tests

**Files:**
- Modify: `pipeline/generate_capabilities.py:24-30`
- Create: `tests/test_generate_capabilities.py`

**Step 1: Write the test file**

```python
"""Tests for generate_capabilities.py wave orchestration utilities."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from generate_capabilities import slugify, slug_dir, load_catalog, load_progress, save_progress


def test_slugify_basic():
    assert slugify("Containerlab") == "containerlab"


def test_slugify_special_chars():
    assert slugify("Open5GS (Docker)") == "open5gs-docker"


def test_slugify_strips_edges():
    assert slugify("  --hello--  ") == "hello"


def test_slug_dir_creates_directory(tmp_path):
    d = slug_dir(tmp_path, "akvorado")
    assert d == tmp_path / "akvorado"
    assert d.is_dir()


def test_slug_dir_idempotent(tmp_path):
    slug_dir(tmp_path, "akvorado")
    d = slug_dir(tmp_path, "akvorado")
    assert d.is_dir()


def test_load_catalog_adds_slugs(tmp_path):
    catalog = [{"name": "Containerlab"}, {"name": "FAUCET"}]
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))
    entries = load_catalog(catalog_path)
    assert entries[0]["slug"] == "containerlab"
    assert entries[1]["slug"] == "faucet"


def test_load_catalog_resolves_collisions(tmp_path):
    catalog = [{"name": "Tool"}, {"name": "Tool"}]
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))
    entries = load_catalog(catalog_path)
    assert entries[0]["slug"] == "tool"
    assert entries[1]["slug"] == "tool-2"


def test_progress_round_trip(tmp_path):
    progress = {"completed": ["a"], "failed": {"b": "reason"}, "in_progress": ["c"]}
    save_progress(tmp_path, progress)
    loaded = load_progress(tmp_path)
    assert loaded == progress


def test_progress_default(tmp_path):
    loaded = load_progress(tmp_path)
    assert loaded == {"completed": [], "failed": {}, "in_progress": []}
```

**Step 2: Run tests to verify they fail (slug_dir doesn't exist yet)**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python3 -m pytest tests/test_generate_capabilities.py -v`
Expected: FAIL — `ImportError: cannot import name 'slug_dir'`

**Step 3: Add `slug_dir` to `generate_capabilities.py`**

Insert after the `slugify` function (after line 30):

```python
def slug_dir(output_dir: Path, slug: str) -> Path:
    """Return and ensure the per-slug output directory exists."""
    d = output_dir / slug
    d.mkdir(parents=True, exist_ok=True)
    return d
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python3 -m pytest tests/test_generate_capabilities.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add pipeline/generate_capabilities.py tests/test_generate_capabilities.py
git commit -m "feat: add slug_dir helper for per-slug output directories"
```

---

### Task 2: Update SKILL.md save paths from flat to nested

**Files:**
- Modify: `skill/map-capabilities/SKILL.md:7-9` (frontmatter description)
- Modify: `skill/map-capabilities/SKILL.md:87` (Researcher save path)
- Modify: `skill/map-capabilities/SKILL.md:114` (Writer save path)

**Step 1: Update frontmatter description**

Change line 8 from:
```
  a catalog. Reads catalog.json as input, writes one {slug}_capability.md per
  entry.
```
to:
```
  a catalog. Reads catalog.json as input, writes one {slug}/capability.md per
  entry inside a per-slug directory.
```

**Step 2: Update Researcher save path**

Change line 87 from:
```
Collect each agent's FACTSHEET JSON output. Save to `$OUTPUT_DIR/{slug}_factsheet.json`.
```
to:
```
Collect each agent's FACTSHEET JSON output. Save to `$OUTPUT_DIR/{slug}/factsheet.json` (create the `{slug}/` directory first).
```

**Step 3: Update Writer save path**

Change line 114 from:
```
Save each output to `$OUTPUT_DIR/{slug}_capability.md`.
```
to:
```
Save each output to `$OUTPUT_DIR/{slug}/capability.md`.
```

**Step 4: Add entry.json save instruction**

After Step 2 (Researcher phase) in SKILL.md, the orchestrating agent also saves the catalog entry. This isn't currently explicit in SKILL.md but happens in practice. Add a note after the Researcher save instruction:

```
Also save the catalog entry JSON to `$OUTPUT_DIR/{slug}/entry.json`.
```

**Step 5: Update Judge file-reading paths**

The Judge phase reads factsheet and capability files. In the FILES TO REVIEW section (lines 130-138), the paths are referenced as `{factsheet_json}` and `{capability_md_content}` which are loaded by the orchestrator. No path changes needed in the Judge prompt itself — the orchestrator reads from the new paths.

**Step 6: Commit**

```bash
git add skill/map-capabilities/SKILL.md
git commit -m "feat: update map-capabilities to use per-slug output directories"
```

---

### Task 3: Verify end-to-end with a dry run

**Files:**
- Read: `pipeline/generate_capabilities.py` (verify helper is present)
- Read: `skill/map-capabilities/SKILL.md` (verify paths updated)

**Step 1: Run all tests**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python3 -m pytest tests/ -v`
Expected: All PASS (both test_pipeline.py and test_generate_capabilities.py)

**Step 2: Manual dry-run of path helper**

Run:
```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python3 -c "
from pathlib import Path
import sys, tempfile
sys.path.insert(0, 'pipeline')
from generate_capabilities import slug_dir
d = slug_dir(Path(tempfile.mkdtemp()), 'akvorado')
print(f'Created: {d}')
print(f'Exists: {d.is_dir()}')
(d / 'capability.md').write_text('# Test')
(d / 'factsheet.json').write_text('{}')
(d / 'entry.json').write_text('{}')
print(f'Files: {sorted(p.name for p in d.iterdir())}')
"
```
Expected:
```
Created: /tmp/.../akvorado
Exists: True
Files: ['capability.md', 'entry.json', 'factsheet.json']
```

**Step 3: Verify no regressions in generate_capabilities.py CLI**

Run:
```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python3 pipeline/generate_capabilities.py --help
```
Expected: Help text prints without errors.
