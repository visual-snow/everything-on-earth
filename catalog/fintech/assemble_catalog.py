#!/usr/bin/env python3
"""Build the fintech catalog from per-domain discovery outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE_ROOT))

from pipeline import run_dedup, run_finalize, run_score, run_site  # type: ignore  # noqa: E402
from utils import load_catalog  # type: ignore  # noqa: E402


STOPWORDS = {
    "accounting",
    "analysis",
    "analytics",
    "api",
    "bank",
    "banking",
    "data",
    "engine",
    "finance",
    "financial",
    "fintech",
    "github",
    "open",
    "opensource",
    "platform",
    "protocol",
    "software",
    "source",
    "system",
    "systems",
    "tool",
    "tooling",
    "tools",
}

KEYWORDS = {
    "4337",
    "account-abstraction",
    "accounting",
    "actuarial",
    "aml",
    "amm",
    "billing",
    "credit",
    "defi",
    "derivatives",
    "dex",
    "erc-4337",
    "fedwire",
    "fibo",
    "fix",
    "fpml",
    "fraud",
    "invoicing",
    "iso-20022",
    "iso-8583",
    "kyc",
    "ledger",
    "market-data",
    "multisig",
    "open-banking",
    "payments",
    "portfolio",
    "psd2",
    "quant",
    "reconciliation",
    "settlement",
    "stablecoin",
    "subscriptions",
    "swift",
    "tax",
    "tokenization",
    "wallet",
    "xbrl",
    "yield-curve",
}

DOMAIN_TAG_HINTS = {
    "payment-processing-gateways": ["payments", "payment-gateway", "checkout", "payment-routing"],
    "billing-subscription-invoicing": ["billing", "subscriptions", "invoicing", "usage-metering"],
    "core-banking-ledger": ["ledger", "core-banking", "double-entry", "transaction-engine"],
    "open-banking-psd2": ["open-banking", "psd2", "account-aggregation", "embedded-finance"],
    "financial-messaging-protocols": ["swift", "fix", "iso-20022", "iso-8583"],
    "defi-lending-borrowing": ["defi", "lending", "borrowing", "stablecoin"],
    "amm-dex-trading-infra": ["amm", "dex", "routing", "market-making"],
    "blockchain-analytics-indexing": ["blockchain-analytics", "indexing", "subgraph", "mev"],
    "smart-contract-security": ["smart-contracts", "security", "fuzzing", "formal-verification"],
    "wallet-infra-tokenization": ["wallet", "multisig", "erc-4337", "tokenization"],
    "credit-scoring-risk-modeling": ["credit", "risk-modeling", "scorecards", "underwriting"],
    "fraud-detection-prevention": ["fraud", "anomaly-detection", "risk-scoring", "transaction-monitoring"],
    "aml-kyc-identity": ["aml", "kyc", "sanctions", "identity"],
    "insurance-actuarial-tech": ["insurance", "actuarial", "claims", "cat-modeling"],
    "accounting-bookkeeping": ["accounting", "bookkeeping", "double-entry", "general-ledger"],
    "financial-market-data": ["market-data", "research-terminal", "symbol-master", "corporate-actions"],
    "regulatory-reporting-compliance": ["regulatory-reporting", "regtech", "compliance", "trade-reporting"],
    "financial-document-processing": ["document-processing", "ocr", "xbrl", "statement-parsing"],
    "financial-data-standards": ["xbrl", "fpml", "fibo", "financial-ontology"],
    "reconciliation-settlement": ["reconciliation", "settlement", "clearing", "transaction-matching"],
    "quant-pricing-derivatives": ["quant", "derivatives", "greeks", "yield-curve"],
    "portfolio-optimization-allocation": ["portfolio", "optimization", "asset-allocation", "risk-parity"],
    "personal-finance-budgeting": ["personal-finance", "budgeting", "expense-tracking", "envelope-budgeting"],
    "financial-ai-nlp": ["financial-ai", "financial-nlp", "sentiment", "llm"],
    "tax-calculation-filing": ["tax", "calculation", "filing", "multi-jurisdiction"],
}

TAG_ALIASES = {
    "4337": "erc-4337",
    "abstraction": "account-abstraction",
    "ach": "ach",
    "accounts": "accounting",
    "amm": "amm",
    "billing": "billing",
    "bookkeeping": "bookkeeping",
    "cdp": "stablecoin",
    "credit": "credit",
    "defi": "defi",
    "derivative": "derivatives",
    "derivatives": "derivatives",
    "dex": "dex",
    "fedwire": "fedwire",
    "fibo": "fibo",
    "fix": "fix",
    "fpml": "fpml",
    "fraud": "fraud",
    "greeks": "greeks",
    "invoices": "invoicing",
    "iso20022": "iso-20022",
    "iso8583": "iso-8583",
    "kyb": "kyc",
    "kyc": "kyc",
    "ledger": "ledger",
    "lending": "lending",
    "metring": "usage-metering",
    "multisig": "multisig",
    "nlp": "financial-nlp",
    "ocr": "ocr",
    "openbanking": "open-banking",
    "payments": "payments",
    "portfolio": "portfolio",
    "psd2": "psd2",
    "quantlib": "quant",
    "reconciliation": "reconciliation",
    "settlement": "settlement",
    "stablecoins": "stablecoin",
    "subscriptions": "subscriptions",
    "swift": "swift",
    "tokenization": "tokenization",
    "wallet": "wallet",
    "xbrl": "xbrl",
}

RELEVANCE_RULES = {
    "payment-processing-gateways": [
        ["payment", "payments", "merchant", "checkout", "payout", "payin"],
        ["gateway", "processor", "processing", "switch", "routing", "acquiring", "acquirer", "provider"],
    ],
    "billing-subscription-invoicing": [
        ["billing", "invoice", "invoicing", "subscription", "recurring", "metering", "usage based"],
    ],
    "core-banking-ledger": [
        ["ledger", "double entry", "transaction engine"],
        ["bank", "banking", "financial", "fintech", "transaction", "core"],
    ],
    "open-banking-psd2": [
        ["open banking", "psd2", "xs2a", "open finance", "account aggregation", "ais", "pis"],
    ],
    "financial-messaging-protocols": [
        ["iso 20022", "iso20022", "iso 8583", "iso8583", "swift", "fedwire", "ach", "fix"],
    ],
    "defi-lending-borrowing": [
        ["defi", "lending", "borrow", "stablecoin", "flash loan", "cdp", "collateral"],
    ],
    "amm-dex-trading-infra": [
        ["amm", "dex", "swap", "liquidity", "order book", "orderbook", "market maker", "pool", "router"],
    ],
    "blockchain-analytics-indexing": [
        ["blockchain", "on chain", "onchain", "subgraph", "indexer", "mev", "forensics", "crypto"],
    ],
    "smart-contract-security": [
        ["smart contract", "solidity", "evm", "audit", "fuzz", "fuzzer", "formal verification", "symbolic execution", "foundry", "slither", "echidna"],
    ],
    "wallet-infra-tokenization": [
        ["wallet", "multisig", "custody", "erc 4337", "account abstraction", "tokenization", "rwa", "security token", "mpc"],
    ],
    "credit-scoring-risk-modeling": [
        ["credit", "scorecard", "underwriting", "pd", "lgd", "ead", "risk model", "default"],
    ],
    "fraud-detection-prevention": [
        ["fraud", "chargeback"],
        ["transaction", "payment", "payments", "financial", "bank", "banking", "merchant", "card"],
    ],
    "aml-kyc-identity": [
        ["aml", "kyc", "kyb", "sanctions", "watchlist", "pep", "identity verification", "transaction monitoring"],
    ],
    "insurance-actuarial-tech": [
        ["insurance", "actuarial", "claims", "reserving", "policy", "underwriting", "catastrophe"],
    ],
    "accounting-bookkeeping": [
        ["accounting", "bookkeeping", "beancount", "hledger", "ledger", "journal", "expense tracker", "personal finance"],
    ],
    "financial-market-data": [
        ["market data", "ticker", "quote", "ohlcv", "symbol", "terminal", "financial data", "stock", "equity", "price"],
    ],
    "regulatory-reporting-compliance": [
        ["regulatory", "reporting", "compliance", "basel", "mifid", "dodd", "trace", "regtech", "trade reporting", "common domain model", "cdm"],
        ["financial", "trade", "market", "bank", "banking", "finos"],
    ],
    "financial-document-processing": [
        ["invoice", "statement", "xbrl", "edgar", "filing", "10 k", "10 q", "sec"],
        ["ocr", "parser", "extract", "extraction", "document"],
    ],
    "financial-data-standards": [
        ["xbrl", "fpml", "fibo", "common domain model", "cdm", "legend", "morphir", "ontology", "schema", "standard"],
    ],
    "reconciliation-settlement": [
        ["reconciliation", "reconcile", "settlement", "clearing", "matching", "matcher"],
        ["transaction", "payment", "payments", "ledger", "provider", "wire", "bank", "banking"],
    ],
    "quant-pricing-derivatives": [
        ["option", "options", "derivative", "swap", "greeks", "yield curve", "interest rate", "fixed income", "pricing", "quantlib"],
    ],
    "portfolio-optimization-allocation": [
        ["portfolio", "allocation", "optimization", "risk parity", "black litterman", "mean variance", "hrp", "robo"],
    ],
    "personal-finance-budgeting": [
        ["personal finance", "budget", "budgeting", "expense", "expense tracker", "envelope", "money manager"],
    ],
    "financial-ai-nlp": [
        ["financial", "finance", "market", "earnings", "stock", "trading"],
        ["nlp", "llm", "bert", "sentiment", "language model", "news", "transcript", "ai"],
    ],
    "tax-calculation-filing": [
        ["tax", "vat", "sales tax", "income tax", "filing", "efile", "e filing", "irs", "1040"],
    ],
}

GLOBAL_META_REJECTS = [
    "curated list",
    "research project",
    "webinar",
]
MIN_FINAL_DISCOVERY_SCORE = 4


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def load_discovery_entries(config: dict, repo_root: Path) -> list[dict]:
    entries: list[dict] = []
    missing: list[str] = []
    for subdomain in config["sub_domains"]:
        discovery_path = repo_root / config["discovery_dir"] / f"{subdomain['id']}.json"
        if not discovery_path.exists():
            missing.append(subdomain["id"])
            continue
        payload = json.loads(discovery_path.read_text())
        if not isinstance(payload, list):
            raise ValueError(f"{discovery_path} does not contain a JSON array")
        entries.extend(normalize_discovery_entry(entry) for entry in payload)
    if missing:
        raise FileNotFoundError("Missing discovery outputs for: " + ", ".join(missing))
    return entries


def chunked(items: list[dict], batch_size: int) -> list[list[dict]]:
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def canonical_repo_name(repo_url: str, fallback: str) -> str:
    parts = [part for part in urlparse(repo_url).path.split("/") if part]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return fallback


def normalize_discovery_entry(entry: dict) -> dict:
    normalized = dict(entry)
    repo_url = normalized.get("repo_url", "")
    normalized["name"] = canonical_repo_name(repo_url, normalized.get("name", ""))
    last_activity = normalized.get("last_activity")
    if isinstance(last_activity, str) and len(last_activity) >= 10:
        normalized["last_activity"] = last_activity[:10]
    description = (normalized.get("description") or "").strip()
    normalized["description"] = description or "No description provided."
    return normalized


def normalize_tag(raw: str) -> str | None:
    raw = raw.strip().lower()
    if not raw or raw in STOPWORDS:
        return None
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    raw = TAG_ALIASES.get(raw, raw)
    if not raw or raw in STOPWORDS or len(raw) < 3:
        return None
    return raw


def normalize_text(raw: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", raw.lower()).split())


def passes_relevance_gate(entry: dict) -> bool:
    text = normalize_text(" ".join([
        entry.get("name", ""),
        entry.get("description", ""),
    ]))
    if any(flag in text for flag in GLOBAL_META_REJECTS):
        return False
    if "awesome " in text or text.startswith("awesome "):
        return False

    groups = RELEVANCE_RULES.get(entry.get("sub_domain", ""))
    if not groups:
        return True

    for group in groups:
        normalized_group = [normalize_text(phrase) for phrase in group]
        if not any(phrase and phrase in text for phrase in normalized_group):
            return False
    return True


def filter_relevant_entries(entries: list[dict]) -> list[dict]:
    return [
        entry
        for entry in entries
        if passes_relevance_gate(entry) and entry.get("score", 0) >= MIN_FINAL_DISCOVERY_SCORE
    ]


def extract_tags(entry: dict) -> list[str]:
    primary_domain = entry.get("sub_domain", "unknown")
    ordered: list[str] = []
    seen: set[str] = set()

    for hint in DOMAIN_TAG_HINTS.get(primary_domain, []):
        if hint not in seen:
            ordered.append(hint)
            seen.add(hint)

    text = " ".join([
        entry.get("name", ""),
        entry.get("description", ""),
    ]).lower()
    for token in re.split(r"[^a-z0-9]+", text):
        tag = normalize_tag(token)
        if not tag or tag in seen:
            continue
        if tag in KEYWORDS or tag in TAG_ALIASES.values():
            ordered.append(tag)
            seen.add(tag)

    return ordered[:6]


def summarize(description: str) -> str:
    description = (description or "").strip() or "No description provided."
    if len(description) <= 140:
        return description
    return description[:137].rstrip() + "..."


def enrich_entries(entries: list[dict], domain_name_by_id: dict[str, str]) -> list[dict]:
    enriched: list[dict] = []
    for entry in entries:
        primary_domain = entry.get("sub_domain", "unknown")
        category = domain_name_by_id.get(primary_domain, primary_domain.replace("-", " ").title())
        enriched.append({
            **entry,
            "discovery_score": entry.get("score"),
            "tags": extract_tags(entry),
            "category": category,
            "summary": summarize(entry.get("description", "")),
        })
    return enriched


def render_explorer(
    topic: str,
    output_dir: Path,
    entries: list[dict],
    domain_name_by_id: dict[str, str],
) -> None:
    template_dir = PIPELINE_ROOT / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    payload = []
    for entry in entries:
        primary_domain = entry.get("sub_domain", "unknown")
        payload.append({
            **entry,
            "domain": domain_name_by_id.get(primary_domain, primary_domain.replace("-", " ").title()),
        })
    html = env.get_template("explorer.html").render(
        topic=topic,
        total=len(payload),
        domain_count=len({e["domain"] for e in payload}),
        catalog_json=json.dumps(payload),
    )
    (output_dir / "explorer.html").write_text(html)


def sync_entry_layout(output_dir: Path) -> None:
    entries = load_catalog(output_dir / "catalog.json")
    write_json(output_dir / "catalog.json", entries)
    for entry in entries:
        slug_dir = output_dir / entry["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)
        write_json(slug_dir / "entry.json", entry)


def build_catalog(
    config_path: Path,
    batch_size: int,
    repo_root: Path | None = None,
    sync_site: bool = False,
) -> Path:
    repo_root = repo_root or REPO_ROOT

    config = load_config(config_path)
    output_dir = repo_root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    domain_name_by_id = {
        subdomain["id"]: subdomain["name"]
        for subdomain in config["sub_domains"]
    }

    raw_entries = load_discovery_entries(config, repo_root=repo_root)
    write_json(output_dir / "raw-discovery.json", raw_entries)

    dedup = run_dedup(raw_entries)
    write_json(output_dir / "dedup.json", dedup)

    relevant = filter_relevant_entries(dedup)
    write_json(output_dir / "relevant.json", relevant)

    scored, _removed = run_score(relevant)
    write_json(output_dir / "scored.json", scored)

    batches = chunked(scored, batch_size)
    enriched_batches: list[list[dict]] = []
    width = max(1, len(str(len(batches) or 1)))
    for idx, batch in enumerate(batches, start=1):
        batch_name = f"{idx:0{width}d}"
        write_json(output_dir / f"enrich-batch-{batch_name}.json", batch)
        enriched_batch = enrich_entries(batch, domain_name_by_id)
        enriched_batches.append(enriched_batch)
        write_json(output_dir / f"enriched-batch-{batch_name}.json", enriched_batch)

    enriched = [entry for batch in enriched_batches for entry in batch]
    if len(enriched) != len(scored):
        raise ValueError("Enrichment changed the entry count")
    write_json(output_dir / "enriched.json", enriched)

    run_finalize(
        enriched,
        topic=config["topic"],
        output_dir=output_dir,
        template_dir=PIPELINE_ROOT / "templates",
    )
    render_explorer(config["topic"], output_dir, enriched, domain_name_by_id)
    sync_entry_layout(output_dir)

    if sync_site:
        run_site(repo_root / "catalog", template_dir=PIPELINE_ROOT / "templates")

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble the fintech catalog from discovery outputs")
    parser.add_argument(
        "--config",
        default=str(Path("catalog") / "fintech" / "swarm-config.json"),
        help="Path to fintech swarm-config.json",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=40,
        help="Batch size used when producing enrich-batch-*.json files",
    )
    parser.add_argument(
        "--sync-site",
        action="store_true",
        help="Regenerate the global catalog site after building fintech",
    )
    args = parser.parse_args()

    build_catalog(
        REPO_ROOT / args.config,
        batch_size=args.batch_size,
        sync_site=args.sync_site,
    )


if __name__ == "__main__":
    main()
