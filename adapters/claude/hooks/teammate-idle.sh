#!/bin/bash
# Hook: teammate-idle.sh
# Trigger: TeammateIdle
# Purpose: Check for unclaimed tasks. If tasks remain, nudge teammate to claim one.
# Exit 2 = keeps teammate working (prevents idle).

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Check for unclaimed tasks by looking at discovery files vs config
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_FILE="$PROJECT_DIR/swarm-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  exit 0  # can't check, allow idle
fi

TOTAL_TASKS=$(jq '.sub_domains | length' "$CONFIG_FILE" 2>/dev/null)
TOTAL_TASKS=$((TOTAL_TASKS + 1))  # +1 for awesome-lists task

COMPLETED=$(ls "$PROJECT_DIR/discovery/"*.json 2>/dev/null | wc -l | tr -d ' ')

REMAINING=$((TOTAL_TASKS - COMPLETED))

if [ "$REMAINING" -gt 0 ]; then
  echo "There are approximately $REMAINING unclaimed tasks remaining. Check TaskList and claim the next one." >&2
  exit 2
fi

exit 0
