# Capability Router Workflow

## Purpose

Route user queries about open-source tool landscapes to the correct domain
skill using a structured capability graph and a cheap classifier model.

## Stages

### 1. Load Context

- Read `capability-graph/exports/csv/domain-routing.csv` for routing hints
- Identify which domains have generated skills by checking for
  `adapters/claude/skills/domain-<name>/SKILL.md`

### 2. Classify

- Use the classifier prompt (`prompts/router-classifier.md`) with the routing
  index as structured input
- The classifier picks a primary domain and optional secondary domain
- Output follows `schemas/route-decision-schema.json`

### 3. Route

- If the primary domain has a generated domain skill, load that skill
- If no generated skill exists, report the matched domain and fall back to
  general catalog search under `catalog/<domain>/`
- Never force-load the wrong domain skill

## Invariants

- The classifier chooses among structured candidates from the routing index;
  it does not invent domains or capabilities
- A domain skill is loaded only when the generated asset exists on disk
- The routing index is built deterministically by `pipeline/build_capability_graph.py`

## Model Configuration

Classifier model is declared in `adapters/claude/models.json` under
`capability-router.classifier`. V1 default: haiku.
