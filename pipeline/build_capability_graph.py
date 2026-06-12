#!/usr/bin/env python3
"""Deterministic capability graph and export builder.

Reads catalog entries across all domains, extracts capabilities from the
telecoms pilot (which has structured provides[] data), and produces:

  ontology/capability-registry.json
  ontology/aliases.csv
  graph/graph.json
  graph/domains/<domain>.json
  exports/csv/domain-routing.csv
  exports/csv/<domain>-capability-map.csv

Also generates Claude skill artifacts from Jinja2 templates when
--adapter claude is specified.

No LLM calls; fully deterministic.
"""

import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def slugify_capability(raw: str) -> str:
    """Normalize a capability string to a stable ID."""
    s = raw.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def label_from_id(cap_id: str) -> str:
    """Convert capability ID to a human label."""
    return cap_id.replace("-", " ").title()


def load_domain_catalog(catalog_root: Path, domain: str) -> list[dict]:
    """Load catalog.json for a domain, return entries."""
    cat_path = catalog_root / domain / "catalog.json"
    if not cat_path.exists():
        return []
    return json.loads(cat_path.read_text())


def load_entry_json(catalog_root: Path, domain: str, slug: str) -> dict | None:
    """Load per-slug entry.json if it exists."""
    p = catalog_root / domain / slug / "entry.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def list_domains(catalog_root: Path) -> list[str]:
    """Return sorted list of domain directory names under catalog_root."""
    return sorted(
        d.name
        for d in catalog_root.iterdir()
        if d.is_dir() and (d / "catalog.json").exists()
    )


# ---------------------------------------------------------------------------
# Domain routing
# ---------------------------------------------------------------------------

def build_domain_routing(catalog_root: Path, domains: list[str]) -> list[dict]:
    """Build global routing hints from all domain catalogs.

    Each row: domain, keyword_or_alias, source, weight
    Sources: domain_name, sub_domain, tag, category
    """
    rows: list[dict] = []
    for domain in domains:
        # Domain name itself is a strong routing signal
        rows.append({
            "domain": domain,
            "keyword_or_alias": domain,
            "source": "domain_name",
            "weight": 1.0,
        })

        entries = load_domain_catalog(catalog_root, domain)
        sub_domains: set[str] = set()
        tags: set[str] = set()
        categories: set[str] = set()

        for entry in entries:
            # Telecoms uses 'domain'/'secondary_domains'; others use 'sub_domain'
            sd = entry.get("sub_domain") or entry.get("domain", "")
            if sd:
                sub_domains.add(sd.lower())
            for sec in entry.get("secondary_domains", []):
                sub_domains.add(sec.lower())
            for sec in entry.get("found_in_domains", []):
                sub_domains.add(sec.lower())
            for tag in entry.get("tags", []):
                tags.add(tag.lower())
            cat = entry.get("category", "")
            if cat:
                categories.add(cat.lower())

        for sd in sorted(sub_domains):
            rows.append({
                "domain": domain,
                "keyword_or_alias": sd,
                "source": "sub_domain",
                "weight": 0.8,
            })
        for tag in sorted(tags):
            rows.append({
                "domain": domain,
                "keyword_or_alias": tag,
                "source": "tag",
                "weight": 0.5,
            })
        for cat in sorted(categories):
            rows.append({
                "domain": domain,
                "keyword_or_alias": cat,
                "source": "category",
                "weight": 0.6,
            })

    return rows


# ---------------------------------------------------------------------------
# Capability extraction (telecoms pilot)
# ---------------------------------------------------------------------------

