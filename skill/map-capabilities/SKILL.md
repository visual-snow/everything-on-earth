---
name: map-capabilities
description: >-
  Generates capability documentation for catalog entries using a three-phase
  agent pipeline (Researcher, Writer, Judge) executed in batched waves of 15.
  Use when the user says "map capabilities", "generate capability docs",
  "capability mapper", or wants to pre-generate sandbox capability files from
  a catalog. Reads catalog.json as input, writes one {slug}/capability.md per
  entry inside a per-slug directory. Handles resumability via wave-progress.json and retries failed entries
  with Judge feedback.
allowed-tools:
  - Agent
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# map-capabilities

Generate capability documentation from a catalog using a Researcher → Writer → Judge agent pipeline.

## Table of Contents

1. [Inputs](#inputs)
2. [Phase 1: Prepare](#phase-1-prepare)
3. [Phase 2: Wave Execution](#phase-2-wave-execution)
4. [Phase 3: Report](#phase-3-report)
5. [Resumability](#resumability)

## Inputs

Required arguments:
- `--catalog PATH` — path to catalog.json (array of entries — minimum required fields: name, repo_url, description)
- `--output-dir PATH` — domain directory where per-framework folders and `wave-progress.json` are written

Example:
```
/map-capabilities --catalog catalog/gaming/catalog.json --output-dir catalog/gaming
```

## Phase 1: Prepare

1. **Load catalog and check progress:**
```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action load --write-config
```

2. **Show status to user:**
   - Total entries, completed, failed, pending, waves remaining
   - If resuming: show what was done and what's left

3. **Ask for confirmation:**
   - "Ready to process the next wave of 15 entries?" (AskUserQuestion)
   - HARD GATE: Do NOT proceed without user approval

## Phase 2: Wave Execution

**Repeat for each wave until all entries are processed.**

### Step 1: Get next wave
```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action next-wave
```
This returns up to 15 catalog entries (retries first, then pending).

### Step 2: Scrape phase (sequential)

For each entry in the wave, the orchestrator fetches external content using firecrawl.
Create the `{slug}/` directory first, then save the catalog entry to `$OUTPUT_DIR/{slug}/entry.json`.

```bash
# 1. Scrape the repo README
firecrawl scrape {repo_url} --format markdown > $OUTPUT_DIR/{slug}/readme-raw.md

# 2. Attempt docker-compose.yml (ignore failure)
firecrawl scrape "https://raw.githubusercontent.com/{owner}/{repo}/main/docker-compose.yml" --format markdown > $OUTPUT_DIR/{slug}/compose-raw.md 2>/dev/null || true

# 3. If README is thin (<50 lines), supplement with search
if [ $(wc -l < $OUTPUT_DIR/{slug}/readme-raw.md) -lt 50 ]; then
  firecrawl search "{name} {description}" --limit 1 --format markdown >> $OUTPUT_DIR/{slug}/readme-raw.md
fi
```

### Step 3: Researcher phase (parallel)

Spawn up to 15 Researcher agents in parallel:

```
Agent({
  model: "sonnet",
  name: "researcher-{slug}",
  allowed-tools: [],
  prompt:
    # Reference injected by SubagentStart hook: capability-researcher.md, capability-factsheet-schema.json

    ## CATALOG ENTRY
    ```json
    {entry_json}
    ```

    ## README CONTENT
    {contents of $OUTPUT_DIR/{slug}/readme-raw.md}

    ## DOCKER COMPOSE (if available)
    {contents of $OUTPUT_DIR/{slug}/compose-raw.md, or "No docker-compose.yml found."}
})
```

Collect each agent's FACTSHEET JSON output. Save to `$OUTPUT_DIR/{slug}/factsheet.json`.

### Step 4: Writer phase (parallel)

Spawn up to 15 Writer agents in parallel:

```
Agent({
  model: "sonnet",
  name: "writer-{slug}",
  allowed-tools: ["Read"],
  prompt:
    # Reference injected by SubagentStart hook: capability-writer.md, gold_sandbox_capabilities.md

    ## FACTSHEET
    ```json
    {factsheet_json}
    ```

    ## JUDGE FEEDBACK (if retry)
    {feedback_or_empty}

    Write the capability document. Return ONLY the markdown content.
})
```

Save each output to `$OUTPUT_DIR/{slug}/capability.md`.

### Step 5: Judge phase (single agent)

Spawn 1 Judge agent to batch-review all outputs from this wave:

```
Agent({
  model: "sonnet",
  name: "judge-wave-{n}",
  allowed-tools: ["Read"],
  prompt:
    # Reference injected by SubagentStart hook: capability-judge.md, gold_sandbox_capabilities.md

    ## FILES TO REVIEW
    {for each slug in wave:}
    ### {slug}
    #### FACTSHEET
    ```json
    {factsheet_json}
    ```
    #### CAPABILITY DOC
    {capability_md_content}
    {end for}
})
```

### Step 6: Process results

Parse Judge output. For each entry:

- **PASS:** Mark as done:
```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action mark-done --slugs passed_slug_1,passed_slug_2
```

- **FAIL:** Mark as failed with reasons:
```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action mark-failed --slugs failed_slug_1 --reasons '{"failed_slug_1":"ABSTRACTION: Docker image found on line 5"}'
```

Failed entries are re-queued with Judge feedback for the next wave.

### Step 7: Report wave results

Show: X passed, Y failed, Z total remaining.
Ask: "Continue to next wave?" (AskUserQuestion)

## Phase 3: Report

When all entries are processed (or user stops):

```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action status
```

Show final summary: total completed, total failed, any remaining.

## Resumability

- `wave-progress.json` tracks completed, failed, and in-progress slugs
- Re-running the skill picks up where it left off
- Failed entries are retried with Judge feedback injected into the Writer prompt
- The `next-wave` action prioritizes retries over new entries

## Hooks

Six hooks enforce deterministic guarantees at every boundary (installed by `install.sh`):

| Event | Matcher | Hook | Purpose |
|-------|---------|------|---------|
| PreToolUse | Agent | `pre-wave.sh` | Validates preconditions before agent spawn (catalog entry, factsheet, capability files) |
| SubagentStart | — | `subagent-context.sh` | Injects prompt templates + reference files into agents |
| PostToolUse | Write | `output-validator.sh` | Validates capability.md structure and abstraction level at write-time |
| PostToolUse | Bash | `wave-completed.sh` | Detects mark-done and injects wave progress summary |
| Notification | — | `statusline.js` | Real-time status bar: catalog name, wave, done/total, pct% |
| SessionStart | — | `session-resume.sh` | Detects incomplete work and injects resumability prompt |

All hooks read `map-capabilities-config.json` (written by `--write-config` during Phase 1) for catalog and output directory paths.

## Reference Files

- `skill/references/capability-researcher.md` — Researcher agent prompt
- `skill/references/capability-writer.md` — Writer agent prompt
- `skill/references/capability-judge.md` — Judge agent prompt
- `skill/references/gold_sandbox_capabilities.md` — Style exemplar
- `skill/references/capability-factsheet-schema.json` — Factsheet JSON schema
- `pipeline/generate_capabilities.py` — Wave orchestration utilities
