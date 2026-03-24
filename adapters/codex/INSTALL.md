# Codex Adapter Install

Install the Codex wrapper skills with the explicit platform installer:

```bash
./install.sh --codex
```

Uninstall them with:

```bash
./install.sh --codex --uninstall
```

## What gets installed

- `adapters/codex/skills/massive-crawl/SKILL.md` -> `$CODEX_HOME/skills/massive-crawl/SKILL.md`
- `adapters/codex/skills/map-capabilities/SKILL.md` -> `$CODEX_HOME/skills/map-capabilities/SKILL.md`

`$CODEX_HOME` defaults to `~/.codex`.

## Entry points

- `$massive-crawl`
- `$map-capabilities`

## Notes

- No `~/.codex/config.toml` edits are required for basic installation.
- Shared workflow assets still live under `workflows/`.
- If a referenced shared workflow file is missing, fail closed and report the exact path.
