#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
SKILL_ROOT="$CODEX_ROOT/skills"
MC_DEST="$SKILL_ROOT/massive-crawl"
MAP_DEST="$SKILL_ROOT/map-capabilities"

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
  rm -rf "$MC_DEST" "$MAP_DEST"
  echo -e "${GREEN}Removed Codex wrapper skills from $SKILL_ROOT.${NC}"
  exit 0
fi

if [[ ! -d "$CODEX_ROOT" ]]; then
  mkdir -p "$CODEX_ROOT"
fi

copy_skill "$REPO_ROOT/adapters/codex/skills/massive-crawl/SKILL.md" "$MC_DEST"
copy_skill "$REPO_ROOT/adapters/codex/skills/map-capabilities/SKILL.md" "$MAP_DEST"

echo -e "${GREEN}Installed Codex wrapper skills.${NC}"
echo "massive-crawl -> $MC_DEST/SKILL.md"
echo "map-capabilities -> $MAP_DEST/SKILL.md"
echo ""
echo "Entry points:"
echo "  \$massive-crawl"
echo "  \$map-capabilities"
echo ""
echo "No global config.toml edits were made."
