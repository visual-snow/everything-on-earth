# External Integrations

**Analysis Date:** 2026-03-27

## APIs & External Services

**Web Search / Crawling:**
- Firecrawl CLI (`firecrawl search ... --categories github --json`) - repo discovery queries
  - Used by: `pipeline/discover_candidates.py`
  - Auth: handled by the Firecrawl CLI tool itself (not stored in this repo)

**GitHub:**
- GitHub CLI (`gh api repos/{owner}/{repo}`) - fetch repo metadata (stars, language, license, last push)
  - Used by: `pipeline/discover_candidates.py`
  - Auth: `gh` CLI must be authenticated on the host machine

**Anthropic Claude API:**
- Accessed via Claude Code agent runtime, not called directly from code
  - Models configured in: `adapters/claude/models.json`
  - Roles: scout (haiku), discoverer (sonnet), enricher (haiku, overridable), researcher/writer/judge (sonnet), classifier (haiku)

**OpenAI-compatible API:**
- Used by `training-stack/medagentsim` service via `OPENAI_API_BASE` env var
  - Default target: `http://ollama:11434/v1` (local Ollama instance)
  - Model: `llama3` by default

**OpenAI Codex / GPT:**
- Codex adapter uses `gpt-5.4-mini` with medium reasoning effort for enrichment
  - Config: `adapters/codex/models.json`

## Data Storage

**Databases:**
- None; all pipeline data stored as JSON files on disk

**File Storage:**
- Local filesystem only
  - Catalog entries: `catalog/<domain>/catalog.json`
  - Discovery artifacts: `raw-discovery.json`, `dedup.json` (working files per run)
  - Capability graph: `capability-graph/graph/`, `capability-graph/exports/`, `capability-graph/ontology/`
  - Generated HTML: `catalog/<domain>/detail/*.html`, `index.html`

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None in the main pipeline
- `training-stack/` services have no auth layer; intended for local use behind nginx reverse proxy

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Hook scripts write to stderr on failure; Claude Code surfaces these in the session
- Pipeline scripts print to stdout/stderr directly

## CI/CD & Deployment

**Hosting:**
- No hosting infrastructure; catalog output is static HTML
- `training-stack/` runs locally via Docker Compose on port 8080

**CI Pipeline:**
- No `.github/` directory; no GitHub Actions workflows configured
- Tests run manually: `python3 -m pytest tests/`

## Claude Code Hook Wiring

All hooks are project-local, configured in `.claude/settings.local.json`.

| Hook Event | Script | Purpose |
|---|---|---|
| `SessionStart` (startup) | `adapters/claude/hooks/supercharge/session-context.sh` | Inject domain context on session open |
| `SessionStart` (compact) | `adapters/claude/hooks/supercharge/compact-restore.sh` | Restore context after compaction |
| `UserPromptSubmit` | `adapters/claude/hooks/supercharge/route-query.py` | Keyword-route prompt to domain capability graph |
| `PostToolUse` (Bash) | `adapters/claude/hooks/post-concat.js` | Auto-trigger pipeline dedup after file concat |
| `PostToolUse` (Bash) | `adapters/claude/hooks/map-capabilities/wave-completed.sh` | Signal wave completion |
| `PostToolUse` (Write) | `adapters/claude/hooks/map-capabilities/output-validator.sh` | Validate written output files |
| `PreToolUse` (TeamCreate) | `adapters/claude/hooks/pre-teamcreate.js` | Pre-flight checks before team spawn |
| `PreToolUse` (Agent) | `adapters/claude/hooks/map-capabilities/pre-wave.sh` | Pre-wave gate check |
| `SubagentStart` | `adapters/claude/hooks/subagent-context.sh` | General subagent context injection |
| `SubagentStart` | `adapters/claude/hooks/map-capabilities/subagent-context.sh` | map-capabilities subagent context |
| `TaskCompleted` | `adapters/claude/hooks/task-completed.sh` | Task completion handler |
| `TeammateIdle` | `adapters/claude/hooks/teammate-idle.sh` | Idle teammate handler |
| `Notification` | `adapters/claude/hooks/statusline.js` | Status line update |
| `Notification` | `adapters/claude/hooks/map-capabilities/statusline.js` | map-capabilities status line |

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## MCP Servers

No MCP server configuration detected in the codebase.

---

*Integration audit: 2026-03-27*
