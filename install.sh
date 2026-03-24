#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  cat <<'EOF'
Usage:
  ./install.sh --claude [--uninstall]
  ./install.sh --codex [--uninstall]
EOF
}

case "${1:-}" in
  --claude)
    shift
    exec "$SCRIPT_DIR/adapters/claude/install.sh" "$@"
    ;;
  --codex)
    shift
    exec "$SCRIPT_DIR/adapters/codex/install.sh" "$@"
    ;;
  --help|-h)
    usage
    exit 0
    ;;
  "")
    usage >&2
    exit 1
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
