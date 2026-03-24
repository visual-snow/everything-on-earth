---
name: map-capabilities
description: >-
  Claude adapter entry point for the shared map-capabilities workflow. Use when
  the user wants capability documentation generated from a catalog. Follow the
  shared contract under workflows/map-capabilities/ and use Claude-specific
  hooks plus models from adapters/claude/.
allowed-tools:
  - Agent
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# map-capabilities

This is the Claude adapter wrapper, not the workflow source of truth.

## Use

1. Read `workflows/map-capabilities/manifest.json`.
2. Follow `workflows/map-capabilities/contract.md`.
3. Use `workflows/map-capabilities/runtime.json` for stage, role, artifact, and invariant boundaries.
4. Use `adapters/claude/models.json` for Claude role defaults.

## Claude-Specific Notes

- Claude hook configuration is project-local in `.claude/settings.local.json`.
- Hook scripts live under `adapters/claude/hooks/map-capabilities/`.

## Boundary

- Do not duplicate shared prompts, schemas, or examples here.
- If a referenced shared workflow file is missing, stop and report the exact path.
