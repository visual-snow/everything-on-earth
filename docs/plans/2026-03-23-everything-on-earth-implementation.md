# everything-on-earth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude Code plugin that discovers every open-source repo for any topic using a TeamCreate agent swarm and a deterministic Python synthesis pipeline.

**Architecture:** Skill (SKILL.md) orchestrates 3 Haiku scouts → interactive brainstorm → TeamCreate swarm of 6-8 Sonnet agents → deterministic `pipeline.py` (dedup/prune/enrich/finalize). Six hooks enforce deterministic guarantees. No LLM touches data >100 objects.

**Tech Stack:** Python 3.9+ (pipeline), Node 18+ (hooks), Bash (hooks), Jinja2 (templates), Anthropic Batch API (enrichment), Firecrawl CLI (search/scrape)

**Design Doc:** `docs/plans/2026-03-23-everything-on-earth-design.md`

**Working Directory:** `/Users/emolero/Documents/GitHub/ot/everything-on-earth/`

---

## Phase 1: Schema & Skeleton

### Task 1.1: Create folder structure

**Files:**
- Create: `skill/references/` (directory)
- Create: `hooks/` (directory)
- Create: `pipeline/templates/` (directory)
- Create: `examples/` (directory)
- Create: `tests/` (directory)
- Create: `tests/fixtures/` (directory)

**Step 1: Create all directories**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
mkdir -p skill/references hooks pipeline/templates examples tests/fixtures
```

**Step 2: Verify structure**

```bash
find . -type d -not -path './.git*' | sort
```

Expected:
```
.
./docs
./docs/plans
./examples
./hooks
./pipeline
./pipeline/templates
./skill
./skill/references
./tests
./tests/fixtures
```

**Step 3: Commit**

```bash
git add -A
git commit -m "scaffold: create folder structure for skill, hooks, pipeline, examples, tests"
```

---

### Task 1.2: Create output-schema.json

This is the universal contract. Every agent writes entries matching this schema. The pipeline validates against it. The hooks check for required fields.

**Files:**
- Create: `skill/references/output-schema.json`

**Step 1: Write the schema**

The schema is a generalized version of the telecom catalog format (see `task-designer/catalog.json` in the parent repo). Fields specific to telecom (protocols, docker_support) are replaced with generic metadata.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "everything-on-earth discovery entry",
  "description": "Schema for a single repository entry discovered by an agent",
  "type": "object",
  "required": ["repo_url", "name", "description", "sub_domain", "score"],
  "properties": {
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "Canonical GitHub/GitLab URL (lowercase, no trailing slash, no .git suffix)"
    },
    "name": {
      "type": "string",
      "description": "Repository name (owner/repo format preferred)"
    },
    "description": {
      "type": "string",
      "minLength": 10,
      "description": "What this repo does in 1-2 sentences"
    },
    "sub_domain": {
      "type": "string",
      "description": "Which sub-domain task discovered this repo (matches sub_domain.id in swarm-config)"
    },
    "score": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10,
      "description": "Relevance score: 0=tangential, 5=relevant, 10=essential"
    },
    "score_rationale": {
      "type": "string",
      "description": "1-sentence justification for the score"
    },
    "stars": {
      "type": ["integer", "null"],
      "description": "GitHub/GitLab star count at discovery time"
    },
    "language": {
      "type": ["string", "null"],
      "description": "Primary programming language"
    },
    "license": {
      "type": ["string", "null"],
      "description": "SPDX license identifier"
    },
    "last_activity": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Last commit or release date (YYYY-MM-DD)"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Added during enrichment stage — normalized topic tags"
    },
    "category": {
      "type": ["string", "null"],
      "description": "Added during enrichment stage — human-readable category"
    },
    "summary": {
      "type": ["string", "null"],
      "description": "Added during enrichment stage — one-line summary"
    },
    "found_in_domains": {
      "type": "array",
      "items": { "type": "string" },
      "description": "All sub-domains that discovered this repo (populated during dedup)"
    }
  },
  "additionalProperties": false
}
```

**Step 2: Validate schema is valid JSON Schema**

```bash
python3 -c "
import json
with open('skill/references/output-schema.json') as f:
    schema = json.load(f)
assert schema['type'] == 'object'
assert 'repo_url' in schema['required']
print(f'Valid schema with {len(schema[\"properties\"])} properties, {len(schema[\"required\"])} required')
"
```

Expected: `Valid schema with 14 properties, 5 required`

**Step 3: Commit**

```bash
git add skill/references/output-schema.json
git commit -m "feat: add output-schema.json — universal contract for discovery entries"
```

---

### Task 1.3: Create agent-prompt-template.md

This is the prompt injected into every teammate by the SubagentStart hook. It tells agents exactly how to search, score, and write results.

**Files:**
- Create: `skill/references/agent-prompt-template.md`

**Step 1: Write the template**

```markdown
# Discovery Agent Instructions

You are a discovery agent in an everything-on-earth swarm. Your job: find every relevant open-source repo for your assigned sub-domain.

## Your Workflow

1. **Claim a task** from `TaskList()` — pick one with status "pending"
2. **Mark it in-progress**: `TaskUpdate(taskId, { status: "in_progress" })`
3. **Read seed queries** from the task metadata
4. **Search**: Run `firecrawl-search` for each seed query (budget: 10 searches per task)
5. **Scrape**: For promising results, run `firecrawl-scrape` to get full README/description (budget: 30 scrapes per task)
6. **Score each repo** 0-10 with a 1-sentence rationale
7. **Write results** to `discovery/{sub-domain-id}.json` as a JSON array matching the output schema
8. **Mark task complete**: `TaskUpdate(taskId, { status: "completed" })`
9. **Claim next task** or go idle if none remain

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 9-10 | Essential — industry-standard tool, widely used, actively maintained |
| 7-8 | Strong — solid tool, good community, clear purpose |
| 5-6 | Relevant — useful but niche, less active, or limited scope |
| 3-4 | Marginal — tangentially related, proof-of-concept, or abandoned |
| 1-2 | Weak — barely related, broken, or superseded |
| 0 | Not relevant — do not include in output |

## Output Format

Write a JSON array to `discovery/{sub-domain-id}.json`. Each entry MUST have these fields:

```json
{
  "repo_url": "https://github.com/owner/repo",
  "name": "owner/repo",
  "description": "What it does in 1-2 sentences",
  "sub_domain": "the-sub-domain-id",
  "score": 8,
  "score_rationale": "Why this score",
  "stars": 1234,
  "language": "Python",
  "license": "MIT",
  "last_activity": "2025-06-15"
}
```

Fields `tags`, `category`, `summary`, and `found_in_domains` are added later by the pipeline — do NOT include them.

## Rules

- **Be thorough.** Use ALL seed queries. Look beyond the first page of results.
- **Be precise.** Use the exact `repo_url` from GitHub/GitLab. No guessing URLs.
- **No duplicates** within your own output file. Dedup across agents happens later.
- **No score 0 repos** in your output. Only include repos scoring >= 1.
- **Budget awareness.** You have 10 searches and 30 scrapes per task. Use them wisely.
- **Do NOT create repos that don't exist.** If a search returns no results, move on.
```

**Step 2: Verify file length (must stay under reference budget)**

```bash
wc -l skill/references/agent-prompt-template.md
```

Expected: ~55-65 lines (well under the budget for hook injection)

**Step 3: Commit**

```bash
git add skill/references/agent-prompt-template.md
git commit -m "feat: add agent-prompt-template.md — injected into teammates by SubagentStart hook"
```

---

### Task 1.4: Create swarm-config.example.json

The config contract with a realistic example topic. Hooks read from this file at runtime.

**Files:**
- Create: `examples/swarm-config.example.json`

**Step 1: Write the example config**

Use the Kubernetes security example from the design doc:

```json
{
  "topic": "Kubernetes Security Tools",
  "constraints": {
    "min_stars": 20,
    "active_since": "2023-01-01",
    "languages": null
  },
  "sub_domains": [
    {
      "id": "network-policy",
      "name": "Network Policy & Service Mesh Security",
      "seed_queries": [
        "kubernetes network policy tool open source",
        "k8s CNI security github",
        "calico network policy engine",
        "cilium network security kubernetes",
        "k8s ingress firewall open source",
        "service mesh security istio linkerd",
        "kubernetes microsegmentation tool",
        "k8s pod network isolation github",
        "kubernetes egress policy controller",
        "network policy editor kubernetes open source"
      ]
    },
    {
      "id": "rbac-access-control",
      "name": "RBAC & Access Control",
      "seed_queries": [
        "kubernetes rbac tool open source",
        "k8s access control audit github",
        "kubernetes permission management",
        "k8s service account security",
        "kubernetes role binding analyzer",
        "rbac-manager kubernetes github",
        "k8s least privilege tool",
        "kubernetes identity management",
        "k8s authentication authorization tool",
        "kubernetes policy engine opa gatekeeper"
      ]
    },
    {
      "id": "image-scanning",
      "name": "Container Image Scanning & Vulnerability Detection",
      "seed_queries": [
        "container image scanner open source",
        "kubernetes vulnerability scanner github",
        "trivy grype container security",
        "docker image CVE scanner",
        "k8s admission controller image policy",
        "container registry security scanning",
        "sbom container security tool",
        "kubernetes image signing verification",
        "container supply chain security",
        "oci image vulnerability database"
      ]
    }
  ],
  "agents": {
    "count": 8,
    "model": "sonnet",
    "budget_per_task": {
      "searches": 10,
      "scrapes": 30
    },
    "tools": ["firecrawl-search", "firecrawl-scrape", "Read", "Write", "Glob"],
    "mode": "bypassPermissions"
  },
  "tasks": {
    "per_subdomain": 1,
    "awesome_lists": 1,
    "total": "sub_domains.length + 1"
  },
  "pipeline": {
    "dedup_key": "repo_url",
    "normalize": "lowercase, strip trailing slash, remove .git suffix",
    "pruning": "interactive",
    "enrichment": "batch_api",
    "max_tokens": 1024
  },
  "output": {
    "catalog": "catalog.json",
    "explorer": "explorer.html",
    "summary": "RESULTS.md",
    "directory": "everything-on-earth-output/"
  },
  "schema_version": "2.0.0"
}
```

