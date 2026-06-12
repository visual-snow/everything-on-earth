#!/usr/bin/env python3
"""Build the legal catalog from per-domain discovery outputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))

from catalog_assembler import (  # type: ignore  # noqa: E402
    CatalogSpec,
    build_catalog as _build_catalog,
    enrich_entries as _enrich_entries,
    extract_tags as _extract_tags,
    run_cli,
)


STOPWORDS = {
    "analysis",
    "analytics",
    "app",
    "application",
    "case",
    "data",
    "github",
    "law",
    "lawyer",
    "lawyers",
    "legal",
    "legaltech",
    "open",
    "opensource",
    "platform",
    "software",
    "source",
    "system",
    "systems",
    "tech",
    "tool",
    "tooling",
    "tools",
}

KEYWORDS = {
    "access",
    "agreement",
    "aml",
    "arbitration",
    "citation",
    "clm",
    "compliance",
    "consent",
    "contract",
    "court",
    "discovery",
    "docket",
    "docassemble",
    "evidence",
    "filing",
    "gdpr",
    "governance",
    "immigration",
    "judicial",
    "justice",
    "kyc",
    "litigation",
    "ontology",
    "patent",
    "privacy",
    "regulatory",
    "sanctions",
    "statute",
    "tax",
    "trademark",
}

DOMAIN_TAG_HINTS = {
    "legal-ai-nlp": ["legal-ai", "legal-nlp", "clause-extraction", "citation"],
    "privacy-data-protection": ["privacy", "gdpr", "dsar", "pii-redaction"],
    "compliance-regulatory-automation": ["compliance", "policy-as-code", "regulatory-change", "audit-controls"],
    "smart-contracts-legal": ["smart-contracts", "computable-contracts", "accord-project", "contract-templates"],
    "contract-analysis-clm": ["contract-analysis", "clm", "clause-review", "redlining"],
    "e-discovery-document-review": ["e-discovery", "document-review", "privilege-review", "redaction"],
    "aml-kyc-identity": ["aml", "kyc", "sanctions", "identity-verification"],
    "legal-research-case-law": ["case-law", "citation", "court-data", "dockets"],
    "legal-document-automation": ["document-automation", "docassemble", "form-assembly", "e-signature"],
    "legal-analytics-prediction": ["legal-analytics", "docket-mining", "judge-analytics", "outcome-prediction"],
    "corporate-governance-entity-mgmt": ["corporate-governance", "entity-management", "cap-table", "board-governance"],
    "court-case-management": ["court-case-management", "e-filing", "docket-management", "judicial-workflow"],
    "access-to-justice-civic-tech": ["access-to-justice", "legal-aid", "self-help", "civic-tech"],
    "ip-patent-trademark": ["patent-search", "trademark", "prior-art", "ip-analytics"],
    "legal-knowledge-ontologies": ["legal-ontology", "knowledge-graph", "akoma-ntoso", "lkif"],
    "digital-forensics-litigation": ["digital-forensics", "chain-of-custody", "evidence-management", "litigation-support"],
    "tax-compliance-automation": ["tax-compliance", "rules-engine", "filing-automation", "vat"],
    "immigration-visa-processing": ["immigration", "visa-processing", "case-intake", "form-automation"],
    "alternative-dispute-resolution": ["odr", "arbitration", "mediation", "dispute-resolution"],
    "legal-practice-management": ["practice-management", "matter-management", "timekeeping", "billing"],
    "curated-lists-meta-sweep": ["awesome-list", "legal-data", "legal-nlp", "privacy"],
}

TAG_ALIASES = {
    "aml": "aml",
    "akoma": "akoma-ntoso",
    "citation": "citation",
    "citations": "citation",
    "complaint": "judicial-workflow",
    "contracts": "contract-analysis",
    "courtlistener": "court-data",
    "courts": "court-data",
    "docassemble": "docassemble",
    "dockets": "dockets",
    "dsar": "dsar",
    "dsars": "dsar",
    "efiling": "e-filing",
    "eyecite": "citation",
    "gdpr": "gdpr",
    "governance": "corporate-governance",
    "juriscraper": "court-data",
    "judicial": "judicial-workflow",
    "justice": "access-to-justice",
    "kyc": "kyc",
    "lexnlp": "legal-nlp",
    "litigation": "litigation-support",
    "lkif": "lkif",
    "mediation": "mediation",
    "odr": "odr",
    "patent": "patent-search",
    "patents": "patent-search",
    "pii": "pii-redaction",
    "privacy": "privacy",
    "sanctions": "sanctions",
    "trademark": "trademark",
    "trademarks": "trademark",
    "visa": "visa-processing",
}


SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    tag_aliases=TAG_ALIASES,
    extra_accept_tags=frozenset(TAG_ALIASES.values()),
)


def enrich_entries(entries: list[dict], domain_name_by_id: dict[str, str]) -> list[dict]:
    return _enrich_entries(entries, domain_name_by_id, SPEC)


def extract_tags(entry: dict) -> list[str]:
    return _extract_tags(entry, SPEC)


def build_catalog(
    config_path: Path,
    batch_size: int,
    repo_root: Path | None = None,
    sync_site: bool = False,
) -> Path:
    return _build_catalog(config_path, batch_size, SPEC, repo_root=repo_root, sync_site=sync_site)


def main() -> None:
    run_cli(SPEC, domain="legal")


if __name__ == "__main__":
    main()
