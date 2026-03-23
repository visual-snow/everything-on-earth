# everything-on-earth — Design Document

**Date:** 2026-03-23
**Status:** Approved (v2 — revised with TeamCreate + hooks research)
**Origin:** Generalized from the swarm-discovery-pipeline skill and telecom meta-analysis case study

## Overview

A Claude Code plugin that discovers every open-source GitHub/GitLab repo for any topic using a TeamCreate agent swarm with self-claiming task coordination and a deterministic synthesis pipeline.

**Core principle:** LLM swarm for discovery (fuzzy, creative, parallel), deterministic Python for synthesis (exact, reliable, auditable). Never use an LLM for set operations on large data.

**Architecture:** Skill + 6 Hooks + TeamCreate + Python Pipeline

**Agent model:** 6-8 Sonnet teammates share a task pool of N sub-domain tasks. Each teammate claims tasks sequentially from the shared list, writes results to disk, and claims the next. No synthesizer agent — concat is deterministic. SubagentStart hook injects reference context into teammates, keeping the parent conversation lean.

## User-Facing Flow

### Invocation

```
/everything-on-earth "Kubernetes security tools"
```

### Phase 1: Brainstorm (interactive, 3-8 questions)

**Step 1 — Scout agents (automatic on invocation):**

Three Haiku scout agents launch immediately as individual `Agent` calls (NOT team members). They run in parallel (~30 seconds, ~$0.01) and return findings to inform the brainstorming:

| Scout | Purpose |
|---|---|
| `awesome-lists-scout` | Searches for existing curated awesome-lists on the topic |
| `query-validator` | Runs 2-3 sample GitHub/firecrawl searches to test seed query quality |
| `landscape-checker` | Checks for existing catalogs, surveys, or databases on the topic |

**Step 2 — Interactive brainstorming:**

The skill asks clarifying questions one at a time, informed by scout findings:
- Constraints (min stars, language, activity recency)
- Known sub-domains the user already has in mind
- Sub-domains surfaced by scouts that the user may not have considered
- Seed repos the user has already found

**Step 3 — Mental model diagram:**

Claude builds a **mental model text diagram** in the conversation that evolves with each answer:

```
+---------------------------------------------------+
|  Everything on Earth                              |
|  Topic: K8s Security Tools                        |
|  Constraints: >=20 stars, active since 2023       |
|                                                   |
|  Sub-domains (draft):                             |
|  |-- network-policy & service mesh                |
|  |-- RBAC & access control                        |
|  |-- image scanning                               |
|  |-- [scout found: runtime security]              |
|  |-- ...?                                         |
|  Agents: ~6-8 (self-claiming from task pool)      |
|  Budget: ~10 searches + ~30 scrapes per task      |
+---------------------------------------------------+
```

The diagram grows iteratively as the user provides input, adds sub-domains, or splits/merges categories. The final version shows the complete task pool and teammate roster:

```
+---------------------------------------------------+
|  Everything on Earth                              |
|  Topic: K8s Security Tools                        |
|  Constraints: >=20 stars, active since 2023       |
|                                                   |
|  Task pool (13 tasks):                            |
|  |-- task-001: network-policy      (10 queries)   |
|  |-- task-002: rbac-access-control (10 queries)   |
|  |-- ...                                          |
|  |-- task-012: supply-chain        (10 queries)   |
|  |-- task-013: awesome-lists       (curated)      |
|                                                   |
|  Teammates: 8 (Sonnet, self-claiming)             |
|  Each claims ~1-2 tasks sequentially              |
|                                                   |
|  Estimated budget:                                |
|  |-- Searches: ~130 (13 tasks x 10)               |
|  |-- Scrapes:  ~390 (13 tasks x 30)               |
|  |-- Total:    ~520 firecrawl credits              |
|  |-- Cost:     ~$4-6 firecrawl + ~$8-12 tokens    |
+---------------------------------------------------+
```

**HARD GATE:** Do NOT write `swarm-config.json` or call TeamCreate until the user explicitly approves the roster.

### Phase 2: Discover (autonomous, ~30 min)

