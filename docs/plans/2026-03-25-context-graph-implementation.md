# Context Graph Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interactive Cytoscape.js context graph page (`graph.html`) where users select a domain and see tools clustered by sub_domain with click-to-highlight-neighbors interaction.

**Architecture:** New `build_graph_data()` helper transforms catalog entries + edges into Cytoscape compound-node format. `run_site()` calls it per domain and renders a new `graph.html` Jinja2 template. All data is embedded at build time (no runtime API calls).

**Tech Stack:** Cytoscape.js (CDN), cytoscape-cise layout (CDN), Jinja2, existing pipeline infrastructure.

---

### Task 1: Add `build_graph_data()` helper

**Files:**
- Modify: `pipeline/pipeline.py:164` (after `compute_edges`)
- Test: `tests/test_pipeline.py`

**Step 1: Write the failing test**

Add to `tests/test_pipeline.py`:

```python
from pipeline import build_graph_data

def test_build_graph_data_creates_nodes():
    entries = [
        {"slug": "tool-a", "name": "Tool A", "sub_domain": "scanning",
         "quality_score": 80, "stars": 1000, "tags": ["sec"],
         "repo_url": "https://github.com/a/a", "summary": "A scanner",
         "found_in_domains": ["scanning"], "_catalog": "cyber"},
        {"slug": "tool-b", "name": "Tool B", "sub_domain": "scanning",
         "quality_score": 60, "stars": 500, "tags": ["sec"],
         "repo_url": "https://github.com/b/b", "summary": "Another scanner",
         "found_in_domains": ["scanning"], "_catalog": "cyber"},
    ]
    edges = [{"source": "tool-a", "target": "tool-b"}]
    result = build_graph_data(entries, edges, "cyber")
    nodes = result["nodes"]
    edge_list = result["edges"]

    # Should have 2 tool nodes + 1 cluster parent node
    ids = [n["data"]["id"] for n in nodes]
    assert "tool-a" in ids
    assert "tool-b" in ids
    assert "scanning" in ids

    # Tool nodes should have parent set to cluster id
    tool_a = next(n for n in nodes if n["data"]["id"] == "tool-a")
    assert tool_a["data"]["parent"] == "scanning"
    assert tool_a["data"]["label"] == "Tool A"
    assert tool_a["data"]["score"] == 80
    assert tool_a["data"]["stars"] == 1000
    assert tool_a["data"]["detail_url"] == "catalog/cyber/detail/tool-a.html"

    # Cluster node should have label
    cluster = next(n for n in nodes if n["data"]["id"] == "scanning")
    assert cluster["data"]["label"] == "scanning"
    assert "parent" not in cluster["data"]

    # Edges should be wrapped in data
    assert len(edge_list) == 1
    assert edge_list[0]["data"]["source"] == "tool-a"
    assert edge_list[0]["data"]["target"] == "tool-b"


def test_build_graph_data_multiple_clusters():
    entries = [
        {"slug": "a", "name": "A", "sub_domain": "scan",
         "quality_score": 80, "stars": 100, "tags": [],
         "repo_url": "https://github.com/a/a", "summary": "A",
         "found_in_domains": ["scan"], "_catalog": "dom"},
        {"slug": "b", "name": "B", "sub_domain": "auth",
         "quality_score": 70, "stars": 200, "tags": [],
         "repo_url": "https://github.com/b/b", "summary": "B",
         "found_in_domains": ["auth"], "_catalog": "dom"},
    ]
    result = build_graph_data(entries, [], "dom")
    ids = [n["data"]["id"] for n in result["nodes"]]
    assert "scan" in ids
    assert "auth" in ids
    assert len(result["nodes"]) == 4  # 2 tools + 2 clusters


def test_build_graph_data_empty():
    result = build_graph_data([], [], "empty")
    assert result == {"nodes": [], "edges": []}
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_build_graph_data_creates_nodes -v`
Expected: FAIL with "cannot import name 'build_graph_data'"

**Step 3: Write minimal implementation**

Add after `compute_edges()` (line 164) in `pipeline/pipeline.py`:

```python
def build_graph_data(entries: list[dict], edges: list[dict], domain_slug: str) -> dict:
    """Transform catalog entries + edges into Cytoscape.js compound-node format.

    Returns {"nodes": [...], "edges": [...]} where each sub_domain becomes
    a parent (compound) node and tool entries become child nodes.
    """
    if not entries:
        return {"nodes": [], "edges": []}

    # Collect unique sub_domains for cluster parent nodes
    clusters: set[str] = set()
    for e in entries:
        clusters.add(e.get("sub_domain", "unknown"))

    nodes = []

    # Cluster (parent) nodes
    for cluster_id in sorted(clusters):
        nodes.append({
            "data": {"id": cluster_id, "label": cluster_id}
        })

    # Tool (child) nodes
    for e in entries:
        cluster_id = e.get("sub_domain", "unknown")
        nodes.append({
            "data": {
                "id": e["slug"],
                "label": e.get("name", e["slug"]),
                "sub_domain": cluster_id,
                "parent": cluster_id,
                "score": e.get("quality_score", e.get("score", 0)),
                "stars": e.get("stars", 0),
                "tags": e.get("tags", []),
                "repo_url": e.get("repo_url", ""),
                "summary": e.get("summary", e.get("description", "")),
                "detail_url": f"catalog/{domain_slug}/detail/{e['slug']}.html",
            }
        })

    # Wrap edges in Cytoscape format
    cy_edges = [{"data": {"source": edge["source"], "target": edge["target"]}} for edge in edges]

    return {"nodes": nodes, "edges": cy_edges}
```

**Step 4: Update the import line in test file**

Change line 10 of `tests/test_pipeline.py`:
```python
from pipeline import normalize_url, run_dedup, run_score, run_finalize, compute_edges, run_site, build_graph_data
```

**Step 5: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -k "build_graph" -v`
Expected: 3 PASSED

**Step 6: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: add build_graph_data() helper for Cytoscape.js context graph"
```

---

### Task 2: Add graph generation to `run_site()`

**Files:**
- Modify: `pipeline/pipeline.py:267-277` (inside `run_site()`, after explorer generation)
- Test: `tests/test_pipeline.py`

**Step 1: Write the failing test**

Add to `tests/test_pipeline.py`:

```python
def test_site_generates_graph_page_html(tmp_path):
    _make_catalog(tmp_path, "testdom", SAMPLE_ENTRIES)
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_site(tmp_path / "catalog", template_dir=template_dir)

    graph_path = tmp_path / "graph.html"
    assert graph_path.exists()
    content = graph_path.read_text()
    assert "DOMAIN_GRAPHS" in content
    assert "cytoscape" in content.lower()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_site_generates_graph_page_html -v`
