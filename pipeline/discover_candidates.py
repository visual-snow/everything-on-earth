#!/usr/bin/env python3
"""Collect GitHub repo candidates for one massive-crawl sub-domain."""

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse


RESERVED_GITHUB_PATHS = {
    "",
    "about",
    "accounts",
    "collections",
    "contact",
    "customer-stories",
    "enterprise",
    "events",
    "explore",
    "features",
    "issues",
    "login",
    "marketplace",
    "new",
    "notifications",
    "organizations",
    "orgs",
    "pricing",
    "pulls",
    "search",
    "settings",
    "signup",
    "site",
    "sponsors",
    "team",
    "topics",
    "trending",
    "users",
}

QUERY_TOKEN_STOPWORDS = {
    "and",
    "analysis",
    "calculator",
    "data",
    "github",
    "model",
    "open",
    "opensource",
    "open-source",
    "python",
    "repo",
    "simulation",
    "software",
    "source",
    "system",
    "systems",
    "tool",
    "toolkit",
    "tools",
}

SHORT_QUERY_TOKENS = {
    "ev",
    "ghg",
    "lca",
    "cmip",
    "era5",
    "ndvi",
    "esg",
    "sdg",
    "csrd",
    "tcfd",
    "issb",
    "leed",
}

NEGATIVE_SIGNAL_TOKENS = {
    "awesome",
    "benchmark",
    "course",
    "dataset",
    "demo",
    "directory",
    "example",
    "examples",
    "notebook",
    "paper",
    "slides",
    "template",
    "tutorial",
}


def normalize_github_repo_url(url: str) -> str | None:
    """Return canonical repo root URL for GitHub repo pages, else None."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None

    parts = [segment for segment in parsed.path.split("/") if segment]
    if len(parts) < 2:
        return None
    if parts[0].lower() in RESERVED_GITHUB_PATHS:
        return None

    owner = parts[0].strip().lower()
    repo = parts[1].strip().lower()
    if not owner or not repo:
        return None
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not repo:
        return None
    return f"https://github.com/{owner}/{repo}"


def extract_repo_urls(search_payload: dict) -> list[str]:
    """Extract unique canonical GitHub repo URLs from a Firecrawl search payload."""
    seen: set[str] = set()
    urls: list[str] = []

    for result in search_payload.get("data", {}).get("web", []):
        raw_url = result.get("url", "")
        repo_url = normalize_github_repo_url(raw_url)
        if not repo_url or repo_url in seen:
            continue
        seen.add(repo_url)
        urls.append(repo_url)
    return urls


def build_entry_from_github_meta(meta: dict, subdomain_id: str) -> dict:
    """Map GitHub API repo metadata into the shared discovery shape."""
    license_value = meta.get("license")
    if isinstance(license_value, dict):
        license_value = license_value.get("spdx_id") or None

    pushed_at = meta.get("pushed_at")
    if pushed_at:
        pushed_at = pushed_at[:10]

    description = (meta.get("description") or "").strip() or "No description provided."

    return {
        "repo_url": normalize_github_repo_url(meta.get("html_url", "")) or meta.get("html_url", ""),
        "name": meta.get("full_name") or "",
        "description": description,
        "sub_domain": subdomain_id,
        "stars": meta.get("stargazers_count"),
        "language": meta.get("language"),
        "license": license_value,
        "last_activity": pushed_at,
    }


def tokenize_text(text: str) -> set[str]:
    """Tokenize query or repo text into normalized domain terms."""
    tokens: set[str] = set()
    for raw in re.findall(r"[a-z0-9]+", text.lower()):
        if raw in QUERY_TOKEN_STOPWORDS:
            continue
        if len(raw) < 4 and raw not in SHORT_QUERY_TOKENS:
            continue
        tokens.add(raw)
    return tokens


def extract_domain_terms(subdomain: dict) -> set[str]:
    """Derive domain-specific terms from a sub-domain's seed queries."""
    terms: set[str] = set()
    for query in subdomain.get("queries", []):
        terms.update(tokenize_text(query))
    return terms


def score_candidate(candidate: dict, domain_terms: set[str]) -> tuple[int, str]:
    """Assign a deterministic 1-10 relevance score and rationale."""
    repo_text = " ".join(
        [
            candidate.get("name", ""),
            candidate.get("description", ""),
        ]
    )
    repo_tokens = tokenize_text(repo_text)
    overlap = sorted(repo_tokens & domain_terms)
    negative_signals = sorted(repo_tokens & NEGATIVE_SIGNAL_TOKENS)

    query_hits = candidate.get("query_hits", 0)
    stars = candidate.get("stars") or 0

    score = 1
    score += min(query_hits, 4)

    if len(overlap) >= 4:
        score += 3
    elif len(overlap) >= 2:
        score += 2
    elif overlap:
        score += 1
    else:
        score -= 2

    if stars >= 1000:
        score += 2
    elif stars >= 100:
        score += 1

    if candidate.get("archived"):
        score -= 2
    if candidate.get("is_fork"):
        score -= 1

    description = candidate.get("description", "")
    if description == "No description provided.":
        score -= 1

    if negative_signals:
        score -= min(2, len(negative_signals))

    score = max(1, min(10, score))

    rationale_bits = [f"Matched {query_hits} quer{'y' if query_hits == 1 else 'ies'}"]
    if overlap:
        rationale_bits.append(f"contains {len(overlap)} domain term{'s' if len(overlap) != 1 else ''} in repo text")
    else:
        rationale_bits.append("shows little direct domain terminology")
    if stars >= 1000:
        rationale_bits.append("has strong GitHub adoption")
    elif stars >= 100:
        rationale_bits.append("has some GitHub adoption")
    if negative_signals:
        rationale_bits.append(f"penalized for {', '.join(negative_signals[:2])}-style signals")
    if candidate.get("archived"):
        rationale_bits.append("archived repo penalty")
    if candidate.get("is_fork"):
        rationale_bits.append("fork penalty")

    return score, "; ".join(rationale_bits) + "."


