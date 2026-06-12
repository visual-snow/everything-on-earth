#!/bin/bash
# SessionStart hook (startup): inject capability graph overview into Claude's context.
# Stdout is added to Claude's context automatically.
set -euo pipefail

GRAPH_ROOT="${CLAUDE_PROJECT_DIR}/capability-graph"

# Guard: skip if graph hasn't been built yet
if [ ! -f "$GRAPH_ROOT/graph/graph.json" ]; then
  exit 0
fi

REGISTRY="$GRAPH_ROOT/ontology/capability-registry.json"
ROUTING="$GRAPH_ROOT/exports/csv/domain-routing.csv"
GRAPH="$GRAPH_ROOT/graph/graph.json"

CAP_COUNT=$(python3 -c "import json; print(len(json.load(open('$REGISTRY'))))" 2>/dev/null || echo "?")
# Read both graph-derived values from a single parse of graph.json (it is large).
{ read -r DOMAINS; read -r EDGE_COUNT; } < <(python3 -c "import json; g=json.load(open('$GRAPH')); print(', '.join(g['domains'])); print(len(g['repo_capability_edges']))" 2>/dev/null) || true
DOMAINS="${DOMAINS:-?}"
EDGE_COUNT="${EDGE_COUNT:-?}"
ROUTE_COUNT=$(wc -l < "$ROUTING" 2>/dev/null | tr -d ' ' || echo "?")

cat <<EOF
<supercharge>
Capability graph loaded. ${CAP_COUNT} capabilities across ${EDGE_COUNT} repo-capability edges.
Domains with deep routing: ${DOMAINS}
Routing index: ${ROUTE_COUNT} hints across all 11 domains.

Key assets:
- capability-graph/ontology/capability-registry.json (canonical capabilities)
- capability-graph/graph/domains/<domain>.json (per-domain slices)
- capability-graph/exports/csv/domain-routing.csv (classifier input)
- capability-graph/exports/csv/<domain>-capability-map.csv (flat mapping)

When a user asks about tools, capabilities, or open-source landscapes in any domain,
use the routing index and domain graph slices as precompiled context. For telecoms,
the full capability graph with evidence traceability is available. Other domains
have routing hints but no generated capability graph yet.
</supercharge>
EOF
