#!/bin/bash
set -euo pipefail

# massive-crawl installer
# Copies skill and hooks to ~/.claude/, registers hooks in settings.json

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DEST="$HOME/.claude/skills/massive-crawl"
HOOKS_DEST="$HOME/.claude/hooks/massive-crawl"
SETTINGS="$HOME/.claude/settings.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Uninstall mode ---
if [[ "${1:-}" == "--uninstall" ]]; then
  echo "Uninstalling massive-crawl + map-capabilities..."
  rm -rf "$SKILL_DEST" "$HOOKS_DEST"
  rm -rf "$HOME/.claude/skills/map-capabilities"
  if [ -f "$SETTINGS" ]; then
    # Remove hook entries containing "massive-crawl" or "map-capabilities"
    python3 -c '
import json, sys
settings_file = sys.argv[1]
with open(settings_file) as f:
    s = json.load(f)
hooks = s.get("hooks", {})
def remove_workflow(workflow_name):
    for event in list(hooks.keys()):
        hooks[event] = [h for h in hooks[event]
                        if not any(workflow_name in hook.get("command","")
                                   for hook in h.get("hooks", []))]
        if not hooks[event]:
            del hooks[event]
remove_workflow("massive-crawl")
remove_workflow("map-capabilities")
s["hooks"] = hooks
with open(settings_file, "w") as f:
    json.dump(s, f, indent=2)
print("Cleaned settings.json")
' "$SETTINGS" 2>/dev/null || echo "Could not clean settings.json automatically"
  fi
  echo -e "${GREEN}Uninstalled.${NC}"
  exit 0
fi

# --- Install mode ---
echo "Installing massive-crawl..."

# Check dependencies
MISSING=()

if ! command -v node &>/dev/null || [[ $(node -v | sed 's/v//' | cut -d. -f1) -lt 18 ]]; then
  MISSING+=("Node.js >= 18")
fi

if ! command -v python3 &>/dev/null; then
  MISSING+=("Python >= 3.9")
fi

if ! command -v jq &>/dev/null; then
  MISSING+=("jq")
fi

if ! command -v firecrawl &>/dev/null; then
  echo -e "${YELLOW}Warning: firecrawl CLI not found. Install with: npm install -g firecrawl${NC}"
  echo -e "${YELLOW}Discovery agents need firecrawl to search. The pre-teamcreate hook will block runs without it.${NC}"
fi

if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
  echo -e "${YELLOW}Warning: FIRECRAWL_API_KEY not set. Set it before running: export FIRECRAWL_API_KEY=your-key${NC}"
fi

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo -e "${RED}Missing required dependencies:${NC}"
  for dep in "${MISSING[@]}"; do
    echo -e "  ${RED}- $dep${NC}"
  done
  exit 1
fi

# Copy skill
mkdir -p "$SKILL_DEST"
cp "$SCRIPT_DIR/skill/massive-crawl/SKILL.md" "$SKILL_DEST/"
cp -r "$SCRIPT_DIR/skill/references" "$SKILL_DEST/"

# Copy map-capabilities sub-skill
MAP_CAP_DEST="$HOME/.claude/skills/map-capabilities"
mkdir -p "$MAP_CAP_DEST"
cp "$SCRIPT_DIR/skill/map-capabilities/SKILL.md" "$MAP_CAP_DEST/"

echo -e "${GREEN}✓ Skill installed to $SKILL_DEST${NC}"

# Copy massive-crawl hooks
mkdir -p "$HOOKS_DEST"
cp "$SCRIPT_DIR/hooks/pre-teamcreate.js" "$SCRIPT_DIR/hooks/subagent-context.sh" \
   "$SCRIPT_DIR/hooks/task-completed.sh" "$SCRIPT_DIR/hooks/teammate-idle.sh" \
   "$SCRIPT_DIR/hooks/post-concat.js" "$SCRIPT_DIR/hooks/statusline.js" "$HOOKS_DEST/"
chmod +x "$HOOKS_DEST/"*
echo -e "${GREEN}✓ Hooks installed to $HOOKS_DEST${NC}"

# Map-capabilities hooks run from $CLAUDE_PROJECT_DIR — no copy needed

# Register hooks in settings.json
python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")

# Load or create settings
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
mc_path = "$CLAUDE_PROJECT_DIR/hooks/massive-crawl"
cap_path = "$CLAUDE_PROJECT_DIR/hooks/map-capabilities"

# Define massive-crawl hook registrations
mc_registrations = {
    "PreToolUse": [{
        "matcher": "TeamCreate",
        "hooks": [{"type": "command", "command": f"node \"{mc_path}/pre-teamcreate.js\""}]
    }],
    "SubagentStart": [{
        "hooks": [{"type": "command", "command": f"\"{mc_path}/subagent-context.sh\""}]
    }],
    "TaskCompleted": [{
        "hooks": [{"type": "command", "command": f"\"{mc_path}/task-completed.sh\""}]
    }],
    "TeammateIdle": [{
        "hooks": [{"type": "command", "command": f"\"{mc_path}/teammate-idle.sh\""}]
    }],
    "PostToolUse": [{
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": f"node \"{mc_path}/post-concat.js\""}]
    }],
    "Notification": [{
        "hooks": [{"type": "command", "command": f"node \"{mc_path}/statusline.js\""}]
    }],
}

# Define map-capabilities hook registrations
cap_registrations = {
    "PreToolUse": [{
        "matcher": "Agent",
        "hooks": [{"type": "command", "command": f"\"{cap_path}/pre-wave.sh\""}]
    }],
    "SubagentStart": [{
        "hooks": [{"type": "command", "command": f"\"{cap_path}/subagent-context.sh\""}]
    }],
    "PostToolUse": [
        {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": f"\"{cap_path}/wave-completed.sh\""}]
        },
        {
            "matcher": "Write",
            "hooks": [{"type": "command", "command": f"\"{cap_path}/output-validator.sh\""}]
        },
    ],
    "Notification": [{
        "hooks": [{"type": "command", "command": f"node \"{cap_path}/statusline.js\""}]
    }],
    "SessionStart": [{
        "hooks": [{"type": "command", "command": f"\"{cap_path}/session-resume.sh\""}]
    }],
}

# Helper: merge registrations into hooks dict, deduping by workflow name
def merge(regs, workflow_name):
    for event, new_entries in regs.items():
        existing = hooks.get(event, [])
        # Remove old entries for this workflow
        existing = [e for e in existing
                    if not any(workflow_name in h.get("command", "")
                              for h in e.get("hooks", []))]
        existing.extend(new_entries)
        hooks[event] = existing

merge(mc_registrations, "massive-crawl")
merge(cap_registrations, "map-capabilities")

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print("✓ Hooks registered in settings.json")
PYEOF

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Usage: /massive-crawl \"your topic\""
echo ""
echo "Pipeline code stays in this repo: $SCRIPT_DIR/pipeline/"
echo "Update: git pull && ./install.sh"
echo "Uninstall: ./install.sh --uninstall"
