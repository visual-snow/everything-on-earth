"""Tests for healthcare catalog assembly helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "catalog" / "healthcare"))

from assemble_catalog import enrich_entries, extract_tags  # type: ignore


def test_enrich_entries_uses_sub_domain_for_category():
    entry = {
        "repo_url": "https://github.com/informatici/openhospital",
        "name": "informatici/openhospital",
        "description": "Open Hospital is an EHR and hospital workflow application.",
        "sub_domain": "hospital-operations-scheduling",
        "found_in_domains": ["ehr-practice-management", "hospital-operations-scheduling"],
        "score": 10,
    }
    domain_name_by_id = {
        "ehr-practice-management": "Electronic Health Records (EHR), Clinical Documentation & Practice Management",
        "hospital-operations-scheduling": "Hospital Operations, Scheduling, Bed Management & Patient Flow",
    }

    enriched = enrich_entries([entry], domain_name_by_id)

    assert enriched[0]["category"] == domain_name_by_id["hospital-operations-scheduling"]


def test_extract_tags_does_not_seed_secondary_domain_tags():
    entry = {
        "repo_url": "https://github.com/openemr/openemr",
        "name": "openemr/openemr",
        "description": "Open source electronic health records and medical practice management solution.",
        "sub_domain": "ehr-practice-management",
        "found_in_domains": ["ehr-practice-management", "dental-specialty-clinics"],
    }

    tags = extract_tags(entry)

    assert "dental" not in tags
    assert "ophthalmology" not in tags
    assert "ehr" in tags