def extract_capabilities(
    catalog_root: Path, domain: str
) -> tuple[list[dict], list[dict], list[dict]]:
    """Extract capabilities from a domain with provides[] in entry.json.

    Returns (capabilities, aliases, repo_capability_edges).
    """
    cap_map: dict[str, dict] = {}       # cap_id -> capability entity
    alias_rows: list[dict] = []          # alias CSV rows
    edges: list[dict] = []               # repo-capability edges

    entries = load_domain_catalog(catalog_root, domain)
    for entry in entries:
        slug = entry.get("slug", "")
        if not slug:
            continue

        full_entry = load_entry_json(catalog_root, domain, slug)
        if not full_entry:
            continue

        provides = full_entry.get("provides", [])
        for raw_cap in provides:
            cap_id = slugify_capability(raw_cap)
            if not cap_id:
                continue

            if cap_id not in cap_map:
                cap_map[cap_id] = {
                    "id": cap_id,
                    "label": label_from_id(cap_id),
                    "aliases": [],
                    "description": "",
                    "domains": [domain],
                    "related_capabilities": [],
                    "implemented_by": [],
                    "evidence": [],
                }

            cap = cap_map[cap_id]

            # Track raw form as alias if different from ID
            if raw_cap != cap_id and raw_cap not in cap["aliases"]:
                cap["aliases"].append(raw_cap)
                alias_rows.append({
                    "capability_id": cap_id,
                    "alias": raw_cap,
                    "source": f"{domain}/{slug}",
                })

            # Link repo
            if slug not in cap["implemented_by"]:
                cap["implemented_by"].append(slug)

            # Evidence from factsheet/capability.md
            factsheet_path = catalog_root / domain / slug / "factsheet.json"
            capability_md_path = catalog_root / domain / slug / "capability.md"
            evidence_entry = {"repo_slug": slug, "domain": domain}
            if factsheet_path.exists():
                evidence_entry["factsheet"] = f"{domain}/{slug}/factsheet.json"
            if capability_md_path.exists():
                evidence_entry["capability_doc"] = f"{domain}/{slug}/capability.md"
            cap["evidence"].append(evidence_entry)

            edges.append({
                "repo_slug": slug,
                "capability_id": cap_id,
                "domain": domain,
                "source_field": "provides",
            })

    # Build related_capabilities by co-occurrence within repos
    repo_caps: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        repo_caps[edge["repo_slug"]].append(edge["capability_id"])

    for slug, caps in repo_caps.items():
        for i, c1 in enumerate(caps):
            for c2 in caps[i + 1 :]:
                if c2 not in cap_map[c1]["related_capabilities"]:
                    cap_map[c1]["related_capabilities"].append(c2)
                if c1 not in cap_map[c2]["related_capabilities"]:
                    cap_map[c2]["related_capabilities"].append(c1)

    capabilities = sorted(cap_map.values(), key=lambda c: c["id"])
    return capabilities, alias_rows, edges


# ---------------------------------------------------------------------------
# Graph builders
# ---------------------------------------------------------------------------

def build_domain_graph_slice(
    domain: str,
    capabilities: list[dict],
    edges: list[dict],
    catalog_root: Path,
) -> dict:
    """Build a domain-specific graph slice."""
    entries = load_domain_catalog(catalog_root, domain)
    repos = []
    for entry in entries:
        slug = entry.get("slug", "")
        if not slug:
            continue
        repos.append({
            "slug": slug,
            "name": entry.get("name", slug),
            "repo_url": entry.get("repo_url", ""),
        })

    return {
        "domain": domain,
        "capabilities": capabilities,
        "repos": repos,
        "repo_capability_edges": edges,
    }


def build_global_graph(domain_slices: dict[str, dict]) -> dict:
    """Build global graph from domain slices."""
    all_capabilities: list[dict] = []
    all_edges: list[dict] = []
    seen_cap_ids: set[str] = set()

    for domain, slice_data in sorted(domain_slices.items()):
        for cap in slice_data["capabilities"]:
            if cap["id"] not in seen_cap_ids:
                all_capabilities.append(cap)
                seen_cap_ids.add(cap["id"])
        all_edges.extend(slice_data["repo_capability_edges"])

    return {
        "domains": list(domain_slices.keys()),
        "capabilities": all_capabilities,
        "repo_capability_edges": all_edges,
    }


def build_capability_map_csv(
    domain: str, edges: list[dict], capabilities: list[dict]
) -> list[dict]:
    """Build flat repo/capability mapping CSV rows."""
    cap_labels = {c["id"]: c["label"] for c in capabilities}
    rows = []
    for edge in edges:
        rows.append({
            "repo_slug": edge["repo_slug"],
            "capability_id": edge["capability_id"],
            "capability_label": cap_labels.get(edge["capability_id"], ""),
            "domain": domain,
        })
    return rows


# ---------------------------------------------------------------------------
# Claude skill generation
# ---------------------------------------------------------------------------

