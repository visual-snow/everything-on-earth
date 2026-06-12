# Context Graph Design

## Overview

Interactive discovery graph for all open-source tools in the catalog. Users select a domain (e.g., cybersecurity) and see tools clustered by sub_domain as visual bubbles, with edges connecting related tools. Clicking a node highlights its neighbors, dimming everything else — answering "if I use this tool, what else do I need?"

## Decisions

- **Library:** Cytoscape.js + CiSE layout extension
- **Visualization:** Clustered bubbles by sub_domain, one domain at a time
- **Interaction:** Click node → highlight connected tools, dim rest. Hover → tooltip. Search → filter/highlight.
- **Edges:** Inferred from existing metadata (shared sub_domain, 2+ shared tags) via existing `compute_edges()`
- **Deployment:** Separate `graph.html` page, linked from explorer and detail pages
- **Data:** All graph data embedded at build time (same static site pattern as explorer)

## Data Model

### Nodes

Each catalog entry becomes a Cytoscape node:

```json
{
  "data": {
    "id": "anchore-grype",
    "label": "Grype",
    "sub_domain": "Vulnerability Scanning",
    "parent": "vulnerability-scanning",
    "score": 85,
    "stars": 8200,
    "tags": ["security", "sbom", "container"],
    "repo_url": "https://github.com/anchore/grype",
    "detail_url": "catalog/cybersecurity/detail/anchore-grype.html"
  }
}
```

### Cluster (parent) nodes

One compound node per sub_domain acts as the visual bubble container:

```json
{
  "data": { "id": "vulnerability-scanning", "label": "Vulnerability Scanning" }
}
```

### Edges

From existing `compute_edges()`:

```json
{ "data": { "source": "anchore-grype", "target": "anchore-syft" } }
```

## Visual Design

- **Layout:** CiSE — tools arranged in circles per sub_domain, clusters positioned by force-directed algorithm
- **Node size:** Scaled by quality_score
- **Node color:** Mapped by sub_domain (distinct hue per cluster)
- **Cluster boundary:** Translucent bubble with sub_domain label
- **Edges:** Thin, low-opacity lines; highlighted on node click
- **Theme:** Obsidian Monolith — #0d1117 background, #58a6ff accent, Space Grotesk font

## Interaction

1. **Hover** — tooltip with name, description, stars, score
2. **Click node** — neighborhood highlight: clicked node + direct connections full opacity, rest dims to 15%
3. **Click background** — reset highlight
4. **Domain dropdown** — switches graph to different domain's data
5. **Search** — text input filters/highlights matching nodes

## Pipeline Integration

### New file: `pipeline/templates/graph.html`

Jinja2 template with Cytoscape.js loaded via CDN. Domain graph data injected at build time.

### Pipeline change: `run_site()` in `pipeline/pipeline.py`

After existing explorer generation, build graph data for each domain and render `graph.html`:

```python
domain_graphs = {}
for domain in domain_catalogs:
    entries = domain["entries"]
    edges = compute_edges(entries)
    domain_graphs[domain["slug"]] = build_graph_data(entries, edges)

graph_html = env.get_template("graph.html").render(
    domain_graphs_json=json.dumps(domain_graphs),
    domain_list_json=json.dumps([d["slug"] for d in domain_catalogs]),
)
(project_root / "graph.html").write_text(graph_html)
```

### New helper: `build_graph_data(entries, edges)`

Transforms flat catalog entries into Cytoscape's `{ nodes: [...], edges: [...] }` format with parent/compound nodes for sub_domain clusters.

### Linking

Add "Graph View" link on `explorer.html` and detail pages pointing to `/graph.html`.

## Tech Stack

| Component | Choice | Size (gzip) |
|-----------|--------|-------------|
| Graph engine | Cytoscape.js v3.33+ | ~131 KB |
| Layout | cytoscape-cise | ~8 KB |
| Data | Build-time JSON embedding | 0 (no runtime fetch) |
| Styling | Inline CSS (Obsidian Monolith tokens) | — |
