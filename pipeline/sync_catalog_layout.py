#!/usr/bin/env python3
"""Sync domain catalogs into folder-per-framework layout."""

import argparse
import json
import shutil
from pathlib import Path

from generate_capabilities import load_catalog


def write_json(path: Path, payload: object) -> None:
    """Write JSON with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def build_use_cases(entry: dict) -> list[str]:
    """Derive telecom use cases from primary and secondary domains."""
    ordered = [entry.get("domain"), *entry.get("secondary_domains", [])]
    seen = set()
    use_cases = []
    for value in ordered:
        if not value or value in seen:
            continue
        seen.add(value)
        use_cases.append(value)
    return use_cases


def sync_existing_domain(domain_dir: Path) -> None:
    """Persist slugs in catalog.json and seed per-framework entry.json files."""
    catalog_path = domain_dir / "catalog.json"
    entries = load_catalog(catalog_path)
    write_json(catalog_path, entries)

    for entry in entries:
        slug_dir = domain_dir / entry["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)
        write_json(slug_dir / "entry.json", entry)


def sync_telecom_domain(repo_root: Path, task_designer_root: Path) -> None:
    """Import telecom catalog and framework artifacts from task-designer."""
    source_catalog = task_designer_root / "data" / "catalog.json"
    source_capabilities = task_designer_root / "data" / "sandbox_capabilities"
    telecom_dir = repo_root / "catalog" / "telecoms"

    entries = load_catalog(source_catalog)
    for entry in entries:
        entry["use_cases"] = build_use_cases(entry)

    write_json(telecom_dir / "catalog.json", entries)

    for entry in entries:
        source_slug_dir = source_capabilities / entry["slug"]
        if not source_slug_dir.is_dir():
            raise FileNotFoundError(
                f"Missing telecom framework folder for slug '{entry['slug']}': {source_slug_dir}"
            )
        shutil.copytree(source_slug_dir, telecom_dir / entry["slug"], dirs_exist_ok=True)


def sync_repo_catalogs(repo_root: Path, task_designer_root: Path) -> None:
    """Apply the approved catalog layout to telecoms, gaming, and cybersecurity."""
    repo_root = repo_root.resolve()
    task_designer_root = task_designer_root.resolve()

    sync_telecom_domain(repo_root, task_designer_root)
    sync_existing_domain(repo_root / "catalog" / "gaming")
    sync_existing_domain(repo_root / "catalog" / "cybersecurity")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync catalog folder-per-framework layout")
    parser.add_argument("--repo-root", default=".", help="Path to repo root")
    parser.add_argument(
        "--task-designer-root",
        default="../task-designer",
        help="Path to task-designer repo root",
    )
    args = parser.parse_args()

    sync_repo_catalogs(
        repo_root=Path(args.repo_root),
        task_designer_root=Path(args.task_designer_root),
    )


if __name__ == "__main__":
    main()
