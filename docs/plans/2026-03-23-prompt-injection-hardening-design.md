# Prompt Injection Hardening via Least-Privilege Tool Access

## Problem

The map-capabilities Researcher agent fetches external README content via WebFetch and also has Read/Grep/Glob access to the local filesystem. A GitHub repo containing prompt injection in its README (increasingly common as anti-scraping measures) could instruct the Researcher to read local files, produce hallucinated factsheets, or deviate from its task.

## Threat Model

Untargeted/accidental injection — random repos containing LLM anti-scraping payloads like "ignore previous instructions." Not targeted adversarial attacks against this specific pipeline.

## Design Decision

Move all external scraping from the Researcher agent to the orchestrator. The Researcher becomes a zero-tool agent that receives pre-fetched content in its prompt. Prompt injection becomes toothless because there are no tools to hijack.

## Tool Access Matrix

| Agent | Before | After | Rationale |
|-------|--------|-------|-----------|
| Orchestrator | Agent, Read, Write, Glob, Grep, Bash, WebFetch, AskUserQuestion | Same + firecrawl via Bash | Trusted code, deterministic commands |
| Researcher | WebSearch, WebFetch, Read, Grep, Glob | **(none)** | Only agent touching external content. Zero tools = zero blast radius. |
| Writer | Read | Read (unchanged) | Processes internal factsheets only |
| Judge | Read | Read (unchanged) | Reviews internal capability docs only |

## What Changes

### 1. Orchestrator gains a scrape step (SKILL.md)

New step between "Get next wave" and "Researcher phase":

```
For each entry in wave:
  1. firecrawl scrape {repo_url} → save to {slug}/readme-raw.md
  2. firecrawl scrape {repo_url}/blob/main/docker-compose.yml → save to {slug}/compose-raw.md (optional, ignore failure)
  3. If readme-raw.md is thin (<50 lines), firecrawl search "{name} {description}" → append top result to readme-raw.md
```

### 2. Researcher agent becomes zero-tool (SKILL.md)

```
Agent({
  model: "sonnet",
  name: "researcher-{slug}",
  allowed-tools: [],
  prompt:
    # Reference injected by SubagentStart hook

    ## CATALOG ENTRY
    {entry_json}

    ## README CONTENT
    {scraped_readme}

    ## DOCKER COMPOSE (if available)
    {scraped_compose}
})
```

### 3. Researcher prompt updated (capability-researcher.md)

- Remove WebFetch workflow steps ("Fetch the repo README", "Scrape docker-compose.yml")
- Replace with: "Analyze the README and compose content provided below"
- Remove "2 WebFetch calls maximum" rule
- Keep all output format and quality rules unchanged

## What Does NOT Change

- Writer agent, Judge agent, hooks, progress tracking, schema validation
- Pipeline orchestration flow (waves, retries, mark-done/mark-failed)
- Output format (factsheet.json, capability.md, wave-progress.json)

## Files to Modify

1. `skill/map-capabilities/SKILL.md` — add scrape step, change Researcher allowed-tools to []
2. `skill/references/capability-researcher.md` — remove WebFetch workflow, add "content provided below" framing
