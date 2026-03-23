# Multi-Agent Swarm Discovery → Catalog Pipeline

**Date**: 2026-03-22
**First application**: Telecom simulator discovery (Open Telco project)
**Status**: Pattern validated, failure modes documented, deterministic rebuild pipeline implemented

---

## Executive Summary

On March 22, 2026, we ran an end-to-end experiment: use Claude Code's multi-agent orchestration (TeamCreate) to discover, catalog, and score every open-source Docker-based telecom simulator on earth. The pipeline worked in two phases — **swarm discovery** (23 parallel agents using Firecrawl to search GitHub) and **catalog synthesis** (merging raw results into a scored, deduplicated catalog).

**Results**: 23 agents across 2 swarms discovered **876 raw repositories** across 23 domain-specific JSON files. The discovery phase worked exceptionally well — parallel LLM agents are great at breadth-first web research.

**Failure**: The synthesis phase failed. An LLM agent tasked with deduplicating 813 JSON objects silently dropped 73 repositories (including industry-standard tools like Netopeer2, pyang, ncclient) while confidently reporting success. The root cause was LLM context saturation at ~100K tokens — the agent resorted to fuzzy name matching instead of exact URL lookups.

**Fix**: A deterministic Python pipeline replaced the LLM synthesizer. URL normalization + set-based lookups recovered all lost data. The final catalog: **528 unique repositories**, scored 0-10, with capability tags and Docker metadata.

**Takeaway**: LLM agents excel at discovery (fuzzy, creative, parallel). They fail at synthesis (deterministic, exact, large-scale data merging). The reusable pattern is: **LLM swarm for discovery → deterministic pipeline for catalog creation**.

---

## 1. The Problem

We wanted to find every open-source simulator that could serve as an agentic scaffolding environment for AI evaluations. Starting knowledge: Open5GS, Free5GC, Kathara, Containerlab. Suspected there were hundreds more across dozens of sub-domains.

**Requirements**:
- Discover repos across a broad domain taxonomy (not just what we already know)
- Capture rich metadata: Docker support, protocols, capabilities, GitHub metrics
- Deduplicate across agents (the same repo appears in multiple domains)
- Score and classify for downstream use (which repos are ready for eval scaffolding?)
- Produce a single, clean JSON catalog

**Why multi-agent**: No single search query covers "5G core simulators" AND "YANG validation tools" AND "traffic generators" AND "satellite NTN emulators." Each sub-domain has its own terminology, GitHub organizations, and discovery paths. Parallel specialists outperform a single generalist.

---

## 2. Architecture: The Swarm Discovery Pattern

### 2.1 Domain Decomposition

The first design decision is splitting the search space into non-overlapping (or minimally overlapping) domains. Each domain gets a dedicated agent.

**Swarm 1** — 13 agents across 12 telecom domains + 1 awesome-lists crawler:

| # | Domain | Agent Focus | Repos Found |
|---|--------|------------|-------------|
| 1 | 5g-core | Open5GS, Free5GC, Magma, OAI CN | 40 |
| 2 | ran-ue | srsRAN, UERANSIM, OAI RAN | ~30 |
| 3 | oran-ric | O-RAN SC, FlexRIC, SD-RAN | 49 |
| 4 | transport | FRRouting, Containerlab, GoBGP | ~35 |
| 5 | sdn-nfv | ONOS, OpenDaylight, Open vSwitch | 41 |
| 6 | monitoring | Prometheus, Zabbix, HOMER | 59 |
| 7 | signaling | Kamailio, FreeSWITCH, HOMER | 24 |
| 8 | traffic-gen | TRex, iperf, hping3 | ~25 |
| 9 | ntn-satellite | OpenSAND, GNURadio | 20 |
| 10 | digital-twin | Eclipse Ditto, FIWARE | ~30 |
| 11 | 6g-research | Sionna, NextGCore, TeraSim | 20 |
| 12 | edge-mec | Akraino, StarlingX | ~25 |
| 13 | awesome-lists | Curated list crawling | ~70 |
| | **Total raw** | | **467** |
| | **After dedup** | | **404 unique** |

**Swarm 2** — 10 agents for a domain blind spot (network configuration management):

