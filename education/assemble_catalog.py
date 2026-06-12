#!/usr/bin/env python3
"""Build the education catalog from per-domain discovery outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

SOURCE_REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_ROOT = SOURCE_REPO_ROOT / "pipeline"
sys.path.insert(0, str(PIPELINE_ROOT))

from pipeline import run_dedup, run_finalize, run_score, run_site  # type: ignore  # noqa: E402
from utils import load_catalog  # type: ignore  # noqa: E402


STOPWORDS = {
    "and",
    "education",
    "github",
    "learning",
    "management",
    "open",
    "opensource",
    "platform",
    "source",
    "student",
    "system",
    "systems",
    "tool",
    "tools",
}

KEYWORDS = {
    "aac",
    "accessibility",
    "adaptive-learning",
    "assessment",
    "authoring",
    "badges",
    "classroom",
    "coding",
    "credentialing",
    "curriculum",
    "flashcards",
    "grading",
    "interactive",
    "language-learning",
    "lms",
    "oer",
    "qti",
    "rostering",
    "scorm",
    "sis",
    "spaced-repetition",
    "tutoring",
    "virtual-labs",
    "xapi",
}

DOMAIN_TAG_HINTS = {
    "lms": ["lms", "course-delivery", "grading", "enrollment"],
    "adaptive-learning": ["adaptive-learning", "tutoring", "mastery", "knowledge-tracing"],
    "assessment-testing": ["assessment", "exams", "autograding", "academic-integrity"],
    "interactive-coding-education": ["coding", "playgrounds", "sandboxes", "autograding"],
    "k12-stem": ["k12", "stem", "simulations", "student-learning"],
    "video-lecture-platforms": ["lecture-capture", "video-learning", "streaming", "annotation"],
    "collaborative-learning": ["collaboration", "peer-review", "whiteboards", "wikis"],
    "curriculum-authoring": ["curriculum", "authoring", "oer", "courseware"],
    "sis": ["sis", "attendance", "transcripts", "enrollment"],
    "gamification-engagement": ["gamification", "badges", "leaderboards", "engagement"],
    "language-learning": ["language-learning", "flashcards", "vocabulary", "reading-support"],
    "accessibility-inclusive-education": ["accessibility", "captioning", "aac", "inclusive-learning"],
    "analytics-learning-dashboards": ["analytics", "dashboards", "engagement", "early-alerts"],
    "virtual-labs-simulations": ["virtual-labs", "simulations", "remote-labs", "science-learning"],
    "classroom-management": ["classroom", "device-management", "monitoring", "scheduling"],
    "research-academic-publishing": ["journals", "peer-review", "publishing", "references"],
    "special-education-therapy": ["special-education", "speech-therapy", "autism-support", "aac"],
    "credentialing-certification": ["credentialing", "certification", "open-badges", "microcredentials"],
    "edtech-infrastructure": ["lti", "xapi", "scorm", "rostering"],
    "ai-teaching-assistants": ["ai-tutoring", "automated-feedback", "question-generation", "essay-scoring"],
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
    if not raw or raw in STOPWORDS or len(raw) < 3:
        return None
    return raw


def extract_tags(entry: dict) -> list[str]:
    domain_ids = entry.get("found_in_domains") or [entry.get("sub_domain", "unknown")]
    ordered: list[str] = []
    seen: set[str] = set()

    for domain_id in domain_ids:
        for hint in DOMAIN_TAG_HINTS.get(domain_id, []):
            if hint not in seen:
                ordered.append(hint)
                seen.add(hint)

    text = " ".join([
        entry.get("name", ""),
        entry.get("description", ""),
        " ".join(domain_ids),
    ]).lower()
    for token in re.split(r"[^a-z0-9]+", text):
        tag = normalize_tag(token)
        if not tag or tag in seen:
            continue
        if tag in KEYWORDS:
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
        domain_ids = entry.get("found_in_domains") or [entry.get("sub_domain", "unknown")]
        primary_domain = domain_ids[0]
        category = domain_name_by_id.get(primary_domain, primary_domain.replace("-", " ").title())
        enriched.append({
            **entry,
            "discovery_score": entry.get("score"),
            "tags": extract_tags(entry),
            "category": category,
            "summary": summarize(entry.get("description", "")),
        })
    return enriched


def render_explorer(topic: str, output_dir: Path, entries: list[dict], domain_slug: str = "education") -> None:
    env = Environment(loader=FileSystemLoader(str(PIPELINE_ROOT / "templates")))
    payload = [{**entry, "domain": domain_slug} for entry in entries]
    html = env.get_template("explorer.html").render(
        topic=topic,
        total=len(payload),
        domain_count=len({d for e in payload for d in (e.get("found_in_domains") or [e.get("sub_domain")])}),
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
    catalog_root: Path | None = None,
) -> Path:
    repo_root = repo_root or SOURCE_REPO_ROOT
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
    render_explorer(config["topic"], output_dir, enriched)
    sync_entry_layout(output_dir)
    run_site(catalog_root, template_dir=PIPELINE_ROOT / "templates")
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble the education catalog from discovery outputs")
    parser.add_argument(
        "--config",
        default=str(Path("education") / "swarm-config.json"),
        help="Path to education swarm-config.json",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=40,
        help="Batch size used when producing enrich-batch-*.json files",
    )
    args = parser.parse_args()

    build_catalog(
        SOURCE_REPO_ROOT / args.config,
        batch_size=args.batch_size,
        repo_root=SOURCE_REPO_ROOT,
        catalog_root=SOURCE_REPO_ROOT / "catalog",
    )


if __name__ == "__main__":
    main()