**Step 2: Validate JSON parses correctly**

```bash
python3 -c "
import json
with open('examples/swarm-config.example.json') as f:
    config = json.load(f)
assert len(config['sub_domains']) >= 3
assert all(len(sd['seed_queries']) >= 8 for sd in config['sub_domains'])
print(f'Valid config: {config[\"topic\"]} with {len(config[\"sub_domains\"])} sub-domains')
"
```

Expected: `Valid config: Kubernetes Security Tools with 3 sub-domains`

**Step 3: Commit**

```bash
git add examples/swarm-config.example.json
git commit -m "feat: add swarm-config.example.json — config contract with K8s security example"
```

---

## Phase 2: Pipeline

### Task 2.1: Create test fixtures

Mock data files that let us test the pipeline without running any agents or LLMs.

**Files:**
- Create: `tests/fixtures/raw-discovery.json`
- Create: `tests/fixtures/swarm-config-test.json`

**Step 1: Write mock raw-discovery.json**

Needs: duplicates (same URL, different cases), missing fields, various scores, multiple sub-domains. ~20 entries is enough to test all pipeline stages.

```json
[
  {
    "repo_url": "https://github.com/aquasecurity/trivy",
    "name": "aquasecurity/trivy",
    "description": "Find vulnerabilities, misconfigurations, secrets, SBOM in containers, Kubernetes, code repositories, clouds and more",
    "sub_domain": "image-scanning",
    "score": 10,
    "score_rationale": "Industry standard container scanner, 20k+ stars",
    "stars": 20000,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-12-01"
  },
  {
    "repo_url": "https://github.com/aquasecurity/Trivy",
    "name": "aquasecurity/trivy",
    "description": "Duplicate entry with different URL casing",
    "sub_domain": "runtime-security",
    "score": 9,
    "score_rationale": "Found again in runtime context",
    "stars": 20000,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-12-01"
  },
  {
    "repo_url": "https://github.com/aquasecurity/trivy.git",
    "name": "aquasecurity/trivy",
    "description": "Duplicate with .git suffix",
    "sub_domain": "supply-chain",
    "score": 8,
    "score_rationale": "Also relevant to supply chain",
    "stars": 20000,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-12-01"
  },
  {
    "repo_url": "https://github.com/cilium/cilium",
    "name": "cilium/cilium",
    "description": "eBPF-based networking, observability, and security for Kubernetes",
    "sub_domain": "network-policy",
    "score": 9,
    "score_rationale": "Leading eBPF CNI with strong network policy support",
    "stars": 18000,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-11-15"
  },
  {
    "repo_url": "https://github.com/open-policy-agent/gatekeeper",
    "name": "open-policy-agent/gatekeeper",
    "description": "Policy engine for Kubernetes admission control using OPA",
    "sub_domain": "rbac-access-control",
    "score": 9,
    "score_rationale": "De facto standard for K8s policy enforcement",
    "stars": 3500,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-10-20"
  },
  {
    "repo_url": "https://github.com/falcosecurity/falco/",
    "name": "falcosecurity/falco",
    "description": "Cloud-native runtime security tool for Linux and Kubernetes",
    "sub_domain": "runtime-security",
    "score": 9,
    "score_rationale": "CNCF graduated runtime security project",
    "stars": 6800,
    "language": "C++",
    "license": "Apache-2.0",
    "last_activity": "2025-11-30"
  },
  {
    "repo_url": "https://github.com/anchore/grype",
    "name": "anchore/grype",
    "description": "Vulnerability scanner for container images and filesystems",
    "sub_domain": "image-scanning",
    "score": 8,
    "score_rationale": "Strong trivy alternative, Anchore ecosystem",
    "stars": 7500,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-09-01"
  },
  {
    "repo_url": "https://github.com/someuser/abandoned-scanner",
    "name": "someuser/abandoned-scanner",
    "description": "Old security scanner, not maintained",
    "sub_domain": "image-scanning",
    "score": 2,
    "score_rationale": "Abandoned 3 years ago",
    "stars": 5,
    "language": "Python",
    "license": null,
    "last_activity": "2021-03-15"
  },
  {
    "repo_url": "https://github.com/kyverno/kyverno",
    "name": "kyverno/kyverno",
    "description": "Kubernetes native policy management — validate, mutate, generate, and clean up resources",
    "sub_domain": "rbac-access-control",
    "score": 9,
    "score_rationale": "CNCF incubating, native K8s policy engine",
    "stars": 5200,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-12-10"
  },
  {
    "repo_url": "",
    "name": "no-url-entry",
    "description": "This entry has no URL and should be pruned",
    "sub_domain": "network-policy",
    "score": 5,
    "score_rationale": "Missing URL",
    "stars": 100,
    "language": "Go",
    "license": "MIT",
    "last_activity": "2025-06-01"
  },
  {
    "repo_url": "https://github.com/kubescape/kubescape",
    "name": "kubescape/kubescape",
    "description": "Kubernetes security platform for risk analysis, compliance, and misconfig scanning",
    "sub_domain": "runtime-security",
    "score": 8,
    "score_rationale": "CNCF sandbox, comprehensive security posture",
    "stars": 9800,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-11-20"
  },
  {
    "repo_url": "https://github.com/derailed/popeye",
    "name": "derailed/popeye",
    "description": "Kubernetes cluster resource sanitizer that scans for misconfigurations",
    "sub_domain": "runtime-security",
    "score": 6,
    "score_rationale": "Useful linter but not strictly security-focused",
    "stars": 4800,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2025-08-10"
  },
  {
    "repo_url": "https://github.com/datreeio/datree",
    "name": "datreeio/datree",
    "description": "Prevent Kubernetes misconfigurations from reaching production",
    "sub_domain": "supply-chain",
    "score": 4,
    "score_rationale": "Company pivoted, OSS project less active",
    "stars": 6700,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2023-06-01"
  },
  {
    "repo_url": "https://github.com/bridgecrewio/checkov",
    "name": "bridgecrewio/checkov",
    "description": "Static analysis tool for infrastructure as code — scans Terraform, K8s, Docker, and more",
    "sub_domain": "supply-chain",
    "score": 7,
    "score_rationale": "Broad IaC scanner covering K8s manifests",
    "stars": 6500,
    "language": "Python",
    "license": "Apache-2.0",
    "last_activity": "2025-10-01"
  },
  {
    "repo_url": "https://github.com/tetratelabs/istio-security",
    "name": "tetratelabs/istio-security",
    "description": "",
    "sub_domain": "network-policy",
    "score": 5,
    "score_rationale": "Empty description should be pruned",
    "stars": 200,
    "language": "Go",
    "license": "Apache-2.0",
    "last_activity": "2024-01-01"
  }
]
```

Then write a minimal test config:

```json
{
  "topic": "Kubernetes Security Tools",
  "constraints": {
    "min_stars": 20,
    "active_since": "2023-01-01",
    "languages": null
  },
  "sub_domains": [
    { "id": "image-scanning", "name": "Image Scanning", "seed_queries": [] },
    { "id": "network-policy", "name": "Network Policy", "seed_queries": [] },
    { "id": "rbac-access-control", "name": "RBAC", "seed_queries": [] },
    { "id": "runtime-security", "name": "Runtime Security", "seed_queries": [] },
    { "id": "supply-chain", "name": "Supply Chain", "seed_queries": [] }
  ],
  "pipeline": {
    "dedup_key": "repo_url",
    "normalize": "lowercase, strip trailing slash, remove .git suffix",
    "pruning": "interactive",
    "enrichment": "batch_api",
    "max_tokens": 1024
  },
  "output": {
    "catalog": "catalog.json",
    "explorer": "explorer.html",
    "summary": "RESULTS.md",
    "directory": "test-output/"
  },
  "schema_version": "2.0.0"
}
```

**Step 2: Validate fixtures**

