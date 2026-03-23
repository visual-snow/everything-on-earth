# README Redesign + Skill Rename — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the discovery skill from `/everything-on-earth` to `/massive-crawl`, update all references, and rewrite README.md with a personal, opinionated tone following the approved 11-section design.

**Architecture:** Two workstreams — (1) rename the skill and update all references across hooks, installer, pipeline, and config files; (2) rewrite README.md from scratch. The rename must happen first since README content references the new skill name.

**Tech Stack:** Markdown, Node.js hooks, Bash installer, Python pipeline, JSON schema

---

### Task 1: Create assets directory and placeholder for hero image

**Files:**
- Create: `assets/.gitkeep`

**Step 1: Create the assets directory**

```bash
mkdir -p assets && touch assets/.gitkeep
```

**Step 2: Commit**

```bash
git add assets/.gitkeep
git commit -m "chore: add assets directory for hero image"
```

---

### Task 2: Rename skill directory — move SKILL.md into `skill/massive-crawl/`

**Files:**
- Move: `skill/SKILL.md` → `skill/massive-crawl/SKILL.md`
- Modify: `skill/massive-crawl/SKILL.md` (frontmatter + body)

**Step 1: Create the new directory and move the file**

```bash
mkdir -p skill/massive-crawl
git mv skill/SKILL.md skill/massive-crawl/SKILL.md
```

**Step 2: Update frontmatter — change `name` from `everything-on-earth` to `massive-crawl`**

In `skill/massive-crawl/SKILL.md`, change lines 2-11 from:

```yaml
name: everything-on-earth
description: >-
  Discovers every open-source GitHub/GitLab repository for any topic using a
  TeamCreate agent swarm and deterministic Python synthesis pipeline. Use when
  the user says "find every repo", "discover all tools", "everything on earth",
  "catalog all open source", "survey the landscape", or wants comprehensive
  GitHub/GitLab discovery for a broad domain. Launches 3 Haiku scouts for
  reconnaissance, asks clarifying questions, then deploys 6-8 Sonnet teammates
  in a self-claiming swarm. Deterministic pipeline handles dedup, pruning,
  enrichment, and finalization. Outputs catalog.json, explorer.html, RESULTS.md.
```

To:

```yaml
name: massive-crawl
description: >-
  Discovers every open-source GitHub/GitLab repository for any topic using a
  TeamCreate agent swarm and deterministic Python synthesis pipeline. Use when
  the user says "massive crawl", "find every repo", "discover all tools",
  "catalog all open source", "survey the landscape", or wants comprehensive
  GitHub/GitLab discovery for a broad domain. Launches 3 Haiku scouts for
  reconnaissance, asks clarifying questions, then deploys 6-8 Sonnet teammates
  in a self-claiming swarm. Deterministic pipeline handles dedup, pruning,
  enrichment, and finalization. Outputs catalog.json, explorer.html, RESULTS.md.
```

**Step 3: Update the body heading**

Change line 33:

```markdown
# everything-on-earth
```

To:

```markdown
# massive-crawl
```

**Step 4: Update the teammate prompt reference in the body**

Change line 120 from:

```
  prompt: "You are a discovery agent in an everything-on-earth swarm.
```

To:

```
  prompt: "You are a discovery agent in a massive-crawl swarm.
```

**Step 5: Commit**

```bash
git add skill/massive-crawl/SKILL.md
git commit -m "feat: rename skill from everything-on-earth to massive-crawl"
```

---

### Task 3: Update agent-prompt-template.md reference

**Files:**
- Modify: `skill/references/agent-prompt-template.md:2`

**Step 1: Update the agent identity line**

Change line 3:

```markdown
You are a discovery agent in an everything-on-earth swarm. Your job: find every relevant open-source repo for your assigned sub-domain.
```

To:

```markdown
You are a discovery agent in a massive-crawl swarm. Your job: find every relevant open-source repo for your assigned sub-domain.
```

**Step 2: Commit**

```bash
git add skill/references/agent-prompt-template.md
git commit -m "chore: update agent template to use massive-crawl name"
```

---

### Task 4: Update output-schema.json title

**Files:**
- Modify: `skill/references/output-schema.json:3`

