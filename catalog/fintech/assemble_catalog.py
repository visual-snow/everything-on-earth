#!/usr/bin/env python3
"""Build the fintech catalog from per-domain discovery outputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))

from catalog_assembler import (  # type: ignore  # noqa: E402
    CatalogSpec,
    RelevanceGate,
    build_catalog as _build_catalog,
    enrich_entries as _enrich_entries,
    extract_tags as _extract_tags,
    passes_relevance_gate as _passes_relevance_gate,
    run_cli,
)


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


RELEVANCE = RelevanceGate(
    rules=RELEVANCE_RULES,
    global_meta_rejects=GLOBAL_META_REJECTS,
    min_score=MIN_FINAL_DISCOVERY_SCORE,
)

SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    tag_aliases=TAG_ALIASES,
    extra_accept_tags=frozenset(TAG_ALIASES.values()),
    relevance=RELEVANCE,
)


def enrich_entries(entries: list[dict], domain_name_by_id: dict[str, str]) -> list[dict]:
    return _enrich_entries(entries, domain_name_by_id, SPEC)


def extract_tags(entry: dict) -> list[str]:
    return _extract_tags(entry, SPEC)


def passes_relevance_gate(entry: dict) -> bool:
    return _passes_relevance_gate(entry, RELEVANCE)


def build_catalog(
    config_path: Path,
    batch_size: int,
    repo_root: Path | None = None,
    sync_site: bool = False,
) -> Path:
    return _build_catalog(config_path, batch_size, SPEC, repo_root=repo_root, sync_site=sync_site)


def main() -> None:
    run_cli(SPEC, domain="fintech")


if __name__ == "__main__":
    main()
