#!/usr/bin/env python3
"""Shared catalog-assembly steps used by every domain's assemble_catalog.py.

Each domain supplies a :class:`CatalogSpec` describing its tag vocabulary and
the handful of behavioural knobs that genuinely differ between domains; the
build steps themselves live here so they exist in exactly one place.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parent
sys.path.insert(0, str(PIPELINE_ROOT))

from pipeline import run_dedup, run_finalize, run_score, run_site  # type: ignore  # noqa: E402
from utils import load_catalog  # type: ignore  # noqa: E402

TEMPLATE_DIR = PIPELINE_ROOT / "templates"


@dataclass(frozen=True)
class RelevanceGate:
    """Per-sub-domain relevance filtering applied before scoring (fintech)."""

    rules: dict[str, list[list[str]]]
    global_meta_rejects: list[str]
    min_score: int


@dataclass(frozen=True)
class CatalogSpec:
    stopwords: frozenset[str]
    keywords: frozenset[str]
    domain_tag_hints: dict[str, list[str]]
    tag_aliases: dict[str, str] = field(default_factory=dict)
    # Slugs (beyond ``keywords``) that also count as a valid free-text tag.
    extra_accept_tags: frozenset[str] = frozenset()
    # When set, seed/group tags from ``found_in_domains`` instead of ``sub_domain``.
    multi_domain: bool = False
    # When set, every explorer entry is labelled with this one domain slug.
    explorer_domain_slug: str | None = None
    # When set, filter entries through a relevance gate before scoring.
    relevance: RelevanceGate | None = None
    # When set, always regenerate the global site after building.
    always_sync_site: bool = False


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


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


def normalize_tag(raw: str, spec: CatalogSpec) -> str | None:
    raw = raw.strip().lower()
    if not raw or raw in spec.stopwords:
        return None
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    raw = spec.tag_aliases.get(raw, raw)
    if not raw or raw in spec.stopwords or len(raw) < 3:
        return None
    return raw


def _entry_domains(entry: dict, spec: CatalogSpec) -> list[str]:
    if spec.multi_domain:
        return entry.get("found_in_domains") or [entry.get("sub_domain", "unknown")]
    return [entry.get("sub_domain", "unknown")]


def extract_tags(entry: dict, spec: CatalogSpec) -> list[str]:
    domain_ids = _entry_domains(entry, spec)
    ordered: list[str] = []
    seen: set[str] = set()

    for domain_id in domain_ids:
        for hint in spec.domain_tag_hints.get(domain_id, []):
            if hint not in seen:
                ordered.append(hint)
                seen.add(hint)

    text_parts = [entry.get("name", ""), entry.get("description", "")]
    if spec.multi_domain:
        text_parts.append(" ".join(domain_ids))
    text = " ".join(text_parts).lower()

    accept = spec.keywords | spec.extra_accept_tags
    for token in re.split(r"[^a-z0-9]+", text):
        tag = normalize_tag(token, spec)
        if not tag or tag in seen:
            continue
        if tag in accept:
            ordered.append(tag)
            seen.add(tag)

    return ordered[:6]


def summarize(description: str) -> str:
    description = (description or "").strip() or "No description provided."
    if len(description) <= 140:
        return description
    return description[:137].rstrip() + "..."


def enrich_entries(
    entries: list[dict],
    domain_name_by_id: dict[str, str],
    spec: CatalogSpec,
) -> list[dict]:
    enriched: list[dict] = []
    for entry in entries:
        primary_domain = _entry_domains(entry, spec)[0]
        category = domain_name_by_id.get(primary_domain, primary_domain.replace("-", " ").title())
        enriched.append({
            **entry,
            "discovery_score": entry.get("score"),
            "tags": extract_tags(entry, spec),
            "category": category,
            "summary": summarize(entry.get("description", "")),
        })
    return enriched


def render_explorer(
    topic: str,
    output_dir: Path,
    entries: list[dict],
    domain_name_by_id: dict[str, str],
    spec: CatalogSpec,
) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    if spec.explorer_domain_slug is not None:
        payload = [{**entry, "domain": spec.explorer_domain_slug} for entry in entries]
        domain_count = len({
            domain_id
            for entry in payload
            for domain_id in (entry.get("found_in_domains") or [entry.get("sub_domain")])
        })
    else:
        payload = []
        for entry in entries:
            primary_domain = entry.get("sub_domain", "unknown")
            payload.append({
                **entry,
                "domain": domain_name_by_id.get(primary_domain, primary_domain.replace("-", " ").title()),
            })
        domain_count = len({entry["domain"] for entry in payload})
    html = env.get_template("explorer.html").render(
        topic=topic,
        total=len(payload),
        domain_count=domain_count,
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


def _normalize_text(raw: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", raw.lower()).split())


def passes_relevance_gate(entry: dict, gate: RelevanceGate) -> bool:
    text = _normalize_text(" ".join([entry.get("name", ""), entry.get("description", "")]))
    if any(flag in text for flag in gate.global_meta_rejects):
        return False
    if "awesome " in text or text.startswith("awesome "):
        return False

    groups = gate.rules.get(entry.get("sub_domain", ""))
    if not groups:
        return True
    for group in groups:
        normalized_group = [_normalize_text(phrase) for phrase in group]
        if not any(phrase and phrase in text for phrase in normalized_group):
            return False
    return True


def filter_relevant_entries(entries: list[dict], gate: RelevanceGate) -> list[dict]:
    return [
        entry
        for entry in entries
        if passes_relevance_gate(entry, gate) and entry.get("score", 0) >= gate.min_score
    ]


def build_catalog(
    config_path: Path,
    batch_size: int,
    spec: CatalogSpec,
    *,
    repo_root: Path | None = None,
    sync_site: bool = False,
    catalog_root: Path | None = None,
) -> Path:
    repo_root = repo_root or REPO_ROOT
    catalog_root = catalog_root or (repo_root / "catalog")

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

    if spec.relevance is not None:
        dedup = filter_relevant_entries(dedup, spec.relevance)
        write_json(output_dir / "relevant.json", dedup)

    scored, _removed = run_score(dedup)
    write_json(output_dir / "scored.json", scored)

    batches = chunked(scored, batch_size)
    enriched_batches: list[list[dict]] = []
    width = max(1, len(str(len(batches) or 1)))
    for idx, batch in enumerate(batches, start=1):
        batch_name = f"{idx:0{width}d}"
        write_json(output_dir / f"enrich-batch-{batch_name}.json", batch)
        enriched_batch = enrich_entries(batch, domain_name_by_id, spec)
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
        template_dir=TEMPLATE_DIR,
    )
    render_explorer(config["topic"], output_dir, enriched, domain_name_by_id, spec)
    sync_entry_layout(output_dir)

    if sync_site or spec.always_sync_site:
        run_site(catalog_root, template_dir=TEMPLATE_DIR)

    return output_dir


def run_cli(spec: CatalogSpec, *, domain: str, default_config: str | None = None) -> None:
    parser = argparse.ArgumentParser(description=f"Assemble the {domain} catalog from discovery outputs")
    parser.add_argument(
        "--config",
        default=default_config or str(Path("catalog") / domain / "swarm-config.json"),
        help=f"Path to {domain} swarm-config.json",
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
        help=f"Regenerate the global catalog site after building {domain}",
    )
    args = parser.parse_args()
    build_catalog(REPO_ROOT / args.config, batch_size=args.batch_size, spec=spec, sync_site=args.sync_site)
