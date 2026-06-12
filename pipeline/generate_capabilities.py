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
import os
import sys
from pathlib import Path

from utils import load_catalog, slugify

TIER_BATCH_SIZE = {1: 10, 2: 5, 3: 3}
TIER_JUDGE_SCOPE = {1: 5, 2: 3, 3: 1}
BOOTSTRAP_SIZE = 5


def classify_tier(entry: dict) -> int:
    """Classify a catalog entry into quality tiers based on stars.

    Tier 1 (>500 stars): well-known, standard processing
    Tier 2 (50-500 stars): mid-tier, extra writer exemplars
    Tier 3 (<50 stars): obscure, deep research + strict validation
    """
    stars = entry.get("stars") or 0
    if stars > 500:
        return 1
    if stars >= 50:
        return 2
    return 3


def build_wave_manifest(entries: list[dict], wave_number: int, domain: str,
                        total_entries: int, output_dir: Path) -> dict:
    """Build wave-manifest.json with tier metadata and style anchors."""
    slugs = []
    for entry in entries:
        tier = classify_tier(entry)
        slugs.append({
            "slug": entry["slug"],
            "tier": tier,
            "stars": entry.get("stars", 0),
        })

    style_anchors = _collect_style_anchors(output_dir, max_anchors=2)

    return {
        "wave": wave_number,
        "domain": domain,
        "total_entries": total_entries,
        "slugs": slugs,
        "batch_size": dict(TIER_BATCH_SIZE),
        "judge_scope": dict(TIER_JUDGE_SCOPE),
        "style_anchors": style_anchors,
    }


def _collect_style_anchors(output_dir: Path, max_anchors: int = 2) -> list[str]:
    """Find approved capability.md files to use as style anchors."""
    anchors = []
    if not output_dir.exists():
        return anchors
    progress_path = output_dir / "wave-progress.json"
    if not progress_path.exists():
        return anchors
    progress = json.loads(progress_path.read_text())
    for slug in progress.get("completed", []):
        cap_path = output_dir / slug / "capability.md"
        if cap_path.exists() and len(anchors) < max_anchors:
            anchors.append(str(cap_path))
    return anchors


def slug_dir(output_dir: Path, slug: str) -> Path:
    """Return and ensure the per-slug output directory exists."""
    d = output_dir / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


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


def write_config(catalog_path: Path, output_dir: Path, total_entries: int) -> None:
    """Write map-capabilities-config.json for hooks to discover paths."""
    config_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    config = {
        "catalog": str(catalog_path.resolve()),
        "output_dir": str(output_dir.resolve()),
        "catalog_name": catalog_path.stem,
        "total_entries": total_entries,
    }
    config_path = Path(config_dir) / "map-capabilities-config.json"
    config_path.write_text(json.dumps(config, indent=2))
    print(f"Wrote {config_path}", file=sys.stderr)


def action_load(entries: list[dict], output_dir: Path, do_write_config: bool = False,
                catalog_path: Path | None = None) -> None:
    """Print catalog summary with tier distribution and initialize progress if needed."""
    if do_write_config and catalog_path:
        write_config(catalog_path, output_dir, len(entries))

    progress = load_progress(output_dir)
    pending = get_pending(entries, progress)
    retries = get_retry_queue(progress)

    tier_counts = {1: 0, 2: 0, 3: 0}
    for e in entries:
        tier_counts[classify_tier(e)] += 1

    pending_by_tier = {1: 0, 2: 0, 3: 0}
    for e in pending:
        pending_by_tier[classify_tier(e)] += 1
    estimated_waves = sum(
        (pending_by_tier[t] + TIER_BATCH_SIZE[t] - 1) // TIER_BATCH_SIZE[t]
        for t in [1, 2, 3]
    )
    estimated_waves += (len(retries) + TIER_BATCH_SIZE[2] - 1) // TIER_BATCH_SIZE[2]

    print(json.dumps({
        "total_entries": len(entries),
        "completed": len(progress["completed"]),
        "failed": len(progress.get("failed", {})),
        "pending": len(pending),
        "retry_queue": len(retries),
        "waves_remaining": estimated_waves,
        "tiers": {"t1": tier_counts[1], "t2": tier_counts[2], "t3": tier_counts[3]},
    }, indent=2))


