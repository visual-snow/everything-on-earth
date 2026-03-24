---
name: map-capabilities
description: >-
  Generates capability documentation from a catalog through the Codex
  adapter. Use when the user says "map capabilities", "generate capability
  docs", "capability mapper", or wants pre-generated capability files from a
  catalog. Invoke with `$map-capabilities` and follow the shared workflow
  assets under `workflows/map-capabilities/`.
---

<codex_skill_adapter>
## Skill Invocation
- This skill is invoked by mentioning `$map-capabilities`.
- Treat the remaining user text as workflow arguments such as `--catalog` and `--output-dir`.

## Platform Mapping
- Shared files under `workflows/map-capabilities/` define stages, prompts, schemas, and invariants.
- Researchers must run only on prefetched artifacts and should not receive live tools.
</codex_skill_adapter>

# map-capabilities

This is a Codex-native wrapper, not the full workflow spec.

## Use

- Invoke with `$map-capabilities`.
- Read `workflows/map-capabilities/manifest.json` first.
- Follow `workflows/map-capabilities/contract.md` for the workflow contract.
- Use `workflows/map-capabilities/runtime.json` for runtime boundaries and orchestration details.

## Behavior

- Keep this adapter thin and deterministic.
- Process one wave only after explicit user approval.
- Researchers operate on prefetched `entry.json`, `readme-raw.md`, and `compose-raw.md` with no live tools.
- Pull supporting prompts, schemas, and examples from the shared workflow tree instead of copying them here.
- Use `adapters/codex/models.json` if the workflow needs the shared enricher default or an override.

## Boundary

- Do not invent Codex hooks or extra runtime behavior.
- If the shared workflow files are missing, report the missing path and stop.