```bash
python3 -c "
import json
with open('tests/fixtures/raw-discovery.json') as f:
    data = json.load(f)
print(f'Fixture: {len(data)} entries')
dupes = [e for e in data if 'trivy' in e['repo_url'].lower()]
print(f'Trivy variants (should be 3): {len(dupes)}')
empty_url = [e for e in data if not e['repo_url']]
print(f'Empty URL entries (should be 1): {len(empty_url)}')
empty_desc = [e for e in data if not e['description']]
print(f'Empty description (should be 1): {len(empty_desc)}')
"
```

Expected:
```
Fixture: 15 entries
Trivy variants (should be 3): 3
Empty URL entries (should be 1): 1
Empty description (should be 1): 1
```

**Step 3: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add mock discovery data and test config for pipeline testing"
```

---

### Task 2.2: Write pipeline.py — Stage 1 (dedup)

The dedup stage is the most critical — it's what the LLM synthesizer failed at. URL normalization + set-based exact matching.

**Files:**
- Create: `pipeline/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test for dedup**

```python
"""Tests for the everything-on-earth deterministic pipeline."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from pipeline import normalize_url, run_dedup


def test_normalize_url_lowercase():
    assert normalize_url("https://github.com/Aqua/Trivy") == "https://github.com/aqua/trivy"


def test_normalize_url_strip_trailing_slash():
    assert normalize_url("https://github.com/falco/falco/") == "https://github.com/falco/falco"


def test_normalize_url_strip_git_suffix():
    assert normalize_url("https://github.com/owner/repo.git") == "https://github.com/owner/repo"


def test_normalize_url_all_at_once():
    assert normalize_url("https://github.com/Owner/Repo.git/") == "https://github.com/owner/repo"


def test_dedup_keeps_highest_score():
    entries = [
        {"repo_url": "https://github.com/owner/repo", "name": "a", "score": 5, "sub_domain": "d1"},
        {"repo_url": "https://github.com/Owner/Repo", "name": "b", "score": 9, "sub_domain": "d2"},
        {"repo_url": "https://github.com/owner/repo.git", "name": "c", "score": 3, "sub_domain": "d3"},
    ]
    result = run_dedup(entries)
    assert len(result) == 1
    assert result[0]["score"] == 9
    assert result[0]["found_in_domains"] == ["d1", "d2", "d3"]


def test_dedup_output_not_larger_than_input():
    entries = [
        {"repo_url": f"https://github.com/owner/repo{i}", "name": f"r{i}", "score": i, "sub_domain": "d1"}
        for i in range(10)
    ]
    result = run_dedup(entries)
    assert len(result) <= len(entries)


def test_dedup_preserves_non_duplicates():
    entries = [
        {"repo_url": "https://github.com/a/one", "name": "one", "score": 5, "sub_domain": "d1"},
        {"repo_url": "https://github.com/b/two", "name": "two", "score": 7, "sub_domain": "d2"},
    ]
    result = run_dedup(entries)
    assert len(result) == 2
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
python3 -m pytest tests/test_pipeline.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline'`

**Step 3: Write dedup implementation in pipeline.py**

```python
#!/usr/bin/env python3
"""
everything-on-earth deterministic pipeline.

Four stages: dedup → prune → enrich → finalize.
Each stage reads a file, transforms it, writes a file.
No LLM touches data after discovery. All operations are exact and auditable.

Usage:
    python pipeline.py --config swarm-config.json
    python pipeline.py --config swarm-config.json --stage dedup
    python pipeline.py --config swarm-config.json --stage prune --min-score 5 --min-stars 20
"""

import argparse
import json
import sys
from pathlib import Path


def normalize_url(url: str) -> str:
    """Normalize a repo URL: lowercase, strip trailing slash, remove .git suffix."""
    url = url.strip().lower()
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    return url


def run_dedup(entries: list[dict]) -> list[dict]:
    """Deduplicate entries by normalized repo_url. Keep highest-scoring entry on collision."""
    seen: dict[str, dict] = {}
    domain_tracker: dict[str, list[str]] = {}

    for entry in entries:
        key = normalize_url(entry["repo_url"])
        if not key:
            continue

        # Track all sub-domains that found this URL
        if key not in domain_tracker:
            domain_tracker[key] = []
        sub_domain = entry.get("sub_domain", "unknown")
        if sub_domain not in domain_tracker[key]:
            domain_tracker[key].append(sub_domain)

        # Keep entry with highest score
        if key not in seen or entry.get("score", 0) > seen[key].get("score", 0):
            seen[key] = dict(entry)
            seen[key]["repo_url"] = key  # Normalize the URL in the kept entry

    # Attach found_in_domains to each surviving entry
    result = []
    for key, entry in seen.items():
        entry["found_in_domains"] = domain_tracker[key]
        result.append(entry)

    assert len(result) <= len(entries), f"Dedup expanded data: {len(result)} > {len(entries)}"
    return result


def main():
    parser = argparse.ArgumentParser(description="everything-on-earth deterministic pipeline")
    parser.add_argument("--config", required=True, help="Path to swarm-config.json")
    parser.add_argument("--stage", default="dedup,prune,enrich,finalize",
                        help="Comma-separated stages to run (default: all)")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum score for pruning")
    parser.add_argument("--min-stars", type=int, default=0, help="Minimum stars for pruning")
    parser.add_argument("--active-since", default=None, help="Minimum last_activity date (YYYY-MM-DD)")
    parser.add_argument("--input-dir", default=".", help="Directory containing input files")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: from config)")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text())
    stages = [s.strip() for s in args.stage.split(",")]
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else Path(config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    for stage in stages:
        if stage == "dedup":
            raw_path = input_dir / "raw-discovery.json"
            raw = json.loads(raw_path.read_text())
            print(f"[dedup] Input: {len(raw)} entries")
            result = run_dedup(raw)
            print(f"[dedup] Output: {len(result)} unique entries ({len(raw) - len(result)} duplicates removed)")
            dedup_path = input_dir / "dedup.json"
            dedup_path.write_text(json.dumps(result, indent=2))
            print(f"[dedup] Wrote {dedup_path}")

            # Print distribution summary
            from collections import Counter
            domains = Counter()
            for entry in result:
                for d in entry.get("found_in_domains", [entry.get("sub_domain", "unknown")]):
                    domains[d] += 1
            print("\n[dedup] Distribution by sub-domain:")
            for domain, count in domains.most_common():
                print(f"  {domain}: {count}")

        elif stage == "prune":
            print(f"[prune] Not yet implemented")
            sys.exit(1)
        elif stage == "enrich":
            print(f"[enrich] Not yet implemented")
            sys.exit(1)
        elif stage == "finalize":
            print(f"[finalize] Not yet implemented")
            sys.exit(1)
        else:
            print(f"Unknown stage: {stage}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All 7 tests PASS

**Step 5: Run dedup on the test fixture to verify end-to-end**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
cp tests/fixtures/raw-discovery.json .
python3 pipeline/pipeline.py --config tests/fixtures/swarm-config-test.json --stage dedup --output-dir test-output
```

Expected output:
```
[dedup] Input: 15 entries
[dedup] Output: 12 unique entries (3 duplicates removed)
...
```

The 3 trivy entries collapse to 1, the empty-URL entry is skipped, leaving 12 unique repos (15 - 3 trivy dupes = 12; the empty URL is skipped by the `if not key` guard giving us 11 — verify exact count).

```bash
python3 -c "import json; d=json.load(open('dedup.json')); print(len(d))"
```

**Step 6: Clean up test artifacts and commit**

```bash
rm -f raw-discovery.json dedup.json
rm -rf test-output
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: implement pipeline Stage 1 (dedup) with URL normalization and set-based matching"
```

---

### Task 2.3: Write pipeline.py — Stage 2 (prune)

Prune applies hard cuts (missing required fields) and soft cuts (below user thresholds).

**Files:**
- Modify: `pipeline/pipeline.py`
- Modify: `tests/test_pipeline.py`

**Step 1: Write failing tests for prune**

Add to `tests/test_pipeline.py`:

