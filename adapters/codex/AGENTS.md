# Codex Adapter Notes

This repository uses a Codex adapter layered on top of shared workflow contracts. Treat the files in `adapters/codex/` as the Codex entry points, install surface, and platform-specific orchestration notes.

## Rules

- Use Codex-native invocation names: `$massive-crawl` and `$map-capabilities`.
- Install the adapter with `./install.sh --codex`.
- Prefer repo-relative references to shared workflow assets under `workflows/<workflow>/`.
- Keep shared contracts platform-neutral. Claude-only task APIs do not belong in `workflows/`.
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
- Do not invent Claude hook behavior or hidden model wiring.