| # | Sub-domain | Repos Found |
|---|-----------|-------------|
| 1 | netconf-servers | 30 |
| 2 | yang-tooling | ~25 |
| 3 | restconf-gnmi | ~20 |
| 4 | netauto-frameworks | ~25 |
| 5 | virtual-nos | ~20 |
| 6 | config-compliance | 23 |
| 7 | config-labs | ~20 |
| 8 | config-modeling | ~25 |
| 9 | netconf-testing | ~25 |
| 10 | snmp-config | 48 |
| | **Total raw** | **409** |

**Combined**: 876 raw entries across 23 JSON files.

### 2.2 Agent Execution Pattern

Each agent followed an identical workflow:

```
1. firecrawl-search: 8-10 targeted GitHub searches per domain
2. firecrawl-scrape: Validate each result (README, Docker support, activity)
3. Snowball: Follow "related projects" links 1-hop deep
4. Output: Structured JSON with standardized schema
```

**TeamCreate configuration**: All 13 (or 10) agents launched in parallel via TeamCreate. A synthesizer task was created with `blockedBy` dependencies on all discovery tasks, forming a DAG: parallel discovery → sequential synthesis.

**Budget**: ~104 firecrawl-search calls + 390-650 firecrawl-scrape calls per swarm.

### 2.3 Output Schema (Per Agent)

Each agent produced a JSON file with this structure per repository:

```json
{
  "name": "open5gs",
  "repo_url": "https://github.com/open5gs/open5gs",
  "description": "Open5GS is a C-language implementation of 5G Core and EPC",
  "sub_domain": "5g-core",
  "docker_support": {
    "has_dockerfile": true,
    "has_compose": true,
    "compose_services_count": 19,
    "docker_evidence": "docker compose -f docker/docker-compose.yml up"
  },
  "github_metrics": {
    "stars": 1200,
    "language": "C",
    "last_commit": "2026-03-15"
  },
  "protocols": ["5G NR", "NAS", "NGAP", "PFCP", "GTP-U"],
  "eval_potential_score": 10,
  "eval_scaffolding_compatibility": "inspect-ai-sandbox",
  "eval_notes": "Production-grade 5G core with 19+ deployment scenarios"
}
```

---

## 3. Timeline: What Actually Happened

### Phase 1: Design (1:02 PM - 1:25 PM)

| Time | Action |
|------|--------|
| 1:02 PM | User invokes `/brainstorming` with the swarm discovery idea |
| 1:11 PM | Explore agent catalogs existing infrastructure (4 known simulators) |
| 1:16 PM | Scope refinement: focus on 5G/6G network engineering |
| 1:20 PM | Swarm design document created — 13 domains, standardized schema |
| 1:25 PM | User invokes `/executing-plans` to begin |

### Phase 2: Infrastructure Setup (1:26 PM - 1:28 PM)

| Time | Action |
|------|--------|
| 1:26 PM | `telecom-simulators/discovery/` directory created |
| 1:26 PM | `telecom-sim-swarm` team created via TeamCreate |
| 1:27 PM | 14 tasks created (13 discovery + 1 synthesizer) |
| 1:28 PM | Dependencies configured: synthesizer blocked by all 13 agents |

### Phase 3: First Swarm Execution (1:29 PM - 1:50 PM)

All 13 agents ran in parallel. Discovery highlights:
- **1:39 PM**: 6G research agent finds 8 cutting-edge platforms (NextGCore, Sionna, TeraSim)
- **1:42 PM**: Discovers `agentic-ai-future-factory` — itself an agentic AI platform for 6G xApp orchestration
- **1:44 PM**: 6G research catalog completed (20 repos, 6 sub-domains)
- **1:46 PM**: Signaling inventory completed (24 tools — Kamailio 2.8k stars, FreeSWITCH 4.7k stars)
- **1:50 PM**: First swarm complete. **467 raw → 404 unique repos** in catalog.json

### Phase 4: Blind Spot Discovery (1:53 PM)

**Critical gap identified**: The 12-domain taxonomy had no coverage for network configuration management. NETCONF servers (Netopeer2), YANG tools (pyang), RESTCONF APIs — all fell between monitoring (telemetry-focused), SDN (OpenFlow-focused), and signaling (Diameter/GTP-focused).

**Decision**: Run a second focused swarm with 10 agents for the `netconf-mgmt` domain.

### Phase 5: Second Swarm Execution (1:54 PM - 2:04 PM)

