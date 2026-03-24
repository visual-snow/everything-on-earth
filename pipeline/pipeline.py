#!/usr/bin/env python3
"""
massive-crawl deterministic pipeline.

Three stages: dedup -> score -> finalize.
Each stage reads a file, transforms it, writes a file.
All stages are deterministic with no LLM involvement.
Enrichment (tags, category, summary) is handled by Claude Code subagents
between score and finalize — see skill/massive-crawl/SKILL.md.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --config swarm-config.json --stage score
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
    """Sort, cluster, and produce catalog.json, RESULTS.md, explorer.html."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"

    entries = sorted(entries, key=effective_score, reverse=True)

    catalog_path = output_dir / "catalog.json"
    catalog_path.write_text(json.dumps(entries, indent=2))

    domain_entries = defaultdict(list)
    for e in entries:
        for d in entry_domains(e):
            domain_entries[d].append(e)

    domains_summary = []
    for d_name in sorted(domain_entries.keys()):
        d_entries = domain_entries[d_name]
        avg = sum(e.get("score", 0) for e in d_entries) / len(d_entries)
        domains_summary.append({"name": d_name, "count": len(d_entries), "avg_score": f"{avg:.1f}"})

    scores = [effective_score(e) for e in entries]
    context = {
        "topic": topic,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(entries),
        "domain_count": len(domain_entries),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains": domains_summary,
        "top_repos": [e for e in entries if effective_score(e) >= 70],
    }

    env = Environment(loader=FileSystemLoader(str(template_dir)))

    results_path = output_dir / "RESULTS.md"
    results_path.write_text(env.get_template("results.md.jinja").render(**context))

    explorer_path = output_dir / "explorer.html"
    explorer_path.write_text(env.get_template("explorer.html").render(
        topic=topic, total=len(entries),
        domain_count=len(domain_entries), catalog_json=json.dumps(entries),
    ))

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")
    print(f"[finalize] Wrote {explorer_path}")


def main():
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
    parser.add_argument("--config", required=True, help="Path to swarm-config.json")
    parser.add_argument("--stage", default="dedup,score,finalize",
                        help="Comma-separated stages to run (default: all)")
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
            dedup_path = output_dir / "dedup.json"
            dedup_path.write_text(json.dumps(result, indent=2))
            print(f"[dedup] Wrote {dedup_path}")

            domains = Counter()
            for entry in result:
                for d in entry_domains(entry):
                    domains[d] += 1
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
