# everything-on-earth

## Hooks

IMPORTANT: All hooks live in the project-level `.claude/settings.local.json` — NEVER in the user's global `~/.claude/settings.json`. This is a plugin used by many people; project hooks must not pollute user configs.

### Hook path rules

- Massive-crawl hooks live at `hooks/` (project root): `hooks/post-concat.js`, `hooks/statusline.js`, etc.
- Map-capabilities hooks live at `hooks/map-capabilities/`.
- YOU MUST verify every hook script path exists on disk before writing or modifying `settings.local.json`. Run `ls` on the path first. A wrong path silently breaks every tool call that triggers that hook.
- When renaming or moving skills, do NOT update hook paths in settings unless you also move the actual files (or vice versa). Path and file must always match.

## Project structure

```
hooks/                  # massive-crawl hook scripts (root level)
hooks/map-capabilities/ # map-capabilities hook scripts (subdirectory)
skill/massive-crawl/    # massive-crawl skill definition
pipeline/               # data pipeline (dedup, prune, enrich, finalize)
```
