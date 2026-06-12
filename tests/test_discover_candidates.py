"""Tests for the trading discovery candidate helper."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from discover_candidates import (  # type: ignore
    build_entry_from_github_meta,
    build_discovery_entries,
    extract_domain_terms,
    extract_repo_urls,
    gather_candidates,
    normalize_github_repo_url,
    run_json_command,
    score_candidate,
)


def test_normalize_github_repo_url_root_and_subpath():
    assert (
        normalize_github_repo_url("https://github.com/Kernc/backtesting.py/tree/master")
        == "https://github.com/kernc/backtesting.py"
    )


def test_normalize_github_repo_url_rejects_non_repo_pages():
    assert normalize_github_repo_url("https://github.com/topics/backtesting-frameworks") is None
    assert normalize_github_repo_url("https://github.com/search?q=vectorbt") is None
    assert normalize_github_repo_url("https://gitlab.com/pallets/flask") is None


def test_extract_repo_urls_filters_and_dedups():
    payload = {
        "data": {
            "web": [
                {"url": "https://github.com/topics/backtesting-frameworks"},
                {"url": "https://github.com/kernc/backtesting.py"},
                {"url": "https://github.com/Kernc/backtesting.py/tree/master"},
                {"url": "https://github.com/mementum/backtrader/issues"},
            ]
        }
    }
    assert extract_repo_urls(payload) == [
        "https://github.com/kernc/backtesting.py",
        "https://github.com/mementum/backtrader",
    ]


def test_build_entry_from_github_meta_maps_fields():
    meta = {
        "full_name": "kernc/backtesting.py",
        "html_url": "https://github.com/kernc/backtesting.py",
        "description": "Backtest trading strategies in Python.",
        "stargazers_count": 8104,
        "language": "Python",
        "license": {"spdx_id": "AGPL-3.0"},
        "pushed_at": "2025-12-20T17:50:49Z",
    }
    entry = build_entry_from_github_meta(meta, "backtesting-frameworks")
    assert entry == {
        "repo_url": "https://github.com/kernc/backtesting.py",
        "name": "kernc/backtesting.py",
        "description": "Backtest trading strategies in Python.",
        "sub_domain": "backtesting-frameworks",
        "stars": 8104,
        "language": "Python",
        "license": "AGPL-3.0",
        "last_activity": "2025-12-20",
    }


def test_build_entry_from_github_meta_handles_missing_optionals():
    meta = {
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "description": "",
        "stargazers_count": 0,
        "language": None,
        "license": None,
        "pushed_at": None,
    }
    entry = build_entry_from_github_meta(meta, "paper-trading-simulation")
    assert entry["description"] == "No description provided."
    assert entry["license"] is None
    assert entry["last_activity"] is None


def test_score_candidate_rewards_domain_overlap_and_query_hits():
    subdomain = {
        "queries": [
            "carbon accounting ghg protocol open source github",
            "scope 1 scope 2 scope 3 emissions tracking github",
        ]
    }
    candidate = {
        "name": "mlco2/codecarbon",
        "description": "Track emissions from compute workloads and estimate carbon impact.",
        "query_hits": 4,
        "matched_queries": subdomain["queries"],
        "stars": 1757,
        "is_fork": False,
        "archived": False,
    }

    score, rationale = score_candidate(candidate, extract_domain_terms(subdomain))

    assert score >= 8
    assert "Matched 4 queries" in rationale
    assert "strong GitHub adoption" in rationale


def test_score_candidate_penalizes_off_topic_match():
    subdomain = {
        "queries": [
            "scope 1 scope 2 scope 3 emissions tracking github",
        ]
    }
    candidate = {
        "name": "httpwg/admin",
        "description": "When you want to speak to the manager.",
        "query_hits": 1,
        "matched_queries": subdomain["queries"],
        "stars": 15,
        "is_fork": False,
        "archived": False,
    }

    score, rationale = score_candidate(candidate, extract_domain_terms(subdomain))

    assert score <= 2
    assert "little direct domain terminology" in rationale


def test_build_discovery_entries_outputs_contract_shape(tmp_path, monkeypatch):
    config_path = tmp_path / "swarm-config.json"
    config_path.write_text(
        """
        {
          "sub_domains": [
            {
              "id": "carbon-accounting-ghg",
              "queries": [
                "carbon accounting ghg protocol open source github",
                "scope 1 scope 2 scope 3 emissions tracking github"
              ]
            }
          ]
        }
        """
    )

    fake_candidates = [
        {
            "repo_url": "https://github.com/mlco2/codecarbon",
            "name": "mlco2/codecarbon",
            "description": "Track emissions from compute workloads and estimate carbon impact.",
            "sub_domain": "carbon-accounting-ghg",
            "stars": 1757,
            "language": "Python",
            "license": "MIT",
            "last_activity": "2026-03-24",
            "query_hits": 4,
            "matched_queries": [
                "carbon accounting ghg protocol open source github",
                "scope 1 scope 2 scope 3 emissions tracking github"
            ],
            "is_fork": False,
            "archived": False,
        }
    ]

    monkeypatch.setattr("discover_candidates.gather_candidates", lambda **_: fake_candidates)

    discovery_entries = build_discovery_entries(
        config_path=config_path,
        subdomain_id="carbon-accounting-ghg",
        per_query_limit=8,
        max_candidates=30,
    )

    assert discovery_entries == [
        {
            "repo_url": "https://github.com/mlco2/codecarbon",
            "name": "mlco2/codecarbon",
            "description": "Track emissions from compute workloads and estimate carbon impact.",
            "sub_domain": "carbon-accounting-ghg",
            "score": discovery_entries[0]["score"],
            "score_rationale": discovery_entries[0]["score_rationale"],
            "stars": 1757,
            "language": "Python",
            "license": "MIT",
            "last_activity": "2026-03-24",
        }
    ]
    assert 1 <= discovery_entries[0]["score"] <= 10
    assert discovery_entries[0]["score_rationale"]


def test_gather_candidates_skips_missing_repo_metadata(tmp_path, monkeypatch):
    config_path = tmp_path / "swarm-config.json"
    config_path.write_text(
        """
        {
          "sub_domains": [
            {
              "id": "carbon-accounting-ghg",
              "queries": [
                "carbon accounting ghg protocol open source github"
              ]
            }
          ]
        }
        """
    )

    monkeypatch.setattr(
        "discover_candidates.search_query",
        lambda query, per_query_limit: [
            "https://github.com/mlco2/codecarbon",
            "https://github.com/missing/repo",
        ],
    )
    monkeypatch.setattr(
        "discover_candidates.fetch_repo_meta",
        lambda repo_url: (
            {
                "full_name": "mlco2/codecarbon",
                "html_url": "https://github.com/mlco2/codecarbon",
                "description": "Track emissions from compute workloads.",
                "stargazers_count": 1757,
                "language": "Python",
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-03-24T18:12:55Z",
                "fork": False,
                "archived": False,
            }
            if repo_url == "https://github.com/mlco2/codecarbon"
            else None
        ),
    )

    candidates = gather_candidates(
        config_path=config_path,
        subdomain_id="carbon-accounting-ghg",
        per_query_limit=8,
        max_candidates=30,
    )

    assert [candidate["name"] for candidate in candidates] == ["mlco2/codecarbon"]


def test_run_json_command_treats_no_results_stdout_as_empty_payload(monkeypatch):
    class Result:
        stdout = "No results found.\n"

    monkeypatch.setattr("discover_candidates.subprocess.run", lambda *args, **kwargs: Result())

    payload = run_json_command(["firecrawl", "search", "nope", "--json"])

    assert payload == {"success": True, "data": {"web": []}}
