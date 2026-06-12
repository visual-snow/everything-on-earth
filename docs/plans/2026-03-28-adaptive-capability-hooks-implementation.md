# Adaptive Capability Hooks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the map-capabilities pipeline adapt batch size, judge scope, researcher depth, and writer exemplars based on repo tier (stars-based classification), coordinated through a `wave-manifest.json` artifact written by the pipeline and consumed by all hooks.

**Architecture:** Tier classification lives in the deterministic Python pipeline (`generate_capabilities.py`) where it's testable. The pipeline writes `wave-manifest.json` alongside its existing `wave-progress.json`. All 6 hooks in `adapters/claude/hooks/map-capabilities/` read the manifest and adapt behavior per tier. No changes to the skill SKILL.md, workflow contract, or shared prompts.

**Tech Stack:** Python 3 (pipeline), Bash (hooks), Node.js (statusline), jq (JSON parsing in hooks), pytest (tests)

**Design doc:** `docs/plans/2026-03-28-adaptive-capability-hooks-design.md`

---

### Task 1: Add tier classification and adaptive wave generation to `generate_capabilities.py`

**Files:**
- Modify: `pipeline/generate_capabilities.py`
- Test: `tests/test_adaptive_hooks.py`

**Step 1: Write the failing tests**

Create `tests/test_adaptive_hooks.py` with tests for the tier classification and adaptive wave generation:

```python
"""Tests for adaptive tiering in generate_capabilities.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from generate_capabilities import classify_tier, build_wave_manifest, action_next_wave


def _entry(slug: str, stars: int) -> dict:
    return {"slug": slug, "stars": stars, "name": slug, "repo_url": f"https://github.com/x/{slug}"}


class TestClassifyTier:
    def test_tier1_above_500(self):
        assert classify_tier(_entry("big", 501)) == 1

    def test_tier2_between_50_and_500(self):
        assert classify_tier(_entry("mid", 200)) == 2

    def test_tier2_at_boundary_50(self):
        assert classify_tier(_entry("edge", 50)) == 2

    def test_tier3_below_50(self):
        assert classify_tier(_entry("small", 49)) == 3

    def test_tier3_zero_stars(self):
        assert classify_tier(_entry("niche", 0)) == 3

    def test_tier1_at_boundary_500(self):
        # 500 is T2, >500 is T1
        assert classify_tier(_entry("boundary", 500)) == 2


class TestBuildWaveManifest:
    def test_manifest_has_required_keys(self):
        entries = [_entry("a", 1000), _entry("b", 100), _entry("c", 10)]
        manifest = build_wave_manifest(entries, wave_number=1, domain="test",
                                       total_entries=3, output_dir=Path("/tmp/test"))
        assert set(manifest.keys()) == {
            "wave", "domain", "total_entries", "slugs",
            "batch_size", "judge_scope", "style_anchors",
        }

    def test_slugs_carry_tier(self):
        entries = [_entry("a", 1000), _entry("b", 10)]
        manifest = build_wave_manifest(entries, wave_number=1, domain="test",
                                       total_entries=2, output_dir=Path("/tmp/test"))
        tiers = {s["slug"]: s["tier"] for s in manifest["slugs"]}
        assert tiers["a"] == 1
        assert tiers["b"] == 3

    def test_style_anchors_from_existing_capability_files(self, tmp_path):
        cap_dir = tmp_path / "big-repo"
        cap_dir.mkdir()
        (cap_dir / "capability.md").write_text("# Big Repo\n## Constraints\n- works")
        entries = [_entry("small", 10)]
        manifest = build_wave_manifest(entries, wave_number=2, domain="test",
                                       total_entries=10, output_dir=tmp_path)
        assert any("big-repo" in a for a in manifest["style_anchors"])


class TestAdaptiveNextWave:
    def test_bootstrap_wave_picks_t1_first(self, tmp_path):
        entries = [
            _entry("obscure", 5),
            _entry("midtier", 200),
            _entry("famous", 2000),
            _entry("famous2", 1500),
            _entry("famous3", 900),
        ]
        output = _capture_next_wave(entries, tmp_path)
        # Bootstrap wave should start with T1 entries
        slugs = [e["slug"] for e in output]
        assert slugs[0] in ("famous", "famous2", "famous3")

    def test_wave_size_respects_tier(self, tmp_path):
        # Create 20 T3 entries — should batch at 3, not 15
        entries = [_entry(f"tiny-{i}", 5) for i in range(20)]
        # Simulate bootstrap already done by marking some completed
        progress = {"completed": ["bootstrap-done"], "failed": {}, "in_progress": []}
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))
        # Also create a style anchor so it's not bootstrap mode
        anchor_dir = tmp_path / "bootstrap-done"
        anchor_dir.mkdir()
        (anchor_dir / "capability.md").write_text("# Anchor\n## Constraints\n- x")
        output = _capture_next_wave(entries, tmp_path)
        assert len(output) <= 5  # T3 batch is 3, but retries may add a couple

    def test_manifest_written_on_next_wave(self, tmp_path):
        entries = [_entry("a", 1000)]
        _capture_next_wave(entries, tmp_path)
        manifest_path = tmp_path / "wave-manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["wave"] >= 1
        assert len(manifest["slugs"]) > 0


def _capture_next_wave(entries, tmp_path):
    """Run action_next_wave and capture its JSON output."""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        action_next_wave(entries, tmp_path)
    return json.loads(buf.getvalue())
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_adaptive_hooks.py -v`
Expected: ImportError or AttributeError for `classify_tier`, `build_wave_manifest`

