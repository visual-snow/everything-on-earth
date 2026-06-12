#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject tier-aware prompt templates + reference files into map-capabilities agents.
# Reads wave-manifest.json for tier classification and style anchors.
# Only activates for agents named researcher-*, writer-*, judge-wave-*.

INPUT=$(cat)

AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // .name // empty')

case "$AGENT_NAME" in
  researcher-*|writer-*|judge-wave-*) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PROMPT_DIR="$PROJECT_DIR/workflows/map-capabilities/prompts"
SCHEMA_DIR="$PROJECT_DIR/workflows/map-capabilities/schemas"
EXAMPLE_DIR="$PROJECT_DIR/workflows/map-capabilities/examples"

# Read config to find output_dir, then read manifest
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"
if [[ -f "$CONFIG_PATH" ]]; then
  OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_PATH")
  MANIFEST_PATH="$OUTPUT_DIR/wave-manifest.json"
else
  MANIFEST_PATH=""
fi

# Look up tier for a slug from the manifest
get_tier() {
  local slug="$1"
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r --arg s "$slug" '.slugs[] | select(.slug == $s) | .tier // 2' "$MANIFEST_PATH"
  else
    echo "2"
  fi
}

# Read style anchors from manifest
get_style_anchors() {
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r '.style_anchors[]' "$MANIFEST_PATH" 2>/dev/null
  fi
}

# Build tier summary for judges
get_tier_summary() {
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r '.slugs | map("- \(.slug): Tier \(.tier) (\(.stars) stars)") | join("\n")' "$MANIFEST_PATH"
  else
    echo "(no tier data available)"
  fi
}

case "$AGENT_NAME" in
  researcher-*)
    SLUG="${AGENT_NAME#researcher-}"
    TIER=$(get_tier "$SLUG")
    PROMPT=$(cat "$PROMPT_DIR/capability-researcher.md" 2>/dev/null)
    SCHEMA=$(cat "$SCHEMA_DIR/capability-factsheet-schema.json" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$SCHEMA" ]]; then
      echo "Warning: Could not read researcher reference files" >&2
      exit 0
    fi

    TIER_DIRECTIVE=""
    if [[ "$TIER" == "2" ]]; then
      TIER_DIRECTIVE="

## Tier 2 Directive
This is a mid-popularity project. Pay extra attention to the README for capability signals that may not be immediately obvious from the repository metadata alone."
    elif [[ "$TIER" == "3" ]]; then
      TIER_DIRECTIVE="

## Tier 3 Directive — Deep Extraction
This is a lesser-known project with limited community visibility. Extract every capability signal you can find. Check README sections, code comments, CI configs, and any documentation files for capability evidence. Be thorough; this project has fewer external references to corroborate capabilities."
    fi

    jq -n --arg prompt "$PROMPT" --arg schema "$SCHEMA" --arg tier "$TIER_DIRECTIVE" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY RESEARCHER REFERENCE:\n\n## Researcher Prompt\n" + $prompt + $tier + "\n\n## Factsheet Schema\n" + $schema)
      }
    }'
    ;;

  writer-*)
    SLUG="${AGENT_NAME#writer-}"
    TIER=$(get_tier "$SLUG")
    PROMPT=$(cat "$PROMPT_DIR/capability-writer.md" 2>/dev/null)
    EXEMPLAR=$(cat "$EXAMPLE_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$EXEMPLAR" ]]; then
      echo "Warning: Could not read writer reference files" >&2
      exit 0
    fi

    ANCHOR_CONTENT=""
    if [[ "$TIER" != "1" ]]; then
      while IFS= read -r anchor_path; do
        if [[ -f "$anchor_path" ]]; then
          ANCHOR_TEXT=$(cat "$anchor_path")
          ANCHOR_CONTENT="$ANCHOR_CONTENT

## Style Anchor (approved output)
$ANCHOR_TEXT"
        fi
      done < <(get_style_anchors)
    fi

    jq -n --arg prompt "$PROMPT" --arg exemplar "$EXEMPLAR" --arg anchors "$ANCHOR_CONTENT" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY WRITER REFERENCE:\n\n## Writer Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $exemplar + $anchors)
      }
    }'
    ;;

  judge-wave-*)
    PROMPT=$(cat "$PROMPT_DIR/capability-judge.md" 2>/dev/null)
    EXEMPLAR=$(cat "$EXAMPLE_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$EXEMPLAR" ]]; then
      echo "Warning: Could not read judge reference files" >&2
      exit 0
    fi

    TIER_SUMMARY=$(get_tier_summary)
    JUDGE_SCOPE=""
    if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
      JUDGE_SCOPE=$(jq -r '"Judge scope limits: T1 review up to \(.judge_scope["1"] // .judge_scope.1 // 5) at once, T2 up to \(.judge_scope["2"] // .judge_scope.2 // 3), T3 review 1:1 per entry."' "$MANIFEST_PATH" 2>/dev/null || echo "")
    fi

    jq -n --arg prompt "$PROMPT" --arg exemplar "$EXEMPLAR" \
          --arg tiers "$TIER_SUMMARY" --arg scope "$JUDGE_SCOPE" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY JUDGE REFERENCE:\n\n## Judge Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $exemplar + "\n\n## Wave Tier Breakdown\n" + $tiers + "\n\n" + $scope)
      }
    }'
    ;;
esac
