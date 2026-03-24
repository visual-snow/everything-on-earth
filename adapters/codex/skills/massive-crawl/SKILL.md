---
name: massive-crawl
description: Thin Codex adapter entry point for the massive-crawl workflow. Invoke with `$massive-crawl` and follow the shared workflow assets under `workflows/massive-crawl/`.
---

# massive-crawl

This is a Codex-native wrapper, not the full workflow spec.

## Use

- Invoke with `$massive-crawl`.
- Read `workflows/massive-crawl/manifest.json` first.
- Follow `workflows/massive-crawl/contract.md` for the workflow contract.
- Use `workflows/massive-crawl/runtime.json` for runtime boundaries and orchestration details.

## Behavior

- Keep the pipeline deterministic: `dedup -> score -> finalize`.
- Treat enrichment as workflow orchestration, not as pipeline logic.
- Use `adapters/codex/models.json` for the enricher model default or override.

## Boundary

- Do not duplicate shared prompt, schema, or example content here.
- If the shared workflow files are missing, report the missing path and stop.
