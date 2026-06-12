# Capability Graph Router Design

**Date:** 2026-03-26
**Status:** Approved in brainstorming
**Project:** everything-on-earth

## Overview

Turn `everything-on-earth` from a large set of domain catalogs into a canonical capability intelligence layer for agents.

The user experience target is **seamless automatic loading**, not explicit querying. Claude should not need the user to ask, "what tools implement X capability?" The correct domain map and capability slice should be loaded automatically through a small router skill plus generated domain skills.

The core design rule is:

**Canonical graph + registries are the source of truth. Generated `SKILL.md` files and CSV mappings are delivery artifacts.**

This follows the part of `ui-ux-pro-max-skill` that is worth copying: one real internal source tree, many assistant-facing outputs.

## Goal

Make Claude able to reason about open-source tools across domains as if the domain map already exists in memory, while keeping the ontology consistent across all verticals.

## Non-Goals

- Do not make `SKILL.md` the canonical ontology
- Do not make CSV the full graph storage format
- Do not require explicit graph queries from the end user
- Do not build all assistant packaging before the ontology is stable

## Product Decision

The approved product boundary is:

1. A **small router skill** detects likely domain and topic from the prompt and repo context
2. The router **invisibly loads** the correct domain skill and capability slice
3. Each domain has its own generated `SKILL.md` and flat mapping CSV assets
4. A global capability graph and capability registry remain canonical underneath

This means "one domain -> one skill" is a good packaging model, but not a good ontology boundary.

## Why This Design

Today, `everything-on-earth` is strongest at breadth and deterministic discovery. It already supports 11 vertical domains and thousands of repo records. Over time, each domain can also get repo-level capability artifacts through `map-capabilities`.

That is necessary, but not sufficient.

Without a canonical graph layer, the system remains a collection of per-repo and per-domain records that an assistant still has to mentally stitch together. That leads to duplicated names, fuzzy category boundaries, and repeated context loading.

The design goal is to compile that evidence into a stable capability layer ahead of time, then expose it through skills in a way that feels native and automatic.

## Architecture

The system is split into three layers.

### 1. Evidence Layer

Existing and already-aligned with the repo:

- discovery pipeline outputs per-domain repo records
- `entry.json` stores repo metadata and ranking fields
- `factsheet.json` stores structured repo-level capability evidence
- `capability.md` stores readable repo-level capability summaries

This layer stays per-domain and per-repo.

### 2. Canonical Ontology Layer

New global source of truth:

- `capability-registry.json` or equivalent structured registry
- alias mapping table
- merge rules
- repo-to-capability edge set with confidence and evidence
- global capability graph

This layer merges equivalent capabilities across domains into one canonical vocabulary.

### 3. Delivery Layer

Generated artifacts for assistant runtime:

- router `SKILL.md`
- one generated domain `SKILL.md` per vertical
- domain CSV mappings for flat lookup use cases
- graph/domain/capability context bundles
- adapter-specific outputs for Claude, Codex, and others later

This layer is generated from the ontology layer and should never become the source of truth.

## Canonical Data Model

### Capability Entity

Each capability is a first-class object with:

- stable `id`
- human `label`
- `aliases[]`
- short description
- `domains[]`
- `related_capabilities[]`
- `implemented_by[]`
- evidence metadata such as mention counts and confidence

### Repository Link

Each repo-to-capability edge stores:

- `repo_id`
- `capability_id`
- relationship type, initially `implements`
- evidence sources from repo artifacts
- evidence snippets
- confidence

### Domain View

A domain is a filtered view over the canonical graph, not a separate ontology.

This allows the same capability to appear in multiple domains without being redefined multiple times.

## Normalization Rules

The graph only works if capability identities stay stable.

Rules:

- capabilities are canonical entities, not free-text tags
- aliases improve retrieval but do not create new ontology nodes
- new canonical capabilities require evidence-backed creation
- low-confidence candidates should be staged for review instead of silently entering the registry
- conflicts across domains should converge into one registry, not fork into domain-local vocabularies