Expected: FAIL (graph.html doesn't exist yet OR template not found)

**Step 3: Create a minimal graph.html template placeholder**

Create `pipeline/templates/graph.html`:

```html
<!DOCTYPE html>
<html><head><title>Graph</title></head>
<body>
<script>const DOMAIN_GRAPHS = {{ domain_graphs_json }};const DOMAIN_LIST = {{ domain_list_json }};</script>
<!-- cytoscape placeholder -->
</body></html>
```

**Step 4: Add graph generation to run_site()**

In `pipeline/pipeline.py`, after the explorer generation block (after line 277), add:

```python
    # Generate context graph page
    domain_graphs = {}
    for domain in domain_catalogs:
        entries = domain["entries"]
        edges = compute_edges(entries)
        domain_graphs[domain["slug"]] = build_graph_data(entries, edges, domain["slug"])

    graph_html = env.get_template("graph.html").render(
        domain_graphs_json=json.dumps(domain_graphs),
        domain_list_json=json.dumps([d["slug"] for d in domain_catalogs]),
    )
    graph_path = project_root / "graph.html"
    graph_path.write_text(graph_html)
    print(f"[site] Wrote {graph_path} (context graph)")
```

**Step 5: Run test to verify it passes**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_site_generates_graph_page_html -v`
Expected: PASS

**Step 6: Run all existing tests to check for regressions**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add pipeline/pipeline.py pipeline/templates/graph.html tests/test_pipeline.py
git commit -m "feat: generate graph.html in run_site() with per-domain graph data"
```

---

### Task 3: Build the full graph.html template

**Files:**
- Modify: `pipeline/templates/graph.html` (replace placeholder)

**Step 1: Write the full template**

Replace `pipeline/templates/graph.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Context Graph — Everything on Earth</title>
<script src="https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js"></script>
<script src="https://unpkg.com/cytoscape-cise@1.0.0/cytoscape-cise.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0d1117;
    color: #c9d1d9;
  }
  .toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    background: #11161d;
    border-bottom: 1px solid #30363d;
  }
  .toolbar h1 {
    font-size: 1.1rem;
    color: #58a6ff;
    white-space: nowrap;
  }
  .toolbar a {
    color: #8b949e;
    text-decoration: none;
    font-size: 0.85rem;
  }
  .toolbar a:hover { color: #58a6ff; }
  .toolbar select, .toolbar input {
    background: #161b22;
    border: 1px solid #30363d;
    color: #c9d1d9;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-size: 0.85rem;
  }
  .toolbar select:focus, .toolbar input:focus {
    border-color: #58a6ff;
    outline: none;
  }
  .toolbar input { min-width: 220px; }
  .spacer { flex: 1; }
  #cy {
    width: 100%;
    height: calc(100vh - 56px);
    background: #0d1117;
  }
  #tooltip {
    position: fixed;
    display: none;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    max-width: 320px;
    font-size: 0.82rem;
    color: #c9d1d9;
    pointer-events: none;
    z-index: 100;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  }
  #tooltip .tt-name { color: #58a6ff; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; }
  #tooltip .tt-desc { color: #8b949e; margin-bottom: 0.4rem; line-height: 1.35; }
  #tooltip .tt-meta { display: flex; gap: 0.5rem; flex-wrap: wrap; }
  #tooltip .tt-meta span { background: #21262d; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.75rem; }
  #tooltip .tt-score { color: #3fb950; font-weight: 600; }
  .stats-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #11161d;
    border-top: 1px solid #30363d;
    padding: 0.4rem 1.5rem;
    font-size: 0.78rem;
    color: #8b949e;
    display: flex;
    gap: 1.5rem;
  }
</style>
</head>
<body>
<div class="toolbar">
  <h1>Context Graph</h1>
  <a href="index.html">&larr; Explorer</a>
  <div class="spacer"></div>
  <select id="domain-picker"></select>
  <input type="text" id="search" placeholder="Search tools...">
</div>
<div id="cy"></div>
<div id="tooltip"></div>
<div class="stats-bar">
  <span id="stat-nodes"></span>
  <span id="stat-edges"></span>
  <span id="stat-clusters"></span>
  <span>Click a node to highlight connections. Click background to reset.</span>
</div>

<script>
const DOMAIN_GRAPHS = {{ domain_graphs_json }};
const DOMAIN_LIST = {{ domain_list_json }};

// Color helper
function domainHue(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return Math.abs(hash) % 360;
}

// Populate domain picker
const picker = document.getElementById('domain-picker');
DOMAIN_LIST.forEach((d, i) => {
  const opt = document.createElement('option');
  opt.value = d;
  opt.textContent = d.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  picker.appendChild(opt);
});

let cy = null;
let highlightActive = false;

function loadDomain(slug) {
  const graph = DOMAIN_GRAPHS[slug];
  if (!graph) return;

  // Assign colors per cluster
  const clusters = [...new Set(graph.nodes.filter(n => !n.data.parent).map(n => n.data.id))];
  const clusterHues = {};
  clusters.forEach((c, i) => { clusterHues[c] = (i * 137.508) % 360; });

  // Add hue to nodes
  graph.nodes.forEach(n => {
    const clusterId = n.data.parent || n.data.id;
    n.data._hue = clusterHues[clusterId] || 0;
  });

  if (cy) cy.destroy();

  cy = cytoscape({
    container: document.getElementById('cy'),
    elements: { nodes: graph.nodes, edges: graph.edges },
    style: [
      {
        selector: 'node:parent',
        style: {
          'background-color': 'data(_hue)',
          'background-opacity': 0.08,
          'border-color': function(ele) { return `hsl(${ele.data('_hue')}, 60%, 45%)`; },
          'border-width': 1.5,
          'border-opacity': 0.5,
          'label': 'data(label)',
          'font-size': 14,
          'color': function(ele) { return `hsl(${ele.data('_hue')}, 70%, 70%)`; },
          'text-valign': 'top',
          'text-halign': 'center',
          'text-margin-y': -8,
          'padding': 20,
          'shape': 'roundrectangle',
        }
      },
      {
        selector: 'node:child',
        style: {
          'background-color': function(ele) { return `hsl(${ele.data('_hue')}, 55%, 55%)`; },
          'width': function(ele) { return Math.max(12, Math.min(40, (ele.data('score') || 50) / 100 * 40)); },
          'height': function(ele) { return Math.max(12, Math.min(40, (ele.data('score') || 50) / 100 * 40)); },
          'label': 'data(label)',
          'font-size': 9,
          'color': '#c9d1d9',
          'text-valign': 'bottom',
          'text-halign': 'center',
          'text-margin-y': 4,
          'text-outline-color': '#0d1117',
          'text-outline-width': 2,
          'border-width': 0,
        }
      },
      {
        selector: 'edge',
        style: {
          'line-color': '#30363d',
          'width': 0.8,
          'opacity': 0.3,
          'curve-style': 'bezier',
        }
      },
      {
        selector: '.highlighted',
        style: { 'opacity': 1 }
      },
      {
        selector: '.highlighted-edge',
        style: { 'line-color': '#58a6ff', 'width': 1.5, 'opacity': 0.8 }
      },
      {
        selector: '.dimmed',
        style: { 'opacity': 0.12 }
      },
    ],
    layout: {
      name: 'cise',
      clusters: function() {
        const clusterMap = {};
        cy.nodes(':child').forEach(n => {
          const p = n.data('parent');
          if (!clusterMap[p]) clusterMap[p] = [];
          clusterMap[p].push(n);
        });
        return Object.values(clusterMap);
      },
      animate: false,
      nodeSeparation: 8,
      idealInterClusterEdgeLengthCoefficient: 2.5,
      allowNodesInsideCircle: true,
    },
    minZoom: 0.15,
    maxZoom: 4,
    wheelSensitivity: 0.3,
  });

  // Stats
  const childNodes = cy.nodes(':child');
  const parentNodes = cy.nodes(':parent');
  document.getElementById('stat-nodes').textContent = `${childNodes.length} tools`;
  document.getElementById('stat-edges').textContent = `${cy.edges().length} connections`;
  document.getElementById('stat-clusters').textContent = `${parentNodes.length} clusters`;

  // Tooltip
  const tooltip = document.getElementById('tooltip');
  cy.on('mouseover', 'node:child', function(e) {
    const d = e.target.data();
    const scoreColor = d.score >= 70 ? '#3fb950' : d.score >= 40 ? '#d29922' : '#8b949e';
    tooltip.innerHTML = `
      <div class="tt-name">${d.label}</div>
      <div class="tt-desc">${d.summary || ''}</div>
      <div class="tt-meta">
        <span class="tt-score" style="color:${scoreColor}">${d.score}</span>
        ${d.stars ? `<span>\u2605 ${Number(d.stars).toLocaleString()}</span>` : ''}
        ${(d.tags || []).slice(0, 3).map(t => `<span>${t}</span>`).join('')}
      </div>`;
    tooltip.style.display = 'block';
  });
  cy.on('mousemove', 'node:child', function(e) {
    const x = e.originalEvent.clientX + 12;
    const y = e.originalEvent.clientY + 12;
    tooltip.style.left = Math.min(x, window.innerWidth - 340) + 'px';
    tooltip.style.top = Math.min(y, window.innerHeight - 120) + 'px';
  });
  cy.on('mouseout', 'node:child', function() {
    tooltip.style.display = 'none';
  });

  // Click to highlight neighbors
  cy.on('tap', 'node:child', function(e) {
    const node = e.target;
    const neighborhood = node.neighborhood().add(node);

    cy.elements().addClass('dimmed').removeClass('highlighted highlighted-edge');
    neighborhood.nodes().removeClass('dimmed').addClass('highlighted');
    neighborhood.edges().removeClass('dimmed').addClass('highlighted-edge');

    // Also un-dim parent compounds of highlighted nodes
    neighborhood.nodes().parent().removeClass('dimmed');

    highlightActive = true;
  });

  // Click background to reset
  cy.on('tap', function(e) {
    if (e.target === cy) {
      cy.elements().removeClass('dimmed highlighted highlighted-edge');
      highlightActive = false;
    }
  });

  // Search
  document.getElementById('search').value = '';
}

// Domain switching
picker.addEventListener('change', () => loadDomain(picker.value));

// Search
document.getElementById('search').addEventListener('input', function() {
  if (!cy) return;
  const q = this.value.toLowerCase().trim();
  if (!q) {
    cy.elements().removeClass('dimmed highlighted highlighted-edge');
    highlightActive = false;
    return;
  }
  const matches = cy.nodes(':child').filter(n => {
    const d = n.data();
    return d.label.toLowerCase().includes(q)
      || (d.summary || '').toLowerCase().includes(q)
      || (d.tags || []).some(t => t.toLowerCase().includes(q));
  });
  cy.elements().addClass('dimmed').removeClass('highlighted highlighted-edge');
  matches.removeClass('dimmed').addClass('highlighted');
  matches.parent().removeClass('dimmed');
  // Also highlight edges between matched nodes
  matches.edgesWith(matches).removeClass('dimmed').addClass('highlighted-edge');
  highlightActive = true;
});

// Load first domain
if (DOMAIN_LIST.length > 0) loadDomain(DOMAIN_LIST[0]);
</script>
</body>
</html>
```

**Step 2: Run the pipeline to verify it renders**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python pipeline/pipeline.py --stage site --catalog-root catalog`

Expected: Output includes `[site] Wrote .../graph.html (context graph)`

**Step 3: Open in browser to visually verify**

Run: `open /Users/emolero/Documents/GitHub/ot/everything-on-earth/graph.html`

Expected: Graph renders with clustered bubbles, domain dropdown works, click-to-highlight works.

**Step 4: Commit**

```bash
git add pipeline/templates/graph.html
git commit -m "feat: full Cytoscape.js context graph with CiSE layout and interaction"
```

---

### Task 4: Add "Graph View" link to explorer

**Files:**
- Modify: `pipeline/templates/explorer.html:173-175` (sidebar, after the eyebrow)

**Step 1: Add the link**

In `pipeline/templates/explorer.html`, after line 175 (`<p class="sidebar-copy">...`), add:

```html
    <a href="graph.html" style="display:inline-block;margin-bottom:0.8rem;color:#58a6ff;font-size:0.84rem;text-decoration:none;">View context graph &rarr;</a>
```

**Step 2: Run pipeline to regenerate**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python pipeline/pipeline.py --stage site --catalog-root catalog`

**Step 3: Verify link exists**

Run: `grep "graph.html" /Users/emolero/Documents/GitHub/ot/everything-on-earth/index.html`

Expected: Line containing `href="graph.html"`

**Step 4: Commit**

```bash
git add pipeline/templates/explorer.html
git commit -m "feat: add Graph View link to explorer sidebar"
```

---

### Task 5: Run full test suite and verify

**Files:**
- None (verification only)

**Step 1: Run all pipeline tests**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`

Expected: All tests PASS including new `test_build_graph_data_*` and `test_site_generates_graph_page_html`

**Step 2: Run full site generation**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python pipeline/pipeline.py --stage site --catalog-root catalog`

Expected: No errors, output shows graph.html generation

**Step 3: Open graph.html and verify interaction**

Run: `open /Users/emolero/Documents/GitHub/ot/everything-on-earth/graph.html`

Verify:
- [ ] Domain dropdown shows all domains
- [ ] Switching domains reloads graph
- [ ] Nodes are clustered by sub_domain
- [ ] Hovering shows tooltip
- [ ] Clicking a node dims everything except neighbors
- [ ] Clicking background resets
- [ ] Search highlights matching nodes
- [ ] Stats bar shows correct counts