def generate_claude_skills(
    output_root: Path,
    pilot_domain: str,
    domains: list[str],
) -> None:
    """Generate Claude skill SKILL.md files from inline templates."""
    # Router skill
    router_dir = REPO_ROOT / "adapters" / "claude" / "skills" / "capability-router"
    router_dir.mkdir(parents=True, exist_ok=True)

    domains_list = "\n".join(f"  - {d}" for d in domains)

    router_skill = f"""\
---
model: disabled
tools:
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Capability Router

Route user questions about open-source tool landscapes to the correct domain
skill using a structured capability graph.

## Trigger

Use this skill when the user asks about open-source tools, capabilities, or
landscapes across any of these domains:
{domains_list}

## Behavior

1. Read the routing context from `capability-graph/exports/csv/domain-routing.csv`
2. Read the workflow contract from `workflows/capability-router/contract.md`
3. Follow the classifier prompt in `workflows/capability-router/prompts/router-classifier.md`
4. Classify the user query to a primary domain (and optional secondary)
5. If the primary domain has a generated domain skill, load it:
   - telecoms -> use the domain-telecoms skill
6. If no generated skill exists for the classified domain, inform the user which
   domain matched and that deep capability routing is not yet available for it.
   Fall back to general catalog search.

## Context Assets

- Routing index: `capability-graph/exports/csv/domain-routing.csv`
- Available domains with generated skills: [{pilot_domain}]
"""
    (router_dir / "SKILL.md").write_text(router_skill)

    # Domain skill (telecoms pilot)
    domain_dir = (
        REPO_ROOT / "adapters" / "claude" / "skills" / f"domain-{pilot_domain}"
    )
    domain_dir.mkdir(parents=True, exist_ok=True)

    domain_skill = f"""\
---
model: disabled
tools:
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Domain: {pilot_domain.title()}

Deep capability-aware navigation of the {pilot_domain} open-source tool catalog.

## Trigger

Use this skill when the user asks about {pilot_domain} tools, capabilities,
protocols, or integration patterns.

## Behavior

1. Load the domain graph slice:
   `capability-graph/graph/domains/{pilot_domain}.json`
2. Load the flat capability map:
   `capability-graph/exports/csv/{pilot_domain}-capability-map.csv`
3. Use the canonical capability registry for definitions and relationships:
   `capability-graph/ontology/capability-registry.json`
4. Treat these assets as precompiled context; do not re-derive capability
   relationships from ad hoc repo searches.
5. Answer the user query using the graph structure:
   - Which repos implement a given capability
   - Which capabilities a given repo provides
   - Related capabilities and cross-repo integration points
   - Evidence traceability back to factsheet.json and capability.md

## Context Assets

- Domain slice: `capability-graph/graph/domains/{pilot_domain}.json`
- Capability map: `capability-graph/exports/csv/{pilot_domain}-capability-map.csv`
- Registry: `capability-graph/ontology/capability-registry.json`
- Aliases: `capability-graph/ontology/aliases.csv`
- Per-repo evidence: `catalog/{pilot_domain}/<slug>/factsheet.json`, `catalog/{pilot_domain}/<slug>/capability.md`
"""
    (domain_dir / "SKILL.md").write_text(domain_skill)


# ---------------------------------------------------------------------------
# CSV/JSON writers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build capability graph and exports from catalog evidence."
    )
    parser.add_argument(
        "--catalog-root",
        type=Path,
        default=REPO_ROOT / "catalog",
        help="Root directory containing domain catalogs",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "capability-graph",
        help="Output directory for graph/ontology/export artifacts",
    )
    parser.add_argument(
        "--pilot-domain",
        default="telecoms",
        help="Domain with structured provides[] data for capability extraction",
    )
    parser.add_argument(
        "--adapter",
        choices=["claude"],
        default=None,
        help="Generate adapter-specific skill artifacts",
    )
    args = parser.parse_args(argv)

    catalog_root: Path = args.catalog_root
    output_root: Path = args.output_root
    pilot_domain: str = args.pilot_domain

    if not catalog_root.exists():
        print(f"Error: catalog root not found: {catalog_root}", file=sys.stderr)
        sys.exit(1)

    domains = list_domains(catalog_root)
    if not domains:
        print(f"Error: no domains found under {catalog_root}", file=sys.stderr)
        sys.exit(1)

    print(f"Domains: {', '.join(domains)}")
    print(f"Pilot domain: {pilot_domain}")

    # 1. Global domain routing CSV
    routing_rows = build_domain_routing(catalog_root, domains)
    write_csv(
        output_root / "exports" / "csv" / "domain-routing.csv",
        routing_rows,
        ["domain", "keyword_or_alias", "source", "weight"],
    )
    print(f"  domain-routing.csv: {len(routing_rows)} rows")

    # 2. Pilot domain capability extraction
    capabilities, alias_rows, edges = extract_capabilities(
        catalog_root, pilot_domain
    )
    print(f"  capabilities: {len(capabilities)}")
    print(f"  aliases: {len(alias_rows)}")
    print(f"  edges: {len(edges)}")

    # 3. Ontology outputs
    write_json(
        output_root / "ontology" / "capability-registry.json",
        capabilities,
    )
    write_csv(
        output_root / "ontology" / "aliases.csv",
        alias_rows,
        ["capability_id", "alias", "source"],
    )

    # 4. Graph outputs
    domain_slice = build_domain_graph_slice(
        pilot_domain, capabilities, edges, catalog_root
    )
    write_json(
        output_root / "graph" / "domains" / f"{pilot_domain}.json",
        domain_slice,
    )

    domain_slices = {pilot_domain: domain_slice}
    global_graph = build_global_graph(domain_slices)
    write_json(output_root / "graph" / "graph.json", global_graph)

    # 5. Capability map CSV
    map_rows = build_capability_map_csv(pilot_domain, edges, capabilities)
    write_csv(
        output_root / "exports" / "csv" / f"{pilot_domain}-capability-map.csv",
        map_rows,
        ["repo_slug", "capability_id", "capability_label", "domain"],
    )
    print(f"  {pilot_domain}-capability-map.csv: {len(map_rows)} rows")

    # 6. Adapter skill generation
    if args.adapter == "claude":
        generate_claude_skills(output_root, pilot_domain, domains)
        print("  Generated Claude skills: capability-router, domain-telecoms")

    print("Done.")


if __name__ == "__main__":
    main()
