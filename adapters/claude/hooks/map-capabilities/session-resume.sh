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
  # Get tier distribution from catalog
  TIER_DIST=$(python3 -c "
import json, sys
entries = json.load(open(sys.argv[1]))
t = {1: 0, 2: 0, 3: 0}
for e in entries:
    s = e.get('stars', 0)
    if s > 500: t[1] += 1
    elif s >= 50: t[2] += 1
    else: t[3] += 1
print(f'T1: {t[1]} | T2: {t[2]} | T3: {t[3]}')
" "$CATALOG" 2>/dev/null || echo "")

  CTX="map-capabilities ($CATALOG_NAME): $COMPLETED/$TOTAL complete, $PENDING pending"
  if [[ -n "$TIER_DIST" ]]; then
    CTX="$CTX | $TIER_DIST"
  fi
  if [[ "$RETRIES" -gt 0 ]]; then
    CTX="$CTX, $RETRIES to retry"
  fi
  CTX="$CTX ($WAVES waves remaining)"
  CTX="$CTX — run /map-capabilities to continue"

  PROGRESS_FILE="$OUTPUT_DIR/wave-progress.json"
  if [[ -f "$PROGRESS_FILE" ]]; then
    STRANDED=$(jq -r '.in_progress | length' "$PROGRESS_FILE" 2>/dev/null || echo 0)
    if [[ "$STRANDED" -gt 0 ]]; then
      CTX="$CTX (note: $STRANDED entries in-progress from last session — will be recovered)"
    fi
  fi
fi

jq -n --arg ctx "$CTX" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $ctx
  }
}'
