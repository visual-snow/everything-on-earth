"""Repository-level contract tests for workflow/adapters layout."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).parent.parent


def _read(path: Path) -> str:
    return path.read_text()


def _skill_description(path: Path) -> str:
    contents = _read(path)
    match = re.search(r"description:\s+>-\n(?P<body>(?:\s+.+\n)+)", contents)
    assert match, f"missing folded description in {path}"
    return " ".join(line.strip() for line in match.group("body").splitlines())


def test_massive_crawl_runtime_contract_matches_current_workflow():
    runtime_path = ROOT / "workflows" / "massive-crawl" / "runtime.json"
    runtime = json.loads(runtime_path.read_text())

    assert runtime["stages"] == [
        "brainstorm",
        "discover",
        "dedup",
        "score",
        "enrich",
        "finalize",
        "gap_review",
    ]
    assert runtime["roles"] == ["scout", "discoverer", "enricher"]
    assert runtime["artifacts"]["scored"] == "scored.json"
    assert runtime["artifacts"]["enriched"] == "enriched.json"
    assert runtime["invariants"]["enrichment_preserves_count"] is True
    assert runtime["invariants"]["enrichment_preserves_order"] is True


def test_workflow_manifests_only_reference_existing_files():
    workflow_dirs = [ROOT / "workflows" / "massive-crawl", ROOT / "workflows" / "map-capabilities"]

    for workflow_dir in workflow_dirs:
        manifest = json.loads((workflow_dir / "manifest.json").read_text())
        for rel_path in manifest["files"]:
            assert (workflow_dir / rel_path).exists(), f"missing {workflow_dir / rel_path}"


def test_codex_enricher_default_mapping_is_declared():
    models_path = ROOT / "adapters" / "codex" / "models.json"
    models = json.loads(models_path.read_text())

    enricher = models["massive-crawl"]["enricher"]
    assert enricher["model"] == "gpt-5.4-mini"
    assert enricher["reasoning_effort"] == "medium"
    assert enricher["allow_override"] is True


def test_claude_project_hook_config_is_present_and_points_to_adapter_hooks():
    settings_path = ROOT / ".claude" / "settings.local.json"
    assert settings_path.exists(), "missing project-local Claude hook config"

    settings = json.loads(_read(settings_path))
    commands = []
    for hook_group in settings["hooks"].values():
        for matcher in hook_group:
            for hook in matcher["hooks"]:
                commands.append(hook["command"])

    assert commands, "expected committed Claude hook commands"
    for command in commands:
        assert "adapters/claude/hooks/" in command, f"stale hook path: {command}"
        assert "$CLAUDE_PROJECT_DIR/hooks/" not in command, f"old hook path still present: {command}"


def test_claude_hook_commands_reference_existing_files():
    settings_path = ROOT / ".claude" / "settings.local.json"
    settings = json.loads(_read(settings_path))

    for hook_group in settings["hooks"].values():
        for matcher in hook_group:
            for hook in matcher["hooks"]:
                command = hook["command"]
                match = re.search(r'adapters/claude/hooks/[^"\s]+', command)
                assert match, f"could not parse hook path from {command}"
                assert (ROOT / match.group(0)).exists(), f"missing hook target: {match.group(0)}"


def test_claude_map_capabilities_wrapper_keeps_side_effect_safety_flags():
    skill_path = ROOT / "adapters" / "claude" / "skills" / "map-capabilities" / "SKILL.md"
    contents = _read(skill_path)

    assert "disable-model-invocation: true" in contents
    assert "context: fork" in contents


def test_adapter_skill_descriptions_include_trigger_language():
    discovery_phrases = {
        "find every repo",
        "discover all tools",
        "massive crawl",
        "catalog all open source",
    }
    capability_phrases = {
        "map capabilities",
        "generate capability docs",
        "capability mapper",
    }

    skill_paths = [
        ROOT / "adapters" / "claude" / "skills" / "massive-crawl" / "SKILL.md",
        ROOT / "adapters" / "codex" / "skills" / "massive-crawl" / "SKILL.md",
    ]
    for path in skill_paths:
        description = _skill_description(path).lower()
        assert any(phrase in description for phrase in discovery_phrases), f"weak discovery triggers in {path}"

    skill_paths = [
        ROOT / "adapters" / "claude" / "skills" / "map-capabilities" / "SKILL.md",
        ROOT / "adapters" / "codex" / "skills" / "map-capabilities" / "SKILL.md",
    ]
    for path in skill_paths:
        description = _skill_description(path).lower()
        assert any(phrase in description for phrase in capability_phrases), f"weak capability triggers in {path}"


def test_shared_massive_crawl_prompt_stays_platform_neutral():
    prompt_path = ROOT / "workflows" / "massive-crawl" / "prompts" / "agent-prompt-template.md"
    contents = _read(prompt_path)

    assert "TaskList(" not in contents
    assert "TaskUpdate(" not in contents
    assert "TeamCreate(" not in contents


def test_map_capabilities_contract_and_claude_wrapper_preserve_toolless_researchers():
    contract_path = ROOT / "workflows" / "map-capabilities" / "contract.md"
    skill_path = ROOT / "adapters" / "claude" / "skills" / "map-capabilities" / "SKILL.md"

    contract = _read(contract_path)
    skill = _read(skill_path)

    assert "researcher" in contract.lower()
    assert "allowed-tools: []" in contract or "allowed-tools: []" in skill


def test_codex_installer_exists_and_root_installer_exposes_platform_flags():
    codex_install = ROOT / "adapters" / "codex" / "install.sh"
    root_install = ROOT / "install.sh"

    assert codex_install.exists(), "missing Codex installer"

    root_contents = _read(root_install)
    assert "--claude" in root_contents
    assert "--codex" in root_contents


def test_platform_installers_are_executable():
    installer_paths = [
        ROOT / "install.sh",
        ROOT / "adapters" / "claude" / "install.sh",
        ROOT / "adapters" / "codex" / "install.sh",
    ]

    for path in installer_paths:
        assert path.exists(), f"missing installer: {path}"
        assert path.stat().st_mode & 0o111, f"installer is not executable: {path}"


def test_project_local_claude_hook_config_is_not_repo_ignored():
    gitignore_path = ROOT / ".gitignore"
    contents = _read(gitignore_path)

    assert "!.claude/" in contents
    assert "!.claude/settings.local.json" in contents
