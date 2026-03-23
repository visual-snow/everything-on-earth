# README Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite README.md from 155-line cluttered format to ~110-line product-page structure with GSD-style formatting.

**Architecture:** Single file rewrite of `README.md`. No new files. Content derived from approved design doc at `docs/plans/2026-03-23-readme-redesign-design.md`. Hero image path unchanged.

**Tech Stack:** GitHub-flavored markdown, HTML `<div align="center">`, `<details>/<summary>`, GitHub alert blocks (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`).

---

### Task 1: Write the complete README.md

**Files:**
- Modify: `README.md` (full rewrite, lines 1-155)

**Step 1: Replace README.md with the redesigned content**

Write the entire file with this exact content:

````markdown
<div align="center">

# everything-on-earth

**Max the fuck out of your Claude subscription by doing a massive parallel crawl that searches everything on earth about whatever you want.**

<p>
  <img src="assets/everything-on-earth.png" alt="everything-on-earth" width="600">
</p>

```bash
git clone https://github.com/eaguaida/everything-on-earth.git
cd everything-on-earth && ./install.sh
```

[Getting Started](#getting-started) · [How It Works](#how-it-works) · [What You Get](#what-you-get)

</div>

---

## Getting Started

```bash
git clone https://github.com/eaguaida/everything-on-earth.git
cd everything-on-earth
./install.sh
```

Then run your first crawl:

```
/massive-crawl "Kubernetes security tools"
```

Scouts research your topic → you approve the plan → a swarm of agents discovers everything → a deterministic pipeline deduplicates, prunes, and finalizes → you get a complete catalog.

> [!NOTE]
> **Requirements:** [Claude Code](https://claude.ai/claude-code) v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, [Firecrawl CLI](https://firecrawl.dev) with `FIRECRAWL_API_KEY`, Node >= 18, Python >= 3.9

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

Takes your catalog and generates rich capability documentation for every entry.

Three-phase agent pipeline per entry:
1. **Researcher** — Scrapes the repo's README and docs, builds a structured factsheet
2. **Writer** — Converts the factsheet into capability documentation matching a style exemplar
3. **Judge** — Reviews outputs against quality criteria, sends failures back for retry

Processes entries in batched waves of 15 with full resumability.

> [!NOTE]
> Interrupted mid-run? It picks up where you left off via `wave-progress.json`.

---

## What You Get

| File | Format | What it is |
|------|--------|------------|
| `catalog.json` | JSON | Machine-readable canonical catalog — load it into any agent's context |
| `explorer.html` | HTML | Browse and filter results in your browser |
| `RESULTS.md` | Markdown | Stats, domain breakdown, top repos |
| `*_capability.md` | Markdown | Per-tool capability docs (via `/map-capabilities`) |

> [!IMPORTANT]
> This plugin uses Claude Code's experimental Agent Teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). It spawns 6-8 Sonnet agents in parallel and will burn tokens. This is a deliberate investment — one run builds a knowledge base that pays for itself across every future session.

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
````

**Step 2: Verify the rewrite**

Run these checks:

```bash
# Line count should be ~110 (target 100-120)
wc -l README.md

# Verify no stale section headers survived
grep -n "Why I Built\|Who This Is For\|Why It Works\|Heads Up\|Requirements$\|Research once" README.md

# Verify all new formatting elements are present
grep -c "!\[NOTE\]\|!\[TIP\]\|!\[IMPORTANT\]\|<details>\|<div align" README.md
```

Expected:
- Line count: 105-115
- Stale headers: no matches
- Formatting elements: 5 matches (1 NOTE, 1 TIP, 1 IMPORTANT, 1 details open + 1 details close... grep will find at least 5)

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README with product-page structure and GSD-style formatting

Removes philosophy sections (Why I Built This, Who This Is For, Why It Works).
Adds GitHub alert blocks, collapsible sections, centered hero.
Requirements merged into Getting Started. Troubleshooting collapsed.
~110 lines, down from 155."
```
