# Next Steps: Virality & Utility Roadmap

## Current state

- 5 domains live (cybersecurity, gaming, trading, telecoms, geopolitics in progress)
- 1,128 repos cataloged, 1,128 detail pages with graph visualization
- Dual-platform: Claude Code (full orchestration) + Codex (discovery running)
- 0 stars, 0 forks — no external distribution yet
- Not hosted anywhere — catalogs only viewable by cloning the repo

## Priority order

Impact is scored on two axes: **virality** (does it bring new people?) and **utility** (does it make the product better for existing users?).

| # | Action | Virality | Utility | Effort |
|---|--------|----------|---------|--------|
| 1 | Host on GitHub Pages | High | Medium | 1 day |
| 2 | Screenshot + GIF in README | High | None | 2 hours |
| 3 | Search engine (`search.py`) | Low | High | 2-3 days |
| 4 | Scale to 10 domains (launch batch) | High | High | 1 week |
| 5 | Staggered weekly domain launches | High | Medium | Ongoing |
| 6 | Routing skill (`/everything-on-earth`) | Low | High | 2-3 days |
| 7 | Freshness: scheduled re-crawl | Low | High | 2-3 days |
| 8 | Multi-platform CLI installer | Medium | Medium | 1 week |

---

## 1. Host on GitHub Pages

**Why first:** Every other distribution action (Reddit posts, HN, tweets) needs a link that works in a browser. Right now there is nothing to link to.

**What to do:**
- Enable GitHub Pages on the repo (Settings > Pages > Deploy from branch)
- Point it at the root — `index.html` already exists and links to all domain catalogs
- All `catalog/<domain>/index.html` and `catalog/<domain>/detail/*.html` work as static files
- No build step needed — it's already plain HTML

**Done when:** `https://eaguaida.github.io/everything-on-earth/` loads the landing page and all domain graphs work.

---

## 2. Screenshot + GIF in README

**Why:** The graph visualization is the single most visually impressive thing in this project. Nobody sees it today. A repo without screenshots converts at a fraction of one with them.

**What to do:**
- Capture one screenshot of the cybersecurity knowledge graph (most nodes, most impressive)
- Capture one GIF showing: landing page → click domain → graph loads → hover on node → click through to detail page
- Add both to `assets/` and reference in `README.md`
- Place them right after the tagline, before "Getting Started"

**Done when:** Opening the GitHub repo shows the graph visualization without scrolling.

---

## 3. Search engine (`search.py`)

**Why:** Turns 5,000+ repos in JSON files into queryable intelligence. This is the foundation for the routing skill, the multi-platform story, and the "Claude that knows every tool" pitch.

**What to build:**
```
pipeline/search.py

Inputs:
  python3 pipeline/search.py "container security" --domain cybersecurity --top 10
  python3 pipeline/search.py "reinforcement learning" --domain trading --top 10
  python3 pipeline/search.py "kubernetes" --all --top 10
  python3 pipeline/search.py "SAST vs DAST" --domain cybersecurity --compare

Outputs:
  Structured text optimized for LLM context (not raw JSON dumps)
  Includes: name, repo_url, score, stars, summary, sub_domain
```

**Implementation approach:**
- BM25 ranking over `name`, `description`, `summary`, `tags`, `sub_domain` fields
- Load all `catalog/*/catalog.json` files
- No external dependencies (follow ui-ux-pro-max pattern — pure Python, stdlib only)
- `--compare` flag returns side-by-side for two tools mentioned in query
- `--sort` flag: `score` (default), `stars`, `name`, `activity`

**Done when:** Claude can call `search.py` and get ranked results from any domain catalog.

---

## 4. Scale to 10 domains (launch batch)

**Why:** "Everything on Earth" with 5 domains is a stretch. With 10 it's credible. With 20 it's undeniable.

**Target domains for launch (10 total):**

| Domain | Status | Why it's in the launch batch |
|--------|--------|------------------------------|
| Cybersecurity | Done | Largest catalog, most impressive graph |
| Gaming | Done | Broad appeal |
| Trading | Done | Active niche community |
| Telecoms | Done | Enterprise credibility |
| Geopolitics | In progress | Unique — nobody else has this |
| Healthcare | Not started | Massive market, high shareability |
| Education | Not started | Broad appeal, underserved niche |
| AI/ML Tools | Not started | Largest GitHub audience |
| DevOps/Infra | Not started | Overlaps with every developer |
| Robotics | Not started | Visual, growing community |

