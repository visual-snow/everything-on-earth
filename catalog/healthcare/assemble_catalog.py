#!/usr/bin/env python3
"""Build the healthcare catalog from per-domain discovery outputs."""

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
    "and",
    "analytics",
    "care",
    "clinical",
    "data",
    "digital",
    "github",
    "health",
    "healthcare",
    "management",
    "medical",
    "open",
    "opensource",
    "source",
    "system",
    "systems",
    "tool",
    "tooling",
    "tools",
}

KEYWORDS = {
    "anatomy",
    "behavioral-health",
    "bioinformatics",
    "cbt",
    "clinical-trials",
    "de-identification",
    "dental",
    "device-bridge",
    "dicom",
    "ehr",
    "emr",
    "epidemiology",
    "fhir",
    "genomics",
    "hipaa",
    "hl7",
    "hospital-ops",
    "imaging",
    "interoperability",
    "lab",
    "lis",
    "loinc",
    "mental-health",
    "molecular-design",
    "nlp",
    "ophthalmology",
    "omop",
    "pathology",
    "patient-records",
    "pharmacy",
    "population-health",
    "practice-management",
    "privacy",
    "radiology",
    "remote-monitoring",
    "simulation",
    "snomed",
    "synthetic-data",
    "telemedicine",
    "terminology",
    "variant-calling",
    "wearables",
}

DOMAIN_TAG_HINTS = {
    "ehr-practice-management": ["ehr", "emr", "patient-records", "practice-management"],
    "medical-imaging-radiology": ["dicom", "imaging", "radiology", "segmentation"],
    "clinical-nlp-text-mining": ["nlp", "clinical-notes", "entity-extraction", "coding"],
    "drug-discovery-molecular-design": ["drug-discovery", "cheminformatics", "docking", "virtual-screening"],
    "genomics-bioinformatics": ["genomics", "bioinformatics", "variant-calling", "pipelines"],
    "fhir-health-interoperability": ["fhir", "hl7", "interoperability", "integration"],
    "epidemiology-disease-surveillance": ["epidemiology", "surveillance", "outbreaks", "modeling"],
    "telemedicine-remote-care": ["telemedicine", "virtual-care", "remote-monitoring", "video"],
    "clinical-trials-research": ["clinical-trials", "research", "recruitment", "data-capture"],
    "medical-ai-diagnostics": ["medical-ai", "diagnostics", "decision-support", "pathology"],
    "pharmacy-medication-management": ["pharmacy", "medication", "prescribing", "drug-safety"],
    "health-data-standards-terminologies": ["terminology", "standards", "ontologies", "vocabularies"],
    "wearable-iot-health": ["wearables", "sensors", "iot", "remote-monitoring"],
    "mental-health-behavioral": ["mental-health", "behavioral-health", "cbt", "screening"],
    "hospital-operations-scheduling": ["hospital-ops", "scheduling", "bed-management", "patient-flow"],
    "public-health-population-analytics": ["public-health", "population-health", "equity", "demographics"],
    "lab-information-systems": ["lis", "lims", "specimen-tracking", "lab-workflows"],
    "dental-specialty-clinics": ["specialty-clinics", "practice-management"],
    "medical-education-simulation": ["education", "simulation", "anatomy", "virtual-patient"],
    "health-data-privacy-deidentification": ["privacy", "de-identification", "synthetic-data", "hipaa"],
}

TAG_ALIASES = {
    "anonymization": "de-identification",
    "anonymizer": "de-identification",
    "behavioral": "behavioral-health",
    "behavioural": "behavioral-health",
    "dentistry": "dental",
    "emr": "emr",
    "eyecare": "ophthalmology",
    "hipaa": "hipaa",
    "ophtha": "ophthalmology",
    "ophthalmic": "ophthalmology",
    "optha": "ophthalmology",
    "patient": "patient-records",
    "patients": "patient-records",
    "practice": "practice-management",
    "prescribing": "medication",
    "telehealth": "telemedicine",
}


SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    tag_aliases=TAG_ALIASES,
    extra_accept_tags=frozenset(
        {"ehr", "emr", "fhir", "hl7", "dicom", "loinc", "omop", "snomed", "uml", "lis"}
    ),
    always_sync_site=True,
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
    run_cli(SPEC, domain="healthcare")


if __name__ == "__main__":
    main()
