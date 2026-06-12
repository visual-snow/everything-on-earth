# Global Explorer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace per-domain explorer.html with a single top-level explorer that aggregates all domain catalogs, with domain filtering and color-coded domain badges.

**Architecture:** A new `explorer` pipeline stage globs `catalog/*/catalog.json`, merges entries with a `domain` field injected from the folder name, and renders an updated explorer.html template to `catalog/explorer.html`. The finalize stage no longer generates explorer.html.

**Tech Stack:** Python 3, Jinja2, vanilla HTML/CSS/JS

---

### Task 1: Remove explorer.html generation from run_finalize

**Files:**
- Modify: `pipeline/pipeline.py:149-162`

**Step 1: Write the failing test**

In `tests/test_pipeline.py`, update the existing finalize test to assert explorer.html is NOT produced:

```python
def test_finalize_produces_catalog_and_results_only(tmp_path):
    entries = [
        {
            "repo_url": "https://github.com/a/b", "name": "a/b", "description": "Tool A",
            "sub_domain": "scanning", "score": 9, "quality_score": 85.2, "discovery_score": 9,
            "stars": 1000, "language": "Go",
            "license": "MIT", "last_activity": "2025-01-01", "tags": ["security"],
            "category": "Scanning", "summary": "A scanning tool", "found_in_domains": ["scanning"]
        },
        {
            "repo_url": "https://github.com/c/d", "name": "c/d", "description": "Tool B",
            "sub_domain": "policy", "score": 7, "quality_score": 52.1, "discovery_score": 7,
            "stars": 500, "language": "Python",
            "license": "Apache-2.0", "last_activity": "2025-06-01", "tags": ["policy"],
            "category": "Policy", "summary": "A policy tool", "found_in_domains": ["policy"]
        },
    ]
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_finalize(entries, topic="Test Topic", output_dir=tmp_path, template_dir=template_dir)

    assert (tmp_path / "catalog.json").exists()
    assert (tmp_path / "RESULTS.md").exists()
    assert not (tmp_path / "explorer.html").exists()  # Explorer is now top-level only

    catalog = json.loads((tmp_path / "catalog.json").read_text())
    assert len(catalog) == 2
    assert catalog[0]["quality_score"] >= catalog[1]["quality_score"]
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_finalize_produces_catalog_and_results_only -v`
Expected: FAIL — `explorer.html` still exists because `run_finalize` still generates it.

**Step 3: Implement — remove explorer generation from run_finalize**

In `pipeline/pipeline.py`, delete lines 149-158 (the explorer.html block) and the corresponding print line. The function becomes:

```python
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

    entries.sort(key=lambda e: e.get("quality_score", e.get("score", 0)), reverse=True)

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

    scores = [e.get("quality_score", e.get("score", 0)) for e in entries]
    context = {
        "topic": topic,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(entries),
        "domain_count": len(domain_entries),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains": domains_summary,
        "top_repos": [e for e in entries if e.get("quality_score", e.get("score", 0)) >= 70],
    }

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    results_tpl = env.get_template("results.md.jinja")
    results_path = output_dir / "RESULTS.md"
    results_path.write_text(results_tpl.render(**context))

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")
```

Also delete the old `test_finalize_produces_three_outputs` test since it's replaced.

