# massive-crawl Contract

Shared source of truth for the `massive-crawl` workflow across Claude and Codex adapters.

## Goal

Discover every relevant open-source repository for a broad topic, then produce canonical catalog artifacts through a deterministic pipeline.

## Phase 1: Brainstorm

- Launch three scout subagents in parallel:
  - `awesome-scout`
  - `query-scout`
  - `landscape-scout`
- Ask the user one question at a time about:
  - known sub-domains
  - seed repos
  - exclusions
- Incorporate scout findings before final approval.
- Maintain a visible mental model showing topic, tasks, teammates, and estimated scope.
- Do not continue without explicit user approval.

## Phase 2: Discover

- Write `swarm-config.json`.
- Create one discovery task per sub-domain plus one curated-lists task.
- Spawn 6-8 `discoverer` agents.
- Each discoverer:
  - claims one pending task
  - searches and scrapes within budget
  - scores repos from 1-10 with rationale
  - writes `discovery/<sub-domain>.json`
  - claims the next task until none remain
- Concat all discovery files into `raw-discovery.json` without LLM synthesis.

## Phase 3: Pipeline

- Run deterministic dedup to create `dedup.json`.
- Run deterministic score to create `scored.json`.
- Split `scored.json` into enrichment batches.
- Spawn parallel `enricher` agents.
- Each enricher returns only:
  - `tags`
  - `category`
  - `summary`
- Merge enrichment back onto the original entries and write `enriched.json`.
- Run deterministic finalize to produce:
  - `catalog.json`
  - `RESULTS.md`
  - `explorer.html`

## Phase 4: Gap Review

- Ask whether important domains are still missing.
- If yes, add follow-up tasks and rerun discovery plus pipeline for the missing areas.
- If no, clean up the swarm/team resources for the current platform.

## Output Contract

Discovery outputs must include:

- `repo_url`
- `name`
- `description`
- `sub_domain`
- `score`
- `score_rationale`
- `stars`
- `language`
- `license`
- `last_activity`

Pipeline/enrichment may additionally attach:

- `found_in_domains`
- `quality_score`
- `tags`
- `category`
- `summary`

## Hard Invariants

- Dedup normalizes repo URLs.
- No LLM performs merge/dedup/finalize logic.
- Enrichment preserves input order.
- Enrichment preserves input count.
- Finalize consumes `enriched.json`.
