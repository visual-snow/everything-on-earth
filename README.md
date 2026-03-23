# everything-on-earth

**A Claude Code plugin that researches any topic once — so your agents never have to again.**

<p align="center">
  <img src="assets/everything-on-earth.png" alt="everything-on-earth" width="600">
</p>

```
/massive-crawl "Kubernetes security tools"
```

[Why I Built This](#why-i-built-this) · [Who This Is For](#who-this-is-for) · [Getting Started](#getting-started) · [How It Works](#how-it-works) · [Why It Works](#why-it-works)

---

## Why I Built This

I'm tired of telling Claude to research the same thing every conversation.

Every new session, the agent burns tokens re-discovering the same tools, the same repos, the same landscape — just to get back to where you were yesterday. You're paying for the same research over and over, and the results are inconsistent because each session explores differently.

So I built a plugin that sends a swarm of agents to find *everything* on earth about a topic, catalogs it with a deterministic pipeline, and produces structured artifacts your agents can retrieve from forever.

This is [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) taken seriously. Instead of agents researching on the fly and hoping they find the right stuff, you pre-compute the knowledge base once. Then every future session starts from a complete, verified catalog — not a blank slate.

One run. Permanent context. No more re-researching.

— **eaguaida**

---

## Who This Is For

Claude Code power users who work deeply in a domain and are sick of watching agents re-discover the same landscape every session. People who care about context engineering — giving agents the right information instead of hoping they find it themselves.

---

## Getting Started

```bash
git clone https://github.com/eaguaida/everything-on-earth.git
cd everything-on-earth
./install.sh
```

Then run your first crawl:

```
/massive-crawl "your topic here"
```

What happens: scouts research your topic → you approve the plan → a swarm of agents discovers everything → a deterministic pipeline deduplicates, prunes, and finalizes → you get a complete catalog.

Uninstall: `./install.sh --uninstall`

---

## How It Works

Two skills, one plugin.

### `/massive-crawl` — Discovery at scale

```
Phase 1: Brainstorm        Phase 2: Discover           Phase 3: Pipeline
+------------------+       +---------------------+     +------------------+
| 3 Haiku scouts   |       | TeamCreate swarm    |     | dedup (auto)     |
| refine topic     | ----> | 6-8 Sonnet agents   | --> | prune (you pick) |
| user approves    |       | self-claim tasks    |     | enrich (Batch)   |
| swarm config     |       | write to disk       |     | finalize         |
+------------------+       +---------------------+     +------------------+
     ~5 min                      ~30 min                     ~10 min
```

**Phase 1: Brainstorm** — Three cheap Haiku scouts search for existing awesome-lists, validate queries, and check for prior art. Claude asks you a few clarifying questions and builds a plan showing sub-domains, teammate count, and estimated scope. You approve before anything expensive runs.

**Phase 2: Discover** — A TeamCreate swarm of 6-8 Sonnet agents shares a task pool. Each agent claims a sub-domain, runs firecrawl searches and scrapes, writes results to disk, then claims the next task. Hooks inject context into agents, validate outputs, and nudge idle teammates.

**Phase 3: Pipeline** — A deterministic Python pipeline handles dedup, pruning, enrichment, and finalization. No LLM touches the merge — that's set-based URL matching. The pipeline pauses after dedup so you can set pruning thresholds.

### `/map-capabilities` — Deep documentation

Takes your catalog and turns each entry into rich capability documentation.

Three-phase agent pipeline:
- **Researcher** — Scrapes each repo's README and docs, builds a structured factsheet
- **Writer** — Converts the factsheet into capability documentation matching a style exemplar
- **Judge** — Batch-reviews outputs against quality criteria, sends failures back for retry

Processes entries in waves of 15 with full resumability — pick up where you left off if interrupted.

---

## Why It Works

### Pre-computed knowledge beats on-the-fly research

Anthropic's [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) article describes agents maintaining "lightweight identifiers" and loading data on demand. This plugin is the supply side — it builds the definitive catalog so your agents have something high-quality to retrieve from, instead of re-researching from scratch every session.

### LLM for creativity, Python for correctness

Agents are excellent at fuzzy, creative, parallel discovery. They are terrible at exact set operations on large data. This plugin enforces that boundary: LLM agents discover, deterministic Python synthesizes. The pipeline never drops repos because it never asks an LLM to merge lists.

### Structured artifacts for agent retrieval

The outputs — `catalog.json`, capability docs, `explorer.html` — are designed to be loaded into agent context, not just read by humans. A future session can load your catalog and reason over 800+ repos without spending a single token on discovery.

---

## What You Get

| File | Format | Purpose |
|------|--------|---------|
| `catalog.json` | JSON | Machine-readable canonical catalog |
| `explorer.html` | HTML | Browse and filter in your browser |
| `RESULTS.md` | Markdown | Stats, domain breakdown, top repos |
| `*_capability.md` | Markdown | Per-tool capability docs (via `/map-capabilities`) |

---

## Heads Up — Experimental

This plugin uses Claude Code's experimental Agent Teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). It spawns 6-8 Sonnet agents in parallel and will burn a lot of tokens. This is not a casual "run it and forget" tool — it's a deliberate investment in building a knowledge base that pays for itself across every future session.

---

## Requirements

- [Claude Code](https://claude.ai/claude-code) v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- [Firecrawl CLI](https://firecrawl.dev) with `FIRECRAWL_API_KEY`
- Node >= 18, Python >= 3.9

---

## Troubleshooting

**Commands not found after install?**
Restart Claude Code to reload skills. Verify files exist in `~/.claude/skills/massive-crawl/`.

**Firecrawl errors?**
Check that `FIRECRAWL_API_KEY` is set and you have credits remaining.

**Pipeline fails?**
Make sure Python >= 3.9 is installed and run `pip install -r requirements.txt`.

---

## License

MIT

---

**Research once. Retrieve forever.**
