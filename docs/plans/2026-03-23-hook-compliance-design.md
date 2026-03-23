# Hook Compliance Pass — Design

## Problem

The map-capabilities skill has 6 hooks designed to enforce quality gates, inject context, track progress, and enable resumability. An audit against CLAUDE.md best practices found:

1. ~~Hooks not registered in settings.json~~ (fixed)
2. Context duplication: SKILL.md `!cat` and SubagentStart hook both inject reference files
3. No tool restrictions on spawned agents
4. Redundant file copy in install.sh
5. Notification collision undocumented
6. Error handling choice in subagent-context.sh undocumented

## Changes

### SKILL.md — Remove `!cat` duplication

Replace `!cat skill/references/...` preprocessor directives with comments indicating hook injection. Agent prompts become structural templates showing only the dynamic data (catalog entry, factsheet, feedback). SubagentStart hook is the single source of truth for reference file injection.

Affects: Researcher, Writer, and Judge agent spawn blocks.

### SKILL.md — Add tool restrictions

Restrict each agent type to minimum required tools:

| Agent | Allowed Tools | Rationale |
|-------|--------------|-----------|
| Researcher | WebSearch, WebFetch, Read, Grep, Glob | Needs web access for research |
| Writer | Read | Transforms factsheet to prose, no external access |
| Judge | Read | Reads and evaluates, never writes |

### install.sh — Remove redundant copy

Remove the block that copies hooks to `~/.claude/hooks/map-capabilities/`. Settings.json references `$CLAUDE_PROJECT_DIR/hooks/map-capabilities/` so the copied files are never executed.

### statusline.js — Document mutual exclusion

Add comment explaining that both massive-crawl and map-capabilities statusline hooks check for their respective config files and exit 0 if absent. No runtime collision possible.

### subagent-context.sh — Document error handling choice

Add comment explaining why `set -euo pipefail` is intentionally omitted: the hook uses `cat ... 2>/dev/null` with empty-string fallback checks. Pipefail would cause early exit before the graceful degradation logic runs.

## Files Modified

- `skill/map-capabilities/SKILL.md` — remove !cat, add tool restrictions
- `install.sh` — remove redundant copy block
- `hooks/map-capabilities/statusline.js` — add mutual exclusion comment
- `hooks/map-capabilities/subagent-context.sh` — add error handling comment
