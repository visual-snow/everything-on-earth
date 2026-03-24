"""Shared utilities for the everything-on-earth pipeline."""

import json
import re
from pathlib import Path


def slugify(name: str) -> str:
    """Convert a catalog entry name to a filesystem-safe slug."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def load_catalog(catalog_path: Path) -> list[dict]:
    """Load catalog.json and add slug field to each entry."""
    entries = json.loads(catalog_path.read_text())
    for entry in entries:
        if "slug" not in entry:
            entry["slug"] = slugify(entry["name"])
    seen: dict[str, int] = {}
    for entry in entries:
        slug = entry["slug"]
        if slug in seen:
            seen[slug] += 1
            entry["slug"] = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 1
    return entries