**Step 3: Implement tier classification and adaptive wave generation**

In `pipeline/generate_capabilities.py`, add the following:

Replace the `WAVE_SIZE = 15` constant with:

```python
TIER_BATCH_SIZE = {1: 10, 2: 5, 3: 3}
TIER_JUDGE_SCOPE = {1: 5, 2: 3, 3: 1}
BOOTSTRAP_SIZE = 5
```

Add `classify_tier` function after the imports:

```python
def classify_tier(entry: dict) -> int:
    """Classify a catalog entry into quality tiers based on stars.

    Tier 1 (>500 stars): well-known, standard processing
    Tier 2 (50-500 stars): mid-tier, extra writer exemplars
    Tier 3 (<50 stars): obscure, deep research + strict validation
    """
    stars = entry.get("stars", 0)
    if stars > 500:
        return 1
    if stars >= 50:
        return 2
    return 3
```

Add `build_wave_manifest` function:

```python
def build_wave_manifest(entries: list[dict], wave_number: int, domain: str,
                        total_entries: int, output_dir: Path) -> dict:
    """Build wave-manifest.json with tier metadata and style anchors."""
    slugs = []
    for entry in entries:
        tier = classify_tier(entry)
        slugs.append({
            "slug": entry["slug"],
            "tier": tier,
            "stars": entry.get("stars", 0),
        })

    style_anchors = _collect_style_anchors(output_dir, max_anchors=2)

    return {
        "wave": wave_number,
        "domain": domain,
        "total_entries": total_entries,
        "slugs": slugs,
        "batch_size": dict(TIER_BATCH_SIZE),
        "judge_scope": dict(TIER_JUDGE_SCOPE),
        "style_anchors": style_anchors,
    }


def _collect_style_anchors(output_dir: Path, max_anchors: int = 2) -> list[str]:
    """Find approved capability.md files to use as style anchors."""
    anchors = []
    if not output_dir.exists():
        return anchors
    progress_path = output_dir / "wave-progress.json"
    if not progress_path.exists():
        return anchors
    progress = json.loads(progress_path.read_text())
    for slug in progress.get("completed", []):
        cap_path = output_dir / slug / "capability.md"
        if cap_path.exists() and len(anchors) < max_anchors:
            anchors.append(str(cap_path))
    return anchors
```

Rewrite `action_next_wave` to be tier-aware:

```python
def _infer_wave_number(progress: dict) -> int:
    """Infer current wave number from completed count and batch sizes."""
    completed = len(progress.get("completed", []))
    return (completed // TIER_BATCH_SIZE[2]) + 1  # approximate


def _is_bootstrap_needed(output_dir: Path) -> bool:
    """Check if this is the first wave (no approved outputs yet)."""
    progress_path = output_dir / "wave-progress.json"
    if not progress_path.exists():
        return True
    progress = json.loads(progress_path.read_text())
    return len(progress.get("completed", [])) == 0


def action_next_wave(entries: list[dict], output_dir: Path) -> None:
    """Output the next wave of entries, tier-sorted with adaptive batch sizes."""
    progress = load_progress(output_dir)

    # Recover stranded in_progress entries
    stranded = progress.get("in_progress", [])
    if stranded:
        for slug in stranded:
            progress["failed"][slug] = "interrupted — recovered by next-wave"
        progress["in_progress"] = []
        save_progress(output_dir, progress)

    retries = get_retry_queue(progress)
    pending = get_pending(entries, progress)

    wave = []

    # Retries get priority
    retry_entries = [e for e in entries if e["slug"] in retries]
    for entry in retry_entries:
        entry_with_feedback = dict(entry)
        entry_with_feedback["_retry_reason"] = progress["failed"][entry["slug"]]
        wave.append(entry_with_feedback)

    if not wave and not pending:
        print(json.dumps({"done": True, "message": "All entries processed"}))
        return

    # Bootstrap mode: pick T1 entries first to create style anchors
    bootstrap = _is_bootstrap_needed(output_dir)
    if bootstrap and not wave:
        t1 = [e for e in pending if classify_tier(e) == 1]
        wave.extend(t1[:BOOTSTRAP_SIZE])
    else:
        # Normal mode: pick entries by tier with adaptive batch sizing
        # Determine dominant tier for this wave
        tiered = {1: [], 2: [], 3: []}
        for e in pending:
            tiered[classify_tier(e)].append(e)

        # Process T3 first (hardest, smallest batches), then T2, then T1
        remaining = TIER_BATCH_SIZE[3] if tiered[3] else TIER_BATCH_SIZE[2] if tiered[2] else TIER_BATCH_SIZE[1]
        remaining -= len(wave)  # account for retries already added

        for tier in [3, 2, 1]:
            if remaining <= 0:
                break
            batch = tiered[tier][:remaining]
            wave.extend(batch)
            remaining -= len(batch)
            if batch:
                break  # single-tier waves for judge coherence

    if not wave:
        print(json.dumps({"done": True, "message": "All entries processed"}))
        return

    # Mark as in_progress
    progress["in_progress"] = [e["slug"] for e in wave]
    for e in wave:
        if e["slug"] in progress.get("failed", {}):
            del progress["failed"][e["slug"]]
    save_progress(output_dir, progress)

    # Write wave manifest for hooks
    entry_lookup = {e["slug"]: e for e in entries}
    manifest_entries = [entry_lookup.get(e["slug"], e) for e in wave]
    domain = _infer_domain(entries)
    manifest = build_wave_manifest(manifest_entries, _infer_wave_number(progress),
                                   domain, len(entries), output_dir)
    (output_dir / "wave-manifest.json").write_text(json.dumps(manifest, indent=2))

    print(json.dumps(wave, indent=2))


def _infer_domain(entries: list[dict]) -> str:
    """Infer domain name from catalog entries."""
    if entries and "found_in_domains" in entries[0]:
        return entries[0]["found_in_domains"][0]
    return "unknown"
```

