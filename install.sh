#!/bin/bash
set -euo pipefail

# everything-on-earth installer
# Copies skill and hooks to ~/.claude/, registers hooks in settings.json

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DEST="$HOME/.claude/skills/everything-on-earth"
HOOKS_DEST="$HOME/.claude/hooks/everything-on-earth"
SETTINGS="$HOME/.claude/settings.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Uninstall mode ---
if [[ "${1:-}" == "--uninstall" ]]; then
  echo "Uninstalling everything-on-earth..."
  rm -rf "$SKILL_DEST" "$HOOKS_DEST"
  if [ -f "$SETTINGS" ]; then
    # Remove our hook entries (entries containing "everything-on-earth")
    python3 -c '
import json, sys
settings_file = sys.argv[1]
with open(settings_file) as f:
    s = json.load(f)
hooks = s.get("hooks", {})
for event in list(hooks.keys()):
    hooks[event] = [h for h in hooks[event]
                     if not any("everything-on-earth" in (hook.get("command",""))
                               for hook in h.get("hooks", []))]
    if not hooks[event]:
        del hooks[event]
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
echo "Installing everything-on-earth..."

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
cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_DEST/"
cp -r "$SCRIPT_DIR/skill/references" "$SKILL_DEST/"

# Copy map-capabilities sub-skill
MAP_CAP_DEST="$HOME/.claude/skills/map-capabilities"
mkdir -p "$MAP_CAP_DEST"
cp "$SCRIPT_DIR/skill/map-capabilities/SKILL.md" "$MAP_CAP_DEST/"

echo -e "${GREEN}✓ Skill installed to $SKILL_DEST${NC}"

# Copy hooks
mkdir -p "$HOOKS_DEST"
cp "$SCRIPT_DIR/hooks/"* "$HOOKS_DEST/"
chmod +x "$HOOKS_DEST/"*
echo -e "${GREEN}✓ Hooks installed to $HOOKS_DEST${NC}"

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
hooks_path = "$CLAUDE_PROJECT_DIR/hooks/everything-on-earth"

# Define our hook registrations
registrations = {
    "PreToolUse": [{
        "matcher": "TeamCreate",
        "hooks": [{"type": "command", "command": f"node \"{hooks_path}/pre-teamcreate.js\""}]
    }],
    "SubagentStart": [{
        "hooks": [{"type": "command", "command": f"\"{hooks_path}/subagent-context.sh\""}]
    }],
    "TaskCompleted": [{
        "hooks": [{"type": "command", "command": f"\"{hooks_path}/task-completed.sh\""}]
    }],
    "TeammateIdle": [{
        "hooks": [{"type": "command", "command": f"\"{hooks_path}/teammate-idle.sh\""}]
    }],
    "PostToolUse": [{
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": f"node \"{hooks_path}/post-concat.js\""}]
    }],
    "Notification": [{
        "hooks": [{"type": "command", "command": f"node \"{hooks_path}/statusline.js\""}]
    }],
}

# Merge registrations (don't clobber existing hooks)
for event, new_entries in registrations.items():
    existing = hooks.get(event, [])
    # Remove any old everything-on-earth entries
    existing = [e for e in existing
                if not any("everything-on-earth" in h.get("command", "")
                          for h in e.get("hooks", []))]
    existing.extend(new_entries)
    hooks[event] = existing

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print("✓ Hooks registered in settings.json")
PYEOF

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Usage: /everything-on-earth \"your topic\""
echo ""
echo "Pipeline code stays in this repo: $SCRIPT_DIR/pipeline/"
echo "Update: git pull && ./install.sh"
echo "Uninstall: ./install.sh --uninstall"