**Step 4: Run test to verify it passes**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "refactor: remove explorer.html generation from finalize stage"
```

---

### Task 2: Add run_explorer function to pipeline.py

**Files:**
- Modify: `pipeline/pipeline.py` (add function after `run_finalize`)
- Test: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
from pipeline import normalize_url, run_dedup, run_score, run_finalize, run_explorer


def test_explorer_merges_domains(tmp_path):
    """run_explorer scans catalog/*/catalog.json and produces catalog/explorer.html."""
    # Set up two domain directories with catalog.json files
    domain_a = tmp_path / "alpha"
    domain_a.mkdir()
    domain_a_catalog = [
        {"repo_url": "https://github.com/a/one", "name": "one", "description": "Tool 1",
         "quality_score": 80, "score": 8, "stars": 1000, "sub_domain": "sub1",
         "found_in_domains": ["sub1"], "tags": ["tag1"]},
    ]
    (domain_a / "catalog.json").write_text(json.dumps(domain_a_catalog))

    domain_b = tmp_path / "beta"
    domain_b.mkdir()
    domain_b_catalog = [
        {"repo_url": "https://github.com/b/two", "name": "two", "description": "Tool 2",
         "quality_score": 60, "score": 6, "stars": 500, "sub_domain": "sub2",
         "found_in_domains": ["sub2"], "tags": ["tag2"]},
    ]
    (domain_b / "catalog.json").write_text(json.dumps(domain_b_catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    explorer_path = tmp_path / "explorer.html"
    assert explorer_path.exists()
    content = explorer_path.read_text()
    assert "alpha" in content  # domain badge
    assert "beta" in content   # domain badge
    assert "one" in content    # repo name from domain_a
    assert "two" in content    # repo name from domain_b


def test_explorer_injects_domain_field(tmp_path):
    """Each entry gets a 'domain' field matching its folder name."""
    domain = tmp_path / "cybersecurity"
    domain.mkdir()
    catalog = [
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool",
         "quality_score": 70, "score": 7, "stars": 100, "sub_domain": "sub",
         "found_in_domains": ["sub"], "tags": []},
    ]
    (domain / "catalog.json").write_text(json.dumps(catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    assert '"domain":"cybersecurity"' in content or '"domain": "cybersecurity"' in content


def test_explorer_skips_non_catalog_dirs(tmp_path):
    """Directories without catalog.json are silently skipped."""
    empty_dir = tmp_path / "empty-domain"
    empty_dir.mkdir()

    real = tmp_path / "real"
    real.mkdir()
    (real / "catalog.json").write_text(json.dumps([
        {"repo_url": "https://github.com/x/y", "name": "y", "description": "Y",
         "quality_score": 50, "score": 5, "stars": 10, "sub_domain": "s",
         "found_in_domains": ["s"], "tags": []},
    ]))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    assert (tmp_path / "explorer.html").exists()


def test_explorer_sorts_by_quality_score(tmp_path):
    """Merged entries are sorted by quality_score descending."""
    domain = tmp_path / "test"
    domain.mkdir()
    catalog = [
        {"repo_url": "https://github.com/a/low", "name": "low", "description": "Low",
         "quality_score": 20, "score": 2, "stars": 10, "sub_domain": "s",
         "found_in_domains": ["s"], "tags": []},
        {"repo_url": "https://github.com/a/high", "name": "high", "description": "High",
         "quality_score": 90, "score": 9, "stars": 10000, "sub_domain": "s",
         "found_in_domains": ["s"], "tags": []},
    ]
    (domain / "catalog.json").write_text(json.dumps(catalog))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    # "high" should appear before "low" in the rendered HTML
    assert content.index("high") < content.index("low")
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_explorer_merges_domains -v`
Expected: FAIL — `ImportError: cannot import name 'run_explorer'`

**Step 3: Implement run_explorer**

Add to `pipeline/pipeline.py` after `run_finalize`:

```python
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

    all_entries.sort(key=lambda e: e.get("quality_score", e.get("score", 0)), reverse=True)

    domains = sorted(set(e["domain"] for e in all_entries))

    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    explorer_tpl = env.get_template("explorer.html")
    context = {
        "topic": "Everything on Earth",
        "total": len(all_entries),
        "domain_count": len(domains),
        "catalog_json": json.dumps(all_entries),
    }
    explorer_path = catalog_root / "explorer.html"
    explorer_path.write_text(explorer_tpl.render(**context))

    print(f"[explorer] Merged {len(all_entries)} entries from {len(domains)} domains")
    print(f"[explorer] Wrote {explorer_path}")
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: add run_explorer function to merge domain catalogs"
```

---

### Task 3: Wire explorer stage into CLI