Also update `action_load` to report tier distribution:

```python
def action_load(entries: list[dict], output_dir: Path, do_write_config: bool = False,
                catalog_path: Path | None = None) -> None:
    """Print catalog summary with tier distribution and initialize progress if needed."""
    if do_write_config and catalog_path:
        write_config(catalog_path, output_dir, len(entries))

    progress = load_progress(output_dir)
    pending = get_pending(entries, progress)
    retries = get_retry_queue(progress)

    tier_counts = {1: 0, 2: 0, 3: 0}
    for e in entries:
        tier_counts[classify_tier(e)] += 1

    # Estimate waves accounting for variable batch sizes
    pending_by_tier = {1: 0, 2: 0, 3: 0}
    for e in pending:
        pending_by_tier[classify_tier(e)] += 1
    estimated_waves = sum(
        (pending_by_tier[t] + TIER_BATCH_SIZE[t] - 1) // TIER_BATCH_SIZE[t]
        for t in [1, 2, 3]
    )
    estimated_waves += (len(retries) + TIER_BATCH_SIZE[2] - 1) // TIER_BATCH_SIZE[2]

    print(json.dumps({
        "total_entries": len(entries),
        "completed": len(progress["completed"]),
        "failed": len(progress.get("failed", {})),
        "pending": len(pending),
        "retry_queue": len(retries),
        "waves_remaining": estimated_waves,
        "tiers": {"t1": tier_counts[1], "t2": tier_counts[2], "t3": tier_counts[3]},
    }, indent=2))
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_adaptive_hooks.py -v`
Expected: All tests PASS

**Step 5: Run existing tests to check no regressions**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_repo_contracts.py tests/test_pipeline.py -v`
Expected: PASS (no existing tests depend on WAVE_SIZE constant)

**Step 6: Commit**

```bash
git add pipeline/generate_capabilities.py tests/test_adaptive_hooks.py
git commit -m "feat: add tier classification and adaptive wave generation to pipeline"
```

---

### Task 2: Update `pre-wave.sh` to read `wave-manifest.json`

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/pre-wave.sh`
- Test: `tests/test_adaptive_hooks.py` (add hook tests)

**Step 1: Write the failing test**

Append to `tests/test_adaptive_hooks.py`:

```python
import subprocess


class TestPreWaveHook:
    """Test pre-wave.sh reads wave-manifest.json for tier info."""

    HOOK_PATH = str(Path(__file__).resolve().parent.parent
                    / "adapters" / "claude" / "hooks" / "map-capabilities" / "pre-wave.sh")

    def test_passthrough_for_non_map_capabilities_agents(self):
        """Non-matching agent names pass through (exit 0, no output)."""
        input_json = json.dumps({"tool_input": {"name": "some-other-agent"}})
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": "/nonexistent"},
        )
        assert result.returncode == 0

    def test_researcher_with_valid_prompt_allowed(self, tmp_path):
        """researcher-slug with valid prompt fields is allowed."""
        _write_config(tmp_path, "catalog.json", str(tmp_path))
        (tmp_path / "catalog.json").write_text("[]")
        input_json = json.dumps({
            "tool_input": {
                "name": "researcher-my-repo",
                "prompt": '{"name": "my-repo", "repo_url": "https://github.com/x/y"}',
            }
        })
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "allow"


def _hook_env():
    import os
    env = dict(os.environ)
    env["PATH"] = os.environ.get("PATH", "/usr/bin:/bin")
    return env


def _write_config(tmp_path, catalog, output_dir):
    config = {"catalog": str(tmp_path / catalog), "output_dir": output_dir, "catalog_name": "test"}
    (tmp_path / "map-capabilities-config.json").write_text(json.dumps(config))
```

**Step 2: Run test to verify it passes (existing behavior)**

Run: `python -m pytest tests/test_adaptive_hooks.py::TestPreWaveHook -v`
Expected: PASS (these test current behavior to confirm no regression)

**Step 3: No functional change to `pre-wave.sh`**

The `pre-wave.sh` hook already validates agent preconditions correctly. Its existing behavior is compatible with the manifest; no changes needed. The manifest is written by `generate_capabilities.py` and consumed by `subagent-context.sh` and `output-validator.sh`.

**Step 4: Commit**

```bash
git add tests/test_adaptive_hooks.py
git commit -m "test: add pre-wave hook regression tests"
```

---

