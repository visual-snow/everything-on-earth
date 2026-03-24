#!/usr/bin/env python3
"""
massive-crawl deterministic pipeline.

Four stages: dedup -> score -> finalize -> explorer.
dedup, score, finalize operate per-domain via --config.
explorer aggregates all domains via --catalog-root.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --stage explorer --catalog-root catalog/
"""

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def effective_score(entry: dict) -> float:
    return entry.get("quality_score", entry.get("score", 0))


def entry_domains(entry: dict) -> list[str]:
    return entry.get("found_in_domains", [entry.get("sub_domain", "unknown")])


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

        if key not in domain_tracker:
            domain_tracker[key] = []
        sub_domain = entry.get("sub_domain", "unknown")
        if sub_domain not in domain_tracker[key]:
            domain_tracker[key].append(sub_domain)

        if key not in seen or entry.get("score", 0) > seen[key].get("score", 0):
            seen[key] = dict(entry)
            seen[key]["repo_url"] = key

    result = []
    for key, entry in seen.items():
        entry["found_in_domains"] = domain_tracker[key]
        result.append(entry)

    assert len(result) <= len(entries), f"Dedup expanded data: {len(result)} > {len(entries)}"
    return result


def run_score(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """Score entries using agent data. Hard cuts for data quality only.

    No soft thresholds, no API calls. Everything that passes hard cuts stays.
    Returns (scored_entries, removed_log).
    """
    scored = []
    removed_log = []

    for entry in entries:
        url = entry.get("repo_url", "").strip()
        desc = entry.get("description", "").strip()

        if not url:
            removed_log.append({"name": entry.get("name", "?"), "reason": "no_url"})
            continue
        if not desc:
            removed_log.append({"name": entry.get("name", "?"), "reason": "no_description"})
            continue

        agent_score = entry.get("score", 0)
        stars = entry.get("stars") or 0

        # Weights: agent relevance (0-10 scaled to 0-60) + log-scaled stars (0-40)
        star_component = min(math.log10(max(stars, 1) + 1) / 5.0, 1.0) * 40
        scored.append({**entry, "quality_score": round(agent_score * 6 + star_component, 1)})

    return scored, removed_log


def run_finalize(
    entries: list[dict],
    topic: str,
    output_dir: Path,
    template_dir: Path | None = None,
) -> None:
    """Validate, cluster, sort, and produce catalog.json and RESULTS.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"

    entries = sorted(entries, key=effective_score, reverse=True)

    catalog_path = output_dir / "catalog.json"
    catalog_path.write_text(json.dumps(entries, indent=2))

    domain_entries = defaultdict(list)
    for entry in entries:
        for domain in entry_domains(entry):
            domain_entries[domain].append(entry)

    domains_summary = []
    for domain_name in sorted(domain_entries.keys()):
        domain_items = domain_entries[domain_name]
        avg = sum(item.get("score", 0) for item in domain_items) / len(domain_items)
        domains_summary.append({"name": domain_name, "count": len(domain_items), "avg_score": f"{avg:.1f}"})

    scores = [effective_score(entry) for entry in entries]
    context = {
        "topic": topic,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(entries),
        "domain_count": len(domain_entries),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains": domains_summary,
        "top_repos": [entry for entry in entries if effective_score(entry) >= 70],
    }

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    results_path = output_dir / "RESULTS.md"
    results_path.write_text(env.get_template("results.md.jinja").render(**context))

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")


def run_explorer(
    catalog_root: Path,
    template_dir: Path | None = None,
) -> None:
    """Merge all domain catalogs and render a single top-level explorer.html."""
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"

    all_entries = []
    for catalog_path in sorted(catalog_root.glob("*/catalog.json")):
        domain_name = catalog_path.parent.name
        entries = json.loads(catalog_path.read_text())
        for entry in entries:
            entry["domain"] = domain_name
        all_entries.extend(entries)

    all_entries.sort(key=effective_score, reverse=True)
    domains = sorted({entry["domain"] for entry in all_entries})

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    explorer_path = catalog_root / "explorer.html"
    explorer_path.write_text(
        env.get_template("explorer.html").render(
            topic="Everything on Earth",
            total=len(all_entries),
            domain_count=len(domains),
            catalog_json=json.dumps(all_entries),
        )
    )

    print(f"[explorer] Merged {len(all_entries)} entries from {len(domains)} domains")
    print(f"[explorer] Wrote {explorer_path}")


def main():
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
    parser.add_argument("--config", default=None, help="Path to swarm-config.json")
    parser.add_argument(
        "--stage",
        default="dedup,score,finalize",
        help="Comma-separated stages to run (default: dedup,score,finalize)",
    )
    parser.add_argument("--input-dir", default=".", help="Directory containing input files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: from config)")
    parser.add_argument("--catalog-root", default=None, help="Root catalog dir for explorer stage")
    args = parser.parse_args()

    stages = [stage.strip() for stage in args.stage.split(",")]

    if "explorer" in stages:
        if not args.catalog_root:
            print("--catalog-root is required for explorer stage", file=sys.stderr)
            sys.exit(1)
        catalog_root = Path(args.catalog_root)
        template_dir = Path(__file__).parent / "templates"
        run_explorer(catalog_root=catalog_root, template_dir=template_dir)
        stages = [stage for stage in stages if stage != "explorer"]

    if not stages:
        return

    if not args.config:
        print("--config is required for dedup/score/finalize stages", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path(args.config).read_text())
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
            dedup_path = output_dir / "dedup.json"
            dedup_path.write_text(json.dumps(result, indent=2))
            print(f"[dedup] Wrote {dedup_path}")

            domains = Counter()
            for entry in result:
                for domain in entry_domains(entry):
                    domains[domain] += 1
            print("\n[dedup] Distribution by sub-domain:")
            for domain, count in domains.most_common():
                print(f"  {domain}: {count}")

        elif stage == "score":
            dedup_path = output_dir / "dedup.json"
            dedup = json.loads(dedup_path.read_text())
            print(f"[score] Input: {len(dedup)} entries")
            result, removed_log = run_score(dedup)
            print(f"[score] Kept: {len(result)}, Removed: {len(removed_log)}")
            for log in removed_log:
                print(f"  REMOVED: {log['name']} — {log['reason']}")
            scored_path = output_dir / "scored.json"
            scored_path.write_text(json.dumps(result, indent=2))
            print(f"[score] Wrote {scored_path}")
        elif stage == "finalize":
            enriched_path = output_dir / "enriched.json"
            enriched = json.loads(enriched_path.read_text())
            print(f"[finalize] Input: {len(enriched)} entries")
            template_dir = Path(__file__).parent / "templates"
            run_finalize(enriched, topic=config["topic"], output_dir=output_dir, template_dir=template_dir)
        else:
            print(f"Unknown stage: {stage}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
