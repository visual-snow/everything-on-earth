#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject agent-prompt-template + output-schema + swarm-config into teammates.
# Only activates for teams named eoe-*.
# The parent conversation never sees this content, keeping context lean.

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

# Only inject for our discovery teams
if [[ "$TEAM_NAME" != eoe-* ]]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
WORKFLOW_DIR="$PROJECT_DIR/workflows/massive-crawl"

TEMPLATE=$(cat "$WORKFLOW_DIR/prompts/agent-prompt-template.md" 2>/dev/null)
SCHEMA=$(cat "$WORKFLOW_DIR/schemas/output-schema.json" 2>/dev/null)
CONFIG=$(cat "$PROJECT_DIR/swarm-config.json" 2>/dev/null)

if [[ -z "$TEMPLATE" || -z "$SCHEMA" ]]; then
  echo "Warning: Could not read reference files from $PROJECT_DIR" >&2
  exit 0
fi

jq -n --arg tpl "$TEMPLATE" --arg sch "$SCHEMA" --arg cfg "$CONFIG" '{
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: ("DISCOVERY AGENT REFERENCE:\n\n## Agent Prompt Template\n" + $tpl + "\n\n## Output Schema\n" + $sch + "\n\n## Swarm Config\n" + $cfg)
  }
}'
