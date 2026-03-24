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
from itertools import combinations
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from utils import load_catalog, slugify


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


def compute_edges(entries: list[dict]) -> list[dict]:
    """Compute graph edges for force-graph visualization.

    Two entries are connected if they share a sub-domain or share >=2 tags.
    Returns list of {source: slug, target: slug} dicts, one per unique pair.
    """
    edges: set[frozenset[str]] = set()

    # Edges from shared sub-domains
    domain_groups: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        for d in entry_domains(e):
            domain_groups[d].append(e["slug"])
    for slugs in domain_groups.values():
        for a, b in combinations(slugs, 2):
            edges.add(frozenset((a, b)))

    # Edges from shared tags (>=2)
    tag_index: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        for t in e.get("tags", []):
            tag_index[t].add(e["slug"])
    slug_pairs: dict[frozenset[str], int] = defaultdict(int)
    for slugs in tag_index.values():
        for a, b in combinations(slugs, 2):
            slug_pairs[frozenset((a, b))] += 1
    for pair, count in slug_pairs.items():
        if count >= 2:
            edges.add(pair)

    return [{"source": sorted(pair)[0], "target": sorted(pair)[1]} for pair in edges]


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

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")


def run_site(
    catalog_root: Path,
    template_dir: Path | None = None,
    capability_root: Path | None = None,
) -> None:
    """Generate the full static site: landing + per-domain graph + per-repo detail pages."""
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"
    if capability_root is None:
        capability_root = catalog_root

    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Discover domains
    domain_catalogs: list[dict] = []
    for catalog_path in sorted(catalog_root.glob("*/catalog.json")):
        domain_slug = catalog_path.parent.name
        entries = load_catalog(catalog_path)
        entries = sorted(entries, key=effective_score, reverse=True)
        sub_domains_set = set()
        for e in entries:
            for d in entry_domains(e):
                sub_domains_set.add(d)
        domain_catalogs.append({
            "slug": domain_slug,
            "name": domain_slug.replace("-", " ").title(),
            "entries": entries,
            "count": len(entries),
            "sub_domain_count": len(sub_domains_set),
        })

    if not domain_catalogs:
        print("[site] No catalog.json files found under", catalog_root)
        return

    total_repos = sum(d["count"] for d in domain_catalogs)

    # Generate landing page
    project_root = catalog_root.parent
    landing_html = env.get_template("landing.html").render(
        domains=domain_catalogs,
        total_repos=total_repos,
    )
    landing_path = project_root / "index.html"
    landing_path.write_text(landing_html)
    print(f"[site] Wrote {landing_path}")

    # Generate per-domain pages
    for domain in domain_catalogs:
        entries = domain["entries"]
        domain_dir = catalog_root / domain["slug"]

        # Compute edges
        edges = compute_edges(entries)

        # Build sub-domain list with counts
        sd_counts: dict[str, int] = defaultdict(int)
        for e in entries:
            for d in entry_domains(e):
                sd_counts[d] += 1
        sub_domains = [{"name": n, "count": c} for n, c in sorted(sd_counts.items())]

        stats = {
            "total": len(entries),
            "domain_count": len(sub_domains),
        }

        # Build neighbor index from edges
        neighbors: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            neighbors[edge["source"]].append(edge["target"])
            neighbors[edge["target"]].append(edge["source"])

        # Graph page
        graph_html = env.get_template("graph.html").render(
            domain_name=domain["name"],
            domain_slug=domain["slug"],
            entries_json=json.dumps(entries),
            edges_json=json.dumps(edges),
            sub_domains=sub_domains,
            stats=stats,
        )
        graph_path = domain_dir / "index.html"
        graph_path.write_text(graph_html)
        print(f"[site] Wrote {graph_path} ({len(entries)} nodes, {len(edges)} edges)")

        # Detail pages
        detail_dir = domain_dir / "detail"
        detail_dir.mkdir(parents=True, exist_ok=True)
        slug_to_entry = {e["slug"]: e for e in entries}

        for entry in entries:
            # Read capability.md if available
            cap_path = capability_root / domain["slug"] / entry["slug"] / "capability.md"
            capability_md = cap_path.read_text() if cap_path.exists() else ""

            # Nearby repos from edges
            nearby_slugs = neighbors.get(entry["slug"], [])
            nearby_repos = sorted(
                [slug_to_entry[s] for s in nearby_slugs if s in slug_to_entry],
                key=effective_score,
                reverse=True,
            )[:10]

            detail_html = env.get_template("detail.html").render(
                entry=entry,
                domain_name=domain["name"],
                domain_slug=domain["slug"],
                capability_md=capability_md,
                nearby_repos=nearby_repos,
            )
            detail_path = detail_dir / f"{entry['slug']}.html"
            detail_path.write_text(detail_html)

        print(f"[site]   {len(entries)} detail pages in {detail_dir}")

    print(f"[site] Done: {total_repos} repos across {len(domain_catalogs)} domains")


def main():
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
    parser.add_argument("--config", default=None, help="Path to swarm-config.json")
    parser.add_argument("--stage", default="dedup,score,finalize",
                        help="Comma-separated stages to run (default: all)")
    parser.add_argument("--input-dir", default=".", help="Directory containing input files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: from config)")
    parser.add_argument("--catalog-root", default=None, help="Root catalog directory (for site stage)")
    parser.add_argument("--capability-root", default=None, help="Root directory for capability.md files")
    args = parser.parse_args()

    stages = [s.strip() for s in args.stage.split(",")]

    # Site stage doesn't need --config
    if "site" in stages:
        catalog_root = Path(args.catalog_root) if args.catalog_root else Path("catalog")
        capability_root = Path(args.capability_root) if args.capability_root else None
        template_dir = Path(__file__).parent / "templates"
        run_site(catalog_root, template_dir=template_dir, capability_root=capability_root)
        return

    if not args.config:
        print("Error: --config is required for dedup/score/finalize stages", file=sys.stderr)
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
