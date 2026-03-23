# Folder-per-slug output restructuring

**Status:** Approved
**Date:** 2026-03-23

## Problem

`map-capabilities` writes all output files flat into `$OUTPUT_DIR`:

```
sandbox_capabilities/
├── wave-progress.json
├── akvorado_capability.md
├── akvorado_entry.json
├── akvorado_factsheet.json
├── containerlab_capability.md
├── containerlab_entry.json
├── containerlab_factsheet.json
└── ... (3 files per tool + progress file)
```

At scale (hundreds of entries across multiple catalogs), this is unnavigable. Each tool's artifacts should be co-located in their own folder.

## Target structure

```
{output-dir}/
├── wave-progress.json
├── akvorado/
│   ├── capability.md
│   ├── entry.json
│   └── factsheet.json
├── containerlab/
│   ├── capability.md
│   ├── entry.json
│   └── factsheet.json
└── ...
```

The output-dir name is already dynamic via `--output-dir` (e.g., `sandbox_capabilities/`, `security_capabilities/`). The change is purely the per-slug subfolder structure within it.

## Design

### 1. `generate_capabilities.py` — add path helper

```python
def slug_dir(output_dir: Path, slug: str) -> Path:
    """Return and ensure the per-slug output directory exists."""
    d = output_dir / slug
    d.mkdir(parents=True, exist_ok=True)
    return d
```

No other changes to this file. `wave-progress.json` stays at output-dir root and only tracks slug strings — never references file paths.

### 2. `SKILL.md` — update 3 save paths

| Stage | Current | New |
|-------|---------|-----|
| Entry dump | `$OUTPUT_DIR/{slug}_entry.json` | `$OUTPUT_DIR/{slug}/entry.json` |
| Researcher | `$OUTPUT_DIR/{slug}_factsheet.json` | `$OUTPUT_DIR/{slug}/factsheet.json` |
| Writer | `$OUTPUT_DIR/{slug}_capability.md` | `$OUTPUT_DIR/{slug}/capability.md` |

Judge phase reads the same paths — references update to match.

### 3. What does NOT change

- `wave-progress.json` format and location
- Agent prompt templates in `skill/references/`
- `pipeline/pipeline.py` (massive-crawl pipeline)
- Catalog input format
- Resumability logic
