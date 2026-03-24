"""GitHub API signal fetching and composite quality scoring.

Fetches real signals (stars, forks, contributors, recency, etc.) from
the GitHub API and computes a 0-100 composite quality score per repo.
Replaces the old "prune" step — no soft thresholds, everything stays.
"""

import math
import os
import re
import time
from datetime import datetime, timezone

import requests


def parse_github_url(url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from a GitHub URL. Returns None for non-GitHub URLs."""
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$", url)
    if match:
        return match.group(1), match.group(2)
    return None


class GitHubClient:
    """Thin wrapper around the GitHub REST API with rate limit handling."""

    BASE = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/vnd.github.v3+json"
        self.session.headers["User-Agent"] = "everything-on-earth-pipeline"
        token = token or os.environ.get("GITHUB_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self._remaining = None

    def _request(self, endpoint: str, params: dict | None = None) -> dict | None:
        """Make a GitHub API request with rate limit handling.

        Returns parsed JSON on success, None on 404.
        Raises on other HTTP errors.
        """
        url = f"{self.BASE}{endpoint}"
        resp = self.session.get(url, params=params, timeout=15)

        # Track rate limit from headers
        self._remaining = int(resp.headers.get("X-RateLimit-Remaining", 999))

        if resp.status_code == 404:
            return None

        if resp.status_code == 403 and self._remaining == 0:
            reset_at = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait = max(reset_at - int(time.time()), 1)
            print(f"  [github] Rate limit hit, waiting {wait}s...")
            time.sleep(wait + 1)
            return self._request(endpoint, params)

        resp.raise_for_status()
        return resp.json()

    def _count_from_link_header(self, endpoint: str, params: dict | None = None) -> int:
        """Get total count from paginated endpoint using Link header."""
        params = dict(params or {})
        params["per_page"] = 1
        url = f"{self.BASE}{endpoint}"
        resp = self.session.get(url, params=params, timeout=15)
        self._remaining = int(resp.headers.get("X-RateLimit-Remaining", 999))

        if resp.status_code == 404:
            return 0

        link = resp.headers.get("Link", "")
        match = re.search(r'page=(\d+)>; rel="last"', link)
        if match:
            return int(match.group(1))
        # No Link header means 0 or 1 items
        if resp.status_code == 200:
            data = resp.json()
            return len(data) if isinstance(data, list) else 0
        return 0

    @property
    def remaining(self) -> int | None:
        return self._remaining

    def get_repo(self, owner: str, repo: str) -> dict | None:
        return self._request(f"/repos/{owner}/{repo}")

    def get_contributors_count(self, owner: str, repo: str) -> int:
        return self._count_from_link_header(f"/repos/{owner}/{repo}/contributors", {"anon": "true"})

    def get_releases_count(self, owner: str, repo: str) -> int:
        return self._count_from_link_header(f"/repos/{owner}/{repo}/releases")

    def get_readme_exists(self, owner: str, repo: str) -> bool:
        result = self._request(f"/repos/{owner}/{repo}/readme")
        return result is not None


def fetch_signals(client: GitHubClient, owner: str, repo: str) -> dict | None:
    """Fetch all quality signals for a repo. Returns None if repo is 404."""
    repo_data = client.get_repo(owner, repo)
    if repo_data is None:
        return None

    contributors = client.get_contributors_count(owner, repo)
    releases = client.get_releases_count(owner, repo)
    has_readme = client.get_readme_exists(owner, repo)

    license_obj = repo_data.get("license")
    license_spdx = license_obj.get("spdx_id") if license_obj else None
    if license_spdx == "NOASSERTION":
        license_spdx = None

    return {
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "subscribers": repo_data.get("subscribers_count", 0),
        "contributors": contributors,
        "releases": releases,
        "last_push": repo_data.get("pushed_at"),
        "license_spdx": license_spdx,
        "has_readme": has_readme,
        "has_wiki": repo_data.get("has_wiki", False),
        "has_pages": repo_data.get("has_pages", False),
        "is_fork": repo_data.get("fork", False),
        "size_kb": repo_data.get("size", 0),
        "archived": repo_data.get("archived", False),
        "created_at": repo_data.get("created_at"),
        "commit_count": None,  # expensive, skip for now
    }


def compute_score(agent_score: int, signals: dict | None) -> float:
    """Compute composite quality score 0-100.

    Components (weights sum to 100):
    - Agent relevance (30%): the 0-10 discovery score, scaled to 0-30
    - Community adoption (25%): log-scaled stars + forks
    - Activity recency (20%): exponential decay from last push
    - Ecosystem maturity (15%): contributors, releases, license, wiki/pages
    - Documentation (10%): has_readme
    """
    agent_component = (agent_score / 10.0) * 30

    if signals is None:
        return round(agent_component, 1)

    # Community adoption (0-25): log scale, capped
    stars = signals.get("stars", 0)
    forks = signals.get("forks", 0)
    # log10(100001) ≈ 5, so a 100k-star repo maxes out this component
    star_score = min(math.log10(max(stars, 1) + 1) / 5.0, 1.0)
    fork_score = min(math.log10(max(forks, 1) + 1) / 4.0, 1.0)
    community_component = (star_score * 0.7 + fork_score * 0.3) * 25

    # Activity recency (0-20): exponential decay, half-life ~1 year
    last_push = signals.get("last_push")
    if last_push:
        try:
            push_date = datetime.fromisoformat(last_push.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - push_date).days
            recency_score = math.exp(-days_ago / 365)
        except (ValueError, TypeError):
            recency_score = 0.5
    else:
        recency_score = 0.5
    recency_component = recency_score * 20

    # Ecosystem maturity (0-15)
    contributors = signals.get("contributors", 1)
    releases = signals.get("releases", 0)
    contrib_score = min(math.log10(max(contributors, 1) + 1) / 2.0, 1.0)  # 100 contributors maxes out
    release_score = min(releases / 20.0, 1.0)
    has_license = 1.0 if signals.get("license_spdx") else 0.0
    has_wiki = 0.5 if signals.get("has_wiki") else 0.0
    has_pages = 0.5 if signals.get("has_pages") else 0.0
    maturity_component = (
        contrib_score * 0.4
        + release_score * 0.2
        + has_license * 0.2
        + (has_wiki + has_pages) * 0.2
    ) * 15

    # Documentation (0-10)
    has_readme = 1.0 if signals.get("has_readme") else 0.0
    doc_component = has_readme * 10

    total = agent_component + community_component + recency_component + maturity_component + doc_component
    return round(min(total, 100.0), 1)
