---
name: massive-crawl
description: >-
  Discovers every open-source GitHub/GitLab repository for any topic using a
  TeamCreate agent swarm and deterministic Python synthesis pipeline. Use when
  the user says "find every repo", "discover all tools", "massive crawl", "find every repo",
  "catalog all open source", "survey the landscape", or wants comprehensive
  GitHub/GitLab discovery for a broad domain. Launches 3 Haiku scouts for
  reconnaissance, asks clarifying questions, then deploys 6-8 Sonnet teammates
  in a self-claiming swarm. Deterministic pipeline handles dedup, pruning,
  and finalization. Enrichment is handled inline via Haiku subagents. Outputs catalog.json, explorer.html, RESULTS.md.
disable-model-invocation: true
context: fork
allowed-tools:
  - Agent
  - TeamCreate
  - TeamDelete
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - SendMessage
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
---

# massive-crawl

Discover every open-source repo for any topic. LLM swarm for discovery, deterministic Python for synthesis.

## Table of Contents

1. [Phase 1: Brainstorm](#phase-1-brainstorm)
2. [Phase 2: Discover](#phase-2-discover)
3. [Phase 3: Pipeline](#phase-3-pipeline)
4. [Phase 4: Gap Review](#phase-4-gap-review)
5. [Reference Files](#reference-files)

## Phase 1: Brainstorm

**On invocation**, immediately launch 3 Haiku scout agents in parallel:

```
Agent(model: "haiku", name: "awesome-scout", prompt: "Search for awesome-lists and curated collections about: $ARGUMENTS. Return: list name, URL, item count, last updated. Use WebSearch and WebFetch.")

Agent(model: "haiku", name: "query-scout", prompt: "Run 2-3 sample searches for: $ARGUMENTS. Use WebSearch. Report: which queries return relevant GitHub repos, which return noise, and suggested refinements.")

Agent(model: "haiku", name: "landscape-scout", prompt: "Check if any existing catalogs, surveys, or comparison databases exist for: $ARGUMENTS. Use WebSearch and WebFetch. Report what you find.")
```

**While scouts run**, ask the user one question at a time:

1. **Known sub-domains**: "What sub-categories do you already know about?"
2. **Seed repos**: "Any repos you've already found that I should know about?"
3. **Exclusions**: "Any repos or categories you want to exclude entirely?"

**When scouts return**, incorporate their findings:
- Show any awesome-lists found (awesome-scout)
- Show query quality results (query-scout)
- Show existing catalogs (landscape-scout)

4. **Scout-informed sub-domains**: "The scouts found [X]. Should I add these sub-domains?" (present as multiple-choice using AskUserQuestion)

**Build the mental model diagram** — update it after each answer:

```
+---------------------------------------------------+
|  Everything on Earth                              |
|  Topic: {topic}                                   |
|  Constraints: {constraints}                       |
|                                                   |
|  Task pool ({N} tasks):                           |
|  |-- task-001: {sub-domain-1}    (10 queries)     |
|  |-- task-002: {sub-domain-2}    (10 queries)     |
|  |-- ...                                          |
|  |-- task-N: awesome-lists       (curated)        |
|                                                   |
|  Teammates: {count} (Sonnet, self-claiming)       |
|  Estimated: ~${cost} firecrawl + ~${tokens} LLM   |
+---------------------------------------------------+
```

5. **Final approval**: "Here's the plan. Ready to launch the swarm?" (AskUserQuestion with Yes/No)

**HARD GATE: Do NOT proceed to Phase 2 until user explicitly approves.**

## Phase 2: Discover

After approval:

1. **Write swarm-config.json** to the working directory with all sub-domains, seed queries, and settings.

2. **Create team**:
```
TeamCreate("eoe-{topic-slug}")
```

3. **Create tasks** — one per sub-domain + 1 awesome-lists task:
```
TaskCreate({
  subject: "{sub-domain-id}",
  description: "Search for all {sub-domain-name} repos. Write results to discovery/{sub-domain-id}.json",
  team_name: "eoe-{topic-slug}"
})
```

4. **Spawn teammates** — 6-8 Sonnet agents:
```
Agent({
  team_name: "eoe-{topic-slug}",
  name: "discoverer-{n}",
  model: "sonnet",
  mode: "bypassPermissions",
  prompt: "You are a discovery agent in a massive-crawl swarm.

Workflow:
1. Call TaskList, claim a pending task via TaskUpdate (status: in_progress).
2. Read seed queries from the task description.
3. Search using firecrawl-search (budget: 10 searches per task).
4. Scrape promising results with firecrawl-scrape (budget: 30 scrapes per task).
5. Score each repo 0-10 (0=tangential, 5=relevant, 10=essential) with a 1-sentence rationale.
6. Write results as a JSON array to discovery/{sub-domain-id}.json.
7. Mark task completed, claim the next pending task. Stop when none remain.

Output schema — each entry in the JSON array MUST have these fields:
  repo_url (string, canonical GitHub/GitLab URL, lowercase, no trailing slash, no .git)
  name (string, owner/repo format)
  description (string, 1-2 sentences, min 10 chars)
  sub_domain (string, matches the task sub-domain id)
  score (integer 1-10, do NOT include score-0 repos)
  score_rationale (string, 1-sentence justification)
  stars (integer or null)
  language (string or null)
  license (string or null, SPDX identifier)
  last_activity (string or null, YYYY-MM-DD)
Do NOT include tags, category, summary, or found_in_domains — these are added by the pipeline later.

Rules:
- Use ALL seed queries. Look beyond the first page of results.
- Use exact repo_url from GitHub/GitLab. Never guess URLs or fabricate repos.
- No duplicates within your output file. Cross-agent dedup happens later.
- Be thorough but stay within search/scrape budgets."
})
```

The SubagentStart hook additionally injects `agent-prompt-template.md`, `output-schema.json`, and `swarm-config.json` into each teammate for full reference.

5. **Wait** for all tasks to complete. Monitor via TaskList.

6. **Concat results** (deterministic — no LLM):
```bash
jq -s 'add' discovery/*.json > raw-discovery.json
echo "Concatenated $(jq length raw-discovery.json) entries from $(ls discovery/*.json | wc -l) files"
```

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

## Phase 4: Gap Review

After presenting results:

1. Ask: "Any domains missing from the results?"
2. If yes: create new tasks on the existing team, spawn 2-3 follow-up agents
3. Merge new discovery files into existing catalog through the same pipeline
4. If no: clean up — `TeamDelete("eoe-{topic-slug}")`

## Reference Files

- `skill/references/agent-prompt-template.md` — injected into teammates by SubagentStart hook
- `skill/references/output-schema.json` — entry schema that hooks validate against