**Step 1: Update the schema title**

Change line 3:

```json
  "title": "everything-on-earth discovery entry",
```

To:

```json
  "title": "massive-crawl discovery entry",
```

**Step 2: Commit**

```bash
git add skill/references/output-schema.json
git commit -m "chore: update output schema title to massive-crawl"
```

---

### Task 5: Update statusline.js hook

**Files:**
- Modify: `hooks/statusline.js:6,9,48`

**Step 1: Update the purpose comment (line 6)**

Change:

```javascript
 * Purpose: Real-time progress display for everything-on-earth runs.
```

To:

```javascript
 * Purpose: Real-time progress display for massive-crawl runs.
```

**Step 2: Update the output format comment (line 9)**

Change:

```javascript
 *   everything-on-earth | {topic} | tasks: {done}/{total} | repos: {count} | {pct}%
```

To:

```javascript
 *   massive-crawl | {topic} | tasks: {done}/{total} | repos: {count} | {pct}%
```

**Step 3: Update the status string (line 48)**

Change:

```javascript
  const status = `everything-on-earth | ${topic} | tasks: ${completedFiles}/${totalDomains} | repos: ${totalRepos} | ${pct}%`;
```

To:

```javascript
  const status = `massive-crawl | ${topic} | tasks: ${completedFiles}/${totalDomains} | repos: ${totalRepos} | ${pct}%`;
```

**Step 4: Commit**

```bash
git add hooks/statusline.js
git commit -m "chore: update statusline hook to use massive-crawl name"
```

---

### Task 6: Update install.sh

**Files:**
- Modify: `install.sh` (lines 4, 8, 9, 19, 22, 31, 46, 82-83, 113, 142, 144, 158)

**Step 1: Update installer comments and paths**

The following substitutions apply across the entire file. Replace ALL occurrences of `everything-on-earth` with `massive-crawl` in these contexts:

1. Line 4 comment: `# massive-crawl installer`
2. Line 8: `SKILL_DEST="$HOME/.claude/skills/massive-crawl"`
3. Line 9: `HOOKS_DEST="$HOME/.claude/hooks/massive-crawl"`
4. Line 19: `echo "Uninstalling massive-crawl..."`
5. Line 22: `# Remove our hook entries (entries containing "massive-crawl")`
6. Line 31: `if not any("massive-crawl" in (hook.get("command",""))`
7. Line 46: `echo "Installing massive-crawl..."`
8. Line 82: `cp "$SCRIPT_DIR/skill/massive-crawl/SKILL.md" "$SKILL_DEST/"`
9. Line 83: `cp -r "$SCRIPT_DIR/skill/references" "$SKILL_DEST/"`
10. Line 113: `hooks_path = "$CLAUDE_PROJECT_DIR/hooks/massive-crawl"`
11. Line 142: `# Remove any old massive-crawl entries`
12. Line 144: `if not any("massive-crawl" in h.get("command", ""))`
13. Line 158: `echo "Usage: /massive-crawl \"your topic\""`

**Step 2: Verify the installer still runs**

```bash
bash -n install.sh
```

Expected: No syntax errors (exit 0).

**Step 3: Commit**

```bash
git add install.sh
git commit -m "chore: update installer paths and messages for massive-crawl rename"
```

---

### Task 7: Update pipeline.py docstring

**Files:**
- Modify: `pipeline/pipeline.py:3,244`

**Step 1: Update module docstring (line 3)**

Change:

```python
everything-on-earth deterministic pipeline.
```

To:

```python
massive-crawl deterministic pipeline.
```

**Step 2: Update argparse description (line 244)**

Change:

```python
    parser = argparse.ArgumentParser(description="everything-on-earth deterministic pipeline")
```

To:

```python
    parser = argparse.ArgumentParser(description="massive-crawl deterministic pipeline")
```

**Step 3: Run existing tests to verify nothing broke**

```bash
cd pipeline && python3 -m pytest ../tests/test_pipeline.py -v
```

Expected: All tests pass.

**Step 4: Commit**

```bash
git add pipeline/pipeline.py
git commit -m "chore: update pipeline docstring for massive-crawl rename"
```