1. Skill writes `swarm-config.json` (the contract)
2. Pre-TeamCreate hook validates config + firecrawl setup + credit budget
3. `TeamCreate("eoe-{topic}")` creates team and shared task list
4. `TaskCreate` x N creates one task per sub-domain + 1 awesome-lists task
5. `Agent` x 6-8 spawns teammates with `team_name` parameter
6. `SubagentStart` hook injects agent-prompt-template + output-schema + swarm-config into each teammate (parent never sees this content)
7. Teammates self-claim tasks from shared list, run firecrawl searches, write results to `discovery/{sub-domain-id}.json`
8. `TaskCompleted` hook validates each output file against schema
9. `TeammateIdle` hook checks for unclaimed tasks — nudges teammate to claim next or allows idle
10. Lead waits for all tasks completed, then runs deterministic concat
11. `post-concat` hook auto-triggers pipeline Stage 1

### Phase 3: Pipeline (semi-interactive)

- Stage 1 (dedup) runs automatically, prints distribution summary
- Claude presents the summary to the user and asks for pruning thresholds
- User sets thresholds (min score, min stars, active since)
- Stages 2-4 run: prune -> enrich -> finalize
- Three outputs written to `everything-on-earth-output/`

### Phase 4: Gap Review (optional)

- Claude asks if any expected domains are missing from results
- If yes, adds new tasks to existing team's task list and spawns 2-3 follow-up teammates (~20% extra budget)
- Merges into existing catalog through the same pipeline

## The `swarm-config.json` Contract

Single source of truth. Hooks read from this file, never from LLM output directly.

```json
{
  "topic": "Kubernetes Security Tools",
  "constraints": {
    "min_stars": 20,
    "active_since": "2023-01-01",
    "languages": null
  },
  "sub_domains": [
    {
      "id": "network-policy",
      "name": "Network Policy & Service Mesh Security",
      "seed_queries": [
        "kubernetes network policy tool open source",
        "k8s CNI security github",
        "calico network policy engine",
        "cilium network security kubernetes",
        "k8s ingress firewall open source",
        "service mesh security istio linkerd",
        "kubernetes microsegmentation tool",
        "k8s pod network isolation github",
        "kubernetes egress policy controller",
        "network policy editor kubernetes open source"
      ]
    }
  ],
  "agents": {
    "count": 8,
    "model": "sonnet",
    "budget_per_task": {
      "searches": 10,
      "scrapes": 30
    },
    "tools": ["firecrawl-search", "firecrawl-scrape", "Read", "Write", "Glob"],
    "mode": "bypassPermissions"
  },
  "tasks": {
    "per_subdomain": 1,
    "awesome_lists": 1,
    "total": "sub_domains.length + 1"
  },
  "pipeline": {
    "dedup_key": "repo_url",
    "normalize": "lowercase, strip trailing slash, remove .git suffix",
    "pruning": "interactive",
    "enrichment": "batch_api",
    "max_tokens": 1024
  },
  "output": {
    "catalog": "catalog.json",
    "explorer": "explorer.html",
    "summary": "RESULTS.md",
    "directory": "everything-on-earth-output/"
  },
  "schema_version": "2.0.0"
}
```

## The Six Hooks

### Hook 1: `pre-teamcreate.js`

**Trigger:** `PreToolUse` on `TeamCreate`
**Purpose:** Gate. Validates config and firecrawl setup before team creation.

Validation rules:
- `swarm-config.json` exists in working directory
- `sub_domains.length >= 3`
- Every sub-domain has 8-10 seed queries
- `schema_version` is supported
- `firecrawl` CLI exists in PATH
- `FIRECRAWL_API_KEY` is set and valid
- Available firecrawl credits >= estimated budget

On failure: `{ "decision": "block", "reason": "..." }` — TeamCreate never fires.

### Hook 2: `subagent-context.sh`

**Trigger:** `SubagentStart` (all agent types, filtered by team name in script)
**Purpose:** Inject reference context into teammates without bloating the parent conversation.

This is the core architectural improvement. The parent conversation never constructs full agent prompts — it just spawns teammates with a short description. The hook injects ~2KB of template + schema + config into each teammate's context at spawn time.