def load_subdomain(config_path: Path, subdomain_id: str) -> dict:
    """Load one sub-domain definition from swarm-config.json."""
    config = json.loads(config_path.read_text())
    for subdomain in config.get("sub_domains", []):
        if subdomain.get("id") == subdomain_id:
            return subdomain
    raise KeyError(f"Unknown subdomain id: {subdomain_id}")


def run_json_command(command: list[str]) -> dict:
    """Run a command that emits JSON to stdout."""
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    stdout = result.stdout.strip()
    if stdout == "No results found.":
        return {"success": True, "data": {"web": []}}
    return json.loads(stdout)


def search_query(query: str, per_query_limit: int) -> list[str]:
    """Run Firecrawl search for one query and return canonical repo URLs."""
    payload = run_json_command(
        [
            "firecrawl",
            "search",
            query,
            "--limit",
            str(per_query_limit),
            "--categories",
            "github",
            "--json",
        ]
    )
    return extract_repo_urls(payload)


def fetch_repo_meta(repo_url: str) -> dict | None:
    """Fetch repo metadata from the GitHub API via gh CLI."""
    owner_repo = repo_url.removeprefix("https://github.com/")
    try:
        return run_json_command(["gh", "api", f"repos/{owner_repo}"])
    except subprocess.CalledProcessError:
        return None


def gather_candidates(
    config_path: Path,
    subdomain_id: str,
    per_query_limit: int,
    max_candidates: int,
) -> list[dict]:
    """Search all queries for a sub-domain and build a ranked candidate list."""
    subdomain = load_subdomain(config_path, subdomain_id)
    url_hits: dict[str, int] = defaultdict(int)
    url_queries: dict[str, list[str]] = defaultdict(list)
    discovery_order: list[str] = []

    for query in subdomain.get("queries", []):
        for repo_url in search_query(query, per_query_limit):
            if repo_url not in url_hits:
                discovery_order.append(repo_url)
            url_hits[repo_url] += 1
            if query not in url_queries[repo_url]:
                url_queries[repo_url].append(query)

    ranked_urls = sorted(
        discovery_order,
        key=lambda url: (-url_hits[url], discovery_order.index(url)),
    )[:max_candidates]

    candidates: list[dict] = []
    for repo_url in ranked_urls:
        meta = fetch_repo_meta(repo_url)
        if not meta:
            continue
        entry = build_entry_from_github_meta(meta, subdomain_id)
        entry["query_hits"] = url_hits[repo_url]
        entry["matched_queries"] = url_queries[repo_url]
        entry["is_fork"] = meta.get("fork", False)
        entry["archived"] = meta.get("archived", False)
        candidates.append(entry)

    candidates.sort(key=lambda entry: (-entry["query_hits"], -(entry.get("stars") or 0), entry["name"]))
    return candidates


def build_discovery_entries(
    config_path: Path,
    subdomain_id: str,
    per_query_limit: int,
    max_candidates: int,
) -> list[dict]:
    """Search, rank, and emit discovery entries that match the workflow contract."""
    subdomain = load_subdomain(config_path, subdomain_id)
    domain_terms = extract_domain_terms(subdomain)
    candidates = gather_candidates(
        config_path=config_path,
        subdomain_id=subdomain_id,
        per_query_limit=per_query_limit,
        max_candidates=max_candidates,
    )

    discovery_entries: list[dict] = []
    for candidate in candidates:
        score, rationale = score_candidate(candidate, domain_terms)
        discovery_entries.append(
            {
                "repo_url": candidate["repo_url"],
                "name": candidate["name"],
                "description": candidate["description"],
                "sub_domain": candidate["sub_domain"],
                "score": score,
                "score_rationale": rationale,
                "stars": candidate.get("stars"),
                "language": candidate.get("language"),
                "license": candidate.get("license"),
                "last_activity": candidate.get("last_activity"),
            }
        )

    discovery_entries.sort(
        key=lambda entry: (-entry["score"], -(entry.get("stars") or 0), entry["name"])
    )
    return discovery_entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover GitHub repo candidates for one sub-domain")
    parser.add_argument("--config", required=True, help="Path to swarm-config.json")
    parser.add_argument("--subdomain-id", required=True, help="Sub-domain id from swarm-config.json")
    parser.add_argument("--output", required=True, help="Where to write the candidate JSON")
    parser.add_argument(
        "--mode",
        choices=["discovery", "candidates"],
        default="discovery",
        help="Emit workflow discovery entries or raw candidate entries",
    )
    parser.add_argument("--per-query-limit", type=int, default=8, help="Firecrawl result limit per query")
    parser.add_argument("--max-candidates", type=int, default=30, help="Max unique repos to keep")
    args = parser.parse_args()

    if args.mode == "candidates":
        payload = gather_candidates(
            config_path=Path(args.config),
            subdomain_id=args.subdomain_id,
            per_query_limit=args.per_query_limit,
            max_candidates=args.max_candidates,
        )
    else:
        payload = build_discovery_entries(
            config_path=Path(args.config),
            subdomain_id=args.subdomain_id,
            per_query_limit=args.per_query_limit,
            max_candidates=args.max_candidates,
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"subdomain_id": args.subdomain_id, "candidate_count": len(payload), "output": str(output_path)}))


if __name__ == "__main__":
    main()
