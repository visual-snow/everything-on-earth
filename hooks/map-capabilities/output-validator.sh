#!/bin/bash
# Hook: output-validator.sh
# Trigger: PostToolUse on Write
# Purpose: Validate capability.md structure and abstraction level at write-time.
# Exit 2 blocks the Write and feeds error back to Claude for correction.
# CLAUDE.md rule: Do NOT mix exit 2 with JSON stdout (JSON is ignored on exit 2).

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only validate capability.md files
if [[ "$FILE_PATH" != */capability.md ]]; then
  exit 0
fi

# Only validate files within our output directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"

if [[ ! -f "$CONFIG_PATH" ]]; then
  exit 0
fi

OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_PATH")

# Normalize paths to prevent traversal via embedded .. sequences (portable, no realpath -m)
IN_OUTPUT=$(python3 -c "
import os, sys
f, o = os.path.normpath(sys.argv[1]), os.path.normpath(sys.argv[2])
print('yes' if f.startswith(o + '/') else 'no')
" "$FILE_PATH" "$OUTPUT_DIR")

case "$IN_OUTPUT" in
  yes) ;;
  *) exit 0 ;;  # Not our file or traversal attempt — passthrough
esac

# Extract content from tool_input (available in PostToolUse on Write)
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

# Fallback: read from disk if content not in tool_input
if [[ -z "$CONTENT" && -f "$FILE_PATH" ]]; then
  CONTENT=$(cat "$FILE_PATH")
fi

if [[ -z "$CONTENT" ]]; then
  echo "output-validator: capability.md content is empty" >&2
  exit 2
fi

# Validation checks
ERRORS=""

# 1. Must start with a heading
FIRST_LINE=$(echo "$CONTENT" | head -n1)
if [[ "$FIRST_LINE" != "#"* ]]; then
  ERRORS="${ERRORS}STRUCTURE: must start with a heading (#)\n"
fi

# 2. Must contain ## Constraints section
if ! echo "$CONTENT" | grep -q '^## Constraints'; then
  ERRORS="${ERRORS}STRUCTURE: missing '## Constraints' section\n"
fi

# 3. Must be <= 60 lines
LINE_COUNT=$(echo "$CONTENT" | wc -l | tr -d ' ')
if [[ "$LINE_COUNT" -gt 60 ]]; then
  ERRORS="${ERRORS}LENGTH: ${LINE_COUNT} lines exceeds 60-line limit\n"
fi

# 4. No Docker image patterns (org/image:tag)
# Narrow pattern with common container namespace prefixes
if echo "$CONTENT" | grep -qE '(docker\.io|ghcr\.io|quay\.io|gcr\.io|registry\.|[a-z0-9]+/[a-z0-9_-]+:[0-9]+\.[0-9]+)'; then
  ERRORS="${ERRORS}ABSTRACTION: Docker image reference detected — use generic descriptions instead\n"
fi

# 5. No port numbers (:\d{4,5} not preceded by letter/year context)
if echo "$CONTENT" | grep -qE ':[0-9]{4,5}[^0-9]|:[0-9]{4,5}$'; then
  ERRORS="${ERRORS}ABSTRACTION: port number detected — omit specific ports\n"
fi

# 6. No file paths (/etc/, /var/, /opt/, /usr/)
if echo "$CONTENT" | grep -qE '/(etc|var|opt|usr|tmp|home)/'; then
  ERRORS="${ERRORS}ABSTRACTION: file path detected — use generic descriptions instead\n"
fi

if [[ -n "$ERRORS" ]]; then
  echo "output-validator: capability.md validation failed:" >&2
  echo -e "$ERRORS" >&2
  exit 2
fi

exit 0