### Task 3: Update `subagent-context.sh` for tier-aware prompt injection

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/subagent-context.sh`
- Test: `tests/test_adaptive_hooks.py`

**Step 1: Write the failing test**

Append to `tests/test_adaptive_hooks.py`:

```python
class TestSubagentContextHook:
    """Test subagent-context.sh injects tier-aware context."""

    HOOK_PATH = str(Path(__file__).resolve().parent.parent
                    / "adapters" / "claude" / "hooks" / "map-capabilities" / "subagent-context.sh")

    def test_researcher_t3_gets_deep_extraction_directive(self, tmp_path):
        """T3 researcher gets extra directive for deep extraction."""
        _setup_manifest(tmp_path, [{"slug": "tiny-lib", "tier": 3, "stars": 5}])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "researcher-tiny-lib"})
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "TIER 3" in ctx or "lesser-known" in ctx.lower() or "deep extraction" in ctx.lower()

    def test_researcher_t1_gets_standard_context(self, tmp_path):
        """T1 researcher gets standard prompt without extra directives."""
        _setup_manifest(tmp_path, [{"slug": "big-lib", "tier": 1, "stars": 5000}])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "researcher-big-lib"})
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "RESEARCHER" in ctx
        # T1 should not have deep extraction directive
        assert "lesser-known" not in ctx.lower()

    def test_writer_t2_gets_style_anchors(self, tmp_path):
        """T2 writer gets style anchor content injected."""
        anchor_dir = tmp_path / "approved-repo"
        anchor_dir.mkdir(parents=True)
        (anchor_dir / "capability.md").write_text("# Approved\n## Constraints\n- solid")
        _setup_manifest(
            tmp_path,
            [{"slug": "mid-lib", "tier": 2, "stars": 200}],
            style_anchors=[str(anchor_dir / "capability.md")],
        )
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "writer-mid-lib"})
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "Style Anchor" in ctx or "style anchor" in ctx.lower()

    def test_judge_gets_tier_metadata(self, tmp_path):
        """Judge gets tier info for each slug in the wave."""
        _setup_manifest(tmp_path, [
            {"slug": "a", "tier": 1, "stars": 1000},
            {"slug": "b", "tier": 3, "stars": 8},
        ])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "judge-wave-1"})
        result = subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "tier" in ctx.lower()


def _setup_manifest(tmp_path, slugs, style_anchors=None):
    manifest = {
        "wave": 1, "domain": "test", "total_entries": len(slugs),
        "slugs": slugs,
        "batch_size": {"1": 10, "2": 5, "3": 3},
        "judge_scope": {"1": 5, "2": 3, "3": 1},
        "style_anchors": style_anchors or [],
    }
    # wave-manifest.json lives in the output_dir; for tests, use tmp_path as output_dir
    (tmp_path / "wave-manifest.json").write_text(json.dumps(manifest))
    # Also write config pointing to this output_dir
    config = {"catalog": str(tmp_path / "catalog.json"), "output_dir": str(tmp_path), "catalog_name": "test"}
    (tmp_path / "map-capabilities-config.json").write_text(json.dumps(config))


def _setup_workflow_files(tmp_path):
    """Create minimal workflow files so the hook can read them."""
    prompts = tmp_path / "workflows" / "map-capabilities" / "prompts"
    schemas = tmp_path / "workflows" / "map-capabilities" / "schemas"
    examples = tmp_path / "workflows" / "map-capabilities" / "examples"
    prompts.mkdir(parents=True)
    schemas.mkdir(parents=True)
    examples.mkdir(parents=True)
    (prompts / "capability-researcher.md").write_text("# Researcher Prompt\nAnalyze the repo.")
    (prompts / "capability-writer.md").write_text("# Writer Prompt\nWrite capability doc.")
    (prompts / "capability-judge.md").write_text("# Judge Prompt\nReview the docs.")
    (schemas / "capability-factsheet-schema.json").write_text('{"type": "object"}')
    (examples / "gold_sandbox_capabilities.md").write_text("# Gold Example\nThis is a good one.")
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_adaptive_hooks.py::TestSubagentContextHook -v`
Expected: FAIL (current hook doesn't read manifest or inject tier-specific content)

**Step 3: Rewrite `subagent-context.sh` with tier-aware injection**

Replace the full contents of `adapters/claude/hooks/map-capabilities/subagent-context.sh`:

```bash
#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject tier-aware prompt templates + reference files into map-capabilities agents.
# Reads wave-manifest.json for tier classification and style anchors.
# Only activates for agents named researcher-*, writer-*, judge-wave-*.

INPUT=$(cat)

AGENT_NAME=$(echo "$INPUT" | jq -r '.agent_name // .name // empty')

case "$AGENT_NAME" in
  researcher-*|writer-*|judge-wave-*) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PROMPT_DIR="$PROJECT_DIR/workflows/map-capabilities/prompts"
SCHEMA_DIR="$PROJECT_DIR/workflows/map-capabilities/schemas"
EXAMPLE_DIR="$PROJECT_DIR/workflows/map-capabilities/examples"

# Read config to find output_dir, then read manifest
CONFIG_PATH="$PROJECT_DIR/map-capabilities-config.json"
if [[ -f "$CONFIG_PATH" ]]; then
  OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_PATH")
  MANIFEST_PATH="$OUTPUT_DIR/wave-manifest.json"
else
  MANIFEST_PATH=""
fi

# Look up tier for a slug from the manifest
get_tier() {
  local slug="$1"
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r --arg s "$slug" '.slugs[] | select(.slug == $s) | .tier // 2' "$MANIFEST_PATH"
  else
    echo "2"  # default to mid-tier if no manifest
  fi
}

# Read style anchors from manifest
get_style_anchors() {
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r '.style_anchors[]' "$MANIFEST_PATH" 2>/dev/null
  fi
}

# Build tier context for judges
get_tier_summary() {
  if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
    jq -r '.slugs | map("- \(.slug): Tier \(.tier) (\(.stars) stars)") | join("\n")' "$MANIFEST_PATH"
  else
    echo "(no tier data available)"
  fi
}

