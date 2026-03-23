#!/bin/bash
# Hook: task-completed.sh
# Trigger: TaskCompleted
# Purpose: Validate agent output file exists and has correct JSON structure.
# Exit 2 = block completion (feeds error back to teammate).

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject // empty')

# Only validate our teams
[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Derive expected output file from task subject (sub-domain id)
SUBDOMAIN_ID=$(echo "$TASK_SUBJECT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
OUTPUT_FILE="discovery/${SUBDOMAIN_ID}.json"

if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Output file $OUTPUT_FILE not found. Write results before completing." >&2
  exit 2
fi

# Validate JSON parses
if ! jq empty "$OUTPUT_FILE" 2>/dev/null; then
  echo "Invalid JSON in $OUTPUT_FILE" >&2
  exit 2
fi

# Validate it's an array with repo_url fields
if ! jq -e '.[0].repo_url' "$OUTPUT_FILE" > /dev/null 2>&1; then
  echo "Invalid output: entries must be an array with repo_url field" >&2
  exit 2
fi

COUNT=$(jq 'length' "$OUTPUT_FILE")
if [ "$COUNT" -lt 1 ]; then
  echo "Output file has 0 entries. Search harder." >&2
  exit 2
fi

echo "Validated $OUTPUT_FILE: $COUNT entries" >&2
exit 0
