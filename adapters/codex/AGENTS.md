# Codex Adapter Notes

This repository uses a thin Codex adapter. Treat the files in `adapters/codex/` as entry points and configuration, not as the source of truth for workflow behavior.

## Rules

- Use Codex-native invocation names: `$massive-crawl` and `$map-capabilities`.
- Prefer repo-relative references to shared workflow assets under `workflows/<workflow>/`.
- Do not duplicate prompt, schema, or example content in the adapter unless there is no shared alternative.
- Keep the current pipeline model in mind: deterministic `dedup -> score -> finalize`.
- Treat enrichment as workflow orchestration. The adapter may select the enricher model, but it should not redefine the enrichment logic here.
- The default enricher model is `gpt-5.4-mini` with `medium` reasoning, unless `adapters/codex/models.json` overrides it.

## Lookup order

1. Read `workflows/<workflow>/manifest.json`.
2. Follow `workflows/<workflow>/contract.md`.
3. Use `workflows/<workflow>/runtime.json` for execution boundaries.
4. Pull supporting content from `prompts/`, `schemas/`, and `examples/` only when needed.

## Failure mode

- If a shared workflow path is missing or inconsistent, stop and report the exact missing file.
- Do not invent hook behavior, extra runtime integration, or hidden model wiring.