---

### Task 8: Update test file docstring

**Files:**
- Modify: `tests/test_pipeline.py:1`

**Step 1: Update docstring**

Change line 1:

```python
"""Tests for the everything-on-earth deterministic pipeline."""
```

To:

```python
"""Tests for the massive-crawl deterministic pipeline."""
```

**Step 2: Run tests to confirm they still pass**

```bash
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All tests pass.

**Step 3: Commit**

```bash
git add tests/test_pipeline.py
git commit -m "chore: update test docstring for massive-crawl rename"
```

---

### Task 9: Update .gitignore output directory reference

**Files:**
- Modify: `.gitignore:8`

**Step 1: Update the output directory ignore pattern**

Change line 8:

```
everything-on-earth-output/
```

To:

```
massive-crawl-output/
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: update gitignore for massive-crawl output directory"
```

---

### Task 10: Update examples/swarm-config.example.json

**Files:**
- Modify: `examples/swarm-config.example.json:84`

**Step 1: Update the output directory reference**

Change:

```json
    "directory": "everything-on-earth-output/"
```

To:

```json
    "directory": "massive-crawl-output/"
```

**Step 2: Commit**

```bash
git add examples/swarm-config.example.json
git commit -m "chore: update example config for massive-crawl output directory"
```

---

### Task 11: Write the new README.md

**Files:**
- Overwrite: `README.md`

**Step 1: Write the full README following the approved design**

The complete content for README.md:

```markdown
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
```

**Step 2: Read the written file to verify it looks correct**

```bash
wc -l README.md
```

Expected: ~150-170 lines.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README with personal tone, two-skill structure, and context engineering framing"
```

---

### Task 12: Verify all references are updated

**Step 1: Search for any remaining "everything-on-earth" in non-docs source files**

```bash
grep -r "everything-on-earth" --include="*.js" --include="*.sh" --include="*.py" --include="*.json" --include="*.md" . | grep -v "docs/plans/" | grep -v "meta-analysis.md" | grep -v ".firecrawl/"
```

Expected: Only hits in:
- `README.md` (the repo name — this is correct, the plugin is still called "everything-on-earth")
- `.gitignore` should have been updated already
- `meta-analysis.md` is historical and should keep the original name

Any other hits need fixing before this task is complete.

**Step 2: Verify install.sh parses cleanly**

```bash
bash -n install.sh
```

Expected: exit 0.

**Step 3: Run pipeline tests**

```bash
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All pass.

**Step 4: Commit any remaining fixes**

```bash
git add -A && git commit -m "chore: fix any remaining old name references"
```

(Only if there are changes to commit.)

---

## Summary of all file changes

| File | Action | What changes |
|------|--------|-------------|
| `assets/.gitkeep` | Create | Empty placeholder for hero image |
| `skill/SKILL.md` | Move → `skill/massive-crawl/SKILL.md` | Frontmatter name, description, body heading, teammate prompt |
| `skill/references/agent-prompt-template.md` | Edit | Agent identity line |
| `skill/references/output-schema.json` | Edit | Schema title |
| `hooks/statusline.js` | Edit | Comments + status string |
| `install.sh` | Edit | All paths, messages, Python hook registration |
| `pipeline/pipeline.py` | Edit | Docstring + argparse description |
| `tests/test_pipeline.py` | Edit | Docstring |
| `.gitignore` | Edit | Output directory pattern |
| `examples/swarm-config.example.json` | Edit | Output directory reference |
| `README.md` | Overwrite | Complete rewrite (11 sections) |

**Files NOT changed (intentional):**
- `docs/plans/*` — historical documents, keep original name
- `meta-analysis.md` — case study, keep original name
- `hooks/pre-teamcreate.js` — checks for `eoe-` team prefix, unchanged
- `hooks/subagent-context.sh` — checks for `eoe-` team prefix, unchanged
- `hooks/task-completed.sh` — checks for `eoe-` team prefix, unchanged
- `hooks/teammate-idle.sh` — checks for `eoe-` team prefix, unchanged
- `hooks/post-concat.js` — no name references, unchanged
- `skill/map-capabilities/SKILL.md` — already correctly named, unchanged
