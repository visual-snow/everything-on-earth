"""Tests for adaptive tiering in generate_capabilities.py and map-capabilities hooks."""

import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from generate_capabilities import (
    action_load,
    action_next_wave,
    build_wave_manifest,
    classify_tier,
)


def _entry(slug: str, stars: int) -> dict:
    return {
        "slug": slug,
        "stars": stars,
        "name": slug,
        "repo_url": f"https://github.com/x/{slug}",
    }


def _capture_next_wave(entries, tmp_path):
    """Run action_next_wave and capture its JSON output."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        action_next_wave(entries, tmp_path)
    return json.loads(buf.getvalue())


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
        assert classify_tier(_entry("boundary", 500)) == 2


class TestBuildWaveManifest:
    def test_manifest_has_required_keys(self):
        entries = [_entry("a", 1000), _entry("b", 100), _entry("c", 10)]
        manifest = build_wave_manifest(
            entries, wave_number=1, domain="test",
            total_entries=3, output_dir=Path("/tmp/test"),
        )
        assert set(manifest.keys()) == {
            "wave", "domain", "total_entries", "slugs",
            "batch_size", "judge_scope", "style_anchors",
        }

    def test_slugs_carry_tier(self):
        entries = [_entry("a", 1000), _entry("b", 10)]
        manifest = build_wave_manifest(
            entries, wave_number=1, domain="test",
            total_entries=2, output_dir=Path("/tmp/test"),
        )
        tiers = {s["slug"]: s["tier"] for s in manifest["slugs"]}
        assert tiers["a"] == 1
        assert tiers["b"] == 3

    def test_style_anchors_from_existing_capability_files(self, tmp_path):
        cap_dir = tmp_path / "big-repo"
        cap_dir.mkdir()
        (cap_dir / "capability.md").write_text("# Big Repo\n## Constraints\n- works")
        progress = {"completed": ["big-repo"], "failed": {}, "in_progress": []}
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))
        entries = [_entry("small", 10)]
        manifest = build_wave_manifest(
            entries, wave_number=2, domain="test",
            total_entries=10, output_dir=tmp_path,
        )
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
        slugs = [e["slug"] for e in output]
        # Bootstrap wave should contain T1 entries
        t1_slugs = {"famous", "famous2", "famous3"}
        assert any(s in t1_slugs for s in slugs)

    def test_wave_size_respects_tier(self, tmp_path):
        entries = [_entry(f"tiny-{i}", 5) for i in range(20)]
        # Simulate bootstrap already done
        progress = {"completed": ["bootstrap-done"], "failed": {}, "in_progress": []}
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))
        anchor_dir = tmp_path / "bootstrap-done"
        anchor_dir.mkdir()
        (anchor_dir / "capability.md").write_text("# Anchor\n## Constraints\n- x")
        output = _capture_next_wave(entries, tmp_path)
        # T3 batch size is 3
        assert len(output) == 3

    def test_manifest_written_on_next_wave(self, tmp_path):
        entries = [_entry("a", 1000)]
        _capture_next_wave(entries, tmp_path)
        manifest_path = tmp_path / "wave-manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["wave"] >= 1
        assert len(manifest["slugs"]) > 0


# ── Hook test helpers ──────────────────────────────────────────────────

HOOKS_DIR = Path(__file__).resolve().parent.parent / "adapters" / "claude" / "hooks" / "map-capabilities"


def _hook_env(project_dir: str = "/nonexistent") -> dict:
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = project_dir
    return env


def _write_config(tmp_path, catalog_name="catalog.json", output_dir=None):
    config = {
        "catalog": str(tmp_path / catalog_name),
        "output_dir": output_dir or str(tmp_path),
        "catalog_name": "test",
    }
    (tmp_path / "map-capabilities-config.json").write_text(json.dumps(config))


def _setup_manifest(tmp_path, slugs, style_anchors=None):
    manifest = {
        "wave": 1, "domain": "test", "total_entries": len(slugs),
        "slugs": slugs,
        "batch_size": {1: 10, 2: 5, 3: 3},
        "judge_scope": {1: 5, 2: 3, 3: 1},
        "style_anchors": style_anchors or [],
    }
    (tmp_path / "wave-manifest.json").write_text(json.dumps(manifest))
    _write_config(tmp_path, output_dir=str(tmp_path))


def _setup_workflow_files(tmp_path):
    """Create minimal workflow files so hooks can read them."""
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


# ── Pre-wave hook tests ───────────────────────────────────────────────

class TestPreWaveHook:
    HOOK = str(HOOKS_DIR / "pre-wave.sh")

    def test_passthrough_for_non_map_capabilities_agents(self):
        input_json = json.dumps({"tool_input": {"name": "some-other-agent"}})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(),
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_researcher_with_valid_prompt_allowed(self, tmp_path):
        _write_config(tmp_path)
        (tmp_path / "catalog.json").write_text("[]")
        input_json = json.dumps({
            "tool_input": {
                "name": "researcher-my-repo",
                "prompt": '{"name": "my-repo", "repo_url": "https://github.com/x/y"}',
            }
        })
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "allow"

    def test_researcher_with_empty_prompt_blocked(self, tmp_path):
        _write_config(tmp_path)
        (tmp_path / "catalog.json").write_text("[]")
        input_json = json.dumps({
            "tool_input": {
                "name": "researcher-my-repo",
                "prompt": "",
            }
        })
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "block"


# ── Subagent-context hook tests ──────────────────────────────────────

class TestSubagentContextHook:
    HOOK = str(HOOKS_DIR / "subagent-context.sh")

    def test_researcher_t3_gets_deep_extraction_directive(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "tiny-lib", "tier": 3, "stars": 5}])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "researcher-tiny-lib"})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "lesser-known" in ctx.lower()

    def test_researcher_t1_gets_standard_context(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "big-lib", "tier": 1, "stars": 5000}])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "researcher-big-lib"})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "RESEARCHER" in ctx
        assert "lesser-known" not in ctx.lower()

    def test_writer_t2_gets_style_anchors(self, tmp_path):
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
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "Style Anchor" in ctx

    def test_writer_t1_no_style_anchors(self, tmp_path):
        anchor_dir = tmp_path / "approved-repo"
        anchor_dir.mkdir(parents=True)
        (anchor_dir / "capability.md").write_text("# Approved\n## Constraints\n- solid")
        _setup_manifest(
            tmp_path,
            [{"slug": "big-lib", "tier": 1, "stars": 5000}],
            style_anchors=[str(anchor_dir / "capability.md")],
        )
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "writer-big-lib"})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "Style Anchor" not in ctx

    def test_judge_gets_tier_metadata(self, tmp_path):
        _setup_manifest(tmp_path, [
            {"slug": "a", "tier": 1, "stars": 1000},
            {"slug": "b", "tier": 3, "stars": 8},
        ])
        _setup_workflow_files(tmp_path)
        input_json = json.dumps({"agent_name": "judge-wave-1"})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "Tier" in ctx
        assert "a" in ctx
        assert "b" in ctx

    def test_passthrough_for_unrelated_agents(self, tmp_path):
        input_json = json.dumps({"agent_name": "some-explorer"})
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""


# ── Output-validator hook tests ──────────────────────────────────────

class TestOutputValidatorHook:
    HOOK = str(HOOKS_DIR / "output-validator.sh")

    def _run_validator(self, tmp_path, slug, content):
        slug_dir = tmp_path / slug
        slug_dir.mkdir(exist_ok=True)
        file_path = str(slug_dir / "capability.md")
        input_json = json.dumps({
            "tool_input": {"file_path": file_path, "content": content}
        })
        return subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )

    def test_t1_rejects_over_60_lines(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "big-repo", "tier": 1, "stars": 2000}])
        content = "# Big Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(60))
        result = self._run_validator(tmp_path, "big-repo", content)
        assert result.returncode == 2

    def test_t1_allows_60_lines(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "big-repo", "tier": 1, "stars": 2000}])
        content = "# Big Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(55))
        result = self._run_validator(tmp_path, "big-repo", content)
        assert result.returncode == 0

    def test_t2_allows_up_to_80_lines(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "mid-repo", "tier": 2, "stars": 200}])
        content = "# Mid Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(70))
        result = self._run_validator(tmp_path, "mid-repo", content)
        assert result.returncode == 0

    def test_t2_rejects_over_80_lines(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "mid-repo", "tier": 2, "stars": 200}])
        content = "# Mid Repo\n## Constraints\n- x\n" + "\n".join(f"line {i}" for i in range(80))
        result = self._run_validator(tmp_path, "mid-repo", content)
        assert result.returncode == 2

    def test_t3_requires_two_constraint_bullets(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "tiny-repo", "tier": 3, "stars": 5}])
        content = "# Tiny Repo\n## Constraints\n- only one bullet\n"
        result = self._run_validator(tmp_path, "tiny-repo", content)
        assert result.returncode == 2

    def test_t3_passes_with_two_constraint_bullets(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "tiny-repo", "tier": 3, "stars": 5}])
        content = "# Tiny Repo\n## Constraints\n- first bullet\n- second bullet\n"
        result = self._run_validator(tmp_path, "tiny-repo", content)
        assert result.returncode == 0

    def test_passthrough_for_non_capability_files(self, tmp_path):
        _setup_manifest(tmp_path, [{"slug": "repo", "tier": 1, "stars": 500}])
        input_json = json.dumps({
            "tool_input": {"file_path": "/some/other/file.md", "content": "hello"}
        })
        result = subprocess.run(
            ["bash", self.HOOK],
            input=input_json, capture_output=True, text=True,
            env=_hook_env(str(tmp_path)),
        )
        assert result.returncode == 0


# ── Integration tests ────────────────────────────────────────────────

class TestAdaptiveIntegration:

    def test_full_cycle_writes_manifest_and_respects_tiers(self, tmp_path):
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
        # Wave 1: bootstrap
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
        catalog = [
            _entry("famous", 2000),
            _entry("mid1", 200),
            _entry("tiny1", 10),
            _entry("tiny2", 5),
        ]
        # Simulate bootstrap complete
        progress = {"completed": ["famous"], "failed": {}, "in_progress": []}
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))
        anchor_dir = tmp_path / "famous"
        anchor_dir.mkdir()
        (anchor_dir / "capability.md").write_text("# Famous\n## Constraints\n- x")

        wave2 = _capture_next_wave(catalog, tmp_path)
        wave2_slugs = [e["slug"] for e in wave2]
        # T3 should be in this wave (processed before T2)
        assert any(s.startswith("tiny") for s in wave2_slugs)

    def test_tier_distribution_in_load(self, tmp_path):
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

    def test_style_anchors_populated_after_bootstrap(self, tmp_path):
        catalog = [
            _entry("famous", 2000),
            _entry("tiny1", 10),
        ]
        # Run bootstrap wave
        _capture_next_wave(catalog, tmp_path)

        # Simulate completing bootstrap
        progress = json.loads((tmp_path / "wave-progress.json").read_text())
        progress["completed"] = progress.pop("in_progress", [])
        progress["in_progress"] = []
        (tmp_path / "wave-progress.json").write_text(json.dumps(progress))

        # Create capability file for completed slug
        for slug in progress["completed"]:
            slug_dir = tmp_path / slug
            slug_dir.mkdir(exist_ok=True)
            (slug_dir / "capability.md").write_text(f"# {slug}\n## Constraints\n- x")

        # Next wave should have style anchors in manifest
        _capture_next_wave(catalog, tmp_path)
        manifest = json.loads((tmp_path / "wave-manifest.json").read_text())
        assert len(manifest["style_anchors"]) > 0

    def test_estimated_waves_accounts_for_tiers(self, tmp_path):
        # 10 T1 (batch 10) + 10 T2 (batch 5) + 9 T3 (batch 3)
        catalog = (
            [_entry(f"big-{i}", 1000) for i in range(10)] +
            [_entry(f"mid-{i}", 200) for i in range(10)] +
            [_entry(f"tiny-{i}", 5) for i in range(9)]
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            action_load(catalog, tmp_path)
        result = json.loads(buf.getvalue())
        # T1: ceil(10/10)=1, T2: ceil(10/5)=2, T3: ceil(9/3)=3 => 6 waves
        assert result["waves_remaining"] == 6