```python
from pipeline import run_prune


def test_prune_removes_empty_url():
    entries = [
        {"repo_url": "", "name": "bad", "description": "No URL", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "good", "description": "Has URL", "score": 5},
    ]
    result, pruned_log = run_prune(entries)
    assert len(result) == 1
    assert result[0]["name"] == "good"


def test_prune_removes_empty_description():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "no-desc", "description": "", "score": 5},
        {"repo_url": "https://github.com/c/d", "name": "has-desc", "description": "A real tool", "score": 5},
    ]
    result, pruned_log = run_prune(entries)
    assert len(result) == 1
    assert result[0]["name"] == "has-desc"


def test_prune_min_score():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "low", "description": "Low score", "score": 2},
        {"repo_url": "https://github.com/c/d", "name": "high", "description": "High score", "score": 8},
    ]
    result, _ = run_prune(entries, min_score=5)
    assert len(result) == 1
    assert result[0]["name"] == "high"


def test_prune_min_stars():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "few", "description": "Few stars", "score": 5, "stars": 10},
        {"repo_url": "https://github.com/c/d", "name": "many", "description": "Many stars", "score": 5, "stars": 500},
    ]
    result, _ = run_prune(entries, min_stars=100)
    assert len(result) == 1
    assert result[0]["name"] == "many"


def test_prune_active_since():
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "old", "description": "Old repo", "score": 5, "last_activity": "2020-01-01"},
        {"repo_url": "https://github.com/c/d", "name": "new", "description": "New repo", "score": 5, "last_activity": "2025-06-01"},
    ]
    result, _ = run_prune(entries, active_since="2023-01-01")
    assert len(result) == 1
    assert result[0]["name"] == "new"


def test_prune_logs_what_was_removed():
    entries = [
        {"repo_url": "", "name": "no-url", "description": "Missing", "score": 5},
        {"repo_url": "https://github.com/a/b", "name": "low-score", "description": "OK", "score": 1},
    ]
    _, pruned_log = run_prune(entries, min_score=3)
    assert len(pruned_log) == 2
    assert any("no_url" in log["reason"] for log in pruned_log)
    assert any("min_score" in log["reason"] for log in pruned_log)
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_pipeline.py::test_prune_removes_empty_url -v
```

Expected: FAIL — `ImportError: cannot import name 'run_prune'`

**Step 3: Implement run_prune in pipeline.py**

Add after `run_dedup`:

```python
def run_prune(
    entries: list[dict],
    min_score: int = 0,
    min_stars: int = 0,
    active_since: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Prune entries by hard cuts (missing fields) and soft cuts (thresholds).

    Returns (kept, pruned_log) where pruned_log explains each removal.
    """
    kept = []
    pruned_log = []

    for entry in entries:
        url = entry.get("repo_url", "").strip()
        desc = entry.get("description", "").strip()
        score = entry.get("score", 0)
        stars = entry.get("stars") or 0
        activity = entry.get("last_activity") or ""

        # Hard cuts
        if not url:
            pruned_log.append({"name": entry.get("name", "?"), "reason": "no_url"})
            continue
        if not desc:
            pruned_log.append({"name": entry.get("name", "?"), "reason": "no_description"})
            continue

        # Soft cuts
        if min_score and score < min_score:
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"min_score ({score} < {min_score})"})
            continue
        if min_stars and stars < min_stars:
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"min_stars ({stars} < {min_stars})"})
            continue
        if active_since and activity and activity < active_since:
            pruned_log.append({"name": entry.get("name", "?"), "reason": f"inactive (last: {activity}, cutoff: {active_since})"})
            continue

        kept.append(entry)

    return kept, pruned_log
```

Update the `main()` prune stage:

```python
        elif stage == "prune":
            dedup_path = input_dir / "dedup.json"
            dedup = json.loads(dedup_path.read_text())
            print(f"[prune] Input: {len(dedup)} entries")
            result, pruned_log = run_prune(
                dedup,
                min_score=args.min_score,
                min_stars=args.min_stars,
                active_since=args.active_since,
            )
            print(f"[prune] Kept: {len(result)}, Pruned: {len(pruned_log)}")
            for log in pruned_log:
                print(f"  PRUNED: {log['name']} — {log['reason']}")
            pruned_path = input_dir / "pruned.json"
            pruned_path.write_text(json.dumps(result, indent=2))
            print(f"[prune] Wrote {pruned_path}")
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_pipeline.py -v -k prune
```

Expected: All 6 prune tests PASS

**Step 5: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: implement pipeline Stage 2 (prune) with hard/soft cuts and removal logging"
```

---

### Task 2.4: Write pipeline.py — Stage 3 (enrich)

Uses Anthropic Batch API to add normalized tags, category, and one-line summary to each entry.

**Files:**
- Modify: `pipeline/pipeline.py`
- Modify: `tests/test_pipeline.py`

**Step 1: Write failing test for enrich**

The test mocks the Anthropic API to avoid real API calls:

```python
from unittest.mock import patch, MagicMock
from pipeline import run_enrich, strip_code_fences


def test_strip_code_fences_json():
    raw = '```json\n{"tags": ["security"]}\n```'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_strip_code_fences_plain():
    raw = '```\n{"tags": ["security"]}\n```'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_strip_code_fences_no_fences():
    raw = '{"tags": ["security"]}'
    assert strip_code_fences(raw) == '{"tags": ["security"]}'


def test_enrich_preserves_count():
    """Enrichment must NEVER drop entries — len(output) == len(input)."""
    entries = [
        {"repo_url": "https://github.com/a/b", "name": "tool-a", "description": "A security tool", "score": 8},
        {"repo_url": "https://github.com/c/d", "name": "tool-b", "description": "Another tool", "score": 7},
    ]
    mock_response = {
        "tags": ["kubernetes", "security"],
        "category": "Security Scanning",
        "summary": "A Kubernetes security scanning tool"
    }

    with patch("pipeline.enrich_single") as mock_enrich:
        mock_enrich.return_value = mock_response
        result = run_enrich(entries, topic="K8s Security", max_tokens=1024)

    assert len(result) == len(entries), f"Enrichment dropped entries: {len(result)} != {len(entries)}"
    assert result[0]["tags"] == ["kubernetes", "security"]
    assert result[0]["category"] == "Security Scanning"
```

**Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_pipeline.py::test_enrich_preserves_count -v
```

Expected: FAIL — `ImportError: cannot import name 'run_enrich'`

**Step 3: Implement enrich in pipeline.py**

```python
import re


def strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM responses."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    pattern = r'^```(?:json)?\s*\n(.*?)\n```$'
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def enrich_single(entry: dict, topic: str, max_tokens: int = 1024) -> dict:
    """Enrich a single entry using Anthropic API. Returns {tags, category, summary}."""
    import anthropic
    client = anthropic.Anthropic()
    prompt = f"""Given this open-source repository in the "{topic}" domain:

Name: {entry['name']}
Description: {entry['description']}
Language: {entry.get('language', 'unknown')}
Score: {entry.get('score', 'N/A')}

Return a JSON object with:
- "tags": array of 3-5 lowercase normalized topic tags
- "category": a human-readable category name (2-4 words)
- "summary": one-line summary of what makes this repo notable (max 100 chars)

Return ONLY the JSON object, no markdown fences or extra text."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text
    cleaned = strip_code_fences(raw)
    return json.loads(cleaned)


def run_enrich(entries: list[dict], topic: str, max_tokens: int = 1024) -> list[dict]:
    """Enrich all entries with tags, category, and summary.

    INVARIANT: len(output) == len(input). Enrichment never drops entries.
    On individual failure, entry gets empty tags/category/summary rather than being dropped.
    """
    result = []
    for i, entry in enumerate(entries):
        enriched = dict(entry)
        try:
            data = enrich_single(entry, topic, max_tokens)
            enriched["tags"] = data.get("tags", [])
            enriched["category"] = data.get("category")
            enriched["summary"] = data.get("summary")
        except Exception as e:
            print(f"  [enrich] Failed for {entry.get('name', '?')}: {e}", file=sys.stderr)
            enriched["tags"] = []
            enriched["category"] = None
            enriched["summary"] = None
        result.append(enriched)
        print(f"  [enrich] {i+1}/{len(entries)}: {entry.get('name', '?')}")

    assert len(result) == len(entries), f"Enrichment dropped entries: {len(result)} != {len(entries)}"
    return result
```

Update the `main()` enrich stage:

```python
        elif stage == "enrich":
            pruned_path = input_dir / "pruned.json"
            pruned = json.loads(pruned_path.read_text())
            print(f"[enrich] Input: {len(pruned)} entries")
            result = run_enrich(pruned, topic=config["topic"], max_tokens=config["pipeline"]["max_tokens"])
            print(f"[enrich] Output: {len(result)} entries (should equal input)")
            enriched_path = input_dir / "enriched.json"
            enriched_path.write_text(json.dumps(result, indent=2))
            print(f"[enrich] Wrote {enriched_path}")
```

**Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_pipeline.py -v -k enrich
```

Expected: All enrich tests PASS (including `test_enrich_preserves_count` using the mock)

**Step 5: Commit**

```bash
git add pipeline/pipeline.py tests/test_pipeline.py
git commit -m "feat: implement pipeline Stage 3 (enrich) with Anthropic API and code fence stripping"
```

---

### Task 2.5: Write pipeline.py — Stage 4 (finalize)

Validates against schema, clusters by sub-domain, sorts by score, and produces all three outputs.

**Files:**
- Modify: `pipeline/pipeline.py`
- Modify: `tests/test_pipeline.py`
- Create: `pipeline/templates/results.md.jinja`
- Create: `pipeline/templates/explorer.html`

**Step 1: Write the Jinja template for RESULTS.md**

Create `pipeline/templates/results.md.jinja`:

```jinja2
# {{ topic }} — Discovery Results

**Generated:** {{ generated_at }}
**Total repos:** {{ total }}
**Sub-domains:** {{ domain_count }}
**Score range:** {{ min_score }}-{{ max_score }}

---

## Distribution

