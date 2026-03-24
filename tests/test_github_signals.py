"""Tests for GitHub API signal fetching and composite quality scoring."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from github_signals import GitHubClient, compute_score, fetch_signals, parse_github_url


# --- parse_github_url tests ---


def test_parse_github_url_standard():
    assert parse_github_url("https://github.com/owner/repo") == ("owner", "repo")


def test_parse_github_url_with_git_suffix():
    assert parse_github_url("https://github.com/owner/repo.git") == ("owner", "repo")


def test_parse_github_url_with_path():
    assert parse_github_url("https://github.com/org/repo/tree/main/src") == ("org", "repo")


def test_parse_github_url_gitlab_returns_none():
    assert parse_github_url("https://gitlab.com/owner/repo") is None


def test_parse_github_url_non_github_returns_none():
    assert parse_github_url("https://bitbucket.org/owner/repo") is None


def test_parse_github_url_empty():
    assert parse_github_url("") is None


def test_parse_github_url_http():
    assert parse_github_url("http://github.com/owner/repo") == ("owner", "repo")


# --- compute_score tests ---


def test_compute_score_no_signals():
    """Without GitHub data, score is agent-score-only (max 30)."""
    score = compute_score(10, None)
    assert score == 30.0


def test_compute_score_zero_agent_no_signals():
    score = compute_score(0, None)
    assert score == 0.0


def test_compute_score_full_signals():
    """Full signals should produce a score above agent-only."""
    signals = {
        "stars": 5000,
        "forks": 500,
        "open_issues": 100,
        "subscribers": 200,
        "contributors": 50,
        "releases": 10,
        "last_push": "2026-03-20T00:00:00Z",
        "license_spdx": "MIT",
        "has_readme": True,
        "has_wiki": True,
        "has_pages": True,
        "is_fork": False,
        "size_kb": 10000,
        "archived": False,
        "created_at": "2020-01-01T00:00:00Z",
        "commit_count": None,
    }
    score = compute_score(8, signals)
    assert 60 < score <= 100


def test_compute_score_high_stars_log_scale():
    """100k stars should not be 100x better than 1k stars."""
    signals_1k = _make_signals(stars=1000)
    signals_100k = _make_signals(stars=100000)

    score_1k = compute_score(5, signals_1k)
    score_100k = compute_score(5, signals_100k)

    # 100k should be higher but not dramatically
    assert score_100k > score_1k
    assert score_100k < score_1k * 3  # less than 3x, not 100x


def test_compute_score_recent_vs_stale():
    """Recently pushed repos should score higher than stale ones."""
    signals_recent = _make_signals(last_push="2026-03-20T00:00:00Z")
    signals_stale = _make_signals(last_push="2022-01-01T00:00:00Z")

    score_recent = compute_score(5, signals_recent)
    score_stale = compute_score(5, signals_stale)

    assert score_recent > score_stale


def test_compute_score_always_in_range():
    """Score should always be between 0 and 100."""
    # Maxed out signals
    signals_max = _make_signals(
        stars=500000, forks=50000, contributors=1000,
        releases=100, last_push="2026-03-24T00:00:00Z",
    )
    score = compute_score(10, signals_max)
    assert 0 <= score <= 100

    # Minimal signals
    signals_min = _make_signals(stars=0, forks=0, contributors=0, releases=0)
    score = compute_score(0, signals_min)
    assert 0 <= score <= 100


def test_compute_score_no_readme_loses_doc_points():
    """Repos without README should lose documentation component."""
    signals_with = _make_signals(has_readme=True)
    signals_without = _make_signals(has_readme=False)

    score_with = compute_score(5, signals_with)
    score_without = compute_score(5, signals_without)

    assert score_with > score_without
    assert score_with - score_without == 10.0  # doc component is 10 points


# --- fetch_signals tests ---


@patch("github_signals.GitHubClient")
def test_fetch_signals_success(MockClient):
    client = MockClient()
    client.get_repo.return_value = {
        "stargazers_count": 5000,
        "forks_count": 300,
        "open_issues_count": 42,
        "subscribers_count": 150,
        "pushed_at": "2026-03-20T00:00:00Z",
        "license": {"spdx_id": "MIT"},
        "has_wiki": True,
        "has_pages": False,
        "fork": False,
        "size": 8000,
        "archived": False,
        "created_at": "2020-01-01T00:00:00Z",
    }
    client.get_contributors_count.return_value = 25
    client.get_releases_count.return_value = 12
    client.get_readme_exists.return_value = True

    result = fetch_signals(client, "owner", "repo")

    assert result is not None
    assert result["stars"] == 5000
    assert result["forks"] == 300
    assert result["contributors"] == 25
    assert result["releases"] == 12
    assert result["has_readme"] is True
    assert result["license_spdx"] == "MIT"
    assert result["is_fork"] is False


@patch("github_signals.GitHubClient")
def test_fetch_signals_404(MockClient):
    client = MockClient()
    client.get_repo.return_value = None

    result = fetch_signals(client, "owner", "deleted-repo")
    assert result is None


@patch("github_signals.GitHubClient")
def test_fetch_signals_no_license(MockClient):
    client = MockClient()
    client.get_repo.return_value = {
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
        "subscribers_count": 20,
        "pushed_at": "2025-01-01T00:00:00Z",
        "license": None,
        "has_wiki": False,
        "has_pages": False,
        "fork": False,
        "size": 500,
        "archived": False,
        "created_at": "2023-06-01T00:00:00Z",
    }
    client.get_contributors_count.return_value = 3
    client.get_releases_count.return_value = 0
    client.get_readme_exists.return_value = True

    result = fetch_signals(client, "owner", "repo")
    assert result["license_spdx"] is None


# --- GitHubClient tests ---


def test_github_client_sets_auth_header():
    client = GitHubClient(token="test-token-123")
    assert client.session.headers["Authorization"] == "Bearer test-token-123"


def test_github_client_no_auth_without_token():
    with patch.dict("os.environ", {}, clear=True):
        client = GitHubClient(token=None)
        assert "Authorization" not in client.session.headers


# --- helpers ---


def _make_signals(**overrides) -> dict:
    """Create a signals dict with sensible defaults, overridden by kwargs."""
    defaults = {
        "stars": 100,
        "forks": 20,
        "open_issues": 10,
        "subscribers": 30,
        "contributors": 5,
        "releases": 3,
        "last_push": "2025-06-01T00:00:00Z",
        "license_spdx": "MIT",
        "has_readme": True,
        "has_wiki": False,
        "has_pages": False,
        "is_fork": False,
        "size_kb": 5000,
        "archived": False,
        "created_at": "2022-01-01T00:00:00Z",
        "commit_count": None,
    }
    defaults.update(overrides)
    return defaults
