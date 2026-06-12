"""Tests for the fintech catalog scaffold and assembly flow."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _load_fintech_assembler():
    module_path = ROOT / "catalog" / "fintech" / "assemble_catalog.py"
    spec = importlib.util.spec_from_file_location("fintech_assemble_catalog", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_fintech_config_has_expected_subdomains_and_waves():
    config_path = ROOT / "catalog" / "fintech" / "swarm-config.json"

    config = json.loads(config_path.read_text())
    subdomain_ids = [subdomain["id"] for subdomain in config["sub_domains"]]
    wave_ids = [wave["id"] for wave in config["waves"]]

    assert config["topic_slug"] == "fintech"
    assert config["output_dir"] == "catalog/fintech"
    assert config["discovery_dir"] == "catalog/fintech/discovery"
    assert config["orchestration"]["wave_count"] == 5
    assert config["orchestration"]["parallel_agents_per_wave"] == 5
    assert subdomain_ids == [
        "payment-processing-gateways",
        "billing-subscription-invoicing",
        "core-banking-ledger",
        "open-banking-psd2",
        "financial-messaging-protocols",
        "defi-lending-borrowing",
        "amm-dex-trading-infra",
        "blockchain-analytics-indexing",
        "smart-contract-security",
        "wallet-infra-tokenization",
        "credit-scoring-risk-modeling",
        "fraud-detection-prevention",
        "aml-kyc-identity",
        "insurance-actuarial-tech",
        "accounting-bookkeeping",
        "financial-market-data",
        "regulatory-reporting-compliance",
        "financial-document-processing",
        "financial-data-standards",
        "reconciliation-settlement",
        "quant-pricing-derivatives",
        "portfolio-optimization-allocation",
        "personal-finance-budgeting",
        "financial-ai-nlp",
        "tax-calculation-filing",
    ]
    assert wave_ids == ["wave-1", "wave-2", "wave-3", "wave-4", "wave-5"]
    assert all(len(wave["subdomains"]) == 5 for wave in config["waves"])


def test_fintech_enrichment_uses_primary_sub_domain_for_category():
    module = _load_fintech_assembler()

    entry = {
        "repo_url": "https://github.com/tigerbeetle/tigerbeetle",
        "name": "tigerbeetle/tigerbeetle",
        "description": "A distributed financial transactions database designed for mission critical safety and performance.",
        "sub_domain": "core-banking-ledger",
        "found_in_domains": ["core-banking-ledger", "reconciliation-settlement"],
        "score": 10,
    }
    domain_name_by_id = {
        "core-banking-ledger": "Core Banking / Ledger",
        "reconciliation-settlement": "Reconciliation / Settlement",
    }

    enriched = module.enrich_entries([entry], domain_name_by_id)

    assert enriched[0]["category"] == "Core Banking / Ledger"
    assert enriched[0]["summary"]
    assert "ledger" in enriched[0]["tags"]


def test_fintech_build_catalog_writes_expected_artifacts(tmp_path):
    module = _load_fintech_assembler()

    config_path = tmp_path / "catalog" / "fintech" / "swarm-config.json"
    discovery_dir = tmp_path / "catalog" / "fintech" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "payment-processing-gateways.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/medusajs/medusa",
                    "name": "medusajs/medusa",
                    "description": "Open-source commerce engine with modular payment provider integrations and checkout workflows.",
                    "sub_domain": "payment-processing-gateways",
                    "score": 9,
                    "score_rationale": "Strong payment orchestration and checkout focus with real ecosystem adoption.",
                    "stars": 28000,
                    "language": "TypeScript",
                    "license": "MIT",
                    "last_activity": "2026-03-25",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Fintech Test Catalog",
                "topic_slug": "fintech",
                "output_dir": "catalog/fintech",
                "discovery_dir": "catalog/fintech/discovery",
                "sub_domains": [
                    {
                        "id": "payment-processing-gateways",
                        "name": "Payment Processing / Gateways",
                        "queries": [],
                    }
                ],
            }
        )
    )

    module.build_catalog(
        config_path=config_path,
        batch_size=10,
        repo_root=tmp_path,
        sync_site=False,
    )

    output_dir = tmp_path / "catalog" / "fintech"
    assert (output_dir / "raw-discovery.json").exists()
    assert (output_dir / "dedup.json").exists()
    assert (output_dir / "scored.json").exists()
    assert (output_dir / "enriched.json").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "RESULTS.md").exists()
    assert (output_dir / "explorer.html").exists()
    assert (output_dir / "medusajs-medusa" / "entry.json").exists()


def test_fintech_relevance_gate_filters_obvious_false_positives():
    module = _load_fintech_assembler()

    relevant = {
        "repo_url": "https://github.com/formancehq/reconciliation",
        "name": "formancehq/reconciliation",
        "description": "Open-source reconciliation service for matching ledger transactions against payment provider data.",
        "sub_domain": "reconciliation-settlement",
    }
    off_topic = {
        "repo_url": "https://github.com/openrefine/openrefine",
        "name": "openrefine/openrefine",
        "description": "Free, open source power tool for working with messy data and improving it.",
        "sub_domain": "reconciliation-settlement",
    }
    ledger_false_positive = {
        "repo_url": "https://github.com/pimterry/loglevel",
        "name": "pimterry/loglevel",
        "description": "Minimal lightweight logging for JavaScript, adding reliable log level methods to wrap any available console.log methods.",
        "sub_domain": "core-banking-ledger",
    }

    assert module.passes_relevance_gate(relevant) is True
    assert module.passes_relevance_gate(off_topic) is False
    assert module.passes_relevance_gate(ledger_false_positive) is False


def test_fintech_build_catalog_excludes_low_score_tail(tmp_path):
    module = _load_fintech_assembler()

    config_path = tmp_path / "catalog" / "fintech" / "swarm-config.json"
    discovery_dir = tmp_path / "catalog" / "fintech" / "discovery"
    discovery_dir.mkdir(parents=True)
    (discovery_dir / "tax-calculation-filing.json").write_text(
        json.dumps(
            [
                {
                    "repo_url": "https://github.com/ustaxes/ustaxes",
                    "name": "ustaxes/ustaxes",
                    "description": "Free US tax filing software.",
                    "sub_domain": "tax-calculation-filing",
                    "score": 5,
                    "score_rationale": "Clear tax filing fit.",
                    "stars": 120,
                    "language": "Python",
                    "license": "GPL-3.0",
                    "last_activity": "2026-03-25",
                },
                {
                    "repo_url": "https://github.com/janimiyarj/ai-tax-agent",
                    "name": "janimiyarj/ai-tax-agent",
                    "description": "An AI tax agent experiment.",
                    "sub_domain": "tax-calculation-filing",
                    "score": 1,
                    "score_rationale": "Barely relevant experiment.",
                    "stars": 4,
                    "language": "Python",
                    "license": "MIT",
                    "last_activity": "2026-03-25",
                }
            ]
        )
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(
            {
                "topic": "Fintech Threshold Test Catalog",
                "topic_slug": "fintech",
                "output_dir": "catalog/fintech",
                "discovery_dir": "catalog/fintech/discovery",
                "sub_domains": [
                    {
                        "id": "tax-calculation-filing",
                        "name": "Tax Calculation / Filing",
                        "queries": [],
                    }
                ],
            }
        )
    )

    output_dir = module.build_catalog(
        config_path=config_path,
        batch_size=10,
        repo_root=tmp_path,
        sync_site=False,
    )

    catalog = json.loads((output_dir / "catalog.json").read_text())

    assert [entry["name"] for entry in catalog] == ["ustaxes/ustaxes"]
