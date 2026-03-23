#!/usr/bin/env python3
"""
Capability mapper — wave orchestration utilities.

Handles catalog loading, wave splitting, progress tracking, and output management.
Agent orchestration happens in the SKILL.md; this script handles the deterministic parts.

Usage:
    python generate_capabilities.py --catalog PATH --output-dir PATH --action load
    python generate_capabilities.py --catalog PATH --output-dir PATH --action status
    python generate_capabilities.py --catalog PATH --output-dir PATH --action next-wave
    python generate_capabilities.py --catalog PATH --output-dir PATH --action mark-done --slugs a,b,c
    python generate_capabilities.py --catalog PATH --output-dir PATH --action mark-failed --slugs a,b --reasons '{"a":"ABSTRACTION: port number","b":"CONSTRAINTS: only 1"}'
"""

import argparse
import json
import re
import sys
from pathlib import Path

WAVE_SIZE = 15


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
    # Detect and resolve slug collisions by appending numeric suffixes
    seen: dict[str, int] = {}
    for entry in entries:
        slug = entry["slug"]
        if slug in seen:
            seen[slug] += 1
            entry["slug"] = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 1
    return entries


def load_progress(output_dir: Path) -> dict:
    """Load or initialize wave-progress.json."""
    progress_path = output_dir / "wave-progress.json"
    if progress_path.exists():
        return json.loads(progress_path.read_text())
    return {"completed": [], "failed": {}, "in_progress": []}


def save_progress(output_dir: Path, progress: dict) -> None:
    """Write wave-progress.json."""
    progress_path = output_dir / "wave-progress.json"
    progress_path.write_text(json.dumps(progress, indent=2))


def get_pending(entries: list[dict], progress: dict) -> list[dict]:
    """Return entries not yet completed or in progress."""
    done = set(progress["completed"])
    in_prog = set(progress.get("in_progress", []))
    return [e for e in entries if e["slug"] not in done and e["slug"] not in in_prog]


def get_retry_queue(progress: dict) -> list[str]:
    """Return slugs that failed and need retry."""
    return list(progress.get("failed", {}).keys())


def action_load(entries: list[dict], output_dir: Path) -> None:
    """Print catalog summary and initialize progress if needed."""
    progress = load_progress(output_dir)
    pending = get_pending(entries, progress)
    retries = get_retry_queue(progress)

    print(json.dumps({
        "total_entries": len(entries),
        "completed": len(progress["completed"]),
        "failed": len(progress.get("failed", {})),
        "pending": len(pending),
        "retry_queue": len(retries),
        "waves_remaining": (len(pending) + len(retries) + WAVE_SIZE - 1) // WAVE_SIZE,
    }, indent=2))


def action_status(entries: list[dict], output_dir: Path) -> None:
    """Print detailed progress status."""
    progress = load_progress(output_dir)
    pending = get_pending(entries, progress)

    print(json.dumps({
        "completed": progress["completed"],
        "failed": progress.get("failed", {}),
        "in_progress": progress.get("in_progress", []),
        "pending_slugs": [e["slug"] for e in pending[:WAVE_SIZE]],
        "total_pending": len(pending),
    }, indent=2))


def action_next_wave(entries: list[dict], output_dir: Path) -> None:
    """Output the next wave of entries to process (retries first, then pending)."""
    progress = load_progress(output_dir)

    # Recover stranded in_progress entries from a previous interrupted run
    stranded = progress.get("in_progress", [])
    if stranded:
        for slug in stranded:
            progress["failed"][slug] = "interrupted — recovered by next-wave"
        progress["in_progress"] = []
        save_progress(output_dir, progress)

    retries = get_retry_queue(progress)
    pending = get_pending(entries, progress)

    wave = []

    # Retries get priority
    retry_entries = [e for e in entries if e["slug"] in retries]
    for entry in retry_entries[:WAVE_SIZE]:
        entry_with_feedback = dict(entry)
        entry_with_feedback["_retry_reason"] = progress["failed"][entry["slug"]]
        wave.append(entry_with_feedback)

    # Fill remaining slots with pending
    remaining = WAVE_SIZE - len(wave)
    if remaining > 0:
        wave.extend(pending[:remaining])

    if not wave:
        print(json.dumps({"done": True, "message": "All entries processed"}))
        return

    # Mark as in_progress
    progress["in_progress"] = [e["slug"] for e in wave]
    # Remove retries from failed
    for e in wave:
        if e["slug"] in progress.get("failed", {}):
            del progress["failed"][e["slug"]]
    save_progress(output_dir, progress)

    print(json.dumps(wave, indent=2))


def action_mark_done(output_dir: Path, slugs: list[str]) -> None:
    """Mark slugs as completed."""
    progress = load_progress(output_dir)
    for slug in slugs:
        if slug not in progress["completed"]:
            progress["completed"].append(slug)
        if slug in progress.get("in_progress", []):
            progress["in_progress"].remove(slug)
    save_progress(output_dir, progress)
    print(json.dumps({"marked_done": slugs, "total_completed": len(progress["completed"])}))


def action_mark_failed(output_dir: Path, slugs: list[str], reasons: dict) -> None:
    """Mark slugs as failed with reasons."""
    progress = load_progress(output_dir)
    valid_slugs = []
    for slug in slugs:
        if slug not in progress.get("in_progress", []):
            print(f"WARNING: slug '{slug}' is not in in_progress, skipping", file=sys.stderr)
            continue
        valid_slugs.append(slug)
        progress["failed"][slug] = reasons.get(slug, "unknown failure")
        progress["in_progress"].remove(slug)
    save_progress(output_dir, progress)
    print(json.dumps({"marked_failed": valid_slugs, "total_failed": len(progress["failed"])}))


def main():
    parser = argparse.ArgumentParser(description="Capability mapper wave utilities")
    parser.add_argument("--catalog", required=True, help="Path to catalog.json")
    parser.add_argument("--output-dir", required=True, help="Output directory for capability files and progress")
    parser.add_argument("--action", required=True,
                        choices=["load", "status", "next-wave", "mark-done", "mark-failed"],
                        help="Action to perform")
    parser.add_argument("--slugs", default="", help="Comma-separated slugs (for mark-done/mark-failed)")
    parser.add_argument("--reasons", default="{}", help="JSON dict of slug->reason (for mark-failed)")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_catalog(catalog_path)

    if args.action == "load":
        action_load(entries, output_dir)
    elif args.action == "status":
        action_status(entries, output_dir)
    elif args.action == "next-wave":
        action_next_wave(entries, output_dir)
    elif args.action == "mark-done":
        slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
        action_mark_done(output_dir, slugs)
    elif args.action == "mark-failed":
        slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
        reasons = json.loads(args.reasons)
        action_mark_failed(output_dir, slugs, reasons)


if __name__ == "__main__":
    main()