```bash
#!/bin/bash
INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

# Only inject for our discovery team
if [[ "$TEAM_NAME" != eoe-* ]]; then
  exit 0
fi

TEMPLATE=$(cat "$CLAUDE_PROJECT_DIR/skill/references/agent-prompt-template.md" 2>/dev/null)
SCHEMA=$(cat "$CLAUDE_PROJECT_DIR/skill/references/output-schema.json" 2>/dev/null)
CONFIG=$(cat "$CLAUDE_PROJECT_DIR/swarm-config.json" 2>/dev/null)

jq -n --arg tpl "$TEMPLATE" --arg sch "$SCHEMA" --arg cfg "$CONFIG" '{
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: ("DISCOVERY AGENT REFERENCE:\n\n## Agent Prompt Template\n" + $tpl + "\n\n## Output Schema\n" + $sch + "\n\n## Swarm Config\n" + $cfg)
  }
}'
```

### Hook 3: `task-completed.sh`

**Trigger:** `TaskCompleted`
**Purpose:** Validates each agent's output file when a task is marked complete.

```bash
#!/bin/bash
INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Derive expected output file from task subject (sub-domain id)
SUBDOMAIN_ID=$(echo "$TASK_SUBJECT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
OUTPUT_FILE="discovery/${SUBDOMAIN_ID}.json"

if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Output file $OUTPUT_FILE not found. Write results before completing." >&2
  exit 2  # blocks completion, feeds back to teammate
fi

# Validate JSON structure
if ! jq -e '.[0].repo_url' "$OUTPUT_FILE" > /dev/null 2>&1; then
  echo "Invalid output: entries must have repo_url field" >&2
  exit 2
fi

COUNT=$(jq 'length' "$OUTPUT_FILE")
if [ "$COUNT" -lt 1 ]; then
  echo "Output file has 0 entries. Search harder." >&2
  exit 2
fi

exit 0
```

### Hook 4: `teammate-idle.sh`

**Trigger:** `TeammateIdle`
**Purpose:** Check if unclaimed tasks remain. If so, nudge teammate to claim one instead of going idle.

```bash
#!/bin/bash
INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Count pending tasks in the team's task directory
PENDING=$(find ~/.claude/tasks/"$TEAM_NAME"/ -name "*.json" \
  -exec jq -r 'select(.status == "pending") | .id' {} \; 2>/dev/null | wc -l | tr -d ' ')

if [ "$PENDING" -gt 0 ]; then
  echo "There are $PENDING unclaimed tasks remaining. Check TaskList and claim the next one." >&2
  exit 2  # keeps teammate working
fi

exit 0  # no more tasks, allow idle
```

### Hook 5: `post-concat.js`

**Trigger:** `PostToolUse` on `Bash`
**Purpose:** Detects when the lead runs the concat command and auto-triggers pipeline Stage 1.

Behavior:
1. Checks if the Bash command produced `raw-discovery.json`
2. Runs `pipeline.py --stage dedup --config swarm-config.json`
3. Injects distribution summary into conversation via `additionalContext`
4. Lead presents summary to user and asks for pruning thresholds

### Hook 6: `statusline.js`

**Trigger:** `Notification`
**Purpose:** Real-time progress display.

```
everything-on-earth | K8s Security | tasks: 9/13 | repos: 342 | 69%
```

Reads task completion status from `~/.claude/tasks/{team-name}/` and counts results in `discovery/*.json` files.

