# Subagent Enrichment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the Anthropic API key dependency from the pipeline by moving enrichment to Claude Code subagents.

**Architecture:** Python pipeline keeps three deterministic stages (dedup, score, finalize). The massive-crawl skill orchestrates enrichment between score and finalize by spawning parallel Haiku subagents that return structured JSON.

**Tech Stack:** Python 3.9+ (pipeline), Claude Code Agent tool with Haiku model (enrichment)

---

### Task 1: Remove enrichment functions from pipeline.py

**Files:**
- Modify: `pipeline/pipeline.py:1-14` (docstring)
- Modify: `pipeline/pipeline.py:98-163` (delete enrich functions)
- Modify: `pipeline/pipeline.py:236` (default stages)
- Modify: `pipeline/pipeline.py:280-288` (delete enrich stage handler)

**Step 1: Delete `strip_code_fences`, `enrich_single`, and `run_enrich` functions**

Remove lines 98-163 (the three functions: `strip_code_fences`, `enrich_single`, `run_enrich`). Also remove the `re` import on line 18 since it's only used by `strip_code_fences`.

**Step 2: Delete the enrich stage handler from `main()`**

Remove the `elif stage == "enrich":` block (lines 280-288).

**Step 3: Update the docstring and default stages**

Update the module docstring (lines 1-14) to reflect three stages:

```python
"""
massive-crawl deterministic pipeline.

Three stages: dedup -> score -> finalize.
Each stage reads a file, transforms it, writes a file.
All stages are deterministic with no LLM involvement.
Enrichment (tags, category, summary) is handled by Claude Code subagents
between score and finalize — see skill/massive-crawl/SKILL.md.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --config swarm-config.json --stage score
"""
```

Update the `--stage` default on line 236:

```python
parser.add_argument("--stage", default="dedup,score,finalize",
                    help="Comma-separated stages to run (default: all)")
```

**Step 4: Run tests to see what breaks**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`

Expected: 4 enrich-related tests fail (ImportError for removed functions). All other tests pass.

**Step 5: Commit**

```bash
git add pipeline/pipeline.py
git commit -m "refactor: remove enrich stage from Python pipeline

Enrichment moves to Claude Code subagents — no more ANTHROPIC_API_KEY needed."
```

---

### Task 2: Remove anthropic from requirements.txt

**Files:**
- Modify: `pipeline/requirements.txt`

**Step 1: Remove the anthropic dependency**

New contents of `pipeline/requirements.txt`:

```
jinja2>=3.1.0
```

**Step 2: Commit**

```bash
git add pipeline/requirements.txt
git commit -m "chore: remove anthropic SDK dependency from requirements"
```

---

### Task 3: Update tests to remove enrich test coverage

**Files:**
- Modify: `tests/test_pipeline.py:1-11` (imports)
- Modify: `tests/test_pipeline.py:109-146` (delete enrich tests)

**Step 1: Update imports**

Replace line 11:
```python
from pipeline import normalize_url, run_dedup, run_score, run_enrich, strip_code_fences, run_finalize
```

With:
```python
from pipeline import normalize_url, run_dedup, run_score, run_finalize
```

Also remove the `from unittest.mock import patch` import on line 6 (only used by enrich tests).

**Step 2: Delete enrich tests**

Delete lines 109-146: the `# --- Enrich tests ---` section containing `test_strip_code_fences_json`, `test_strip_code_fences_plain`, `test_strip_code_fences_no_fences`, and `test_enrich_preserves_count`.

**Step 3: Run tests to verify all pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_pipeline.py -v`

Expected: All remaining tests PASS (normalize_url x4, dedup x3, score x5, finalize x1 = 13 tests).

**Step 4: Commit**

```bash
git add tests/test_pipeline.py
git commit -m "test: remove enrich tests — enrichment now handled by subagents"
```

---

### Task 4: Update SKILL.md Phase 3 with subagent enrichment

**Files:**
- Modify: `skill/massive-crawl/SKILL.md:162-172` (Phase 3)

**Step 1: Replace Phase 3 content**

Replace lines 162-172 with:

```markdown
## Phase 3: Pipeline

The post-concat hook auto-triggers dedup. After dedup completes:

1. **Show distribution summary** to user
2. **Run scoring**:
```bash
python3 pipeline/pipeline.py --config swarm-config.json --stage score
```
3. **Enrich via subagents** — read `scored.json`, chunk entries into batches of ~30, launch parallel Haiku agents:
```
For each batch, spawn:
Agent({
  model: "haiku",
  prompt: "Topic: \"{topic}\"

Enrich each repository entry below. For each, return:
- tags: 3-5 lowercase normalized topic tags
- category: human-readable category name (2-4 words)
- summary: one-line summary of what makes this notable (max 100 chars)

Return a JSON array in the SAME ORDER as input. Return ONLY the JSON array.

{batch_json}"
})
```
4. **Merge results** — parse each agent's JSON response, merge `tags`, `category`, `summary` onto original entries. If a batch returns malformed JSON or wrong count, fall back to empty values (tags=[], category=null, summary=null). Write `enriched.json`.
5. **Finalize**:
```bash
python3 pipeline/pipeline.py --config swarm-config.json --stage finalize
```
6. **Present results**: Show RESULTS.md summary, link to explorer.html
```

**Step 2: Update the skill description in frontmatter**

Update line 11 to remove "enrichment" from what the pipeline does:

```
  enrichment, and finalization. Outputs catalog.json, explorer.html, RESULTS.md.
```

becomes:

```
  and finalization. Enrichment is handled inline via Haiku subagents. Outputs catalog.json, explorer.html, RESULTS.md.
```

**Step 3: Commit**

```bash
git add skill/massive-crawl/SKILL.md
git commit -m "feat: replace API-based enrichment with parallel Haiku subagents in SKILL.md"
```

---

### Task 5: Verify end-to-end pipeline stages still work

**Step 1: Run full test suite**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/ -v`

Expected: All tests PASS.

**Step 2: Verify pipeline CLI accepts the new default stages**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python pipeline/pipeline.py --help`

Expected: `--stage` default shows `dedup,score,finalize` (not `dedup,score,enrich,finalize`).

**Step 3: Verify no references to anthropic SDK remain in pipeline code**

Run: `grep -r "anthropic\|ANTHROPIC_API_KEY" pipeline/`

Expected: No matches.
