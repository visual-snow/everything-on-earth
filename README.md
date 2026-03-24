# everything-on-earth

Dual-platform workflow repo for Claude Code and Codex.

It discovers broad open-source landscapes once, writes canonical catalog artifacts, and can generate capability documentation from those catalogs.

## Architecture

```text
workflows/        shared contracts, prompts, schemas, examples
adapters/claude/  Claude-specific skills, hooks, installer
adapters/codex/   Codex-specific skills, docs, model config
pipeline/         deterministic Python stages
.claude/          project-local Claude hook configuration
```

## Current massive-crawl flow

1. Brainstorm with scouts and explicit user approval
2. Discover via platform-native agents
3. Deterministic pipeline:
   - `dedup`
   - `score`
   - `finalize`
4. Workflow-native enrichment between `score` and `finalize`

The Python pipeline is deterministic. Enrichment is not in `pipeline.py`; it is handled by workflow orchestration and written back as `enriched.json`.

## Claude Code

Install the Claude wrapper skills:

```bash
./install.sh
```

The repo keeps Claude hook configuration project-local in `.claude/settings.local.json`.

Entry points:

- `/massive-crawl`
- `/map-capabilities`

## Codex

See:

- `adapters/codex/INSTALL.md`
- `adapters/codex/AGENTS.md`

Entry points:

- `$massive-crawl`
- `$map-capabilities`

The Codex adapter keeps model defaults in `adapters/codex/models.json`.

## Shared Source Of Truth

Each workflow owns:

- `contract.md`
- `runtime.json`
- `manifest.json`
- `prompts/`
- `schemas/`
- `examples/`

Adapters should stay thin and point at shared workflow assets instead of duplicating prompt or schema content.