case "$AGENT_NAME" in
  researcher-*)
    SLUG="${AGENT_NAME#researcher-}"
    TIER=$(get_tier "$SLUG")
    PROMPT=$(cat "$PROMPT_DIR/capability-researcher.md" 2>/dev/null)
    SCHEMA=$(cat "$SCHEMA_DIR/capability-factsheet-schema.json" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$SCHEMA" ]]; then
      echo "Warning: Could not read researcher reference files" >&2
      exit 0
    fi

    TIER_DIRECTIVE=""
    if [[ "$TIER" == "2" ]]; then
      TIER_DIRECTIVE="

## Tier 2 Directive
This is a mid-popularity project. Pay extra attention to the README for capability signals that may not be immediately obvious from the repository metadata alone."
    elif [[ "$TIER" == "3" ]]; then
      TIER_DIRECTIVE="

## Tier 3 Directive — Deep Extraction
This is a lesser-known project with limited community visibility. Extract every capability signal you can find. Check README sections, code comments, CI configs, and any documentation files for capability evidence. Be thorough; this project has fewer external references to corroborate capabilities."
    fi

    jq -n --arg prompt "$PROMPT" --arg schema "$SCHEMA" --arg tier "$TIER_DIRECTIVE" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY RESEARCHER REFERENCE:\n\n## Researcher Prompt\n" + $prompt + $tier + "\n\n## Factsheet Schema\n" + $schema)
      }
    }'
    ;;

  writer-*)
    SLUG="${AGENT_NAME#writer-}"
    TIER=$(get_tier "$SLUG")
    PROMPT=$(cat "$PROMPT_DIR/capability-writer.md" 2>/dev/null)
    EXEMPLAR=$(cat "$EXAMPLE_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$EXEMPLAR" ]]; then
      echo "Warning: Could not read writer reference files" >&2
      exit 0
    fi

    ANCHOR_CONTENT=""
    if [[ "$TIER" != "1" ]]; then
      while IFS= read -r anchor_path; do
        if [[ -f "$anchor_path" ]]; then
          ANCHOR_TEXT=$(cat "$anchor_path")
          ANCHOR_CONTENT="$ANCHOR_CONTENT

## Style Anchor (approved output)
$ANCHOR_TEXT"
        fi
      done < <(get_style_anchors)
    fi

    jq -n --arg prompt "$PROMPT" --arg exemplar "$EXEMPLAR" --arg anchors "$ANCHOR_CONTENT" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY WRITER REFERENCE:\n\n## Writer Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $exemplar + $anchors)
      }
    }'
    ;;

  judge-wave-*)
    PROMPT=$(cat "$PROMPT_DIR/capability-judge.md" 2>/dev/null)
    EXEMPLAR=$(cat "$EXAMPLE_DIR/gold_sandbox_capabilities.md" 2>/dev/null)
    if [[ -z "$PROMPT" || -z "$EXEMPLAR" ]]; then
      echo "Warning: Could not read judge reference files" >&2
      exit 0
    fi

    TIER_SUMMARY=$(get_tier_summary)
    JUDGE_SCOPE=""
    if [[ -n "$MANIFEST_PATH" && -f "$MANIFEST_PATH" ]]; then
      JUDGE_SCOPE=$(jq -r '"Judge scope limits: T1 review up to \(.judge_scope["1"] // 5) at once, T2 up to \(.judge_scope["2"] // 3), T3 review 1:1 per entry."' "$MANIFEST_PATH" 2>/dev/null)
    fi

    jq -n --arg prompt "$PROMPT" --arg exemplar "$EXEMPLAR" \
          --arg tiers "$TIER_SUMMARY" --arg scope "$JUDGE_SCOPE" '{
      hookSpecificOutput: {
        hookEventName: "SubagentStart",
        additionalContext: ("CAPABILITY JUDGE REFERENCE:\n\n## Judge Prompt\n" + $prompt + "\n\n## Style Exemplar\n" + $exemplar + "\n\n## Wave Tier Breakdown\n" + $tiers + "\n\n" + $scope)
      }
    }'
    ;;
esac
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_adaptive_hooks.py::TestSubagentContextHook -v`
Expected: PASS

**Step 5: Commit**

```bash
git add adapters/claude/hooks/map-capabilities/subagent-context.sh tests/test_adaptive_hooks.py
git commit -m "feat: tier-aware prompt injection in subagent-context hook"
```

---

### Task 4: Update `output-validator.sh` for tier-sensitive validation

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/output-validator.sh`
- Test: `tests/test_adaptive_hooks.py`

**Step 1: Write the failing test**

Append to `tests/test_adaptive_hooks.py`:

```python
class TestOutputValidatorHook:
    """Test output-validator.sh applies tier-sensitive rules."""

    HOOK_PATH = str(Path(__file__).resolve().parent.parent
                    / "adapters" / "claude" / "hooks" / "map-capabilities" / "output-validator.sh")

    def test_t1_rejects_over_60_lines(self, tmp_path):
        """T1 repo: 60-line limit enforced."""
        _setup_manifest(tmp_path, [{"slug": "big-repo", "tier": 1, "stars": 2000}])
        content = "# Big Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(60))
        result = self._run_validator(tmp_path, "big-repo", content)
        assert result.returncode == 2

    def test_t2_allows_up_to_80_lines(self, tmp_path):
        """T2 repo: 80-line limit."""
        _setup_manifest(tmp_path, [{"slug": "mid-repo", "tier": 2, "stars": 200}])
        content = "# Mid Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(70))
        result = self._run_validator(tmp_path, "mid-repo", content)
        assert result.returncode == 0

    def test_t3_requires_two_constraint_bullets(self, tmp_path):
        """T3 repo: must have at least 2 bullets in Constraints."""
        _setup_manifest(tmp_path, [{"slug": "tiny-repo", "tier": 3, "stars": 5}])
        content = "# Tiny Repo\n## Constraints\n- only one bullet\n"
        result = self._run_validator(tmp_path, "tiny-repo", content)
        assert result.returncode == 2

    def test_t3_passes_with_two_constraint_bullets(self, tmp_path):
        """T3 repo: passes with 2+ bullets in Constraints."""
        _setup_manifest(tmp_path, [{"slug": "tiny-repo", "tier": 3, "stars": 5}])
        content = "# Tiny Repo\n## Constraints\n- first bullet\n- second bullet\n"
        result = self._run_validator(tmp_path, "tiny-repo", content)
        assert result.returncode == 0

    def _run_validator(self, tmp_path, slug, content):
        slug_dir = tmp_path / slug
        slug_dir.mkdir(exist_ok=True)
        file_path = str(slug_dir / "capability.md")
        input_json = json.dumps({
            "tool_input": {"file_path": file_path, "content": content}
        })
        return subprocess.run(
            ["bash", self.HOOK_PATH],
            input=input_json, capture_output=True, text=True,
            env={**_hook_env(), "CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_adaptive_hooks.py::TestOutputValidatorHook -v`