## Hook Registration in `settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "TeamCreate",
        "hooks": [{ "type": "command", "command": "node ~/.claude/hooks/everything-on-earth/pre-teamcreate.js" }]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/everything-on-earth/subagent-context.sh" }]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/everything-on-earth/task-completed.sh" }]
      }
    ],
    "TeammateIdle": [
      {
        "hooks": [{ "type": "command", "command": "~/.claude/hooks/everything-on-earth/teammate-idle.sh" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "node ~/.claude/hooks/everything-on-earth/post-concat.js" }]
      }
    ],
    "Notification": [
      {
        "hooks": [{ "type": "command", "command": "node ~/.claude/hooks/everything-on-earth/statusline.js" }]
      }
    ]
  }
}
```

## Deterministic Pipeline (`pipeline.py`)

Single Python file, four stages. Each stage reads a file, transforms it, writes a file.

### Interface

```bash
python pipeline.py --config swarm-config.json
python pipeline.py --config swarm-config.json --stage dedup
python pipeline.py --config swarm-config.json --stage prune,enrich,finalize --min-score 5 --min-stars 20
```

### Stage 1: Dedup

- Reads `raw-discovery.json`
- URL normalization: `lowercase -> strip trailing / -> remove .git suffix`
- Set-based dedup on normalized `repo_url`
- Keeps entry with highest score on collision
- Asserts: `len(output) <= len(input)` and `len(output) >= 1`
- Writes `dedup.json`

### Stage 2: Prune

- Reads `dedup.json` + user thresholds from CLI args
- Hard cuts: no `repo_url`, no `description`
- Soft cuts: below `--min-score`, below `--min-stars`, inactive before `--active-since`
- Logs exactly what was pruned and why
- Writes `pruned.json`

### Stage 3: Enrich

- Reads `pruned.json`
- Anthropic Batch API, one item per request
- Enriches: normalized tags, category assignment, one-line summary
- Strips markdown code fences from responses
- `max_tokens >= 1024`
- Asserts: `len(output) == len(input)` (enrichment never drops items)
- Writes `enriched.json`

### Stage 4: Finalize

- Reads `enriched.json`
- Schema validation against `output-schema.json`
- Clusters by sub-domain, sorts by score descending
- Writes three outputs:
  - `catalog.json` — canonical machine-readable output
  - `explorer.html` — injects catalog into HTML template
  - `RESULTS.md` — stats, domain breakdown, top-scored items via Jinja template

### Dependencies

```
anthropic>=0.40.0
jinja2>=3.1.0
```

### Intermediate files

Every stage writes to disk: `dedup.json`, `pruned.json`, `enriched.json`. If Stage 3 fails, restart from `pruned.json`, not from scratch.

## File Structure

```
everything-on-earth/
|-- README.md
|-- install.sh
|
|-- skill/
|   |-- SKILL.md
|   +-- references/
|       |-- agent-prompt-template.md
|       +-- output-schema.json
|
|-- hooks/
|   |-- pre-teamcreate.js
|   |-- subagent-context.sh
|   |-- task-completed.sh
|   |-- teammate-idle.sh
|   |-- post-concat.js
|   +-- statusline.js
|
|-- pipeline/
|   |-- pipeline.py
|   |-- requirements.txt
|   +-- templates/
|       |-- explorer.html
|       +-- results.md.jinja
|
+-- examples/
    +-- swarm-config.example.json