| Sub-domain | Repos | Avg Score |
|-----------|-------|-----------|
{% for domain in domains %}
| {{ domain.name }} | {{ domain.count }} | {{ domain.avg_score }} |
{% endfor %}

---

## Top Repos (score >= 8)

{% for entry in top_repos %}
### {{ entry.name }} ({{ entry.score }}/10)

{{ entry.description }}

- **URL:** {{ entry.repo_url }}
- **Stars:** {{ entry.stars or 'N/A' }}
- **Language:** {{ entry.language or 'N/A' }}
- **Category:** {{ entry.category or 'N/A' }}
- **Found in:** {{ entry.found_in_domains | join(', ') }}

{% endfor %}

---

## Full Catalog

See `catalog.json` for the complete machine-readable dataset.
See `explorer.html` to browse interactively.
```

**Step 2: Write the explorer.html template**

Create `pipeline/templates/explorer.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ topic }} — Explorer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }
  h1 { color: #58a6ff; margin-bottom: 0.5rem; }
  .stats { color: #8b949e; margin-bottom: 1.5rem; }
  .controls { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
  input, select { background: #161b22; border: 1px solid #30363d; color: #c9d1d9; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.9rem; }
  input:focus, select:focus { border-color: #58a6ff; outline: none; }
  input[type="text"] { min-width: 300px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1rem; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; transition: border-color 0.2s; }
  .card:hover { border-color: #58a6ff; }
  .card h3 { color: #58a6ff; font-size: 1rem; margin-bottom: 0.5rem; }
  .card h3 a { color: inherit; text-decoration: none; }
  .card h3 a:hover { text-decoration: underline; }
  .card p { color: #8b949e; font-size: 0.85rem; line-height: 1.4; margin-bottom: 0.75rem; }
  .meta { display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.8rem; color: #8b949e; }
  .meta span { background: #21262d; padding: 0.15rem 0.5rem; border-radius: 4px; }
  .score { color: #3fb950; font-weight: 600; }
  .tag { background: #1f3a5f; color: #58a6ff; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
  .count { color: #8b949e; margin-bottom: 1rem; }
  .hidden { display: none; }
</style>
</head>
<body>
<h1>{{ topic }}</h1>
<p class="stats">{{ total }} repos across {{ domain_count }} sub-domains</p>

<div class="controls">
  <input type="text" id="search" placeholder="Filter by name, description, or tag...">
  <select id="domain-filter">
    <option value="">All sub-domains</option>
  </select>
  <select id="sort-by">
    <option value="score">Sort by score</option>
    <option value="stars">Sort by stars</option>
    <option value="name">Sort by name</option>
  </select>
</div>

<p class="count" id="count"></p>
<div class="grid" id="grid"></div>

<script>
const CATALOG = {{ catalog_json }};

const domainFilter = document.getElementById('domain-filter');
const domains = [...new Set(CATALOG.flatMap(e => e.found_in_domains || [e.sub_domain]))].sort();
domains.forEach(d => {
  const opt = document.createElement('option');
  opt.value = d; opt.textContent = d;
  domainFilter.appendChild(opt);
});

function render(entries) {
  const grid = document.getElementById('grid');
  grid.innerHTML = entries.map(e => `
    <div class="card">
      <h3><a href="${e.repo_url}" target="_blank">${e.name}</a></h3>
      <p>${e.summary || e.description}</p>
      <div class="meta">
        <span class="score">${e.score}/10</span>
        ${e.stars ? `<span>★ ${e.stars.toLocaleString()}</span>` : ''}
        ${e.language ? `<span>${e.language}</span>` : ''}
        ${e.license ? `<span>${e.license}</span>` : ''}
      </div>
      <div class="meta" style="margin-top:0.5rem">
        ${(e.tags || []).map(t => `<span class="tag">${t}</span>`).join('')}
      </div>
    </div>
  `).join('');
  document.getElementById('count').textContent = `Showing ${entries.length} of ${CATALOG.length}`;
}

function applyFilters() {
  let filtered = [...CATALOG];
  const q = document.getElementById('search').value.toLowerCase();
  const domain = domainFilter.value;
  const sort = document.getElementById('sort-by').value;

  if (q) filtered = filtered.filter(e =>
    e.name.toLowerCase().includes(q) ||
    (e.description || '').toLowerCase().includes(q) ||
    (e.tags || []).some(t => t.includes(q))
  );
  if (domain) filtered = filtered.filter(e =>
    (e.found_in_domains || [e.sub_domain]).includes(domain)
  );

  if (sort === 'score') filtered.sort((a, b) => b.score - a.score);
  else if (sort === 'stars') filtered.sort((a, b) => (b.stars || 0) - (a.stars || 0));
  else if (sort === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name));

  render(filtered);
}

document.getElementById('search').addEventListener('input', applyFilters);
domainFilter.addEventListener('change', applyFilters);
document.getElementById('sort-by').addEventListener('change', applyFilters);
applyFilters();
</script>
</body>
</html>
```

**Step 3: Write failing test for finalize**

Add to `tests/test_pipeline.py`:

```python
from pipeline import run_finalize


def test_finalize_produces_three_outputs(tmp_path):
    entries = [
        {
            "repo_url": "https://github.com/a/b", "name": "a/b", "description": "Tool A",
            "sub_domain": "scanning", "score": 9, "stars": 1000, "language": "Go",
            "license": "MIT", "last_activity": "2025-01-01", "tags": ["security"],
            "category": "Scanning", "summary": "A scanning tool", "found_in_domains": ["scanning"]
        },
        {
            "repo_url": "https://github.com/c/d", "name": "c/d", "description": "Tool B",
            "sub_domain": "policy", "score": 7, "stars": 500, "language": "Python",
            "license": "Apache-2.0", "last_activity": "2025-06-01", "tags": ["policy"],
            "category": "Policy", "summary": "A policy tool", "found_in_domains": ["policy"]
        },
    ]
    template_dir = Path(__file__).parent.parent / "pipeline" / "templates"
    run_finalize(entries, topic="Test Topic", output_dir=tmp_path, template_dir=template_dir)

    assert (tmp_path / "catalog.json").exists()
    assert (tmp_path / "explorer.html").exists()
    assert (tmp_path / "RESULTS.md").exists()

    catalog = json.loads((tmp_path / "catalog.json").read_text())
    assert len(catalog) == 2
    assert catalog[0]["score"] >= catalog[1]["score"]  # sorted descending
```

**Step 4: Run test to verify it fails**

```bash
python3 -m pytest tests/test_pipeline.py::test_finalize_produces_three_outputs -v
```

Expected: FAIL — `ImportError: cannot import name 'run_finalize'`

**Step 5: Implement run_finalize in pipeline.py**

```python
from datetime import datetime


def run_finalize(
    entries: list[dict],
    topic: str,
    output_dir: Path,
    template_dir: Path | None = None,
) -> None:
    """Validate, cluster, sort, and produce three output files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates"

    # Sort by score descending
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)

    # 1. catalog.json
    catalog_path = output_dir / "catalog.json"
    catalog_path.write_text(json.dumps(entries, indent=2))

    # 2. RESULTS.md via Jinja
    from collections import Counter, defaultdict
    from jinja2 import Environment, FileSystemLoader

    domain_entries = defaultdict(list)
    for e in entries:
        for d in e.get("found_in_domains", [e.get("sub_domain", "unknown")]):
            domain_entries[d].append(e)

    domains_summary = []
    for d_name in sorted(domain_entries.keys()):
        d_entries = domain_entries[d_name]
        avg = sum(e.get("score", 0) for e in d_entries) / len(d_entries)
        domains_summary.append({"name": d_name, "count": len(d_entries), "avg_score": f"{avg:.1f}"})

    scores = [e.get("score", 0) for e in entries]
    context = {
        "topic": topic,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(entries),
        "domain_count": len(domain_entries),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "domains": domains_summary,
        "top_repos": [e for e in entries if e.get("score", 0) >= 8],
    }

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    results_tpl = env.get_template("results.md.jinja")
    results_path = output_dir / "RESULTS.md"
    results_path.write_text(results_tpl.render(**context))

    # 3. explorer.html via Jinja
    explorer_tpl = env.get_template("explorer.html")
    explorer_context = {
        "topic": topic,
        "total": len(entries),
        "domain_count": len(domain_entries),
        "catalog_json": json.dumps(entries),
    }
    explorer_path = output_dir / "explorer.html"
    explorer_path.write_text(explorer_tpl.render(**explorer_context))

    print(f"[finalize] Wrote {catalog_path} ({len(entries)} entries)")
    print(f"[finalize] Wrote {results_path}")
    print(f"[finalize] Wrote {explorer_path}")
```

Update the `main()` finalize stage:

```python
        elif stage == "finalize":
            enriched_path = input_dir / "enriched.json"
            enriched = json.loads(enriched_path.read_text())
            print(f"[finalize] Input: {len(enriched)} entries")
            out_dir = Path(args.output_dir) if args.output_dir else output_dir
            template_dir = Path(__file__).parent / "templates"
            run_finalize(enriched, topic=config["topic"], output_dir=out_dir, template_dir=template_dir)
```

**Step 6: Run all tests**

```bash
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All tests PASS

**Step 7: Commit**

```bash
git add pipeline/pipeline.py pipeline/templates/ tests/test_pipeline.py
git commit -m "feat: implement pipeline Stages 3-4 (enrich + finalize) with Jinja templates and explorer UI"
```

---

### Task 2.6: Create requirements.txt and verify full pipeline end-to-end

**Files:**
- Create: `pipeline/requirements.txt`

**Step 1: Write requirements.txt**

```
anthropic>=0.40.0
jinja2>=3.1.0
```

**Step 2: Run the full pipeline on fixtures (dedup + prune only — enrich needs API key)**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
cp tests/fixtures/raw-discovery.json .
python3 pipeline/pipeline.py --config tests/fixtures/swarm-config-test.json --stage dedup --output-dir test-output
python3 pipeline/pipeline.py --config tests/fixtures/swarm-config-test.json --stage prune --min-score 3 --min-stars 20 --output-dir test-output
```

Verify dedup.json and pruned.json exist with correct counts:

```bash
python3 -c "
import json
d = json.load(open('dedup.json'))
p = json.load(open('pruned.json'))
print(f'Dedup: {len(d)}, Pruned: {len(p)}')
assert len(p) <= len(d)
print('Pipeline stages 1-2 validated ✓')
"
```

**Step 3: Clean up and commit**

```bash
rm -f raw-discovery.json dedup.json pruned.json
rm -rf test-output
git add pipeline/requirements.txt
git commit -m "chore: add requirements.txt (anthropic, jinja2)"
```

---

## Phase 3: SKILL.md

### Task 3.1: Write SKILL.md

The main orchestration skill that drives the entire workflow.

**Files:**
- Create: `skill/SKILL.md`

**Step 1: Write the SKILL.md**

Must follow the Anthropic Architect rules from CLAUDE.md:
- Frontmatter: name (lowercase-hyphens), description (third-person, WHAT + WHEN + trigger keywords), max 1024 chars
- Body under 500 lines
- References one level deep only
- Concrete examples, not abstract descriptions

```markdown
---
name: everything-on-earth
description: >-
  Discovers every open-source GitHub/GitLab repository for any topic using a
  TeamCreate agent swarm and deterministic Python synthesis pipeline. Use when
  the user says "find every repo", "discover all tools", "everything on earth",
  "catalog all open source", "survey the landscape", or wants comprehensive
  GitHub/GitLab discovery for a broad domain. Launches 3 Haiku scouts for
  reconnaissance, asks clarifying questions, then deploys 6-8 Sonnet teammates
  in a self-claiming swarm. Deterministic pipeline handles dedup, pruning,
  enrichment, and finalization. Outputs catalog.json, explorer.html, RESULTS.md.
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

# everything-on-earth

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

1. **Constraints**: "What minimum star count, language filter, or activity recency do you want?" (offer: >=20 stars + active since 2023 as default)
2. **Known sub-domains**: "What sub-categories do you already know about?"
3. **Seed repos**: "Any repos you've already found that I should know about?"

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
  prompt: "You are a discovery agent. Check TaskList for unclaimed tasks, claim one, search using firecrawl, write results, then claim the next task. Stop when no tasks remain."
})
```

The SubagentStart hook automatically injects `agent-prompt-template.md`, `output-schema.json`, and `swarm-config.json` into each teammate.

5. **Wait** for all tasks to complete. Monitor via TaskList.

6. **Concat results** (deterministic — no LLM):
```bash
jq -s 'add' discovery/*.json > raw-discovery.json
echo "Concatenated $(jq length raw-discovery.json) entries from $(ls discovery/*.json | wc -l) files"
```

## Phase 3: Pipeline

The post-concat hook auto-triggers dedup. After dedup completes:

1. **Show distribution summary** to user
2. **Ask for pruning thresholds** using AskUserQuestion:
   - Minimum score (default: 3)
   - Minimum stars (default: 0)
   - Active since (default: none)
3. **Run remaining stages**:
```bash
python3 pipeline/pipeline.py --config swarm-config.json --stage prune,enrich,finalize --min-score {score} --min-stars {stars}
```
4. **Present results**: Show RESULTS.md summary, link to explorer.html

## Phase 4: Gap Review

After presenting results:

1. Ask: "Any domains missing from the results?"
2. If yes: create new tasks on the existing team, spawn 2-3 follow-up agents
3. Merge new discovery files into existing catalog through the same pipeline
4. If no: clean up — `TeamDelete("eoe-{topic-slug}")`

## Reference Files

- `skill/references/agent-prompt-template.md` — injected into teammates by SubagentStart hook
- `skill/references/output-schema.json` — entry schema that hooks validate against
```

**Step 2: Verify SKILL.md is under 500 lines**

```bash
wc -l skill/SKILL.md
```

Expected: ~140-160 lines (well under 500)

**Step 3: Validate frontmatter**

```bash
head -20 skill/SKILL.md
```

Verify: name is lowercase-hyphens, description includes trigger keywords, allowed-tools listed.

**Step 4: Commit**

```bash
git add skill/SKILL.md
git commit -m "feat: add SKILL.md — orchestration skill for everything-on-earth discovery workflow"
```

---

## Phase 4: Hooks

### Task 4.1: Write pre-teamcreate.js (gate hook)

Validates config and firecrawl setup before any agents spawn.

**Files:**
- Create: `hooks/pre-teamcreate.js`

**Step 1: Write the hook**

```javascript
#!/usr/bin/env node

/**
 * Hook: pre-teamcreate.js
 * Trigger: PreToolUse on TeamCreate
 * Purpose: Gate — validates swarm-config.json and firecrawl setup before team creation.
 *
 * Exit behavior:
 *   - stdout JSON with { decision: "block", reason } → blocks TeamCreate
 *   - stdout JSON with { decision: "allow" } → allows TeamCreate
 *   - exit 0 with no JSON → allows (passthrough for non-eoe teams)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const teamName = input.tool_input?.name || '';

// Only gate our teams
if (!teamName.startsWith('eoe-')) {
  process.exit(0);
}

const errors = [];
const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const configPath = path.join(projectDir, 'swarm-config.json');

// 1. Config file exists
if (!fs.existsSync(configPath)) {
  errors.push('swarm-config.json not found in project directory');
} else {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    // 2. Minimum sub-domains
    if (!config.sub_domains || config.sub_domains.length < 3) {
      errors.push(`Need >= 3 sub-domains, found ${config.sub_domains?.length || 0}`);
    }

    // 3. Seed queries per sub-domain
    if (config.sub_domains) {
      for (const sd of config.sub_domains) {
        const qCount = sd.seed_queries?.length || 0;
        if (qCount < 8) {
          errors.push(`Sub-domain "${sd.id}" has ${qCount} seed queries (need 8-10)`);
        }
      }
    }

    // 4. Schema version
    if (config.schema_version !== '2.0.0') {
      errors.push(`Unsupported schema_version: ${config.schema_version} (expected 2.0.0)`);
    }
  } catch (e) {
    errors.push(`Invalid JSON in swarm-config.json: ${e.message}`);
  }
}

// 5. Firecrawl CLI exists
try {
  execSync('which firecrawl', { stdio: 'pipe' });
} catch {
  errors.push('firecrawl CLI not found in PATH. Install: npm install -g firecrawl');
}

// 6. FIRECRAWL_API_KEY is set
if (!process.env.FIRECRAWL_API_KEY) {
  errors.push('FIRECRAWL_API_KEY environment variable not set');
}

if (errors.length > 0) {
  const result = {
    decision: 'block',
    reason: `Pre-TeamCreate validation failed:\n${errors.map(e => `  - ${e}`).join('\n')}`
  };
  process.stdout.write(JSON.stringify(result));
} else {
  const result = { decision: 'allow' };
  process.stdout.write(JSON.stringify(result));
}
```

**Step 2: Make executable and verify**

```bash
chmod +x hooks/pre-teamcreate.js
node -c hooks/pre-teamcreate.js  # syntax check
echo '{"tool_input":{"name":"eoe-test"}}' | CLAUDE_PROJECT_DIR=/tmp node hooks/pre-teamcreate.js
```

Expected: JSON output with `decision: "block"` (since config doesn't exist in /tmp)

**Step 3: Commit**

```bash
git add hooks/pre-teamcreate.js
git commit -m "feat: add pre-teamcreate.js — gate hook validates config and firecrawl before team creation"
```

---

### Task 4.2: Write subagent-context.sh (context injection hook)

The most architecturally important hook — injects reference materials into teammates without bloating the parent conversation.

**Files:**
- Create: `hooks/subagent-context.sh`

**Step 1: Write the hook**

```bash
#!/bin/bash
# Hook: subagent-context.sh
# Trigger: SubagentStart
# Purpose: Inject agent-prompt-template + output-schema + swarm-config into teammates.
# Only activates for teams named eoe-*.
# The parent conversation never sees this content, keeping context lean.

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

# Only inject for our discovery teams
if [[ "$TEAM_NAME" != eoe-* ]]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

TEMPLATE=$(cat "$PROJECT_DIR/skill/references/agent-prompt-template.md" 2>/dev/null)
SCHEMA=$(cat "$PROJECT_DIR/skill/references/output-schema.json" 2>/dev/null)
CONFIG=$(cat "$PROJECT_DIR/swarm-config.json" 2>/dev/null)

if [[ -z "$TEMPLATE" || -z "$SCHEMA" ]]; then
  echo "Warning: Could not read reference files from $PROJECT_DIR" >&2
  exit 0
fi

jq -n --arg tpl "$TEMPLATE" --arg sch "$SCHEMA" --arg cfg "$CONFIG" '{
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: ("DISCOVERY AGENT REFERENCE:\n\n## Agent Prompt Template\n" + $tpl + "\n\n## Output Schema\n" + $sch + "\n\n## Swarm Config\n" + $cfg)
  }
}'
```

**Step 2: Make executable and verify**

```bash
chmod +x hooks/subagent-context.sh
echo '{"team_name":"eoe-test"}' | CLAUDE_PROJECT_DIR=/Users/emolero/Documents/GitHub/ot/everything-on-earth bash hooks/subagent-context.sh | jq .
```

Expected: JSON with `hookSpecificOutput.additionalContext` containing the template, schema, and config.

**Step 3: Commit**

```bash
git add hooks/subagent-context.sh
git commit -m "feat: add subagent-context.sh — injects reference materials into teammates at spawn"
```

---

### Task 4.3: Write task-completed.sh (output validation hook)

Validates that agents write proper output before marking tasks complete.

**Files:**
- Create: `hooks/task-completed.sh`

**Step 1: Write the hook**

```bash
#!/bin/bash
# Hook: task-completed.sh
# Trigger: TaskCompleted
# Purpose: Validate agent output file exists and has correct JSON structure.
# Exit 2 = block completion (feeds error back to teammate).

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject // empty')

# Only validate our teams
[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Derive expected output file from task subject (sub-domain id)
SUBDOMAIN_ID=$(echo "$TASK_SUBJECT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
OUTPUT_FILE="discovery/${SUBDOMAIN_ID}.json"

if [ ! -f "$OUTPUT_FILE" ]; then
  echo "Output file $OUTPUT_FILE not found. Write results before completing." >&2
  exit 2
fi

# Validate JSON parses
if ! jq empty "$OUTPUT_FILE" 2>/dev/null; then
  echo "Invalid JSON in $OUTPUT_FILE" >&2
  exit 2
fi

# Validate it's an array with repo_url fields
if ! jq -e '.[0].repo_url' "$OUTPUT_FILE" > /dev/null 2>&1; then
  echo "Invalid output: entries must be an array with repo_url field" >&2
  exit 2
fi

COUNT=$(jq 'length' "$OUTPUT_FILE")
if [ "$COUNT" -lt 1 ]; then
  echo "Output file has 0 entries. Search harder." >&2
  exit 2
fi

echo "Validated $OUTPUT_FILE: $COUNT entries" >&2
exit 0
```

**Step 2: Make executable**

```bash
chmod +x hooks/task-completed.sh
```

**Step 3: Commit**

```bash
git add hooks/task-completed.sh
git commit -m "feat: add task-completed.sh — validates agent output files on task completion"
```

---

### Task 4.4: Write teammate-idle.sh (task claiming redirector)

**Files:**
- Create: `hooks/teammate-idle.sh`

**Step 1: Write the hook**

```bash
#!/bin/bash
# Hook: teammate-idle.sh
# Trigger: TeammateIdle
# Purpose: Check for unclaimed tasks. If tasks remain, nudge teammate to claim one.
# Exit 2 = keeps teammate working (prevents idle).

INPUT=$(cat)
TEAM_NAME=$(echo "$INPUT" | jq -r '.team_name // empty')

[[ "$TEAM_NAME" != eoe-* ]] && exit 0

# Check for unclaimed tasks by looking at discovery files vs config
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CONFIG_FILE="$PROJECT_DIR/swarm-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  exit 0  # can't check, allow idle
fi

TOTAL_TASKS=$(jq '.sub_domains | length' "$CONFIG_FILE" 2>/dev/null)
TOTAL_TASKS=$((TOTAL_TASKS + 1))  # +1 for awesome-lists task

COMPLETED=$(ls "$PROJECT_DIR/discovery/"*.json 2>/dev/null | wc -l | tr -d ' ')

REMAINING=$((TOTAL_TASKS - COMPLETED))

if [ "$REMAINING" -gt 0 ]; then
  echo "There are approximately $REMAINING unclaimed tasks remaining. Check TaskList and claim the next one." >&2
  exit 2
fi

exit 0
```

**Step 2: Make executable**

```bash
chmod +x hooks/teammate-idle.sh
```

**Step 3: Commit**

```bash
git add hooks/teammate-idle.sh
git commit -m "feat: add teammate-idle.sh — redirects idle agents to unclaimed tasks"
```

---

### Task 4.5: Write post-concat.js (pipeline auto-trigger)

**Files:**
- Create: `hooks/post-concat.js`

**Step 1: Write the hook**

```javascript
#!/usr/bin/env node

/**
 * Hook: post-concat.js
 * Trigger: PostToolUse on Bash
 * Purpose: Detect when lead concatenates discovery files, auto-trigger dedup.
 *
 * Looks for raw-discovery.json in the Bash command output.
 * If found, runs pipeline Stage 1 (dedup) and injects summary into conversation.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const command = input.tool_input?.command || '';
const output = input.tool_result?.stdout || '';

// Only trigger on jq concat commands that produce raw-discovery.json
if (!command.includes('raw-discovery.json') || !command.includes('discovery/')) {
  process.exit(0);
}

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const rawPath = path.join(projectDir, 'raw-discovery.json');

if (!fs.existsSync(rawPath)) {
  process.exit(0);
}

// Run dedup stage
try {
  const configPath = path.join(projectDir, 'swarm-config.json');
  const pipelinePath = path.join(projectDir, 'pipeline', 'pipeline.py');

  const result = execSync(
    `python3 "${pipelinePath}" --config "${configPath}" --stage dedup`,
    { cwd: projectDir, encoding: 'utf8', timeout: 60000 }
  );

  // Read dedup results for summary
  const dedupPath = path.join(projectDir, 'dedup.json');
  if (fs.existsSync(dedupPath)) {
    const dedup = JSON.parse(fs.readFileSync(dedupPath, 'utf8'));
    const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));

    const summary = [
      `Pipeline Stage 1 (dedup) complete:`,
      `  Raw entries: ${raw.length}`,
      `  After dedup: ${dedup.length}`,
      `  Duplicates removed: ${raw.length - dedup.length}`,
      ``,
      `Ask the user for pruning thresholds (min score, min stars, active since) before running Stage 2.`,
    ].join('\n');

    const hookOutput = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: summary,
      }
    };
    process.stdout.write(JSON.stringify(hookOutput));
  }
} catch (e) {
  // Don't block on pipeline failure — let the lead handle it
  console.error(`[post-concat] Pipeline dedup failed: ${e.message}`);
}

process.exit(0);
```

**Step 2: Make executable and syntax check**

```bash
chmod +x hooks/post-concat.js
node -c hooks/post-concat.js
```

**Step 3: Commit**

```bash
git add hooks/post-concat.js
git commit -m "feat: add post-concat.js — auto-triggers pipeline dedup after discovery concat"
```

---

### Task 4.6: Write statusline.js (progress display)

**Files:**
- Create: `hooks/statusline.js`

**Step 1: Write the hook**

```javascript
#!/usr/bin/env node

/**
 * Hook: statusline.js
 * Trigger: Notification
 * Purpose: Real-time progress display for everything-on-earth runs.
 *
 * Output format:
 *   everything-on-earth | {topic} | tasks: {done}/{total} | repos: {count} | {pct}%
 */

const fs = require('fs');
const path = require('path');

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const configPath = path.join(projectDir, 'swarm-config.json');

// Only show status if a run is in progress
if (!fs.existsSync(configPath)) {
  process.exit(0);
}

try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const topic = config.topic || 'unknown';
  const totalDomains = (config.sub_domains?.length || 0) + 1; // +1 for awesome-lists

  // Count completed discovery files
  const discoveryDir = path.join(projectDir, 'discovery');
  let completedFiles = 0;
  let totalRepos = 0;

  if (fs.existsSync(discoveryDir)) {
    const files = fs.readdirSync(discoveryDir).filter(f => f.endsWith('.json'));
    completedFiles = files.length;

    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(discoveryDir, file), 'utf8'));
        totalRepos += Array.isArray(data) ? data.length : 0;
      } catch {
        // skip malformed files
      }
    }
  }

  const pct = totalDomains > 0 ? Math.round((completedFiles / totalDomains) * 100) : 0;
  const status = `everything-on-earth | ${topic} | tasks: ${completedFiles}/${totalDomains} | repos: ${totalRepos} | ${pct}%`;

  const hookOutput = {
    hookSpecificOutput: {
      hookEventName: 'Notification',
      statusMessage: status,
    }
  };
  process.stdout.write(JSON.stringify(hookOutput));
} catch {
  // Silently exit on any error — status is non-critical
  process.exit(0);
}
```

**Step 2: Make executable**

```bash
chmod +x hooks/statusline.js
node -c hooks/statusline.js
```

**Step 3: Commit**

```bash
git add hooks/statusline.js
git commit -m "feat: add statusline.js — real-time progress display during discovery runs"
```

---

## Phase 5: Install & Integration

### Task 5.1: Write install.sh

The installer copies skill + hooks, registers hooks in settings.json, and checks dependencies.

**Files:**
- Create: `install.sh`

**Step 1: Write the installer**

```bash
#!/bin/bash
set -euo pipefail

# everything-on-earth installer
# Copies skill and hooks to ~/.claude/, registers hooks in settings.json

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DEST="$HOME/.claude/skills/everything-on-earth"
HOOKS_DEST="$HOME/.claude/hooks/everything-on-earth"
SETTINGS="$HOME/.claude/settings.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Uninstall mode ---
if [[ "${1:-}" == "--uninstall" ]]; then
  echo "Uninstalling everything-on-earth..."
  rm -rf "$SKILL_DEST" "$HOOKS_DEST"
  if [ -f "$SETTINGS" ]; then
    # Remove our hook entries (entries containing "everything-on-earth")
    python3 -c "
import json, sys
with open('$SETTINGS') as f:
    s = json.load(f)
hooks = s.get('hooks', {})
for event in list(hooks.keys()):
    hooks[event] = [h for h in hooks[event]
                     if not any('everything-on-earth' in (hook.get('command',''))
                               for hook in h.get('hooks', []))]
    if not hooks[event]:
        del hooks[event]
s['hooks'] = hooks
with open('$SETTINGS', 'w') as f:
    json.dump(s, f, indent=2)
print('Cleaned settings.json')
" 2>/dev/null || echo "Could not clean settings.json automatically"
  fi
  echo -e "${GREEN}Uninstalled.${NC}"
  exit 0
fi

# --- Install mode ---
echo "Installing everything-on-earth..."

# Check dependencies
MISSING=()

if ! command -v node &>/dev/null || [[ $(node -v | sed 's/v//' | cut -d. -f1) -lt 18 ]]; then
  MISSING+=("Node.js >= 18")
fi

if ! command -v python3 &>/dev/null; then
  MISSING+=("Python >= 3.9")
fi

if ! command -v jq &>/dev/null; then
  MISSING+=("jq")
fi

if ! command -v firecrawl &>/dev/null; then
  echo -e "${YELLOW}Warning: firecrawl CLI not found. Install with: npm install -g firecrawl${NC}"
  echo -e "${YELLOW}Discovery agents need firecrawl to search. The pre-teamcreate hook will block runs without it.${NC}"
fi

if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
  echo -e "${YELLOW}Warning: FIRECRAWL_API_KEY not set. Set it before running: export FIRECRAWL_API_KEY=your-key${NC}"
fi

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo -e "${RED}Missing required dependencies:${NC}"
  for dep in "${MISSING[@]}"; do
    echo -e "  ${RED}- $dep${NC}"
  done
  exit 1
fi

# Copy skill
mkdir -p "$SKILL_DEST"
cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_DEST/"
cp -r "$SCRIPT_DIR/skill/references" "$SKILL_DEST/"
echo -e "${GREEN}✓ Skill installed to $SKILL_DEST${NC}"

# Copy hooks
mkdir -p "$HOOKS_DEST"
cp "$SCRIPT_DIR/hooks/"* "$HOOKS_DEST/"
chmod +x "$HOOKS_DEST/"*
echo -e "${GREEN}✓ Hooks installed to $HOOKS_DEST${NC}"

# Register hooks in settings.json
python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/.claude/settings.json")

# Load or create settings
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
hooks_dir = os.path.expanduser("~/.claude/hooks/everything-on-earth")

# Define our hook registrations
registrations = {
    "PreToolUse": [{
        "matcher": "TeamCreate",
        "hooks": [{"type": "command", "command": f"node {hooks_dir}/pre-teamcreate.js"}]
    }],
    "SubagentStart": [{
        "hooks": [{"type": "command", "command": f"{hooks_dir}/subagent-context.sh"}]
    }],
    "TaskCompleted": [{
        "hooks": [{"type": "command", "command": f"{hooks_dir}/task-completed.sh"}]
    }],
    "TeammateIdle": [{
        "hooks": [{"type": "command", "command": f"{hooks_dir}/teammate-idle.sh"}]
    }],
    "PostToolUse": [{
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": f"node {hooks_dir}/post-concat.js"}]
    }],
    "Notification": [{
        "hooks": [{"type": "command", "command": f"node {hooks_dir}/statusline.js"}]
    }],
}

# Merge registrations (don't clobber existing hooks)
for event, new_entries in registrations.items():
    existing = hooks.get(event, [])
    # Remove any old everything-on-earth entries
    existing = [e for e in existing
                if not any("everything-on-earth" in h.get("command", "")
                          for h in e.get("hooks", []))]
    existing.extend(new_entries)
    hooks[event] = existing

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print("✓ Hooks registered in settings.json")
PYEOF

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Usage: /everything-on-earth \"your topic\""
echo ""
echo "Pipeline code stays in this repo: $SCRIPT_DIR/pipeline/"
echo "Update: git pull && ./install.sh"
echo "Uninstall: ./install.sh --uninstall"
```

**Step 2: Make executable and test**

```bash
chmod +x install.sh
# Dry-run: check syntax
bash -n install.sh
```

**Step 3: Commit**

```bash
git add install.sh
git commit -m "feat: add install.sh — copies skill/hooks and registers in settings.json"
```

---

### Task 5.2: Add .gitignore and finalize repo structure

**Files:**
- Create: `.gitignore`

**Step 1: Write .gitignore**

```
# Runtime outputs
discovery/
raw-discovery.json
dedup.json
pruned.json
enriched.json
swarm-config.json
everything-on-earth-output/
test-output/

# Python
__pycache__/
*.pyc
.venv/

# OS
.DS_Store

# IDE
.vscode/
.idea/
```

**Step 2: Verify final file structure**

```bash
find . -type f -not -path './.git*' | sort
```

Expected:
```
./.gitignore
./docs/plans/2026-03-23-everything-on-earth-design.md
./docs/plans/2026-03-23-everything-on-earth-implementation.md
./examples/swarm-config.example.json
./hooks/post-concat.js
./hooks/pre-teamcreate.js
./hooks/statusline.js
./hooks/subagent-context.sh
./hooks/task-completed.sh
./hooks/teammate-idle.sh
./install.sh
./meta-analysis.md
./pipeline/pipeline.py
./pipeline/requirements.txt
./pipeline/templates/explorer.html
./pipeline/templates/results.md.jinja
./README.md
./skill/references/agent-prompt-template.md
./skill/references/output-schema.json
./skill/SKILL.md
./tests/fixtures/raw-discovery.json
./tests/fixtures/swarm-config-test.json
./tests/test_pipeline.py
```

**Step 3: Run all tests one final time**

```bash
cd /Users/emolero/Documents/GitHub/ot/everything-on-earth
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All tests PASS

**Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore for runtime artifacts, Python cache, and OS files"
```

---

### Task 5.3: Update README with install instructions

**Files:**
- Modify: `README.md`

The README already has the correct architecture description. Update the install section to point to the correct repo path:

**Step 1: Verify README is current**

```bash
head -10 README.md
```

The README was already written during the design phase and is accurate. No changes needed unless the repo URL has changed.

**Step 2: Commit if any changes were made**

If README needed updates:

```bash
git add README.md
git commit -m "docs: update README with final install instructions"
```

---

## Summary

| Phase | Tasks | Key Files | Tests |
|-------|-------|-----------|-------|
| 1. Schema & Skeleton | 1.1-1.4 | output-schema.json, agent-prompt-template.md, swarm-config.example.json | JSON validation |
| 2. Pipeline | 2.1-2.6 | pipeline.py, test_pipeline.py, templates/ | 15+ pytest tests |
| 3. SKILL.md | 3.1 | skill/SKILL.md | Frontmatter + line count validation |
| 4. Hooks | 4.1-4.6 | 6 hook files (js/sh) | Syntax checks, manual stdin tests |
| 5. Install | 5.1-5.3 | install.sh, .gitignore | Dry-run, final structure check |

**Total:** 15 tasks, ~22 files to create, ~15+ automated tests.

**Critical path:** Schema (1.2) → Pipeline dedup (2.2) → Pipeline prune (2.3) → Pipeline finalize (2.5) → SKILL.md (3.1) → Install (5.1)

**Parallelizable:** Tasks 2.4 (enrich) and templates (2.5 templates) can run alongside 2.2/2.3. All 6 hooks (Phase 4) are independent and can be built in parallel.
