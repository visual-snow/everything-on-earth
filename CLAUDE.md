# everything-on-earth

## Hooks

IMPORTANT: Claude hook configuration lives in the project-level [`.claude/settings.local.json`](./.claude/settings.local.json), never in a user's global `~/.claude/settings.json`.

## Project Structure

```text
workflows/                # shared workflow contracts, prompts, schemas, examples
adapters/claude/          # Claude-specific skills, hooks, installer
adapters/codex/           # Codex-specific skills, config, install docs
pipeline/                 # deterministic Python pipeline
.claude/settings.local.json
```

## Path Rules

- Claude hook scripts live under `adapters/claude/hooks/`
- Claude adapter prompts live under `adapters/claude/prompts/`
- Claude skill wrappers live under `adapters/claude/skills/`
- Shared source-of-truth files live under `workflows/<workflow>/`
- If you change a hook path, update [`.claude/settings.local.json`](./.claude/settings.local.json) in the same change
- Verify every referenced hook target exists on disk before changing `.claude/settings.local.json`
