---
name: massive-crawl
description: >-
  Claude adapter entry point for the shared massive-crawl workflow. Use when
  the user wants broad GitHub/GitLab discovery for a topic. Follow the shared
  contract under workflows/massive-crawl/ and use Claude-specific hooks plus
  models from adapters/claude/.
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

## Boundary

- Do not duplicate shared prompts, schemas, or examples here.
- If a referenced shared workflow file is missing, stop and report the exact path.
