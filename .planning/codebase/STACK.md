# Technology Stack

**Analysis Date:** 2026-03-27

## Languages

**Primary:**
- Python 3 (>=3.9 required, 3.11 in Docker images, 3.14 in dev env) - pipeline scripts, hooks, tests
- JavaScript / Node.js - Claude hook scripts (CommonJS, no transpilation)
- Bash - installer scripts, hook shell scripts

**Secondary:**
- HTML + Jinja2 - catalog page templates (`pipeline/templates/`)
- JSON - config files, workflow schemas, capability graph artifacts

## Runtime

**Environment:**
- Python 3 (stdlib only, plus `jinja2`) for the pipeline
- Node.js >= 18 (declared in `package.json` engines field) for JS hooks
- Docker Compose for `training-stack/` sub-project only

**Package Manager:**
- npm (Node) - `package.json` present, `node_modules/` present; no lockfile committed
- pip (Python) - `pipeline/requirements.txt` (single dep: `jinja2>=3.1.0`)

## Frameworks

**Pipeline:**
- Jinja2 >= 3.1.0 - HTML and Markdown templating for catalog page generation (`pipeline/pipeline.py`, `pipeline/build_capability_graph.py`)

**Testing:**
- pytest - invoked via `python3 -m pytest tests/` (declared in `package.json` scripts)

**Build/Dev:**
- No build step for the pipeline or hooks; all scripts run directly
- `install.sh` copies skill files into `~/.claude/skills/`

## Key Dependencies

**Pipeline (Python):**
- `jinja2` - only third-party Python dependency; used to render catalog HTML and Markdown reports

**Hooks (Node.js):**
- `puppeteer` - present in `node_modules/` (likely for scraping or screenshot tasks)
- `yargs` - CLI argument parsing
- `zod` - schema validation
- `js-yaml` - YAML parsing
- `proxy-agent` - HTTP proxy support

**External CLI tools (must be installed separately):**
- `firecrawl` CLI - web search for repo discovery (`pipeline/discover_candidates.py`)
- `gh` CLI (GitHub CLI) - GitHub API calls for repo metadata (`pipeline/discover_candidates.py`)
- `python3` - checked at install time by `adapters/claude/install.sh`

## Configuration

**Environment:**
- No `.env` file in repo; env vars injected at runtime by Claude Code (`CLAUDE_PROJECT_DIR`)
- `training-stack/docker-compose.yml` uses `OPENAI_API_BASE`, `OPENAI_API_KEY`, `MODEL_NAME` for medagentsim service

**Build:**
- `pipeline/requirements.txt` - Python deps
- `package.json` - Node metadata and npm scripts
- `.claude/settings.local.json` - Claude Code hook wiring (project-local, committed)
- `adapters/claude/models.json` - Claude model role assignments per workflow
- `adapters/codex/models.json` - Codex model role assignments per workflow

## Platform Requirements

**Development:**
- Python >= 3.9
- Node.js >= 18
- `firecrawl` CLI on PATH (for discovery)
- `gh` CLI on PATH and authenticated (for GitHub API calls)
- Claude Code (for hook-driven workflows)

**Production:**
- `training-stack/`: Docker Compose; services run nginx:alpine, ollama/ollama, python:3.11-slim
- Catalog HTML: static files, no server required

---

*Stack analysis: 2026-03-27*
