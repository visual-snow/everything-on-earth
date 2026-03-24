#!/bin/bash
# Hook: session-resume.sh
# Trigger: SessionStart
# Purpose: Detect incomplete map-capabilities work and inject resumability prompt.
# Reuses generate_capabilities.py --action load for counts (no reimplemented logic).

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"

# No config = no active run — silent exit
if [[ ! -f "$CONFIG_PATH" ]]; then
  exit 0
fi

CATALOG=$(jq -r '.catalog' "$CONFIG_PATH")
OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_PATH")
CATALOG_NAME=$(jq -r '.catalog_name' "$CONFIG_PATH")

# Validate paths still exist
if [[ ! -f "$CATALOG" ]]; then
  exit 0
fi

# Get authoritative summary from pipeline
SUMMARY=$(python3 "$PROJECT_DIR/pipeline/generate_capabilities.py" \
  --catalog "$CATALOG" --output-dir "$OUTPUT_DIR" --action load 2>/dev/null) || exit 0

TOTAL=$(echo "$SUMMARY" | jq -r '.total_entries')
COMPLETED=$(echo "$SUMMARY" | jq -r '.completed')
PENDING=$(echo "$SUMMARY" | jq -r '.pending')
RETRIES=$(echo "$SUMMARY" | jq -r '.retry_queue')
WAVES=$(echo "$SUMMARY" | jq -r '.waves_remaining')

if [[ "$PENDING" -eq 0 && "$RETRIES" -eq 0 ]]; then
  CTX="map-capabilities ($CATALOG_NAME): all $TOTAL entries processed."
else
  CTX="map-capabilities ($CATALOG_NAME): $COMPLETED/$TOTAL complete, $PENDING pending"
  if [[ "$RETRIES" -gt 0 ]]; then
    CTX="$CTX, $RETRIES to retry"
  fi
  CTX="$CTX ($WAVES waves remaining)"
  CTX="$CTX — run /map-capabilities --catalog $CATALOG --output-dir $OUTPUT_DIR to continue"

  # Check for stranded in_progress entries
  PROGRESS_FILE="$OUTPUT_DIR/wave-progress.json"
  if [[ -f "$PROGRESS_FILE" ]]; then
    STRANDED=$(jq -r '.in_progress | length' "$PROGRESS_FILE" 2>/dev/null || echo 0)
    if [[ "$STRANDED" -gt 0 ]]; then
      CTX="$CTX (note: $STRANDED entries were in-progress when last session ended — they will be recovered on next wave)"
    fi
  fi
fi

jq -n --arg ctx "$CTX" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $ctx
  }
}'
