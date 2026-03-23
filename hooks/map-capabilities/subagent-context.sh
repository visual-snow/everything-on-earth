#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject prompt templates + reference files into map-capabilities agents.
# Only activates for agents named researcher-*, writer-*, judge-wave-*.
# The parent conversation never sees this content, keeping context lean.

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

# Emit SubagentStart context JSON from two reference files
emit_context() {
  local label="$1" key1="$2" file1="$3" key2="$4" file2="$5"
  local content1 content2
  content1=$(cat "$file1" 2>/dev/null)
  content2=$(cat "$file2" 2>/dev/null)
  if [[ -z "$content1" || -z "$content2" ]]; then
    echo "Warning: Could not read reference files for $label from $REF_DIR" >&2
    exit 0
  fi
  jq -n --arg c1 "$content1" --arg c2 "$content2" \
    --arg label "$label" --arg k1 "$key1" --arg k2 "$key2" '{
    hookSpecificOutput: {
      hookEventName: "SubagentStart",
      additionalContext: ("CAPABILITY " + $label + " REFERENCE:\n\n## " + $k1 + "\n" + $c1 + "\n\n## " + $k2 + "\n" + $c2)
    }
  }'
}

case "$AGENT_NAME" in
  researcher-*)
    emit_context "RESEARCHER" \
      "Researcher Prompt" "$REF_DIR/capability-researcher.md" \
      "Factsheet Schema"  "$REF_DIR/capability-factsheet-schema.json"
    ;;
  writer-*)
    emit_context "WRITER" \
      "Writer Prompt"   "$REF_DIR/capability-writer.md" \
      "Style Exemplar"  "$REF_DIR/gold_sandbox_capabilities.md"
    ;;
  judge-wave-*)
    emit_context "JUDGE" \
      "Judge Prompt"    "$REF_DIR/capability-judge.md" \
      "Style Exemplar"  "$REF_DIR/gold_sandbox_capabilities.md"
    ;;
esac