**Done when:** 10 `catalog/<domain>/index.html` pages exist with graph visualizations and the landing page shows all 10.

---

## 5. Staggered weekly domain launches

**Why:** 20 domains = 20 independent content marketing events. Each targets a different niche community.

**Cadence:**
```
Week 0:  Launch with 10 domains
         → HN: "Every open-source tool on Earth, mapped by AI agents"
         → Twitter/X thread showing the knowledge graphs
         → r/programming, r/opensource

Week 1:  Domain 11 drops → post to its niche subreddit
Week 2:  Domain 12 drops → post to its niche subreddit
...
Week 10: Domain 20 drops → post to its niche subreddit
```

**Per-launch content:**
- Reddit post to niche community with 2-3 surprising findings from the catalog
- Screenshot of that domain's knowledge graph
- Link to the hosted page
- Brief mention: "Part of everything-on-earth — 20 domains, X,000 repos, auto-generated by AI agents"

**Done when:** All 20 domains are live with at least one community post each.

---

## 6. Routing skill (`/everything-on-earth`)

**Why:** Makes Claude "know" everything-on-earth. One entry point that routes to search, discovery, documentation, or comparison based on user intent.

**Routing logic:**
```
"what's the best X"       → search.py --domain auto --top 5 --sort score
"find tools for X"        → search.py --all --top 10
"compare X vs Y"          → search.py --compare
"catalog all X"           → /massive-crawl
"document these tools"    → /map-capabilities
"explore cybersecurity"   → list sub-domains + top tools per sub-domain
"how many domains"        → inventory summary
```

**File:** `adapters/claude/skills/everything-on-earth/SKILL.md` (Claude) + equivalent Codex wrapper

**Done when:** A user can type natural-language questions about open-source tools and get answers backed by real catalog data.

---

## 7. Freshness: scheduled re-crawl

**Why:** Catalogs decay. Star counts change, repos get archived, new tools appear. Without freshness, the search engine gives confident answers from stale data — worse than no answer.

**What to build:**
- GitHub Action on a monthly cron schedule
- For each domain: re-run the pipeline's scoring stage against the GitHub API
- Update `stars`, `last_activity`, `archived` status
- Flag repos with no activity in 12+ months as `stale`
- Commit updated `catalog.json` files automatically

**Scope:** This is NOT re-running the full discovery swarm. It's a lightweight metadata refresh hitting the GitHub API for existing repos only.

**Done when:** A monthly GitHub Action keeps star counts and activity dates current across all catalogs.

---

## 8. Multi-platform CLI installer

**Why:** Expands the audience from "Claude Code + Codex users" to "anyone using an AI coding assistant."

**What to build:**
```bash
npx everything-on-earth init
```

- Detect which AI assistant is present (steal ui-ux-pro-max's `detect.ts` pattern)
- Install platform-specific skill files
- Download latest `catalog.json` files from GitHub releases
- For Claude/Codex: install full skills (search + discover + document)
- For Cursor/Windsurf/others: install search-only skill (read side, not write side)

**Platform support tiers:**

| Tier | Platforms | What they get |
|------|-----------|---------------|
| Full | Claude Code, Codex | Search + discover + document + routing |
| Read | Cursor, Windsurf, Copilot, Kiro, others | Search + browse catalogs |

**Done when:** `npx everything-on-earth init` works on Claude Code, Codex, and at least 2 other platforms.

---

## Sequencing

```
Week 1:  [1] Host on GitHub Pages + [2] README screenshots
         (Unblocks all distribution)

Week 1:  [3] Build search.py in parallel
         (Unblocks routing skill and multi-platform)

Week 2:  [4] Scale to 10 domains
         (Unblocks launch)

Week 3:  Launch week — post to HN + broad communities
         [5] Begin weekly domain drops

Week 4+: [6] Routing skill + [7] Freshness cron
         (Product depth while weekly drops drive top-of-funnel)

Week 6+: [8] Multi-platform CLI
         (Expand audience after proving traction)
```

## Key constraint

Do not let the multi-platform architecture become a month-long yak shave before launching. The biggest leverage right now is: host the site, show the graphs, post to communities. The routing layer and CLI make power users happy; the hosted site makes the top of the funnel work. Ship distribution first, depth second.
