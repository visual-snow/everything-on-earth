---
name: massive-crawl
description: >-
  Discovers every open-source GitHub/GitLab repository for a topic through the
  Claude adapter. Use when the user says "find every repo", "discover all
  tools", "massive crawl", "catalog all open source", or "survey the
  landscape". Follow the shared workflow under workflows/massive-crawl/ and
  use Claude-specific hooks, task claiming, and model defaults from
  adapters/claude/.
disable-model-invocation: true
context: fork
allowed-tools:
  - Agent
  - TeamCreate
  - TeamDelete
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - SendMessage
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
---

# massive-crawl

This is the Claude adapter wrapper, not the workflow source of truth.

## Use

1. Read `workflows/massive-crawl/manifest.json`.
2. Follow `workflows/massive-crawl/contract.md`.
3. Use `workflows/massive-crawl/runtime.json` for stage, role, artifact, and invariant boundaries.
4. Use `adapters/claude/models.json` for Claude role defaults.

## Claude-Specific Notes

- Claude discovery uses TeamCreate plus task claiming.
- Claude hook configuration is project-local in `.claude/settings.local.json`.
- Hook scripts live under `adapters/claude/hooks/`.
- Discovery-agent instructions live under `adapters/claude/prompts/`.

## Boundary

- Do not duplicate shared prompts, schemas, or examples here.
- If a referenced shared workflow file is missing, stop and report the exact path.
