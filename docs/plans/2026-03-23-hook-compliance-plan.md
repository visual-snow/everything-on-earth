# Hook Compliance Pass — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bring map-capabilities hooks into full CLAUDE.md compliance by removing context duplication, adding tool restrictions, cleaning up install.sh, and documenting design choices.

**Architecture:** Four files modified — SKILL.md gets the bulk of changes (remove !cat, add allowed-tools to agents), install.sh loses a redundant copy block, two hooks get documentation comments.

**Tech Stack:** Markdown (SKILL.md), Bash (install.sh, subagent-context.sh), Node.js (statusline.js)

---

### Task 1: Remove !cat duplication and add tool restrictions in SKILL.md

**Files:**
- Modify: `skill/map-capabilities/SKILL.md:70-85` (Researcher block)
- Modify: `skill/map-capabilities/SKILL.md:93-114` (Writer block)
- Modify: `skill/map-capabilities/SKILL.md:120-142` (Judge block)

**Step 1: Replace Researcher agent block (lines 74-85)**

Replace the current block:
```
Agent({
  model: "sonnet",
  name: "researcher-{slug}",
  prompt: !`cat skill/references/capability-researcher.md`

    ## CATALOG ENTRY
    ```json
    {entry_json}
    ```
})
```

With:
```
Agent({
  model: "sonnet",
  name: "researcher-{slug}",
  allowed-tools: ["WebSearch", "WebFetch", "Read", "Grep", "Glob"],
  prompt:
    # Reference injected by SubagentStart hook: capability-researcher.md, capability-factsheet-schema.json

    ## CATALOG ENTRY
    ```json
    {entry_json}
    ```
})
```

**Step 2: Replace Writer agent block (lines 95-114)**

Replace the current block:
```
Agent({
  model: "sonnet",
  name: "writer-{slug}",
  prompt: !`cat skill/references/capability-writer.md`

    ## FACTSHEET
    ```json
    {factsheet_json}
    ```

    ## STYLE EXEMPLAR
    !`cat skill/references/gold_sandbox_capabilities.md`

    ## JUDGE FEEDBACK (if retry)
    {feedback_or_empty}

    Write the capability document. Return ONLY the markdown content.
})
```

With:
```
Agent({
  model: "sonnet",
  name: "writer-{slug}",
  allowed-tools: ["Read"],
  prompt:
    # Reference injected by SubagentStart hook: capability-writer.md, gold_sandbox_capabilities.md

    ## FACTSHEET
    ```json
    {factsheet_json}
    ```

    ## JUDGE FEEDBACK (if retry)
    {feedback_or_empty}

    Write the capability document. Return ONLY the markdown content.
})
```

**Step 3: Replace Judge agent block (lines 122-142)**

Replace the current block:
```
Agent({
  model: "sonnet",
  name: "judge-wave-{n}",
  prompt: !`cat skill/references/capability-judge.md`

    ## STYLE EXEMPLAR
    !`cat skill/references/gold_sandbox_capabilities.md`

    ## FILES TO REVIEW
    {for each slug in wave:}
    ### {slug}
    #### FACTSHEET
    ```json
    {factsheet_json}
    ```
    #### CAPABILITY DOC
    {capability_md_content}
    {end for}
})
```

With:
```
Agent({
  model: "sonnet",
  name: "judge-wave-{n}",
  allowed-tools: ["Read"],
  prompt:
    # Reference injected by SubagentStart hook: capability-judge.md, gold_sandbox_capabilities.md

    ## FILES TO REVIEW
    {for each slug in wave:}
    ### {slug}
    #### FACTSHEET
    ```json
    {factsheet_json}
    ```
    #### CAPABILITY DOC
    {capability_md_content}
    {end for}
})
```

**Step 4: Verify SKILL.md is under 500 lines**

Run: `wc -l skill/map-capabilities/SKILL.md`
Expected: under 500 (was 205, should shrink to ~190)

**Step 5: Commit**

```bash
git add skill/map-capabilities/SKILL.md
git commit -m "refactor: remove !cat duplication, add tool restrictions to map-capabilities agents"
```

---

### Task 2: Remove redundant hook copy from install.sh

**Files:**
- Modify: `install.sh:102-107` (remove 6-line block)

**Step 1: Remove the redundant copy block**

Delete lines 102-107:
```bash
# Copy map-capabilities hooks
MAP_CAP_HOOKS_DEST="$HOME/.claude/hooks/map-capabilities"
mkdir -p "$MAP_CAP_HOOKS_DEST"
cp "$SCRIPT_DIR/hooks/map-capabilities/"* "$MAP_CAP_HOOKS_DEST/"
chmod +x "$MAP_CAP_HOOKS_DEST/"*
echo -e "${GREEN}✓ Map-capabilities hooks installed to $MAP_CAP_HOOKS_DEST${NC}"
```

Also update the uninstall block (line 21) to remove the now-unnecessary `$HOME/.claude/hooks/map-capabilities` cleanup:

Change line 21 from:
```bash
  rm -rf "$HOME/.claude/skills/map-capabilities" "$HOME/.claude/hooks/map-capabilities"
```
To:
```bash
  rm -rf "$HOME/.claude/skills/map-capabilities"
```

**Step 2: Verify install.sh still runs without errors**

Run: `bash -n install.sh`
Expected: no output (syntax valid)

**Step 3: Commit**

```bash
git add install.sh
git commit -m "fix: remove redundant hook copy — hooks run from project dir via \$CLAUDE_PROJECT_DIR"
```

---

### Task 3: Add documentation comments to hooks

**Files:**
- Modify: `hooks/map-capabilities/statusline.js:8-10` (add comment)
- Modify: `hooks/map-capabilities/subagent-context.sh:1-7` (add comment)

**Step 1: Add mutual exclusion comment to statusline.js**

After the existing header comment block (after line 10), add:

```javascript
 * Mutual exclusion: This hook and massive-crawl/statusline.js both register on
 * Notification without matchers. Each checks for its own config file
 * (map-capabilities-config.json vs swarm-config.json) and exits 0 if absent.
 * No runtime collision is possible — only one config exists at a time.
```

Insert this as lines 10-13, before the closing `*/`.

**Step 2: Add error handling comment to subagent-context.sh**

After line 6, add:

```bash
#
# Note: set -euo pipefail is intentionally omitted. This hook uses
# cat ... 2>/dev/null with empty-string fallback checks for graceful
# degradation. Pipefail would cause early exit before fallback logic runs.
```

**Step 3: Commit**

```bash
git add hooks/map-capabilities/statusline.js hooks/map-capabilities/subagent-context.sh
git commit -m "docs: document mutual exclusion and error handling choices in hooks"
```

---

### Task 4: Final verification

**Step 1: Verify all hooks are executable**

Run: `ls -la hooks/map-capabilities/`
Expected: all `.sh` files have execute permission

**Step 2: Verify settings.json has all 6 hooks registered**

Run: `grep -c "map-capabilities" ~/.claude/settings.json`
Expected: 6 (one per hook)

**Step 3: Verify SKILL.md has no remaining !cat directives**

Run: `grep '!.cat' skill/map-capabilities/SKILL.md`
Expected: no matches

**Step 4: Verify SKILL.md has allowed-tools on all agent blocks**

Run: `grep 'allowed-tools' skill/map-capabilities/SKILL.md`
Expected: 3 matches (researcher, writer, judge)
