#!/bin/bash
# Hook: wave-completed.sh
# Trigger: PostToolUse on Bash
# Purpose: Detect mark-done completion and inject wave progress summary.
# Only triggers when generate_capabilities.py mark-done runs successfully.
# Non-gating — uses additionalContext, never exit 2.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only trigger on mark-done commands for our pipeline
case "$COMMAND" in
  *generate_capabilities.py*mark-done*) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"

if [[ ! -f "$CONFIG_PATH" ]]; then
  exit 0
fi

CATALOG=$(jq -r '.catalog' "$CONFIG_PATH")
OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_PATH")
CATALOG_NAME=$(jq -r '.catalog_name' "$CONFIG_PATH")

# Get authoritative progress from the pipeline script
STATUS=$(python3 "$PROJECT_DIR/pipeline/generate_capabilities.py" \
  --catalog "$CATALOG" --output-dir "$OUTPUT_DIR" --action status 2>/dev/null) || exit 0

COMPLETED=$(echo "$STATUS" | jq -r '.completed | length')
FAILED=$(echo "$STATUS" | jq -r '.failed | length')
IN_PROGRESS=$(echo "$STATUS" | jq -r '.in_progress | length')
TOTAL_PENDING=$(echo "$STATUS" | jq -r '.total_pending')

# Count total from catalog
TOTAL=$(jq 'length' "$CATALOG" 2>/dev/null || echo "?")
DONE=$((COMPLETED))
REMAINING=$((TOTAL - DONE))

# Per-tier stats from manifest
TIER_STATS=""
WAVE_NUM="?"
MANIFEST_PATH="$OUTPUT_DIR/wave-manifest.json"
if [[ -f "$MANIFEST_PATH" ]]; then
  WAVE_NUM=$(jq -r '.wave' "$MANIFEST_PATH")
  TIER_STATS=$(jq -r '
    .slugs | group_by(.tier) | map(
      "T\(.[0].tier): \(length)"
    ) | join(" | ")
  ' "$MANIFEST_PATH" 2>/dev/null || echo "")
fi

if [[ "$REMAINING" -le 0 && "$FAILED" -eq 0 ]]; then
  SUMMARY="map-capabilities ($CATALOG_NAME): All $TOTAL entries processed successfully."
else
  SUMMARY="map-capabilities ($CATALOG_NAME) wave $WAVE_NUM: $DONE/$TOTAL done"
  if [[ -n "$TIER_STATS" ]]; then
    SUMMARY="$SUMMARY | $TIER_STATS"
  fi
  if [[ "$FAILED" -gt 0 ]]; then
    SUMMARY="$SUMMARY | $FAILED to retry"
  fi
  if [[ "$REMAINING" -gt 0 ]]; then
    SUMMARY="$SUMMARY | $REMAINING remaining"
  fi
fi

jq -n --arg ctx "$SUMMARY" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: $ctx
  }
}'
