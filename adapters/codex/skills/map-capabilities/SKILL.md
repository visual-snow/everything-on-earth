---
name: map-capabilities
description: Thin Codex adapter entry point for the map-capabilities workflow. Invoke with `$map-capabilities` and follow the shared workflow assets under `workflows/map-capabilities/`.
---

# map-capabilities

This is a Codex-native wrapper, not the full workflow spec.

## Use

- Invoke with `$map-capabilities`.
- Read `workflows/map-capabilities/manifest.json` first.
- Follow `workflows/map-capabilities/contract.md` for the workflow contract.
- Use `workflows/map-capabilities/runtime.json` for runtime boundaries and orchestration details.

## Behavior

- Keep this adapter thin and deterministic.
- Pull supporting prompts, schemas, and examples from the shared workflow tree instead of copying them here.
- Use `adapters/codex/models.json` if the workflow needs the shared enricher default or an override.

## Boundary

- Do not invent Codex hooks or extra runtime behavior.
- If the shared workflow files are missing, report the missing path and stop.
