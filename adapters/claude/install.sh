#!/bin/bash
set -euo pipefail

# Claude adapter installer
# Installs only the wrapper skills globally. Hook wiring stays project-local
# through .claude/settings.local.json committed in this repository.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MC_DEST="$HOME/.claude/skills/massive-crawl"
MAP_DEST="$HOME/.claude/skills/map-capabilities"
ROUTER_DEST="$HOME/.claude/skills/capability-router"
DOMAIN_TELECOMS_DEST="$HOME/.claude/skills/domain-telecoms"
SUPERCHARGE_DEST="$HOME/.claude/skills/supercharge"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

copy_skill() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  cp "$src" "$dest/SKILL.md"
}

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -rf "$MC_DEST" "$MAP_DEST" "$ROUTER_DEST" "$DOMAIN_TELECOMS_DEST" "$SUPERCHARGE_DEST"
  echo -e "${GREEN}Removed Claude wrapper skills from ~/.claude/skills.${NC}"
  echo "Project-local hooks remain managed by $REPO_ROOT/.claude/settings.local.json"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}Missing required dependency: Python >= 3.9${NC}"
  exit 1
fi

copy_skill "$REPO_ROOT/adapters/claude/skills/massive-crawl/SKILL.md" "$MC_DEST"
copy_skill "$REPO_ROOT/adapters/claude/skills/map-capabilities/SKILL.md" "$MAP_DEST"
copy_skill "$REPO_ROOT/adapters/claude/skills/capability-router/SKILL.md" "$ROUTER_DEST"
copy_skill "$REPO_ROOT/adapters/claude/skills/domain-telecoms/SKILL.md" "$DOMAIN_TELECOMS_DEST"
copy_skill "$REPO_ROOT/adapters/claude/skills/supercharge/SKILL.md" "$SUPERCHARGE_DEST"

echo -e "${GREEN}Installed Claude wrapper skills.${NC}"
echo "massive-crawl -> $MC_DEST/SKILL.md"
echo "map-capabilities -> $MAP_DEST/SKILL.md"
echo "capability-router -> $ROUTER_DEST/SKILL.md"
echo "domain-telecoms -> $DOMAIN_TELECOMS_DEST/SKILL.md"
echo "supercharge -> $SUPERCHARGE_DEST/SKILL.md"
echo ""
echo "Project-local hook config lives at:"
echo "  $REPO_ROOT/.claude/settings.local.json"
echo ""
echo "Use this repository from within Claude Code so project-local hooks resolve correctly."
