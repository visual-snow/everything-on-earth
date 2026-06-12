# Global Explorer Design

**Date:** 2026-03-24
**Status:** Approved

## Problem

Each domain gets its own `explorer.html` scoped to that domain's data only. The explorer should be a single top-level page that aggregates all scraped domains.

## Design

### Architecture

A new `explorer` stage in `pipeline.py` that:
1. Scans `catalog/*/catalog.json` to find all domain catalogs
2. Merges entries, injecting a `domain` field from the folder name into each entry
3. Renders the updated template to `catalog/explorer.html`

Per-domain `finalize` stage stops generating `explorer.html` inside domain folders.

### Template Changes

`pipeline/templates/explorer.html` gets:
- **Domain filter dropdown** — alongside existing sub-domain filter, populated from unique `domain` values
- **Domain badge on cards** — colored pill with domain name, distinct from tag pills
- **Title and stats** — "Everything on Earth — Explorer" with "N repos across M domains"
- **Domain-aware color coding** — each domain gets a consistent hue via name hash-to-hsl

### Pipeline Changes

**`pipeline.py`:**
- New `run_explorer(catalog_root)` function — globs `catalog_root/*/catalog.json`, merges, renders to `catalog_root/explorer.html`
- New `--catalog-root` argument used when `--stage explorer` is specified
- `run_finalize()` — remove explorer.html generation (lines 149-158)

**CLI usage:**
```bash
# Per-domain (unchanged)
python pipeline.py --config catalog/cybersecurity/swarm-config.json --stage dedup,score,finalize

# Global explorer (new, run after any/all domains)
python pipeline.py --stage explorer --catalog-root catalog/
```

### What Gets Removed
- Explorer generation from `run_finalize()`
- Existing per-domain `explorer.html` files
- References to `explorer.html` in RESULTS.md template (or update to point to `../explorer.html`)
