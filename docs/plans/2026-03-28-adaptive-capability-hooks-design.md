# Adaptive Capability Hooks Design

## Problem

The map-capabilities pipeline was built for telecoms (166 entries) with fixed waves of 15. Scaling to larger domains (biology 565, cybersecurity 397, healthcare 348) degrades quality three ways:

1. **Judge saturation** - reviewing 15 capability docs at once leads to rubber-stamping
2. **Researcher depth** - obscure repos (common in larger domains) need more context
3. **Consistency drift** - after 20+ waves, writer style diverges with no memory of prior waves

## Solution: Repo Tiering Through Hooks

Classify repos by signals (stars, activity), then adapt every hook's behavior per tier. No changes to the skill or contract; all adaptation flows through hooks.

### Tier Classification

| Signal | Tier 1 (well-known) | Tier 2 (mid) | Tier 3 (obscure) |
|--------|---------------------|--------------|-------------------|
| Stars | >500 | 50-500 | <50 |
| Batch size | 10 | 5 | 3 |
| Judge scope | 5 per review | 3 per review | 1:1 per entry |
| Researcher context | Standard prompt | + README emphasis | + README inlined + deep extraction note |
| Writer exemplars | 1 gold exemplar | + 1-2 style anchors | + 2 style anchors + stricter validator |

### Coordination Artifact: `wave-manifest.json`

Written by `pre-wave.sh` before each wave. Read by all downstream hooks.

```json
{
  "wave": 3,
  "domain": "healthcare",
  "total_entries": 348,
  "slugs": [
    {"slug": "openmrs-openmrs-core", "tier": 1, "stars": 4200},
    {"slug": "some-niche-tool", "tier": 3, "stars": 12}
  ],
  "batch_size": {"tier1": 10, "tier2": 5, "tier3": 3},
  "judge_scope": {"tier1": 5, "tier2": 3, "tier3": 1},
  "style_anchors": [
    "catalog/healthcare/openmrs-openmrs-core/capability.md"
  ]
}
```

### Hook Changes

#### 1. `pre-wave.sh` (PreToolUse) — becomes the brain

- Reads catalog.json, classifies each slug by stars + last_activity
- Computes batch size per tier
- Collects style anchors from previously approved capability.md files
- Writes `wave-manifest.json`
- Detects bootstrap condition (no approved outputs) and forces T1-first wave
- Sorts remaining work: T3 first (hardest), then T2, then T1

#### 2. `subagent-context.sh` (SubagentStart) — tier-aware injection

Researchers:
- T1: standard prompt + factsheet schema
- T2: standard prompt + factsheet schema + README emphasis directive
- T3: standard prompt + factsheet schema + pre-fetched README inlined + deep extraction directive

Writers:
- All tiers: writer prompt + gold exemplar
- T2/T3: additionally inject 1-2 style anchors from approved T1 outputs

Judges:
- Inject tier metadata so judge calibrates expected depth per entry

#### 3. `output-validator.sh` (PostToolUse on Write) — tier-sensitive rules

- T1: current rules, 60-line limit
- T2: structural rules, 80-line limit
- T3: structural rules, 80-line limit, require >= 2 bullets in Constraints section

#### 4. `wave-completed.sh` (PostToolUse on Bash) — per-tier metrics

Report format: `healthcare wave 3: 5/348 done | T1: 3/3 ok | T2: 1/1 ok | T3: 1/2 (1 retry) | 343 remaining`

#### 5. `session-resume.sh` (SessionStart) — tier distribution

Show tier breakdown: `healthcare: 12/348 complete | T1: 45 repos | T2: 187 repos | T3: 116 repos | ~52 waves remaining`

Wave estimate accounts for variable batch sizes.

#### 6. `statusline.js` (Notification) — current tier context

Format: `map-capabilities | healthcare | 12/348 | 3% | wave 3 T3x3`

### Wave Scheduling

1. Wave 1 (bootstrap): 3-5 T1 repos, outputs become style anchors
2. Subsequent waves: T3 first (small batches, high risk, fresh context), then T2, then T1
3. Batch sizes per tier ensure judge never reviews more than 5 at once

### Bootstrap Protocol

First wave detects no approved exemplars exist. Forces T1-only batch of 3-5 well-known repos. Their approved outputs populate `style_anchors[]` for all subsequent waves.

## Files Modified

| File | Change |
|------|--------|
| `adapters/claude/hooks/map-capabilities/pre-wave.sh` | Add tiering logic, wave-manifest.json writer |
| `adapters/claude/hooks/map-capabilities/subagent-context.sh` | Read manifest, tier-aware prompt injection |
| `adapters/claude/hooks/map-capabilities/output-validator.sh` | Read manifest, tier-sensitive validation rules |
| `adapters/claude/hooks/map-capabilities/wave-completed.sh` | Per-tier metrics reporting |
| `adapters/claude/hooks/map-capabilities/session-resume.sh` | Tier distribution in resume context |
| `adapters/claude/hooks/map-capabilities/statusline.js` | Show current tier in status line |

## Files Not Modified

- `adapters/claude/skills/map-capabilities/SKILL.md` — no skill changes
- `workflows/map-capabilities/contract.md` — contract stays the same
- `workflows/map-capabilities/prompts/*` — shared prompts unchanged