```

## Installation

```bash
git clone https://github.com/you/everything-on-earth.git
cd everything-on-earth
./install.sh
```

`install.sh` performs:
1. Copies skill -> `~/.claude/skills/everything-on-earth/`
2. Copies hooks -> `~/.claude/hooks/everything-on-earth/`
3. Registers hooks in `settings.json` with correct triggers and matchers
4. Checks dependencies: Node >= 18, Python >= 3.9, firecrawl CLI, `FIRECRAWL_API_KEY`

Pipeline code stays in the cloned repo (referenced by path). Update with `git pull`.

Uninstall: `./install.sh --uninstall` removes skill, hooks, and settings entries.

## Firecrawl Dependency

Firecrawl is a hard dependency. Discovery agents need `firecrawl-search` and `firecrawl-scrape` to search and validate repos in real-time.

**Three gates prevent misconfigured runs:**
1. `install.sh` checks for firecrawl CLI and API key, prints setup instructions if missing
2. Hook 1 (`pre-teamcreate.js`) validates firecrawl is working and credits are sufficient before any agents spawn
3. The brainstorming phase shows estimated credit cost in the mental model diagram before user approves

**Typical cost:** 400-600 firecrawl credits (~$4-6) per run, plus ~$8-12 in LLM tokens for 8 teammates.

## Failure Modes and Mitigations

| Failure Mode | Mitigation |
|---|---|
| Context saturation — LLM can't track 100+ objects | Deterministic Python for any operation touching >100 objects |
| Parent context bloat — template text x N agents | SubagentStart hook injects template; parent never sees it |
| Fuzzy matching — LLM "recognizes" names instead of exact lookup | URL normalization + set-based exact lookups in `pipeline.py` |
| Silent data loss — LLM drops items while reporting success | Count assertions at every pipeline stage boundary |
| Confident false metrics — LLM reports plausible but wrong numbers | Never trust LLM-reported counts — `pipeline.py` verifies programmatically |
| Taxonomy blind spots — decomposition misses sub-domains | Scout agents + gap review phase + awesome-lists task |
| Schema divergence — agents use different field names | `output-schema.json` + TaskCompleted hook validates every output |
| Batch API code fences — LLM wraps JSON in markdown | `pipeline.py` strips markdown fences from all LLM responses |
| Token truncation — LLM response cut short | `max_tokens >= 1024` for all structured output |
| Firecrawl not configured | Three gates: install check, pre-TeamCreate hook, brainstorm budget display |
| Agents launched before user approval | HARD GATE in SKILL.md: no TeamCreate until explicit user approval |
| Seed queries too similar across sub-domains | Query-validator scout tests 2-3 searches before brainstorm concludes |
| Task starvation — all tasks claimed before slow agent finishes | TeammateIdle hook redirects idle agents; budget_per_task caps work per claim |
| Teammate never marks task complete | TaskCompleted hook enforces output file exists; lead monitors task list |
| Synthesizer LLM drops data | Eliminated — deterministic `jq` concat replaces LLM synthesizer |

## Design Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Resource types | GitHub/GitLab repos only | Fixed schema, fixed dedup key, fixed pipeline |
| Mental model format | Text diagram in conversation | Iterative, visible, no tooling dependency |
| Architecture | Skill + 6 Hooks + TeamCreate | Hooks enforce deterministic guarantees; TeamCreate coordinates parallel work |
| Agent count | 6-8 flexible (self-claiming) | Docs recommend 3-5; flexible claiming recovers from slow agents; ~50% token savings vs 1:1 mapping |
| Agent model | Sonnet | Balances capability and cost; Haiku too weak for creative search, Opus unnecessary |
| Context injection | SubagentStart hook | Keeps parent lean (~50K tokens); template never enters parent context |
| Synthesizer | Eliminated (deterministic concat) | Meta-analysis proved LLMs fail at 100+ object synthesis; `jq -s 'add'` is exact |
| Scout agents | 3 Haiku agents before brainstorm | Validates seed queries and discovers existing curated lists cheaply (~$0.01) |
| Task coordination | TeamCreate shared task list | Self-claiming avoids lead bottleneck; file locking prevents race conditions |
| Pipeline autonomy | Interactive (pause after dedup) | Pruning is a judgment call the user should own |
| Pipeline code | Shipped as `pipeline.py` | Auditable, trustable, updatable via git pull |
| Distribution | Standalone repo | Clean separation from meta-analysis case study |
| Outputs | JSON + HTML + Markdown | Machine, browser, and quick-glance consumption |
| Firecrawl | Hard dependency | Can't discover "everything on earth" without searching the earth |

## Appendix: TeamCreate Orchestration Sequence

Detailed sequence for Phase 2 implementation:

```
Lead (main conversation):
  1. Write swarm-config.json
  2. TeamCreate("eoe-k8s-security")
     -> HOOK: pre-teamcreate.js validates config [PreToolUse]
  3. TaskCreate x 13 (one per sub-domain + awesome-lists)
     Each task: { subject: "{sub-domain-id}", description: "...", metadata: { seed_queries: [...] } }
  4. Agent x 8 (spawn teammates)
     Each: Agent({ team_name: "eoe-k8s-security", name: "discoverer-{n}", prompt: "You are a discovery agent. Claim tasks from the shared task list and search for repos." })
     -> HOOK: subagent-context.sh injects template+schema+config [SubagentStart]
  5. Wait for all tasks completed
     -> HOOK: teammate-idle.sh nudges idle agents to claim tasks [TeammateIdle]
     -> HOOK: task-completed.sh validates output files [TaskCompleted]
  6. Bash("jq -s 'add' discovery/*.json > raw-discovery.json")
     -> HOOK: post-concat.js triggers pipeline [PostToolUse]
  7. SendMessage({ to: "*", type: "shutdown_request" })  -- only if needed
  8. TeamDelete("eoe-k8s-security")

Each Teammate:
  1. Receives injected context (template, schema, config) via SubagentStart hook
  2. TaskList() -> finds unclaimed tasks
  3. TaskUpdate(taskId, { status: "in_progress", owner: "discoverer-{n}" })
  4. Reads seed_queries from task metadata
  5. firecrawl-search x 10 per task
  6. firecrawl-scrape on promising results
  7. Scores each repo (0-10) with rationale
  8. Write("discovery/{sub-domain-id}.json", results)
     -> HOOK: task-completed.sh validates output [TaskCompleted]
  9. TaskUpdate(taskId, { status: "completed" })
  10. TaskList() -> claim next unclaimed task or go idle
      -> HOOK: teammate-idle.sh checks for remaining tasks [TeammateIdle]
```