| Time | Discovery |
|------|-----------|
| 1:54 PM | Netopeer2 confirmed — THE reference NETCONF server, plus Docker Hub image |
| 1:55 PM | Robot Framework NETCONF tools, YANG validation suites |
| 1:56 PM | Python automation frameworks (Nautobot, Nornir, netwarden) |
| 1:57 PM | Cisco pyATS test automation, hier_config remediation |
| 1:58 PM | NETCONF test harnesses, network automation labs |
| 1:59 PM | Comprehensive NETCONF catalog: 30 servers/simulators |
| 2:04 PM | **10 JSON files totaling 9,793 lines** completed |

**Combined total**: 876 raw repositories across 23 discovery files.

### Phase 6: Synthesizer Deployment and Failure (2:06 PM - 2:47 PM)

**2:06 PM** — Deployed `mgmt-synthesizer` agent (claude-opus-4-6, bypassPermissions) with a 7-step merge workflow:
1. Read existing catalog (404 repos, 14,384 lines)
2. Read 10 new discovery files (409 repos, 9,793 lines)
3. Deduplicate via URL normalization
4. Score new repos 0-10 across 5 dimensions
5. Classify scaffolding compatibility
6. Write merged catalog
7. Report metrics

**What it reported**: "409 → 58 unique after intra-dedup, 7 existing enriched, 51 new added"

**What actually happened**: It dropped 73 repositories silently. The 51 should have been 73+7=80. Notable losses:

| Repository | Why It Matters |
|-----------|----------------|
| Netopeer2 (CESNET) | THE reference NETCONF server — found in 5 discovery files |
| sysrepo | YANG datastore backend — found in 4 files |
| pyang (2.1k stars) | THE YANG validator |
| ncclient | THE Python NETCONF client |
| Cisco YANG Suite | Full YANG development environment |
| libyang | C YANG parser library |
| ygot | OpenConfig Go YANG tools |
| notconf | Best lightweight NETCONF simulator |
| ...and 65 more | Network management essentials |

### Phase 7: Root Cause Analysis

The synthesizer processed **~100K+ tokens** of structured JSON containing **813 repository objects**. Four failure modes:

1. **Context saturation**: 813 JSON objects exceeded reliable LLM tracking capacity. The agent couldn't accurately scan all 404 existing URLs while processing 58 new candidates.

2. **Fuzzy matching instead of exact lookups**: The agent "recognized" repo names (Netopeer2, sysrepo, pyang) and assumed they were already in the catalog without doing exact URL comparison. They weren't — swarm 1 never searched for them.

3. **No verification step**: No output count vs input count check. A simple `len(output) >= len(existing) + len(new)` assertion would have caught the loss immediately.

4. **Confident false reporting**: The agent reported success with plausible metrics ("51 new repos added, 7 enriched") — no error, no warning, no uncertainty signal.

### Phase 8: Deterministic Recovery (2:47 PM - 3:36 PM)

**Decision**: Abandon LLM-based synthesis entirely. Rebuild from raw data using Python.

A deterministic Python script recovered the lost data:
```python
# URL normalization
def normalize(url):
    return url.lower().rstrip('/').removesuffix('.git')

# O(1) exact lookup
existing_urls = {normalize(r['repo_url']) for r in catalog}

# Find every missing repo
missing = [r for r in new_repos if normalize(r['repo_url']) not in existing_urls]
# Result: 73 missing (not 0 as the agent claimed)
```

**Full 4-stage rebuild pipeline** implemented at `scripts/rebuild_catalog/`:

| Stage | Purpose | Implementation |
|-------|---------|---------------|
| Stage 1: Dedup | 876 → ~500 unique | URL normalization, merge-by-richest-metadata |
| Stage 2: Prune | Remove low-quality entries | Hard cuts (no URL, no Docker) + soft cuts (score threshold) |
| Stage 3: Enrich | Add capability tags, scores | Anthropic Batch API (Haiku) — 166 entries, 100% success |
| Stage 4: Finalize | Domain clustering, schema validation | JSON schema enforcement, field normalization |

**Stage 3 debugging cycle** (instructive for reuse):
- First batch: 0% parse rate — Claude wrapped JSON responses in markdown code fences (`` ```json ... ``` ``)
- Fix: Strip markdown fences → 92% parse rate
- Remaining 13 failures: truncated JSON from `max_tokens=300`
- Fix: Increase to `max_tokens=1024` → **100% parse rate, zero failures**

### Phase 9: HTML Explorer and Delivery (3:48 PM - 4:00 PM)

- User: *"let me see it, make an interactive html"*
- Built `data/catalog_explorer.html` — self-contained viewer with 166 repos embedded as inline JSON (~191KB)
- Bug: duplicate `const DATA` declaration (old empty init + new inline data) → caught via Puppeteer screenshot automation
- User: *"perfect, commit and push that catalog, you did a great job"*

