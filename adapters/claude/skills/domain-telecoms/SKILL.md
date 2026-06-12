---
model: disabled
tools:
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Domain: Telecoms

Deep capability-aware navigation of the telecoms open-source tool catalog.

## Trigger

Use this skill when the user asks about telecoms tools, capabilities,
protocols, or integration patterns.

## Behavior

1. Load the domain graph slice:
   `capability-graph/graph/domains/telecoms.json`
2. Load the flat capability map:
   `capability-graph/exports/csv/telecoms-capability-map.csv`
3. Use the canonical capability registry for definitions and relationships:
   `capability-graph/ontology/capability-registry.json`
4. Treat these assets as precompiled context; do not re-derive capability
   relationships from ad hoc repo searches.
5. Answer the user query using the graph structure:
   - Which repos implement a given capability
   - Which capabilities a given repo provides
   - Related capabilities and cross-repo integration points
   - Evidence traceability back to factsheet.json and capability.md

## Context Assets

- Domain slice: `capability-graph/graph/domains/telecoms.json`
- Capability map: `capability-graph/exports/csv/telecoms-capability-map.csv`
- Registry: `capability-graph/ontology/capability-registry.json`
- Aliases: `capability-graph/ontology/aliases.csv`
- Per-repo evidence: `catalog/telecoms/<slug>/factsheet.json`, `catalog/telecoms/<slug>/capability.md`
