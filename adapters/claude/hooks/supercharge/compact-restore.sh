#!/bin/bash
# SessionStart hook (compact): re-inject capability graph overview after compaction.
# Same output as session-context.sh so Claude retains domain awareness.
set -euo pipefail

exec "$CLAUDE_PROJECT_DIR/adapters/claude/hooks/supercharge/session-context.sh"
