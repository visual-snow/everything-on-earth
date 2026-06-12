#!/usr/bin/env python3
"""Build the legal catalog from per-domain discovery outputs."""

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

    scored, _removed = run_score(dedup)
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
    parser = argparse.ArgumentParser(description="Assemble the legal catalog from discovery outputs")
    parser.add_argument(
        "--config",
        default=str(Path("catalog") / "legal" / "swarm-config.json"),
        help="Path to legal swarm-config.json",
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
        help="Regenerate the global catalog site after building legal",
    )
    args = parser.parse_args()

    build_catalog(
        REPO_ROOT / args.config,
        batch_size=args.batch_size,
        sync_site=args.sync_site,
    )


if __name__ == "__main__":
    main()