def action_status(entries: list[dict], output_dir: Path) -> None:
    """Print detailed progress status."""
    progress = load_progress(output_dir)
    pending = get_pending(entries, progress)

    print(json.dumps({
        "completed": progress["completed"],
        "failed": progress.get("failed", {}),
        "in_progress": progress.get("in_progress", []),
        "pending_slugs": [e["slug"] for e in pending[:TIER_BATCH_SIZE[1]]],
        "total_pending": len(pending),
    }, indent=2))


def _infer_wave_number(progress: dict) -> int:
    """Infer current wave number from completed count."""
    completed = len(progress.get("completed", []))
    return (completed // TIER_BATCH_SIZE[2]) + 1


def _is_bootstrap_needed(output_dir: Path) -> bool:
    """Check if this is the first wave (no approved outputs yet)."""
    progress_path = output_dir / "wave-progress.json"
    if not progress_path.exists():
        return True
    progress = json.loads(progress_path.read_text())
    return len(progress.get("completed", [])) == 0


def _infer_domain(entries: list[dict]) -> str:
    """Infer domain name from catalog entries."""
    if entries and "found_in_domains" in entries[0]:
        return entries[0]["found_in_domains"][0]
    return "unknown"


def action_next_wave(entries: list[dict], output_dir: Path) -> None:
    """Output the next wave of entries, tier-sorted with adaptive batch sizes."""
    progress = load_progress(output_dir)

    # Recover stranded in_progress entries
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
    for entry in retry_entries:
        entry_with_feedback = dict(entry)
        entry_with_feedback["_retry_reason"] = progress["failed"][entry["slug"]]
        wave.append(entry_with_feedback)

    if not wave and not pending:
        print(json.dumps({"done": True, "message": "All entries processed"}))
        return

    # Bootstrap mode: pick T1 entries first to create style anchors
    bootstrap = _is_bootstrap_needed(output_dir)
    if bootstrap and not wave:
        t1 = [e for e in pending if classify_tier(e) == 1]
        wave.extend(t1[:BOOTSTRAP_SIZE])
        # If not enough T1, fill with T2
        if len(wave) < BOOTSTRAP_SIZE:
            t2 = [e for e in pending if classify_tier(e) == 2]
            wave.extend(t2[:BOOTSTRAP_SIZE - len(wave)])
    elif not wave:
        # Normal mode: single-tier waves for judge coherence
        tiered = {1: [], 2: [], 3: []}
        for e in pending:
            tiered[classify_tier(e)].append(e)

        # Process T3 first (hardest), then T2, then T1
        for tier in [3, 2, 1]:
            if tiered[tier]:
                batch_size = TIER_BATCH_SIZE[tier]
                wave.extend(tiered[tier][:batch_size])
                break

    if not wave:
        print(json.dumps({"done": True, "message": "All entries processed"}))
        return

    # Mark as in_progress
    progress["in_progress"] = [e["slug"] for e in wave]
    for e in wave:
        if e["slug"] in progress.get("failed", {}):
            del progress["failed"][e["slug"]]
    save_progress(output_dir, progress)

    # Write wave manifest for hooks
    entry_lookup = {e["slug"]: e for e in entries}
    manifest_entries = [entry_lookup.get(e["slug"], e) for e in wave]
    domain = _infer_domain(entries)
    manifest = build_wave_manifest(manifest_entries, _infer_wave_number(progress),
                                   domain, len(entries), output_dir)
    (output_dir / "wave-manifest.json").write_text(json.dumps(manifest, indent=2))

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
    parser.add_argument("--write-config", action="store_true",
                        help="Write map-capabilities-config.json for hook discovery (use with --action load)")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_catalog(catalog_path)

    if args.action == "load":
        action_load(entries, output_dir, do_write_config=args.write_config,
                    catalog_path=catalog_path)
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
