---
model: disabled
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
---

# Supercharge

Feed Claude the entire everything-on-earth capability graph. Run this once to
build the graph from all domain catalogs, wire hooks for automatic context
injection, and verify the pipeline end-to-end. After that, hooks keep Claude
domain-aware across sessions without any further invocation.

## Trigger

Use this skill when the user says "supercharge", "feed context",
"load capabilities", "wire the graph", or wants Claude to know about all
cataloged tools and domains.

## Behavior

When invoked, execute every step below in order. Do not skip steps.

### Step 1: Build the capability graph

Run the deterministic builder. This reads all 11 domain catalogs, extracts
capabilities from the telecoms pilot (the only domain with structured
`provides[]` data), and generates all graph/ontology/export artifacts plus
Claude skill files.

```bash
python3 "$CLAUDE_PROJECT_DIR/pipeline/build_capability_graph.py" --adapter claude
```

Print the builder output so the user sees domain counts, capability counts,
and edge counts.

### Step 2: Verify hooks are wired in settings

Read `.claude/settings.local.json` and confirm these three hook entries exist:

| Event | Matcher | Script |
|-------|---------|--------|
| `SessionStart` | `startup` | `adapters/claude/hooks/supercharge/session-context.sh` |
| `SessionStart` | `compact` | `adapters/claude/hooks/supercharge/compact-restore.sh` |
| `UserPromptSubmit` | (none) | `adapters/claude/hooks/supercharge/route-query.py` |

If any are missing, add them to the settings file. Follow the existing hook
format in the file.

### Step 3: Verify generated skills exist

Confirm these files are on disk:
- `adapters/claude/skills/capability-router/SKILL.md`
- `adapters/claude/skills/domain-telecoms/SKILL.md`

If missing, re-run Step 1 with `--adapter claude`.

### Step 4: Smoke-test the hooks

Run the session-context hook and show its output:
```bash
CLAUDE_PROJECT_DIR="$PWD" bash adapters/claude/hooks/supercharge/session-context.sh
```

Run the route-query hook with a telecoms prompt and confirm it routes correctly:
```bash
echo '{"prompt":"What tools handle 5G core network functions?"}' | CLAUDE_PROJECT_DIR="$PWD" python3 adapters/claude/hooks/supercharge/route-query.py
```

Run a non-matching prompt and confirm it produces no output:
```bash
echo '{"prompt":"Help me write a Python function"}' | CLAUDE_PROJECT_DIR="$PWD" python3 adapters/claude/hooks/supercharge/route-query.py
```

### Step 5: Report to the user

Print a summary:
- How many capabilities, edges, and domains were built
- Which hooks are wired and what they do
- That every future session in this project will auto-inject domain context
- That every prompt is keyword-matched against the routing index; matching
  prompts get domain-specific context injected automatically

## What the hooks do after supercharge runs

1. **SessionStart (startup)**: Injects capability graph overview so Claude is
   domain-aware from the first message
2. **UserPromptSubmit**: Keyword-matches every prompt against 3,000+ routing
   hints; when a domain matches, injects that domain's capability summary,
   top capabilities, and graph asset paths
3. **SessionStart (compact)**: Re-injects the overview after context compaction
   so domain awareness survives compression

## Hook scripts

All live under `adapters/claude/hooks/supercharge/`:
- `session-context.sh` — SessionStart (startup + compact)
- `compact-restore.sh` — delegates to session-context.sh
- `route-query.py` — UserPromptSubmit keyword router

## Rebuilding

To refresh the graph after new catalogs are added or entries change:
```
/supercharge
```
It re-runs the builder and re-verifies everything.
