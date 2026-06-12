# Subagent Enrichment — Remove Anthropic API Key Dependency

**Date:** 2026-03-24
**Status:** Approved

## Problem

The pipeline's `enrich` stage calls `anthropic.Anthropic()` from Python, which requires `ANTHROPIC_API_KEY` in the shell environment. Claude Code has its own API key internally but doesn't expose it to child processes. This makes the enrichment stage fail unless the user manually sets the key.

## Solution

Move enrichment out of the Python pipeline and into Claude Code subagents. Python handles deterministic stages (dedup, score, finalize). Claude Code handles LLM work natively.

## Architecture

```
python pipeline.py --stage dedup,score          # deterministic Python
         ↓
skill reads scored.json, chunks into batches
         ↓
spawn N parallel subagents (haiku model)        # Claude Code native
each batch → {tags, category, summary}
         ↓
skill merges results → writes enriched.json
         ↓
python pipeline.py --stage finalize             # deterministic Python
```

## Changes

### pipeline.py
- Delete `enrich_single()`, `run_enrich()`, `strip_code_fences()`
- Delete the `enrich` case from the CLI stage handler
- Update docstring to reflect three stages: dedup, score, finalize

### requirements.txt
- Remove `anthropic>=0.40.0`

### SKILL.md (Phase 3)
Replace the single pipeline invocation with:
1. `python pipeline.py --stage dedup,score`
2. Read `scored.json`, chunk entries into batches of ~30
3. Launch parallel Haiku subagents, one per batch
4. Parse JSON responses, merge enrichment fields onto entries
5. Write `enriched.json`
6. `python pipeline.py --stage finalize`

### Subagent spec
- **Model:** Haiku
- **Tools:** None (pure text-in, JSON-out)
- **Batch size:** ~30 entries
- **Parallelism:** All batches launched simultaneously

### Prompt per subagent
```
Topic: "{topic}"

Enrich each repository. For each, return:
- tags: 3-5 lowercase normalized topic tags
- category: human-readable category name (2-4 words)
- summary: one-line summary, max 100 chars

Return a JSON array in the same order as input.

[entries as JSON]
```

### Error handling
If a subagent returns malformed JSON or wrong entry count, fall back to empty tags/category/summary for that batch. Invariant preserved: `len(output) == len(input)`.

## What stays the same
- dedup, score, finalize stages — untouched
- File contract: scored.json → enriched.json → finalize
- Output schema: entries get tags, category, summary fields
- tests/test_pipeline.py — update to remove enrich tests
