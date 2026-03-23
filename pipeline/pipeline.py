#!/usr/bin/env python3
"""
everything-on-earth deterministic pipeline.

Four stages: dedup -> prune -> enrich -> finalize.
Each stage reads a file, transforms it, writes a file.
No LLM touches data after discovery. All operations are exact and auditable.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --config swarm-config.json --stage prune --min-score 5 --min-stars 20
"""

import argparse
import json
import sys
from pathlib import Path


def normalize_url(url: str) -> str:
    """Normalize a repo URL: lowercase, strip trailing slash, remove .git suffix."""
    url = url.strip().lower()
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    return url


def run_dedup(entries: list[dict]) -> list[dict]:
    """Deduplicate entries by normalized repo_url. Keep highest-scoring entry on collision."""
    seen: dict[str, dict] = {}
    domain_tracker: dict[str, list[str]] = {}

    for entry in entries:
        key = normalize_url(entry["repo_url"])
        if not key:
            continue

        # Track all sub-domains that found this URL
        if key not in domain_tracker:
            domain_tracker[key] = []
        sub_domain = entry.get("sub_domain", "unknown")
        if sub_domain not in domain_tracker[key]:
            domain_tracker[key].append(sub_domain)

        # Keep entry with highest score
        if key not in seen or entry.get("score", 0) > seen[key].get("score", 0):
            seen[key] = dict(entry)
            seen[key]["repo_url"] = key  # Normalize the URL in the kept entry

    # Attach found_in_domains to each surviving entry
    result = []
    for key, entry in seen.items():
        entry["found_in_domains"] = domain_tracker[key]
        result.append(entry)

    assert len(result) <= len(entries), f"Dedup expanded data: {len(result)} > {len(entries)}"
    return result


def main():
    parser = argparse.ArgumentParser(description="everything-on-earth deterministic pipeline")
    parser.add_argument("--config", required=True, help="Path to swarm-config.json")
    parser.add_argument("--stage", default="dedup,prune,enrich,finalize",
                        help="Comma-separated stages to run (default: all)")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum score for pruning")
    parser.add_argument("--min-stars", type=int, default=0, help="Minimum stars for pruning")
    parser.add_argument("--active-since", default=None, help="Minimum last_activity date (YYYY-MM-DD)")
    parser.add_argument("--input-dir", default=".", help="Directory containing input files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: from config)")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text())
    stages = [s.strip() for s in args.stage.split(",")]
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else Path(config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    for stage in stages:
        if stage == "dedup":
            raw_path = input_dir / "raw-discovery.json"
            raw = json.loads(raw_path.read_text())
            print(f"[dedup] Input: {len(raw)} entries")
            result = run_dedup(raw)
            print(f"[dedup] Output: {len(result)} unique entries ({len(raw) - len(result)} duplicates removed)")
            dedup_path = input_dir / "dedup.json"
            dedup_path.write_text(json.dumps(result, indent=2))
            print(f"[dedup] Wrote {dedup_path}")

            # Print distribution summary
            from collections import Counter
            domains = Counter()
            for entry in result:
                for d in entry.get("found_in_domains", [entry.get("sub_domain", "unknown")]):
                    domains[d] += 1
            print("\n[dedup] Distribution by sub-domain:")
            for domain, count in domains.most_common():
                print(f"  {domain}: {count}")

        elif stage == "prune":
            print(f"[prune] Not yet implemented")
            sys.exit(1)
        elif stage == "enrich":
            print(f"[enrich] Not yet implemented")
            sys.exit(1)
        elif stage == "finalize":
            print(f"[finalize] Not yet implemented")
            sys.exit(1)
        else:
            print(f"Unknown stage: {stage}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