**Files:**
- Modify: `pipeline/pipeline.py:165-225` (main function)
- Test: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
import subprocess

def test_cli_explorer_stage(tmp_path):
    """The --stage explorer --catalog-root flag works end-to-end."""
    domain = tmp_path / "testdomain"
    domain.mkdir()
    (domain / "catalog.json").write_text(json.dumps([
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool",
         "quality_score": 70, "score": 7, "stars": 100, "sub_domain": "sub",
         "found_in_domains": ["sub"], "tags": ["test"]},
    ]))

    pipeline_path = Path(__file__).parent.parent / "pipeline" / "pipeline.py"
    result = subprocess.run(
        [sys.executable, str(pipeline_path), "--stage", "explorer", "--catalog-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (tmp_path / "explorer.html").exists()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_cli_explorer_stage -v`
Expected: FAIL — unrecognized argument `--catalog-root`

**Step 3: Implement — update main() to handle explorer stage**

In `pipeline/pipeline.py`, update the `main()` function:

```python
def main():
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
    parser.add_argument("--config", default=None, help="Path to swarm-config.json")
    parser.add_argument("--stage", default="dedup,score,finalize",
                        help="Comma-separated stages to run (default: dedup,score,finalize)")
    parser.add_argument("--input-dir", default=".", help="Directory containing input files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: from config)")
    parser.add_argument("--catalog-root", default=None, help="Root catalog dir for explorer stage")
    args = parser.parse_args()

    stages = [s.strip() for s in args.stage.split(",")]

    # Explorer stage doesn't need --config
    if "explorer" in stages:
        if not args.catalog_root:
            print("--catalog-root is required for explorer stage", file=sys.stderr)
            sys.exit(1)
        catalog_root = Path(args.catalog_root)
        template_dir = Path(__file__).parent / "templates"
        run_explorer(catalog_root=catalog_root, template_dir=template_dir)
        # Remove explorer from stages so the rest can proceed if combined
        stages = [s for s in stages if s != "explorer"]

    if not stages:
        return

    # Remaining stages need --config
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

            from collections import Counter
            domains = Counter()
            for entry in result:
                for d in entry.get("found_in_domains", [entry.get("sub_domain", "unknown")]):
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
            out_dir = Path(args.output_dir) if args.output_dir else output_dir
            template_dir = Path(__file__).parent / "templates"
            run_finalize(enriched, topic=config["topic"], output_dir=out_dir, template_dir=template_dir)
        else:
            print(f"Unknown stage: {stage}", file=sys.stderr)
            sys.exit(1)
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: wire explorer stage into pipeline CLI with --catalog-root flag"
```

---

### Task 4: Update explorer.html template with domain filter and badges

**Files:**
- Modify: `pipeline/templates/explorer.html`

**Step 1: Write the failing test**

```python
def test_explorer_template_has_domain_filter(tmp_path):
    """The rendered explorer.html contains a domain filter dropdown."""
    domain = tmp_path / "cybersecurity"
    domain.mkdir()
    (domain / "catalog.json").write_text(json.dumps([
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool",
         "quality_score": 70, "score": 7, "stars": 100, "sub_domain": "sub",
         "found_in_domains": ["sub"], "tags": []},
    ]))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    assert 'id="domain-type-filter"' in content
    assert "All domains" in content


def test_explorer_template_has_domain_badge(tmp_path):
    """Each card in explorer.html shows a domain badge."""
    domain = tmp_path / "cybersecurity"
    domain.mkdir()
    (domain / "catalog.json").write_text(json.dumps([
        {"repo_url": "https://github.com/a/b", "name": "tool", "description": "A tool",
         "quality_score": 70, "score": 7, "stars": 100, "sub_domain": "sub",
         "found_in_domains": ["sub"], "tags": []},
    ]))

    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_explorer(catalog_root=tmp_path, template_dir=template_dir)

    content = (tmp_path / "explorer.html").read_text()
    assert "domain-badge" in content
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py::test_explorer_template_has_domain_filter tests/test_pipeline.py::test_explorer_template_has_domain_badge -v`
Expected: FAIL — no `domain-type-filter` id or `domain-badge` class in current template

**Step 3: Replace the explorer.html template**

Overwrite `pipeline/templates/explorer.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ topic }} — Explorer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }
  h1 { color: #58a6ff; margin-bottom: 0.5rem; }
  .stats { color: #8b949e; margin-bottom: 1.5rem; }
  .controls { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  input, select { background: #161b22; border: 1px solid #30363d; color: #c9d1d9; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.9rem; }
  input:focus, select:focus { border-color: #58a6ff; outline: none; }
  input[type="text"] { min-width: 300px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1rem; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; transition: border-color 0.2s; }
  .card:hover { border-color: #58a6ff; }
  .card h3 { color: #58a6ff; font-size: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
  .card h3 a { color: inherit; text-decoration: none; }
  .card h3 a:hover { text-decoration: underline; }
  .card p { color: #8b949e; font-size: 0.85rem; line-height: 1.4; margin-bottom: 0.75rem; }
  .meta { display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.8rem; color: #8b949e; }
  .meta span { background: #21262d; padding: 0.15rem 0.5rem; border-radius: 4px; }
  .score { color: #3fb950; font-weight: 600; }
  .tag { background: #1f3a5f; color: #58a6ff; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
  .domain-badge { padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
  .count { color: #8b949e; margin-bottom: 1rem; }
  .hidden { display: none; }
</style>
</head>
<body>
<h1>{{ topic }}</h1>
<p class="stats">{{ total }} repos across {{ domain_count }} domains</p>

<div class="controls">
  <input type="text" id="search" placeholder="Filter by name, description, or tag...">
  <select id="domain-type-filter">
    <option value="">All domains</option>
  </select>
  <select id="domain-filter">
    <option value="">All sub-domains</option>
  </select>
  <select id="sort-by">
    <option value="score">Sort by quality score</option>
    <option value="stars">Sort by stars</option>
    <option value="activity">Sort by activity</option>
    <option value="name">Sort by name</option>
  </select>
</div>

<p class="count" id="count"></p>
<div class="grid" id="grid"></div>

<script>
const CATALOG = {{ catalog_json }};

function domainHue(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return Math.abs(hash) % 360;
}

// Populate domain type filter
const domainTypeFilter = document.getElementById('domain-type-filter');
const domainTypes = [...new Set(CATALOG.map(e => e.domain).filter(Boolean))].sort();
domainTypes.forEach(d => {
  const opt = document.createElement('option');
  opt.value = d; opt.textContent = d;
  domainTypeFilter.appendChild(opt);
});

// Populate sub-domain filter
const domainFilter = document.getElementById('domain-filter');
const subDomains = [...new Set(CATALOG.flatMap(e => e.found_in_domains || [e.sub_domain]))].sort();
subDomains.forEach(d => {
  const opt = document.createElement('option');
  opt.value = d; opt.textContent = d;
  domainFilter.appendChild(opt);
});

function render(entries) {
  const grid = document.getElementById('grid');
  grid.innerHTML = entries.map(e => {
    const hue = domainHue(e.domain || 'unknown');
    const badgeBg = `hsla(${hue}, 60%, 25%, 0.8)`;
    const badgeColor = `hsl(${hue}, 80%, 75%)`;
    return `
    <div class="card">
      <h3>
        <a href="${e.repo_url}" target="_blank">${e.name}</a>
        ${e.domain ? `<span class="domain-badge" style="background:${badgeBg};color:${badgeColor}">${e.domain}</span>` : ''}
      </h3>
      <p>${e.summary || e.description}</p>
      <div class="meta">
        <span class="score" style="color: ${e.quality_score >= 70 ? '#3fb950' : e.quality_score >= 40 ? '#d29922' : '#8b949e'}">${e.quality_score ?? e.score}</span>
        ${e.discovery_score != null ? `<span>relevance ${e.discovery_score}/10</span>` : ''}
        ${e.stars ? `<span>★ ${e.stars.toLocaleString()}</span>` : ''}
        ${e.language ? `<span>${e.language}</span>` : ''}
        ${e.license ? `<span>${e.license}</span>` : ''}
      </div>
      <div class="meta" style="margin-top:0.5rem">
        ${(e.tags || []).map(t => `<span class="tag">${t}</span>`).join('')}
      </div>
    </div>
  `}).join('');
  document.getElementById('count').textContent = `Showing ${entries.length} of ${CATALOG.length}`;
}

function applyFilters() {
  let filtered = [...CATALOG];
  const q = document.getElementById('search').value.toLowerCase();
  const domainType = domainTypeFilter.value;
  const subDomain = domainFilter.value;
  const sort = document.getElementById('sort-by').value;

  if (q) filtered = filtered.filter(e =>
    e.name.toLowerCase().includes(q) ||
    (e.description || '').toLowerCase().includes(q) ||
    (e.tags || []).some(t => t.includes(q))
  );
  if (domainType) filtered = filtered.filter(e => e.domain === domainType);
  if (subDomain) filtered = filtered.filter(e =>
    (e.found_in_domains || [e.sub_domain]).includes(subDomain)
  );

  if (sort === 'score') filtered.sort((a, b) => (b.quality_score ?? b.score ?? 0) - (a.quality_score ?? a.score ?? 0));
  else if (sort === 'stars') filtered.sort((a, b) => (b.stars || 0) - (a.stars || 0));
  else if (sort === 'activity') filtered.sort((a, b) => (b.last_activity || '').localeCompare(a.last_activity || ''));
  else if (sort === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name));

  render(filtered);
}

document.getElementById('search').addEventListener('input', applyFilters);
domainTypeFilter.addEventListener('change', applyFilters);
domainFilter.addEventListener('change', applyFilters);
document.getElementById('sort-by').addEventListener('change', applyFilters);
applyFilters();
</script>
</body>
</html>
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add pipeline/templates/explorer.html tests/test_pipeline.py
git commit -m "feat: add domain filter dropdown and color-coded domain badges to explorer"
```

---

### Task 5: Update RESULTS.md template reference

**Files:**
- Modify: `pipeline/templates/results.md.jinja:40`

**Step 1: Update the reference**

Change line 40 from:
```
See `explorer.html` to browse interactively.
```
to:
```
See `../explorer.html` to browse interactively.
```

**Step 2: Run existing tests**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git add pipeline/templates/results.md.jinja
git commit -m "fix: update explorer.html reference to point to top-level"
```

---

### Task 6: Clean up existing per-domain explorer.html

**Files:**
- Delete: `catalog/cybersecurity/explorer.html`

**Step 1: Remove the file**

```bash
rm catalog/cybersecurity/explorer.html
```

**Step 2: Generate new top-level explorer**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
python pipeline/pipeline.py --stage explorer --catalog-root catalog/
```

Expected output:
```
[explorer] Merged N entries from 1 domains
[explorer] Wrote catalog/explorer.html
```

**Step 3: Verify explorer.html works**

```bash
open catalog/explorer.html
```

Manually verify:
- Title says "Everything on Earth — Explorer"
- Domain filter dropdown shows "cybersecurity"
- Each card has a colored domain badge
- Search and sort work as before

**Step 4: Commit**

```bash
git rm catalog/cybersecurity/explorer.html
git add catalog/explorer.html
git commit -m "chore: replace per-domain explorer with top-level global explorer"
```

---

### Task 7: Update pipeline docstring

**Files:**
- Modify: `pipeline/pipeline.py:1-15`

**Step 1: Update the module docstring**

```python
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
```

**Step 2: Run tests to verify nothing broke**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`
Expected: ALL PASS

**Step 3: Commit**

```bash
git add pipeline/pipeline.py
git commit -m "docs: update pipeline docstring with explorer stage usage"
```
