---
name: map-capabilities
description: >-
  Generates capability documentation for catalog entries using a three-phase
  agent pipeline (Researcher, Writer, Judge) executed in batched waves of 15.
  Use when the user says "map capabilities", "generate capability docs",
  "capability mapper", or wants to pre-generate sandbox capability files from
  a catalog. Reads catalog.json as input, writes one {slug}_capability.md per
  entry. Handles resumability via wave-progress.json and retries failed entries
  with Judge feedback.
allowed-tools:
  - Agent
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - WebFetch
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
- `--output-dir PATH` — directory where capability .md files and wave-progress.json are written

Example:
```
/map-capabilities --catalog path/to/catalog.json --output-dir path/to/output
```

## Phase 1: Prepare

1. **Load catalog and check progress:**
```bash
python3 pipeline/generate_capabilities.py --catalog $CATALOG --output-dir $OUTPUT_DIR --action load
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

### Step 2: Researcher phase (parallel)

Spawn up to 15 Researcher agents in parallel:

```
Agent({
  model: "sonnet",
  name: "researcher-{slug}",
  prompt: !`cat skill/references/capability-researcher.md`

    ## CATALOG ENTRY
    ```json
    {entry_json}
    ```
})
```

Collect each agent's FACTSHEET JSON output. Save to `$OUTPUT_DIR/{slug}_factsheet.json`.

### Step 3: Writer phase (parallel)

Spawn up to 15 Writer agents in parallel:

```
Agent({
  model: "sonnet",
  name: "writer-{slug}",
  prompt: !`cat skill/references/capability-writer.md`

    ## FACTSHEET
    ```json
    {factsheet_json}
    ```

    ## STYLE EXEMPLAR
    !`cat skill/references/gold_sandbox_capabilities.md`

    ## JUDGE FEEDBACK (if retry)
    {feedback_or_empty}

    Write the capability document. Return ONLY the markdown content.
})
```

Save each output to `$OUTPUT_DIR/{slug}_capability.md`.

### Step 4: Judge phase (single agent)

Spawn 1 Judge agent to batch-review all outputs from this wave:

```
Agent({
  model: "sonnet",
  name: "judge-wave-{n}",
  prompt: !`cat skill/references/capability-judge.md`

    ## STYLE EXEMPLAR
    !`cat skill/references/gold_sandbox_capabilities.md`

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

### Step 5: Process results

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

### Step 6: Report wave results

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

## Reference Files

- `skill/references/capability-researcher.md` — Researcher agent prompt
- `skill/references/capability-writer.md` — Writer agent prompt
- `skill/references/capability-judge.md` — Judge agent prompt
- `skill/references/gold_sandbox_capabilities.md` — Style exemplar
- `skill/references/capability-factsheet-schema.json` — Factsheet JSON schema
- `pipeline/generate_capabilities.py` — Wave orchestration utilities
