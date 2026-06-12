<div align="center">

# everything-on-earth

[![npm version](https://img.shields.io/badge/npm-v0.1.0-cb3837)](https://www.npmjs.com/package/everything-on-earth)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![claude code](https://img.shields.io/badge/Claude_Code-plugin-7c3aed)](https://claude.ai/claude-code)

<p>
  <img src="assets/everything-on-earth.png" alt="everything-on-earth" width="600">
</p>

**Max the fuck out of your AI subscriptions by doing a massive parallel crawl that searches everything on earth about whatever you want.**

[Getting Started](#getting-started) · [How It Works](#how-it-works) · [What You Get](#what-you-get)

</div>

---

## Getting Started

After installing, run your first crawl:

```
/massive-crawl "Kubernetes security tools"
```

Scouts research your topic → you approve the plan → a swarm of agents discovers everything → a deterministic pipeline deduplicates, prunes, and finalizes → you get a complete catalog.

> [!NOTE]
> **Requirements**
> - [Claude Code](https://claude.ai/claude-code) v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
> - [Firecrawl CLI](https://firecrawl.dev) with `FIRECRAWL_API_KEY`
> - Node >= 18, Python >= 3.9

Uninstall: `./install.sh --uninstall`

---

## How It Works

### `/massive-crawl` — Discovery at scale

```
Phase 1: Brainstorm        Phase 2: Discover           Phase 3: Pipeline
+------------------+       +---------------------+     +------------------+
| 3 Haiku scouts   |       | TeamCreate swarm    |     | dedup (auto)     |
| run recon        | ----> | 6-8 Sonnet agents   | --> | prune (you pick) |
| user approves    |       | self-claim tasks    |     | enrich (Batch)   |
| swarm config     |       | write to disk       |     | finalize         |
+------------------+       +---------------------+     +------------------+
     ~5 min                      ~30 min                     ~10 min
```

**Brainstorm** — Three cheap scouts run recon on your topic in parallel while you answer a few questions. They check what's already been cataloged, test which search queries return signal vs noise, and map the landscape. You review their findings, shape the plan, and approve before the expensive swarm launches.

**Discover** — A swarm of 6-8 Sonnet agents shares a task pool. Each agent claims a sub-domain, runs firecrawl searches and scrapes, writes results to disk, then claims the next task.

**Pipeline** — Deterministic Python handles dedup, pruning, enrichment, and finalization. No LLM touches the merge — set-based URL matching only.

> [!TIP]
> The pipeline pauses after dedup so you can set pruning thresholds before it continues.

<details>
<summary><strong>Pipeline internals</strong></summary>

- **Dedup** — Set-based URL matching across all agent outputs. No LLM involved.
- **Prune** — You set score thresholds. Entries below the cutoff are dropped.
- **Enrich** — Batch API call adds metadata (stars, language, license, last activity).
- **Finalize** — Produces `catalog.json`, `explorer.html`, and `RESULTS.md`.

</details>

### `/map-capabilities` — Deep documentation

Takes a domain catalog and generates rich capability documentation for every entry
inside that domain's folder.

Three-phase agent pipeline per entry:
1. **Researcher** — Scrapes the repo's README and docs, builds a structured factsheet
2. **Writer** — Converts the factsheet into capability documentation matching a style exemplar
3. **Judge** — Reviews outputs against quality criteria, sends failures back for retry

Processes entries in batched waves of 15 with full resumability.

> [!NOTE]
> Interrupted mid-run? It picks up where you left off via `wave-progress.json`.

### `/supercharge` — Feed Claude the full capability graph

```
/supercharge
```

One invocation builds a canonical capability graph from all 11 domain catalogs,
generates Claude skill artifacts, and wires hooks that keep Claude domain-aware
across every future session.

After supercharge runs, three hooks fire automatically:

1. **SessionStart** — Injects capability graph overview so Claude knows all domains, capability counts, and key asset paths from the first message
2. **UserPromptSubmit** — Keyword-matches every prompt against 3,000+ routing hints; when a domain matches, injects that domain's capability summary and graph pointers
3. **Compact restore** — Re-injects the overview after context compaction so domain awareness survives compression

V1 is Claude-first. Telecoms is the pilot domain with a full capability graph (1,330 capabilities, 1,939 repo-capability edges). All 11 domains have routing hints for classification; deep capability graphs for other domains will be added as their `provides[]` data is populated.

Run `/supercharge` again any time catalogs change to rebuild the graph and re-verify hooks.

---

## What You Get

| File | Format | What it is |
|------|--------|------------|
| `catalog.json` | JSON | Machine-readable canonical catalog — load it into any agent's context |
| `explorer.html` | HTML | Browse and filter results in your browser |
| `RESULTS.md` | Markdown | Stats, domain breakdown, top repos |
| `catalog/<domain>/<slug>/capability.md` | Markdown | Per-tool capability docs (via `/map-capabilities`) |
| `capability-graph/ontology/capability-registry.json` | JSON | Canonical capability entities with relationships and evidence |
| `capability-graph/graph/domains/<domain>.json` | JSON | Per-domain graph slice (capabilities, repos, edges) |
| `capability-graph/exports/csv/domain-routing.csv` | CSV | Routing hints for all 11 domains (classifier input) |

> [!IMPORTANT]
> This plugin uses Claude Code's experimental Agent Teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).
> It spawns 6-8 Sonnet agents in parallel and will burn tokens.
> One run builds a knowledge base that pays for itself across every future session.

---

<details>
<summary><strong>Troubleshooting</strong></summary>

**Commands not found after install?**
Restart Claude Code to reload skills. Verify files exist in `~/.claude/skills/massive-crawl/`.

**Firecrawl errors?**
Check that `FIRECRAWL_API_KEY` is set and you have credits remaining.

**Pipeline fails?**
Make sure Python >= 3.9 is installed and run `pip install -r requirements.txt`.

</details>

---

## License

MIT
