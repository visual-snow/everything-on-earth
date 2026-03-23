#!/usr/bin/env python3
"""
massive-crawl deterministic pipeline.

Four stages: dedup -> prune -> enrich -> finalize.
Each stage reads a file, transforms it, writes a file.
The dedup, prune, and finalize stages are deterministic with no LLM involvement.
The enrich stage uses the Anthropic API to add tags, categories, and summaries.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --config swarm-config.json --stage prune --min-score 5 --min-stars 20
"""

import argparse
import json
import re
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


def run_prune(
    entries: list[dict],
    min_score: int = 0,
    min_stars: int = 0,
    active_since: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Prune entries by hard cuts (missing fields) and soft cuts (thresholds).

    Returns (kept, pruned_log) where pruned_log explains each removal.
    """
    kept = []
    pruned_log = []

    for entry in entries:
        url = entry.get("repo_url", "").strip()
        desc = entry.get("description", "").strip()
        score = entry.get("score", 0)
        stars = entry.get("stars") or 0
        activity = entry.get("last_activity") or ""

        # Hard cuts
        if not url:
            pruned_log.append({"name": entry.get("name", "?"), "reason": "no_url"})
            continue
        if not desc:
            pruned_log.append({"name": entry.get("name", "?"), "reason": "no_description"})
            continue

        # Soft cuts
        if min_score and score < min_score:
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"min_score ({score} < {min_score})"})
            continue
        if min_stars and stars < min_stars:
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"min_stars ({stars} < {min_stars})"})
            continue
        if active_since and (not activity or activity < active_since):
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"inactive (last: {activity}, cutoff: {active_since})"})
            continue

        kept.append(entry)

    return kept, pruned_log


def strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM responses."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    pattern = r'^```(?:json)?\s*\n(.*?)\n```'
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def enrich_single(entry: dict, topic: str, max_tokens: int = 1024) -> dict:
    """Enrich a single entry using Anthropic API (synchronous, one call per entry).

    Returns {tags, category, summary}.
    """
    import anthropic
    client = anthropic.Anthropic()
    prompt = f"""Given this open-source repository in the "{topic}" domain:

Name: {entry['name']}
Description: {entry['description']}
Language: {entry.get('language', 'unknown')}
Score: {entry.get('score', 'N/A')}

Return a JSON object with:
- "tags": array of 3-5 lowercase normalized topic tags
- "category": a human-readable category name (2-4 words)
- "summary": one-line summary of what makes this repo notable (max 100 chars)

Return ONLY the JSON object, no markdown fences or extra text."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text
    cleaned = strip_code_fences(raw)
    return json.loads(cleaned)


def run_enrich(entries: list[dict], topic: str, max_tokens: int = 1024) -> list[dict]:
    """Enrich all entries with tags, category, and summary.

    INVARIANT: len(output) == len(input). Enrichment never drops entries.
    On individual failure, entry gets empty tags/category/summary rather than being dropped.
    """
    result = []
    for i, entry in enumerate(entries):
        enriched = dict(entry)
        try:
            data = enrich_single(entry, topic, max_tokens)
            enriched["tags"] = data.get("tags", [])
            enriched["category"] = data.get("category")
            enriched["summary"] = data.get("summary")
        except Exception as e:
            print(f"  [enrich] Failed for {entry.get('name', '?')}: {e}", file=sys.stderr)
            enriched["tags"] = []
            enriched["category"] = None
            enriched["summary"] = None
        result.append(enriched)
        print(f"  [enrich] {i+1}/{len(entries)}: {entry.get('name', '?')}")

    assert len(result) == len(entries), f"Enrichment dropped entries: {len(result)} != {len(entries)}"
    return result


def run_finalize(
    entries: list[dict],
    topic: str,
    output_dir: Path,
    template_dir: Path | None = None,
) -> None:
    """Validate, cluster, sort, and produce three output files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"

    # Sort by score descending
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)

    # 1. catalog.json
    catalog_path = output_dir / "catalog.json"
    catalog_path.write_text(json.dumps(entries, indent=2))

    # 2. RESULTS.md via Jinja
    from collections import Counter, defaultdict
    from datetime import datetime
    from jinja2 import Environment, FileSystemLoader

    domain_entries = defaultdict(list)
    for e in entries:
        for d in e.get("found_in_domains", [e.get("sub_domain", "unknown")]):
            domain_entries[d].append(e)

    domains_summary = []
    for d_name in sorted(domain_entries.keys()):
        d_entries = domain_entries[d_name]
        avg = sum(e.get("score", 0) for e in d_entries) / len(d_entries)
        domains_summary.append({"name": d_name, "count": len(d_entries), "avg_score": f"{avg:.1f}"})

    scores = [e.get("score", 0) for e in entries]
    context = {
        "topic": topic,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(entries),
        "domain_count": len(domain_entries),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains": domains_summary,
        "top_repos": [e for e in entries if e.get("score", 0) >= 8],
    }

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    results_tpl = env.get_template("results.md.jinja")
    results_path = output_dir / "RESULTS.md"
    results_path.write_text(results_tpl.render(**context))

    # 3. explorer.html via Jinja
    explorer_tpl = env.get_template("explorer.html")
    explorer_context = {
        "topic": topic,
        "total": len(entries),
        "domain_count": len(domain_entries),
        "catalog_json": json.dumps(entries),
    }
    explorer_path = output_dir / "explorer.html"
    explorer_path.write_text(explorer_tpl.render(**explorer_context))

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")
    print(f"[finalize] Wrote {explorer_path}")


def main():
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
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
            dedup_path = output_dir / "dedup.json"
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
            dedup_path = output_dir / "dedup.json"
            dedup = json.loads(dedup_path.read_text())
            print(f"[prune] Input: {len(dedup)} entries")
            result, pruned_log = run_prune(
                dedup,
                min_score=args.min_score,
                min_stars=args.min_stars,
                active_since=args.active_since,
            )
            print(f"[prune] Kept: {len(result)}, Pruned: {len(pruned_log)}")
            for log in pruned_log:
                print(f"  PRUNED: {log['name']} — {log['reason']}")
            pruned_path = output_dir / "pruned.json"
            pruned_path.write_text(json.dumps(result, indent=2))
            print(f"[prune] Wrote {pruned_path}")
        elif stage == "enrich":
            pruned_path = output_dir / "pruned.json"
            pruned = json.loads(pruned_path.read_text())
            print(f"[enrich] Input: {len(pruned)} entries")
            result = run_enrich(pruned, topic=config["topic"], max_tokens=config["pipeline"]["max_tokens"])
            print(f"[enrich] Output: {len(result)} entries (should equal input)")
            enriched_path = output_dir / "enriched.json"
            enriched_path.write_text(json.dumps(result, indent=2))
            print(f"[enrich] Wrote {enriched_path}")
        elif stage == "finalize":
            enriched_path = output_dir / "enriched.json"
            enriched = json.loads(enriched_path.read_text())
            print(f"[finalize] Input: {len(enriched)} entries")
            out_dir = Path(args.output_dir) if args.output_dir else output_dir
            template_dir = Path(__file__).parent / "templates"
            run_finalize(enriched, topic=config["topic"], output_dir=out_dir, template_dir=template_dir)
        else:
            print(f"Unknown stage: {stage}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
