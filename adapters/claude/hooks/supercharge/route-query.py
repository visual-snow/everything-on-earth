#!/usr/bin/env python3
"""UserPromptSubmit hook: keyword-match user prompts against the domain routing
index and inject relevant domain context into Claude's conversation.

Reads JSON from stdin (UserPromptSubmit event), writes additional context to
stdout. Only injects context when the prompt clearly matches a domain.
"""

import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
GRAPH_ROOT = PROJECT_DIR / "capability-graph"
ROUTING_CSV = GRAPH_ROOT / "exports" / "csv" / "domain-routing.csv"

# Domains with generated capability graph slices
DEEP_DOMAINS = {"telecoms"}

# Minimum score to inject context (avoid noise on generic queries)
MIN_SCORE = 1.5


def load_routing_index() -> dict[str, list[tuple[str, float]]]:
    """Load routing CSV into domain -> [(keyword, weight)] mapping."""
    index: dict[str, list[tuple[str, float]]] = defaultdict(list)
    if not ROUTING_CSV.exists():
        return index
    with open(ROUTING_CSV) as f:
        for row in csv.DictReader(f):
            index[row["domain"]].append(
                (row["keyword_or_alias"].lower(), float(row["weight"]))
            )
    return index


def score_query(prompt: str, index: dict[str, list[tuple[str, float]]]) -> list[tuple[str, float]]:
    """Score each domain against the user prompt. Return sorted (domain, score) pairs.

    Handles compound keywords like '5g-core-network' by splitting on hyphens
    and scoring based on how many parts match prompt tokens. A full compound
    match scores higher than partial matches.
    """
    prompt_lower = prompt.lower()
    # Normalize punctuation for token extraction
    prompt_normalized = prompt_lower.replace("-", " ").replace("/", " ").replace(".", " ")
    tokens = set(prompt_normalized.split())
    scores: dict[str, float] = {}

    for domain, keywords in index.items():
        score = 0.0
        for keyword, weight in keywords:
            # Split compound keyword into parts
            parts = keyword.replace("/", "-").split("-")
            parts = [p for p in parts if p]

            if not parts:
                continue

            if len(parts) == 1:
                # Simple keyword: exact token match
                if parts[0] in tokens:
                    score += weight
            else:
                # Compound keyword: score by fraction of parts matched
                matched = sum(1 for p in parts if p in tokens)
                if matched > 0:
                    fraction = matched / len(parts)
                    # Full match gets full weight; partial gets proportional
                    # Bonus for multi-part matches to reward specificity
                    specificity_bonus = 1.0 + (matched - 1) * 0.3
                    score += weight * fraction * specificity_bonus

        if score > 0:
            scores[domain] = round(score, 2)

    return sorted(scores.items(), key=lambda x: -x[1])


def load_domain_summary(domain: str) -> str:
    """Load a concise summary for a matched domain."""
    slice_path = GRAPH_ROOT / "graph" / "domains" / f"{domain}.json"
    map_path = GRAPH_ROOT / "exports" / "csv" / f"{domain}-capability-map.csv"

    parts = []
    if slice_path.exists():
        data = json.loads(slice_path.read_text())
        cap_count = len(data.get("capabilities", []))
        repo_count = len(data.get("repos", []))
        edge_count = len(data.get("repo_capability_edges", []))
        parts.append(
            f"{domain}: {cap_count} capabilities, {repo_count} repos, "
            f"{edge_count} edges"
        )
        # Top 10 most-connected capabilities
        cap_impl_counts = {
            c["id"]: len(c.get("implemented_by", []))
            for c in data.get("capabilities", [])
        }
        top_caps = sorted(cap_impl_counts.items(), key=lambda x: -x[1])[:10]
        if top_caps:
            parts.append("Top capabilities: " + ", ".join(
                f"{cid} ({n} repos)" for cid, n in top_caps
            ))
        parts.append(f"Graph slice: capability-graph/graph/domains/{domain}.json")
        if map_path.exists():
            parts.append(f"Flat map: capability-graph/exports/csv/{domain}-capability-map.csv")
    else:
        # Domain without deep graph; just note routing matched
        catalog_path = PROJECT_DIR / "catalog" / domain / "catalog.json"
        if catalog_path.exists():
            entries = json.loads(catalog_path.read_text())
            parts.append(f"{domain}: {len(entries)} catalog entries (no deep capability graph yet)")
            parts.append(f"Catalog: catalog/{domain}/catalog.json")

    return "\n".join(parts)


def main() -> None:
    if not ROUTING_CSV.exists():
        sys.exit(0)

    event = json.load(sys.stdin)
    prompt = event.get("prompt", "")
    if not prompt:
        sys.exit(0)

    index = load_routing_index()
    ranked = score_query(prompt, index)

    if not ranked or ranked[0][1] < MIN_SCORE:
        sys.exit(0)

    primary_domain, primary_score = ranked[0]
    secondary = None
    if len(ranked) > 1 and ranked[1][1] >= primary_score * 0.8:
        secondary = ranked[1][0]

    lines = [f"<supercharge-route domain=\"{primary_domain}\" score=\"{primary_score:.1f}\">"]
    lines.append(load_domain_summary(primary_domain))

    if secondary:
        lines.append(f"\nSecondary match: {secondary}")
        lines.append(load_domain_summary(secondary))

    if primary_domain in DEEP_DOMAINS:
        lines.append(
            f"\nDeep routing available. Use capability-graph/graph/domains/{primary_domain}.json "
            "and capability-graph/ontology/capability-registry.json for structured answers."
        )

    lines.append("</supercharge-route>")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