---

## 4. What Worked

### Parallel LLM Discovery

23 agents running in parallel discovered **876 repositories** across **23 sub-domains** in under 30 minutes. Key strengths:

- **Breadth**: Each agent specialized in domain terminology ("NETCONF server docker" vs "5G core simulator" vs "YANG validation tool") — searches no single agent would generate
- **Snowball effect**: Agents followed "related projects" links, discovering repos not in any search results
- **Redundant coverage**: The same important repo (e.g., Netopeer2) was found by 5 different agents — redundancy protected against any single agent missing it
- **Rich metadata**: Agents scraped READMEs, Docker evidence, GitHub metrics — not just URLs

### TeamCreate Orchestration

The DAG pattern (13 parallel → 1 sequential) worked perfectly for the discovery phase:
- Tasks with explicit `blockedBy` dependencies
- Team configuration with agent specs and tool access
- bypassPermissions mode for autonomous execution

### Domain Decomposition

Splitting "telecom simulators" into 12 sub-domains (then adding a 13th) produced far better coverage than a flat search would have. The blind spot discovery (no netconf-mgmt domain) was caught by reviewing results — leading to a targeted second swarm of 10 additional agents.

---

## 5. What Failed

### LLM Synthesis at Scale

**The core lesson**: LLM agents cannot reliably perform deterministic data processing at scale.

When processing ~100K tokens of structured JSON (813 objects), the LLM:
- Used **fuzzy name matching** instead of exact URL lookups
- **Silently dropped data** (73 repos) while reporting success
- Produced **plausible but wrong metrics** ("51 added" vs actual 73 needed)
- Gave **no uncertainty signal** — it didn't say "I might have missed some"

This is not a model capability issue — it's a fundamental mismatch between task type and tool. Deduplication is a deterministic operation. Set membership, URL normalization, and merge logic require exact computation, not probabilistic inference.

### Taxonomy Gaps

The initial 12-domain taxonomy had a management-plane blind spot. This is inherent to any decomposition — you can't search for what you don't know exists. The mitigation is:
1. Review first swarm results for gaps
2. Run targeted follow-up swarms for missing domains
3. Include an "awesome-lists" crawler as a catch-all agent

### Schema Divergence

Swarm 1 and Swarm 2 agents used different schemas (`repo_url` vs `github_repo`/`github_url`, `sub_domain` vs `sub_domains`). This made merging harder. Mitigation: enforce a shared JSON schema across all agents.

---

## 6. The Reusable Pattern

This architecture generalizes beyond telecoms. Replace the domain taxonomy and search terms, keep the pipeline.

### Step 1: Domain Decomposition

Split your target space into 10-15 non-overlapping sub-domains. Each gets a discovery agent.

**Example for security tools**:
| Domain | Search Terms |
|--------|-------------|
| web-scanners | OWASP ZAP, Nuclei, Burp alternatives |
| network-security | Suricata, Zeek, Snort |
| container-security | Trivy, Falco, Aqua |
| sast-dast | Semgrep, CodeQL, Bandit |
| ... | ... |

### Step 2: Swarm Discovery (LLM agents)

```
TeamCreate:
  - N discovery agents (parallel, each with firecrawl tools)
  - 1 synthesizer task (blockedBy all discovery agents)
  - Standardized JSON output schema (enforced)
  - Budget: ~10 searches + ~30 scrapes per agent
```

Each agent runs the same loop: search → validate → snowball → output JSON.

### Step 3: Gap Review

After swarm 1 completes, manually review results for missing sub-domains. Run targeted follow-up swarms as needed. Budget ~20% extra for gap-filling.

### Step 4: Deterministic Catalog Pipeline (Python, NOT LLM)

```
raw-discovery.json (all swarm outputs concatenated)
    │
    ├── Stage 1: Dedup (URL normalization + set lookups)
    ├── Stage 2: Prune (hard cuts: no URL/no Docker; soft cuts: score threshold)
    ├── Stage 3: Enrich (Batch API for capability tags — max_tokens >= 1024)
    └── Stage 4: Finalize (schema validation, domain clustering)
    │
    ▼
catalog.json (clean, scored, tagged)
```

**Critical**: Stage 1-2 and Stage 4 MUST be deterministic Python. Stage 3 can use LLM (Batch API) because it processes one repo at a time — no cross-referencing, no dedup, no merging.