## Recommended Artifact Strategy

Use **CSV for flat mappings**, not for the full graph.

Good CSV use cases:

- alias -> canonical capability id
- repo -> capability id
- domain -> capability id
- routing hints

Bad CSV use cases:

- full graph topology
- evidence-rich relationships
- recursive related-capability structures
- anything that depends on nested or multi-hop graph semantics

Keep graph-shaped data in JSON or another structured graph-friendly format. Generate CSV alongside it where lookup tables are helpful.

## Data Flow

Build flow:

1. discovery pipeline creates or refreshes repo entries per domain
2. `map-capabilities` creates repo-level capability evidence
3. capability extraction produces candidate phrases and mappings
4. normalization merges them into canonical capability ids
5. graph build produces global and sliced graph artifacts
6. delivery generation produces router/domain skills and mapping CSVs

This keeps discovery separate from runtime retrieval.

## Router Skill Behavior

The router skill is intentionally small.

Responsibilities:

- infer likely domain from prompt and repo context
- choose the correct domain skill or small set of domain skills
- load the relevant capability slice automatically
- stay invisible to the user

The router should **not**:

- contain the full ontology itself
- dump all 11 domains into context
- act as the canonical store

The router is a dispatcher, not the knowledge base.

## Domain Skill Behavior

Each domain gets its own generated `SKILL.md`.

That skill should:

- describe the domain vocabulary and retrieval intent
- reference the domain capability slice
- reference the domain CSV mappings for flat lookup cases
- guide Claude toward using canonical capability ids and domain terminology consistently

Each domain skill is therefore a compiled, assistant-friendly view over the canonical graph.

## Suggested Repository Shape

Exact paths can change, but the logical separation should be:

```text
catalog/
  domain/repo evidence

ontology/
  capability-registry.json
  aliases.csv or aliases.json
  merge-rules.json

graph/
  graph.json
  domains/
  capabilities/

exports/
  domain-context/
  capability-context/
  csv/

adapters/
  claude/skills/router/
  claude/skills/domain-*/
  codex/skills/router/
  codex/skills/domain-*/
```

The important rule is separation between canonical ontology assets and generated assistant artifacts.

## Quality Controls

Main failure modes:

- label explosion
- false merges
- noisy repo-to-capability edges
- domain-specific naming bias contaminating the global registry

Guardrails:

- version the registry and merge rules
- keep evidence and confidence on every edge
- require evidence-backed creation for new canonical ids
- route ambiguous mappings into a review queue instead of silently merging them
- ensure every exported capability node can be traced back to repo evidence

## Testing

Required testing areas:

- schema validation for registry, edges, and exports
- normalization tests for synonym collapse and false-merge prevention
- regression fixtures across multiple domains to ensure stable canonical ids
- export tests to confirm domain skills and CSV mappings reflect the graph correctly
- traceability tests to ensure every graph capability and edge maps back to evidence

## Scope For Planning

This spec defines the end-state architecture, but the next implementation plan should stay focused.

The first planning target should be:

1. canonical capability registry
2. normalization step from repo evidence to capability ids
3. graph build outputs
4. generated router skill + one generated domain skill pattern

Out of scope for the first implementation plan:

- full cross-assistant packaging across every adapter
- advanced runtime APIs
- broad contributor UX

## Acceptance Criteria

The design is successful when:

- Claude receives relevant domain/capability context automatically through the router flow
- equivalent capabilities across domains converge to the same canonical id when they mean the same thing
- generated domain skills remain thin delivery artifacts, not divergent ontologies
- graph exports are reproducible from evidence + ontology rules
- the user experience feels seamless rather than query-driven

## Final Decision

Adopt this boundary:

**canonical graph + registries -> generated domain `SKILL.md` + CSV mappings -> small router skill auto-loads the right slice**

That is the most coherent way to make `everything-on-earth` feel like Claude already knows the open-source landscape, without sacrificing ontology quality underneath.
