---
model: disabled
tools:
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Capability Router

Route user questions about open-source tool landscapes to the correct domain
skill using a structured capability graph.

## Trigger

Use this skill when the user asks about open-source tools, capabilities, or
landscapes across any of these domains:
  - telecoms

## Behavior

1. Read the routing context from `capability-graph/exports/csv/domain-routing.csv`
2. Read the workflow contract from `workflows/capability-router/contract.md`
3. Follow the classifier prompt in `workflows/capability-router/prompts/router-classifier.md`
4. Classify the user query to a primary domain (and optional secondary)
5. If the primary domain has a generated domain skill, load it:
   - telecoms -> use the domain-telecoms skill
6. If no generated skill exists for the classified domain, inform the user which
   domain matched and that deep capability routing is not yet available for it.
   Fall back to general catalog search.

## Context Assets

- Routing index: `capability-graph/exports/csv/domain-routing.csv`
- Available domains with generated skills: [telecoms]
