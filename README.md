# everything-on-earth

A Claude Code plugin that discovers every open-source GitHub/GitLab repo for any topic using parallel agent swarms and a deterministic synthesis pipeline.

```
/everything-on-earth "Kubernetes security tools"
```

## How It Works

**LLM agents for discovery, deterministic Python for synthesis.** Never use an LLM for set operations on large data.

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

### Phase 1: Brainstorm

Three cheap Haiku scout agents search for existing awesome-lists, validate seed queries, and check for prior art. Claude asks you 3-8 clarifying questions and builds a mental model diagram showing sub-domains, teammate count, and estimated budget. You approve before anything expensive runs.

### Phase 2: Discover

A TeamCreate swarm of 6-8 Sonnet teammates shares a task pool (one task per sub-domain). Each teammate claims tasks from the shared list, runs firecrawl searches and scrapes, writes results to `discovery/{sub-domain}.json`, then claims the next task. A `SubagentStart` hook injects the prompt template and output schema into each teammate -- the parent conversation never sees this content, keeping context lean.

### Phase 3: Pipeline

A deterministic Python pipeline (`pipeline.py`) handles dedup, pruning, enrichment, and finalization. No LLM touches the merge or dedup -- that's `jq -s 'add'` and set-based URL matching. The pipeline pauses after dedup so you can set pruning thresholds.

### Outputs

| File | Format | Purpose |
|------|--------|---------|
| `catalog.json` | JSON | Machine-readable canonical output |
| `explorer.html` | HTML | Browse and filter in your browser |
| `RESULTS.md` | Markdown | Stats, domain breakdown, top repos |

## Architecture

```
Skill (SKILL.md)
  |-- 3 Haiku scouts (individual Agent calls)
  |-- swarm-config.json (the contract)
  |
  +-- TeamCreate swarm
       |-- 6-8 Sonnet teammates (self-claiming from task pool)
       |-- SubagentStart hook (injects template + schema)
       |-- TaskCompleted hook (validates output JSON)
       |-- TeammateIdle hook (nudges to claim next task)
       |
       +-- Deterministic concat (jq, not an LLM)
            |
            +-- pipeline.py (dedup -> prune -> enrich -> finalize)

6 Hooks:
  1. pre-teamcreate.js    -- gate: validates config + firecrawl
  2. subagent-context.sh  -- injects template into teammates
  3. task-completed.sh    -- validates output files
  4. teammate-idle.sh     -- redirects idle agents to unclaimed tasks
  5. post-concat.js       -- triggers pipeline after concat
  6. statusline.js        -- real-time progress bar
```

## Why This Architecture

This design was born from a real failure. In March 2026, a 23-agent swarm discovered 876 telecom simulator repos in 30 minutes -- but the LLM synthesizer silently dropped 73 critical repos (including industry standards like Netopeer2 and pyang) while confidently reporting success. Root cause: context saturation at ~100K tokens caused fuzzy name matching instead of exact URL lookups.

The fix: deterministic Python for any operation touching >100 objects. LLM agents are excellent at fuzzy, creative, parallel discovery. They are terrible at exact set operations. This plugin enforces that boundary architecturally.

See [meta-analysis.md](meta-analysis.md) for the full case study.

## Requirements

- [Claude Code](https://claude.com/claude-code) v2.1.32+ with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- [Firecrawl CLI](https://firecrawl.dev) with `FIRECRAWL_API_KEY`
- Node >= 18, Python >= 3.9

## Install

```bash
git clone https://github.com/eaguaida/everything-on-earth.git
cd everything-on-earth
./install.sh
```

Installs the skill to `~/.claude/skills/`, hooks to `~/.claude/hooks/`, and registers hook triggers in `settings.json`.

Uninstall: `./install.sh --uninstall`

## Cost

| Component | Typical Cost |
|-----------|-------------|
| Firecrawl credits | ~$4-6 (400-600 credits) |
| LLM tokens (8 Sonnet teammates) | ~$8-12 |
| Batch API enrichment | ~$1-3 |
| **Total per run** | **~$13-21** |

## License

MIT
