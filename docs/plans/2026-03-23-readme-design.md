# README Design: everything-on-earth

**Date:** 2026-03-23
**Status:** Approved

## Context

Redesign the README.md to be friendly and compelling for Claude Code power users. Inspired by the GSD (get-shit-done) README structure: personal opinionated tone, progressive disclosure from motivation → usage → technical depth.

The plugin is called `everything-on-earth` and contains two skills:
- `/massive-crawl` — Discovery swarm that finds every open-source repo for a topic
- `/map-capabilities` — Three-phase agent pipeline that generates capability documentation from catalogs

Core value proposition: **Research once, retrieve forever.** Instead of agents re-researching a domain every conversation, pre-compute a definitive catalog and capability map that agents can retrieve from.

Intellectual foundation: [Anthropic's context engineering article](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## Audience

Claude Code power users who work deeply in a domain and are tired of re-researching every session.

## Tone

Personal, opinionated, first person. Like GSD but focused on the "tired of re-researching" frustration rather than "no enterprise roleplay."

## Section Structure

### 1. Hero
- Hero image: `assets/everything-on-earth.png`
- One-liner: "A Claude Code plugin that researches any topic once — so your agents never have to again."
- Command example: `/massive-crawl "Kubernetes security tools"`

### 2. Why I Built This
- Personal frustration: telling Claude to research X every conversation
- Every session burns tokens re-discovering the same landscape
- Solution: swarm agents to find everything, catalog deterministically, produce structured artifacts
- This is context engineering taken seriously — pre-compute the knowledge base
- Link to Anthropic's context engineering article
- Author sign-off

### 3. Who This Is For
- Claude Code power users
- People sick of re-researching domains
- People who care about context engineering — giving agents the right information

### 4. Getting Started
- git clone + ./install.sh
- First run: `/massive-crawl "your topic here"`
- Brief flow: brainstorm → swarm → pipeline → outputs
- Uninstall: `./install.sh --uninstall`

### 5. How It Works

**`/massive-crawl` — Discovery at scale**
- Phase 1: Brainstorm — 3 Haiku scouts, user approves before expensive work
- Phase 2: Discover — TeamCreate swarm of 6-8 Sonnet agents, self-claiming tasks
- Phase 3: Pipeline — Deterministic Python (dedup → prune → enrich → finalize)
- ASCII diagram of the three phases

**`/map-capabilities` — Deep documentation**
- Researcher → Writer → Judge pipeline
- Processes in waves of 15 with resumability
- Turns catalog entries into rich capability docs

### 6. Why It Works
- Pre-computed knowledge > on-the-fly research
- LLM for creativity, Python for correctness
- Structured artifacts designed for agent retrieval (catalog.json, capability docs)
- Link to Anthropic context engineering article

### 7. What You Get
- Table: catalog.json, explorer.html, RESULTS.md, *_capability.md

### 8. Experimental Warning
- Uses experimental Agent Teams feature
- Spawns 6-8 Sonnet agents in parallel
- Will burn a lot of tokens — deliberate investment, not casual usage

### 9. Requirements
- Claude Code v2.1.32+ with CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
- Firecrawl CLI + FIRECRAWL_API_KEY
- Node >= 18, Python >= 3.9

### 10. Troubleshooting
- Commands not found → restart Claude Code
- Firecrawl errors → check API key/credits
- Pipeline fails → check Python, requirements.txt

### 11. License
- MIT
- Closing tagline: "Research once. Retrieve forever."

## Code Changes Required

1. **Rename skill**: `skill/SKILL.md` → `skill/massive-crawl/SKILL.md`
   - Update frontmatter `name` to `massive-crawl`
   - Update description to reflect new name
2. **Update install.sh**: Reference new skill path
3. **Update hook paths**: If any reference old skill name
4. **Copy hero image**: `assets/everything-on-earth.png`
5. **Write README.md**: Full rewrite following this design
