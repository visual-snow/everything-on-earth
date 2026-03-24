# Codex Adapter Install

This directory is a thin Codex-facing adapter for the repository's shared workflow structure.

## What this adapter expects

- Shared workflow assets live under `workflows/massive-crawl/` and `workflows/map-capabilities/`.
- Each workflow should expose `contract.md`, `runtime.json`, `prompts/`, `schemas/`, `examples/`, and `manifest.json`.
- The Codex entry points are the wrapper skills in `adapters/codex/skills/`.
- The default enricher model is configured in `adapters/codex/models.json`.

## How to use it

- Invoke the discovery workflow with `$massive-crawl`.
- Invoke the documentation workflow with `$map-capabilities`.
- Keep the wrapper skills thin: they should point at the shared workflow files instead of duplicating prompt or schema content.

## Updating the adapter

- Edit `adapters/codex/models.json` to override model defaults.
- Update the wrapper skills if the shared workflow contract or file layout changes.
- Keep behavior grounded in the current pipeline: deterministic `dedup -> score -> finalize`, with enrichment handled by workflow orchestration.

## Notes

- This adapter does not define any extra hooks or hidden runtime behavior.
- If a referenced shared workflow file is missing, fail closed and report the exact path.