Expected: FAIL (current hook uses fixed 60-line limit for all tiers, no constraint bullet check)

**Step 3: Update `output-validator.sh` with tier-sensitive rules**

In `adapters/claude/hooks/map-capabilities/output-validator.sh`, replace the validation section. After the `IN_OUTPUT` check (line 36), replace everything from `CONTENT=` onward:

```bash
# Extract content from tool_input
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

if [[ -z "$CONTENT" && -f "$FILE_PATH" ]]; then
  CONTENT=$(cat "$FILE_PATH")
fi

if [[ -z "$CONTENT" ]]; then
  echo "output-validator: capability.md content is empty" >&2
  exit 2
fi

# Determine tier from wave-manifest.json
SLUG=$(basename "$(dirname "$FILE_PATH")")
TIER="2"  # default
MANIFEST_PATH="$OUTPUT_DIR/wave-manifest.json"
if [[ -f "$MANIFEST_PATH" ]]; then
  FOUND_TIER=$(jq -r --arg s "$SLUG" '.slugs[] | select(.slug == $s) | .tier // empty' "$MANIFEST_PATH")
  if [[ -n "$FOUND_TIER" ]]; then
    TIER="$FOUND_TIER"
  fi
fi

# Set tier-specific limits
case "$TIER" in
  1) MAX_LINES=60; MIN_CONSTRAINT_BULLETS=0 ;;
  2) MAX_LINES=80; MIN_CONSTRAINT_BULLETS=0 ;;
  3) MAX_LINES=80; MIN_CONSTRAINT_BULLETS=2 ;;
  *) MAX_LINES=60; MIN_CONSTRAINT_BULLETS=0 ;;
esac

ERRORS=""

# 1. Must start with a heading
FIRST_LINE=$(echo "$CONTENT" | head -n1)
if [[ "$FIRST_LINE" != "#"* ]]; then
  ERRORS="${ERRORS}STRUCTURE: must start with a heading (#)\n"
fi

# 2. Must contain ## Constraints section
if ! echo "$CONTENT" | grep -q '^## Constraints'; then
  ERRORS="${ERRORS}STRUCTURE: missing '## Constraints' section\n"
fi

# 3. Line limit (tier-sensitive)
LINE_COUNT=$(echo "$CONTENT" | wc -l | tr -d ' ')
if [[ "$LINE_COUNT" -gt "$MAX_LINES" ]]; then
  ERRORS="${ERRORS}LENGTH: ${LINE_COUNT} lines exceeds ${MAX_LINES}-line limit (tier $TIER)\n"
fi

# 4. No Docker image patterns
if echo "$CONTENT" | grep -qE '(docker\.io|ghcr\.io|quay\.io|gcr\.io|registry\.|[a-z0-9]+/[a-z0-9_-]+:[0-9]+\.[0-9]+)'; then
  ERRORS="${ERRORS}ABSTRACTION: Docker image reference detected — use generic descriptions instead\n"
fi

# 5. No port numbers
if echo "$CONTENT" | grep -qE ':[0-9]{4,5}[^0-9]|:[0-9]{4,5}$'; then
  ERRORS="${ERRORS}ABSTRACTION: port number detected — omit specific ports\n"
fi

# 6. No file paths
if echo "$CONTENT" | grep -qE '/(etc|var|opt|usr|tmp|home)/'; then
  ERRORS="${ERRORS}ABSTRACTION: file path detected — use generic descriptions instead\n"
fi

# 7. T3 minimum constraint bullets
if [[ "$MIN_CONSTRAINT_BULLETS" -gt 0 ]]; then
  CONSTRAINT_SECTION=$(echo "$CONTENT" | sed -n '/^## Constraints/,/^## /p' | grep -c '^- ')
  if [[ "$CONSTRAINT_SECTION" -lt "$MIN_CONSTRAINT_BULLETS" ]]; then
    ERRORS="${ERRORS}DEPTH: tier $TIER requires >= $MIN_CONSTRAINT_BULLETS constraint bullets, found $CONSTRAINT_SECTION\n"
  fi
fi

if [[ -n "$ERRORS" ]]; then
  echo "output-validator: capability.md validation failed (tier $TIER):" >&2
  echo -e "$ERRORS" >&2
  exit 2
fi

exit 0
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_adaptive_hooks.py::TestOutputValidatorHook -v`
Expected: PASS

**Step 5: Commit**

