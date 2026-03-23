#!/bin/bash
# Hook: pre-wave.sh
# Trigger: PreToolUse on Agent
# Purpose: Gate — validates preconditions before map-capabilities agent spawns.
#
# Agent name patterns:
#   researcher-{slug} → verify catalog entry JSON present in prompt
#   writer-{slug}     → verify factsheet.json exists for slug
#   judge-wave-{n}    → verify all in_progress slugs have capability.md
#   other             → passthrough (exit 0)
#
# Uses JSON {"decision": "block/allow"} on stdout (PreToolUse pattern).
# NEVER mixes exit 2 with JSON stdout (CLAUDE.md rule).

set -euo pipefail

INPUT=$(cat)
AGENT_NAME=$(echo "$INPUT" | jq -r '.tool_input.name // empty')

# Passthrough for non-map-capabilities agents
if [[ -z "$AGENT_NAME" ]]; then
  exit 0
fi

case "$AGENT_NAME" in
  researcher-*|writer-*|judge-wave-*) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"

# If no config, we're not in a map-capabilities run — passthrough
if [[ ! -f "$CONFIG_PATH" ]]; then
  exit 0
fi

# Read config once, parse twice — avoids two jq subprocess spawns per agent spawn
CONFIG=$(cat "$CONFIG_PATH")
CATALOG=$(echo "$CONFIG" | jq -r '.catalog')
OUTPUT_DIR=$(echo "$CONFIG" | jq -r '.output_dir')

# Validate config paths exist
if [[ ! -f "$CATALOG" ]]; then
  jq -n --arg r "map-capabilities config error: catalog not found at $CATALOG" \
    '{decision: "block", reason: $r}'
  exit 0
fi

block() {
  jq -n --arg r "$1" '{decision: "block", reason: $r}'
  exit 0
}

allow() {
  echo '{"decision": "allow"}'
  exit 0
}

case "$AGENT_NAME" in
  researcher-*)
    SLUG="${AGENT_NAME#researcher-}"
    # Verify catalog entry data is in the prompt
    PROMPT=$(echo "$INPUT" | jq -r '.tool_input.prompt // empty')
    if [[ -z "$PROMPT" ]]; then
      block "researcher-$SLUG: agent prompt is empty"
    fi
    # Check prompt contains required catalog fields
    if ! echo "$PROMPT" | grep -q '"name"'; then
      block "researcher-$SLUG: prompt missing catalog entry 'name' field"
    fi
    if ! echo "$PROMPT" | grep -q '"repo_url"'; then
      block "researcher-$SLUG: prompt missing catalog entry 'repo_url' field"
    fi
    allow
    ;;

  writer-*)
    SLUG="${AGENT_NAME#writer-}"
    FACTSHEET="$OUTPUT_DIR/$SLUG/factsheet.json"
    if [[ ! -f "$FACTSHEET" ]]; then
      block "writer-$SLUG: factsheet.json not found at $FACTSHEET — run researcher first"
    fi
    # Validate factsheet is parseable JSON
    if ! jq empty "$FACTSHEET" 2>/dev/null; then
      block "writer-$SLUG: factsheet.json is not valid JSON"
    fi
    allow
    ;;

  judge-wave-*)
    # Verify all in_progress slugs have capability.md
    PROGRESS_FILE="$OUTPUT_DIR/wave-progress.json"
    if [[ ! -f "$PROGRESS_FILE" ]]; then
      block "judge: wave-progress.json not found — no wave in progress"
    fi
    IN_PROGRESS=$(jq -r '.in_progress[]' "$PROGRESS_FILE" 2>/dev/null)
    MISSING=""
    for SLUG in $IN_PROGRESS; do
      CAP_FILE="$OUTPUT_DIR/$SLUG/capability.md"
      if [[ ! -f "$CAP_FILE" ]]; then
        MISSING="$MISSING $SLUG"
      fi
    done
    if [[ -n "$MISSING" ]]; then
      block "judge: missing capability.md for:$MISSING — run writers first"
    fi
    allow
    ;;
esac
