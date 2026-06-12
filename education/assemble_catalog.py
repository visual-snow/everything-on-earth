#!/usr/bin/env python3
"""Build the education catalog from per-domain discovery outputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from catalog_assembler import (  # type: ignore  # noqa: E402
    CatalogSpec,
    build_catalog as _build_catalog,
    enrich_entries as _enrich_entries,
    extract_tags as _extract_tags,
    run_cli,
)


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


SPEC = CatalogSpec(
    stopwords=frozenset(STOPWORDS),
    keywords=frozenset(KEYWORDS),
    domain_tag_hints=DOMAIN_TAG_HINTS,
    multi_domain=True,
    explorer_domain_slug="education",
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
    catalog_root: Path | None = None,
) -> Path:
    return _build_catalog(
        config_path, batch_size, SPEC, repo_root=repo_root, catalog_root=catalog_root
    )


def main() -> None:
    run_cli(SPEC, domain="education", default_config="education/swarm-config.json")


if __name__ == "__main__":
    main()