### Step 5: Delivery

Build an HTML explorer for human review. Embed the catalog as inline JSON for a self-contained file.

---

## 7. Failure Modes and Mitigations

| Failure Mode | Where It Hits | Mitigation |
|-------------|--------------|------------|
| Context saturation | LLM synthesis of large JSON | Use deterministic Python for any operation touching >100 objects |
| Fuzzy matching | LLM dedup/merge | URL normalization + set-based exact lookups |
| Silent data loss | LLM reporting | Input/output count assertions at every pipeline stage |
| Confident false metrics | LLM synthesis | Never trust LLM-reported counts — verify programmatically |
| Taxonomy blind spots | Domain decomposition | Review pass after swarm 1 + awesome-lists catch-all agent |
| Schema divergence | Multi-swarm merges | Enforce shared JSON schema with validation before agents run |
| Batch API code fences | Stage 3 enrichment | Strip markdown fences from LLM responses |
| Token truncation | Stage 3 enrichment | Set max_tokens >= 1024 (not 300) |
| Duplicate declarations | HTML embedding | Puppeteer-based automated testing of generated artifacts |

---

## 8. Key Numbers

| Metric | Value |
|--------|-------|
| Total discovery agents | 23 (13 + 10) |
| Raw repositories found | 876 |
| Discovery time | ~30 minutes per swarm |
| Unique after dedup | 528 |
| Repos silently dropped by LLM synthesizer | 73 |
| Repos recovered by Python script | 73 (100%) |
| Batch API enrichment success rate | 100% (after two bug fixes) |
| Final curated catalog | 166 entries (after pruning) |
| Top-scored repos (8+) | 44 |
| Perfect-score repos (10) | 6 (Eclipse Ditto, Magma, Open5GS, Zabbix, docker_open5gs, free5GC) |
| Firecrawl budget per swarm | ~100 searches + ~400 scrapes |

---

## 9. Files Produced

### Discovery Layer
- `telecom-simulators/discovery/*.json` — 13 domain files from swarm 1
- `telecom-simulators/discovery/netconf-mgmt/*.json` — 10 domain files from swarm 2
- `task-designer/raw-discovery.json` — 876 raw entries (ground truth)

### Pipeline Layer
- `scripts/rebuild_catalog/` — 4-stage deterministic Python pipeline
  - `stage1_dedup.py` — URL normalization + merge-by-richest
  - `stage2_prune.py` — Hard/soft quality cuts
  - `stage3_enrich.py` — Anthropic Batch API enrichment
  - `__main__.py` — CLI entry point

### Catalog Layer
- `data/catalog.json` — 166 curated, scored, tagged repositories
- `data/catalog_compact.json` — Compacted for HTML embedding (~191KB)
- `data/catalog_explorer.html` — Self-contained interactive viewer
- `data/enriched.json` — Stage 3 output with capability tags

### Documentation Layer
- `docs/plans/2026-03-22-telecom-simulator-swarm-design.md` — Architecture
- `docs/plans/2026-03-22-telecom-simulator-swarm-plan.md` — Execution plan
- `docs/plans/2026-03-22-catalog-rebuild-design.md` — Python pipeline design
- `task-designer/synthesizer_mistake.md` — Original failure report (superseded by this document)

---

## 10. Applying This to a New Domain

To run this pipeline for a different domain (e.g., "every open-source ML training framework with Docker support"):

1. **Decompose**: Split "ML training" into sub-domains (distributed training, hyperparameter tuning, experiment tracking, model serving, data pipelines, etc.)
2. **Design agents**: One per sub-domain, each with 8-10 firecrawl-search queries
3. **Run swarm**: TeamCreate with N parallel agents + 1 post-processing task
4. **Review gaps**: Check results for missing sub-domains, run follow-up swarm
5. **Concat raw data**: Merge all agent JSON outputs into `raw-discovery.json`
6. **Run deterministic pipeline**: `python -m rebuild_catalog raw-discovery.json --output catalog.json`
7. **Enrich via Batch API**: Add capability tags, scores (one-at-a-time, not batch merge)
8. **Build HTML explorer**: Embed catalog inline for self-contained viewer

**Time estimate**: ~2 hours end-to-end (design: 30min, swarm: 30min, gap review: 15min, pipeline: 30min, delivery: 15min).

**Cost estimate**: ~$5-15 in API calls depending on domain breadth and scrape depth.
