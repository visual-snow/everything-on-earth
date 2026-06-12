#!/usr/bin/env python3
"""Build the biology catalog from per-domain discovery outputs."""

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
    "biology",
    "data",
    "github",
    "open",
    "opensource",
    "pipeline",
    "pipelines",
    "platform",
    "science",
    "software",
    "source",
    "system",
    "systems",
    "tool",
    "tooling",
    "tools",
    "workflow",
    "workflows",
}

KEYWORDS = {
    "16s",
    "acmg",
    "agtech",
    "ancient-dna",
    "atac-seq",
    "biodiversity",
    "bioimage",
    "cell-segmentation",
    "cheminformatics",
    "chip-seq",
    "clinical-genomics",
    "connectomics",
    "conservation",
    "cryo-em",
    "de-novo-assembly",
    "directed-evolution",
    "docking",
    "dna-methylation",
    "ecology",
    "epidemiology",
    "epigenomics",
    "genome-assembly",
    "genomics",
    "gbif",
    "histopathology",
    "hla",
    "immunoinformatics",
    "long-read",
    "marine-biology",
    "mass-spectrometry",
    "maxent",
    "metabolomics",
    "metagenomics",
    "microscopy",
    "molecular-dynamics",
    "nanopore",
    "neoantigen",
    "neuron",
    "pathway-modeling",
    "paleogenomics",
    "pacbio",
    "phenology",
    "phylogenetics",
    "plant-phenotyping",
    "plankton",
    "precision-agriculture",
    "proteomics",
    "protein-design",
    "protein-engineering",
    "qsar",
    "rna-seq",
    "sbml",
    "sc-rna-seq",
    "single-cell",
    "sir",
    "slide-seq",
    "smiles",
    "spatial-omics",
    "spatial-transcriptomics",
    "synthetic-biology",
    "taxonomic-classification",
    "transcriptomics",
    "variant-calling",
    "visium",
}

DOMAIN_TAG_HINTS = {
    "genomics": ["genomics", "variant-calling", "genome-assembly", "sequence-analysis"],
    "transcriptomics": ["transcriptomics", "rna-seq", "single-cell", "differential-expression"],
    "proteomics": ["proteomics", "mass-spectrometry", "peptide-identification", "protein-quantification"],
    "metabolomics": ["metabolomics", "metabolite-annotation", "lc-ms", "pathway-analysis"],
    "epigenomics": ["epigenomics", "atac-seq", "chip-seq", "dna-methylation"],
    "metagenomics": ["metagenomics", "microbiome", "taxonomic-classification", "shotgun-sequencing"],
    "structural-biology": ["structural-biology", "cryo-em", "molecular-dynamics", "docking"],
    "bioinformatics-pipelines": ["bioinformatics-pipelines", "nextflow", "snakemake", "reproducibility"],
    "systems-biology": ["systems-biology", "sbml", "pathway-modeling", "network-biology"],
    "phylogenetics": ["phylogenetics", "molecular-evolution", "tree-inference", "phylogenomics"],
    "computational-neuroscience": ["computational-neuroscience", "neuron", "brian2", "nest"],
    "cheminformatics": ["cheminformatics", "smiles", "qsar", "drug-discovery"],
    "ecology-conservation": ["ecology", "conservation", "species-distribution", "maxent"],
    "marine-biology": ["marine-biology", "ocean-microbiome", "plankton", "fisheries"],
    "climate-biology": ["climate-biology", "phenology", "ecological-forecasting", "species-climate"],
    "biodiversity-informatics": ["biodiversity", "gbif", "occurrence-data", "taxonomy"],
    "biomedical-imaging": ["biomedical-imaging", "bioimage", "microscopy", "histopathology"],
    "clinical-genomics": ["clinical-genomics", "genomics", "variant-interpretation", "acmg"],
    "immunoinformatics": ["immunoinformatics", "epitope-prediction", "hla", "neoantigen"],
    "synthetic-biology": ["synthetic-biology", "genetic-circuits", "dna-assembly", "metabolic-engineering"],
    "epidemiology-disease-modeling": ["epidemiology", "sir", "outbreak-modeling", "phylodynamics"],
    "long-read-sequencing": ["long-read", "nanopore", "pacbio", "iso-seq"],
    "spatial-omics": ["spatial-omics", "spatial-transcriptomics", "visium", "slide-seq"],
    "agricultural-biology-agtech": ["agtech", "crop-genomics", "plant-phenotyping", "precision-agriculture"],
    "protein-engineering-directed-evolution": ["protein-engineering", "directed-evolution", "protein-design", "enzyme-engineering"],
    "connectomics": ["connectomics", "neuronal-reconstruction", "synapse-segmentation", "em-imaging"],
    "ancient-dna-paleogenomics": ["ancient-dna", "paleogenomics", "archaeogenomics", "contamination-detection"],
}

TAG_ALIASES = {
    "adna": "ancient-dna",
    "archaeogenomics": "archaeogenomics",
    "bioimage": "bioimage",
    "biodiversityinformatics": "biodiversity",
    "chip": "chip-seq",
    "chipseq": "chip-seq",
    "connectome": "connectomics",
    "cryoem": "cryo-em",
    "epitope": "epitope-prediction",
    "gbif": "gbif",
    "hla": "hla",
    "histopathology": "histopathology",
    "immunopeptidomics": "immunoinformatics",
    "isoseq": "iso-seq",
    "lcms": "lc-ms",
    "metabarcoding": "biodiversity",
    "microbiome": "microbiome",
    "nanopore": "nanopore",
    "pacbio": "pacbio",
    "paleogenetics": "paleogenomics",
    "rnaseq": "rna-seq",
    "scrnaseq": "sc-rna-seq",
    "singlecell": "single-cell",
    "slideseq": "slide-seq",
    "visium": "visium",
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
        if tag in KEYWORDS or tag in DOMAIN_TAG_HINTS:
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
    parser = argparse.ArgumentParser(description="Assemble the biology catalog from discovery outputs")
    parser.add_argument(
        "--config",
        default=str(Path("catalog") / "biology" / "swarm-config.json"),
        help="Path to biology swarm-config.json",
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
        help="Regenerate the global catalog site after building biology",
    )
    args = parser.parse_args()

    build_catalog(
        REPO_ROOT / args.config,
        batch_size=args.batch_size,
        sync_site=args.sync_site,
    )


if __name__ == "__main__":
    main()
