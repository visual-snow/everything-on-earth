---
name: massive-crawl
description: >-
  Discovers every open-source GitHub/GitLab repository for a topic through the
  Codex adapter. Use when the user says "find every repo", "discover all
  tools", "massive crawl", "catalog all open source", or "survey the
  landscape". Invoke with `$massive-crawl` and follow the shared workflow
  assets under `workflows/massive-crawl/`.
---

<codex_skill_adapter>
## Skill Invocation
- This skill is invoked by mentioning `$massive-crawl`.
- Treat the remaining user text as the discovery topic plus any CLI-style flags.

## Platform Mapping
- Shared files under `workflows/massive-crawl/` define stages, artifacts, and schemas.
- Codex-specific orchestration lives in this adapter and may use Codex collaboration primitives instead of Claude `TeamCreate`/`TaskList` APIs.
</codex_skill_adapter>

# massive-crawl

This is a Codex-native wrapper, not the full workflow spec.

## Use

- Invoke with `$massive-crawl`.
- Read `workflows/massive-crawl/manifest.json` first.
- Follow `workflows/massive-crawl/contract.md` for the workflow contract.
- Use `workflows/massive-crawl/runtime.json` for runtime boundaries and orchestration details.
- Use `adapters/codex/models.json` for the enricher default or override.

## Behavior

- Brainstorm first, then launch Codex-native scouts/discoverers using the shared artifact contract.
- Keep the pipeline deterministic: `dedup -> score -> finalize`.
- Treat enrichment as workflow orchestration, not as pipeline logic.
- Do not rely on Claude-only task APIs from shared prompts.

## Boundary

- Do not duplicate shared prompt, schema, or example content here.
- If the shared workflow files are missing, report the missing path and stop.