```bash
git add adapters/claude/hooks/map-capabilities/output-validator.sh tests/test_adaptive_hooks.py
git commit -m "feat: tier-sensitive validation in output-validator hook"
```

---

### Task 5: Update `wave-completed.sh` with per-tier metrics

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/wave-completed.sh`

**Step 1: Update hook to report per-tier stats**

Replace the summary-building section (after `TOTAL=` line) in `adapters/claude/hooks/map-capabilities/wave-completed.sh`:

```bash
TOTAL=$(jq 'length' "$CATALOG" 2>/dev/null || echo "?")
DONE=$((COMPLETED))
REMAINING=$((TOTAL - DONE))

# Per-tier stats from manifest
TIER_STATS=""
MANIFEST_PATH="$OUTPUT_DIR/wave-manifest.json"
if [[ -f "$MANIFEST_PATH" ]]; then
  WAVE_NUM=$(jq -r '.wave' "$MANIFEST_PATH")
  TIER_STATS=$(jq -r '
    .slugs | group_by(.tier) | map(
      "T\(.[0].tier): \(length)"
    ) | join(" | ")
  ' "$MANIFEST_PATH" 2>/dev/null)
fi

if [[ "$REMAINING" -le 0 && "$FAILED" -eq 0 ]]; then
  SUMMARY="map-capabilities ($CATALOG_NAME): All $TOTAL entries processed successfully."
else
  SUMMARY="map-capabilities ($CATALOG_NAME) wave ${WAVE_NUM:-?}: $DONE/$TOTAL done"
  if [[ -n "$TIER_STATS" ]]; then
    SUMMARY="$SUMMARY | $TIER_STATS"
  fi
  if [[ "$FAILED" -gt 0 ]]; then
    SUMMARY="$SUMMARY | $FAILED to retry"
  fi
  if [[ "$REMAINING" -gt 0 ]]; then
    SUMMARY="$SUMMARY | $REMAINING remaining"
  fi
fi
```

**Step 2: Commit**

```bash
git add adapters/claude/hooks/map-capabilities/wave-completed.sh
git commit -m "feat: per-tier metrics in wave-completed hook"
```

---

### Task 6: Update `session-resume.sh` with tier distribution and wire into settings

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/session-resume.sh`
- Modify: `.claude/settings.local.json`

**Step 1: Update `session-resume.sh` to show tier distribution**

Replace the summary-building section (after `WAVES=`) in `adapters/claude/hooks/map-capabilities/session-resume.sh`:

```bash
if [[ "$PENDING" -eq 0 && "$RETRIES" -eq 0 ]]; then
  CTX="map-capabilities ($CATALOG_NAME): all $TOTAL entries processed."
else
  # Get tier distribution from catalog
  TIER_DIST=$(python3 -c "
import json, sys
entries = json.load(open(sys.argv[1]))
t = {1: 0, 2: 0, 3: 0}
for e in entries:
    s = e.get('stars', 0)
    if s > 500: t[1] += 1
    elif s >= 50: t[2] += 1
    else: t[3] += 1
print(f'T1: {t[1]} | T2: {t[2]} | T3: {t[3]}')
" "$CATALOG" 2>/dev/null || echo "")

  CTX="map-capabilities ($CATALOG_NAME): $COMPLETED/$TOTAL complete, $PENDING pending"
  if [[ -n "$TIER_DIST" ]]; then
    CTX="$CTX | $TIER_DIST"
  fi
  if [[ "$RETRIES" -gt 0 ]]; then
    CTX="$CTX, $RETRIES to retry"
  fi
  CTX="$CTX ($WAVES waves remaining)"
  CTX="$CTX — run /map-capabilities to continue"

  PROGRESS_FILE="$OUTPUT_DIR/wave-progress.json"
  if [[ -f "$PROGRESS_FILE" ]]; then
    STRANDED=$(jq -r '.in_progress | length' "$PROGRESS_FILE" 2>/dev/null || echo 0)
    if [[ "$STRANDED" -gt 0 ]]; then
      CTX="$CTX (note: $STRANDED entries in-progress from last session — will be recovered)"
    fi
  fi
fi
```

**Step 2: Wire `session-resume.sh` into `.claude/settings.local.json`**

The `session-resume.sh` hook exists on disk but is not wired in settings. Add it to the `SessionStart` array.

In `.claude/settings.local.json`, after the existing `compact` SessionStart entry (line 21 closing brace), add:

```json
,
{
  "matcher": "startup",
  "hooks": [
    {
      "type": "command",
      "command": "\"$CLAUDE_PROJECT_DIR/adapters/claude/hooks/map-capabilities/session-resume.sh\""
    }
  ]
}
```

**Step 3: Commit**

```bash
git add adapters/claude/hooks/map-capabilities/session-resume.sh .claude/settings.local.json
git commit -m "feat: tier distribution in session-resume hook, wire into settings"
```

---

### Task 7: Update `statusline.js` to show current tier

**Files:**
- Modify: `adapters/claude/hooks/map-capabilities/statusline.js`

**Step 1: Update statusline to read manifest**

After the existing `inProgress` calculation (around line 45), add manifest reading and modify the status string:

```javascript
  // Read wave manifest for tier info
  const manifestPath = path.join(outputDir, 'wave-manifest.json');
  let waveNum = '?';
  let tierLabel = '';

  if (fs.existsSync(manifestPath)) {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    waveNum = manifest.wave || '?';
    // Show dominant tier and batch size
    if (Array.isArray(manifest.slugs) && manifest.slugs.length > 0) {
      const tiers = manifest.slugs.map(s => s.tier);
      const dominant = tiers.sort()[Math.floor(tiers.length / 2)]; // median tier
      tierLabel = ` | wave ${waveNum} T${dominant}x${manifest.slugs.length}`;
    }
  }
```

Then update the status string construction:

```javascript
  let status = `map-capabilities | ${catalogName} | ${done}/${total} | ${pct}%${tierLabel}`;
```

And remove the separate `inProgress` and `failed` appendages since the tier label replaces them for conciseness. Keep the failed counter:

```javascript
  if (failed > 0) {
    status += ` | ${failed} retry`;
  }
```

**Step 2: Commit**

```bash
git add adapters/claude/hooks/map-capabilities/statusline.js
git commit -m "feat: show tier context in statusline hook"
```

---

### Task 8: Integration test — full wave cycle

**Files:**
- Test: `tests/test_adaptive_hooks.py`

**Step 1: Write integration test**

Append to `tests/test_adaptive_hooks.py`:

```python
class TestAdaptiveIntegration:
    """Integration: full wave cycle with tiering."""

    def test_full_cycle_writes_manifest_and_respects_tiers(self, tmp_path):
        """Run next-wave, verify manifest, check tier-based batch sizing."""
        catalog = [
            _entry("famous", 2000),
            _entry("famous2", 1500),
            _entry("famous3", 900),
            _entry("mid1", 200),
            _entry("mid2", 100),
            _entry("tiny1", 10),
            _entry("tiny2", 5),
            _entry("tiny3", 3),
        ]
        (tmp_path / "catalog.json").write_text(json.dumps(catalog))

        # Wave 1: bootstrap — should pick T1 entries
        wave1 = _capture_next_wave(catalog, tmp_path)
        manifest = json.loads((tmp_path / "wave-manifest.json").read_text())
        wave1_slugs = {e["slug"] for e in wave1}

        # Bootstrap should pick T1 repos
        assert "famous" in wave1_slugs or "famous2" in wave1_slugs

        # All manifest slugs should have tier info
        for s in manifest["slugs"]:
            assert "tier" in s
            assert s["tier"] in (1, 2, 3)

    def test_post_bootstrap_processes_t3_first(self, tmp_path):
        """After bootstrap, T3 repos get processed first."""
        catalog = [
            _entry("famous", 2000),
            _entry("mid1", 200),
            _entry("tiny1", 10),
            _entry("tiny2", 5),
        ]
        # Simulate bootstrap complete
        progress = {"completed": ["famous"], "failed": {}, "in_progress": []}
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))
        # Create style anchor
        anchor_dir = tmp_path / "famous"
        anchor_dir.mkdir()
        (anchor_dir / "capability.md").write_text("# Famous\n## Constraints\n- x")

        wave2 = _capture_next_wave(catalog, tmp_path)
        wave2_slugs = [e["slug"] for e in wave2]
        # T3 should come before T2
        t3_idx = [i for i, s in enumerate(wave2_slugs) if s.startswith("tiny")]
        t2_idx = [i for i, s in enumerate(wave2_slugs) if s.startswith("mid")]
        if t3_idx and t2_idx:
            assert min(t3_idx) < min(t2_idx)

    def test_tier_distribution_in_load(self, tmp_path):
        """action_load reports tier distribution."""
        import io
        from contextlib import redirect_stdout
        catalog = [
            _entry("big", 1000), _entry("mid", 200),
            _entry("small1", 10), _entry("small2", 5),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            action_load(catalog, tmp_path)
        result = json.loads(buf.getvalue())
        assert "tiers" in result
        assert result["tiers"]["t1"] == 1
        assert result["tiers"]["t2"] == 1
        assert result["tiers"]["t3"] == 2
```

**Step 2: Run all tests**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/test_adaptive_hooks.py -v`
Expected: All PASS

**Step 3: Run full test suite for regressions**

Run: `cd /Users/emolero/Documents/GitHub/ot/everything-on-earth && python -m pytest tests/ -v --tb=short`
Expected: All PASS

**Step 4: Commit**

```bash
git add tests/test_adaptive_hooks.py
git commit -m "test: integration tests for adaptive tiering pipeline"
```

---

### Summary of Changes

| File | Lines Changed (approx) | Change Type |
|------|----------------------|-------------|
| `pipeline/generate_capabilities.py` | +120, -30 | Add tiering, adaptive wave gen, manifest writer |
| `adapters/claude/hooks/map-capabilities/subagent-context.sh` | Full rewrite (~120 lines) | Tier-aware prompt injection |
| `adapters/claude/hooks/map-capabilities/output-validator.sh` | +25, -10 | Tier-sensitive validation rules |
| `adapters/claude/hooks/map-capabilities/wave-completed.sh` | +15, -5 | Per-tier metrics |
| `adapters/claude/hooks/map-capabilities/session-resume.sh` | +20, -5 | Tier distribution display |
| `adapters/claude/hooks/map-capabilities/statusline.js` | +15, -3 | Tier label in status |
| `.claude/settings.local.json` | +8 | Wire session-resume.sh |
| `tests/test_adaptive_hooks.py` | ~250 (new) | Full test coverage |

### Dependency Order

```
Task 1 (pipeline) → Task 3 (subagent-context) → Task 4 (output-validator)
                  → Task 5 (wave-completed)
                  → Task 6 (session-resume + wiring)
                  → Task 7 (statusline)
Task 2 (pre-wave regression) — independent
Task 8 (integration) — after all others
```

Tasks 3-7 can run in parallel after Task 1 is complete.
