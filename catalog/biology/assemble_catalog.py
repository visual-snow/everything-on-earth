#!/usr/bin/env python3
"""Build the biology catalog from per-domain discovery outputs."""

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

SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    tag_aliases=TAG_ALIASES,
    extra_accept_tags=frozenset(DOMAIN_TAG_HINTS),
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
    run_cli(SPEC, domain="biology")


if __name__ == "__main__":
    main()
