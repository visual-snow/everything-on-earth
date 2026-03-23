#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject prompt templates + reference files into map-capabilities agents.
# Only activates for agents named researcher-*, writer-*, judge-wave-*.
# The parent conversation never sees this content, keeping context lean.
#
# Note: set -euo pipefail is intentionally omitted. This hook uses
# cat ... 2>/dev/null with empty-string fallback checks for graceful
# degradation. Pipefail would cause early exit before fallback logic runs.

INPUT=$(cat)

# Check both agent_name and name fields (standalone Agent calls may use either)
AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // .name // empty')

# Only inject for our agents
case "$AGENT_NAME" in
  researcher-*|writer-*|judge-wave-*) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
REF_DIR="$PROJECT_DIR/skill/references"

case "$AGENT_NAME" in
  researcher-*)
    RESEARCHER_PROMPT=$(cat "$REF_DIR/capability-researcher.md" 2>/dev/null)
    SCHEMA=$(cat "$REF_DIR/capability-factsheet-schema.json" 2>/dev/null)
    if [[ -z "$RESEARCHER_PROMPT" || -z "$SCHEMA" ]]; then
      echo "Warning: Could not read researcher reference files from $REF_DIR" >&2
      exit 0
    fi
    jq -n --arg prompt "$RESEARCHER_PROMPT" --arg schema "$SCHEMA" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY RESEARCHER REFERENCE:\n\n## Researcher Prompt\n" + $prompt + "\n\n## Factsheet Schema\n" + $schema)
      }
    }'
    ;;

  writer-*)
    WRITER_PROMPT=$(cat "$REF_DIR/capability-writer.md" 2>/dev/null)
    GOLD=$(cat "$REF_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$WRITER_PROMPT" || -z "$GOLD" ]]; then
      echo "Warning: Could not read writer reference files from $REF_DIR" >&2
      exit 0
    fi
    jq -n --arg prompt "$WRITER_PROMPT" --arg gold "$GOLD" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY WRITER REFERENCE:\n\n## Writer Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $gold)
      }
    }'
    ;;

  judge-wave-*)
    JUDGE_PROMPT=$(cat "$REF_DIR/capability-judge.md" 2>/dev/null)
    GOLD=$(cat "$REF_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$JUDGE_PROMPT" || -z "$GOLD" ]]; then
      echo "Warning: Could not read judge reference files from $REF_DIR" >&2
      exit 0
    fi
    jq -n --arg prompt "$JUDGE_PROMPT" --arg gold "$GOLD" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY JUDGE REFERENCE:\n\n## Judge Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $gold)
      }
    }'
    ;;
esac
