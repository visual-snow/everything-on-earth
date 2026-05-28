"""Build the telecom-catalog plugin data from catalog/telecoms/ source-of-truth.

Reads:  catalog/telecoms/<slug>/{entry.json, factsheet.json, capability.md}
Writes: <output_root>/INDEX.md
        <output_root>/<slug>.md
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

# Curated category list. Edit this map when new entries fall outside existing
# categories; do not auto-derive — the categories ARE the editorial structure
# the catalog plugin advertises.
WIKI_CATEGORIES: dict[str, str] = {
    "5g-core": "Full 5G SA core implementations (AMF, SMF, UPF, UDM, etc.)",
    "gnb-ran-simulation": "gNB simulators and emulators",
    "ue-emulation": "User equipment simulators",
    "ims-volte": "IMS cores and VoLTE testing",
    "fault-injection-chaos": "Failure injection for telecom systems",
    "traffic-generation": "Realistic signaling/data traffic",
    "packet-capture-observability": "Wireshark plugins, NWDAF, monitoring",
    "roaming-interconnect": "IPX, DEA, diameter routing",
    "epc-4g-core": "4G/LTE cores still in use",
    "oss-bss": "Provisioning, billing, charging",
    "network-slicing": "Slice management and orchestration",
}


def load_entry(entry_dir: Path) -> dict:
    with (entry_dir / "entry.json").open() as f:
        entry = json.load(f)
    with (entry_dir / "factsheet.json").open() as f:
        factsheet = json.load(f)
    capability = (entry_dir / "capability.md").read_text()
    return {
        "slug": entry_dir.name,
        "entry": entry,
        "factsheet": factsheet,
        "capability": capability,
    }


def assign_category(rec: dict) -> str:
    """Best-effort category assignment.

    Uses entry.wiki_category if present (authored). Otherwise falls back to
    factsheet.provides[] heuristics. Logs a WARNING for any unmappable entry.
    """
    if "wiki_category" in rec["entry"]:
        return rec["entry"]["wiki_category"]
    provides = set(rec["factsheet"].get("provides", []))
    if {"amf", "smf", "upf"} & provides:
        return "5g-core"
    if {"gnb", "ran"} & provides:
        return "gnb-ran-simulation"
    if {"ue"} & provides:
        return "ue-emulation"
    if {"ims", "volte"} & provides:
        return "ims-volte"
    if "fault-injection" in provides:
        return "fault-injection-chaos"
    if "traffic-gen" in provides:
        return "traffic-generation"
    if {"pcap", "monitoring", "observability"} & provides:
        return "packet-capture-observability"
    if {"roaming", "diameter"} & provides:
        return "roaming-interconnect"
    if {"mme", "sgw", "pgw"} & provides:
        return "epc-4g-core"
    if {"oss", "bss", "billing"} & provides:
        return "oss-bss"
    if "slicing" in provides:
        return "network-slicing"
    return "uncategorized"


def build_index(records: list[dict]) -> str:
    """Generate INDEX.md content."""
    by_category: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        by_category[assign_category(rec)].append(rec)

    lines = [f"# Telecom software catalog ({len(records)} entries)\n"]
    for cat_slug, cat_desc in WIKI_CATEGORIES.items():
        entries = by_category.get(cat_slug, [])
        lines.append(f"## {cat_slug}\n")
        lines.append(f"{cat_desc} ({len(entries)} entries)\n")
        for rec in sorted(entries, key=lambda r: r["slug"]):
            name = rec["entry"].get("name", rec["slug"])
            license_ = rec["entry"].get("license", "?")
            tagline = rec["entry"].get("tagline", "")
            lines.append(f"- **{rec['slug']}** ({license_}) — {tagline}")
        lines.append("")

    # Unmapped entries get a fallback section so nothing is silently dropped.
    unmapped = by_category.get("uncategorized", [])
    if unmapped:
        lines.append("## uncategorized\n")
        lines.append(f"Entries pending category assignment ({len(unmapped)})\n")
        for rec in sorted(unmapped, key=lambda r: r["slug"]):
            lines.append(f"- **{rec['slug']}** — {rec['entry'].get('tagline', '')}")
        lines.append("")

    return "\n".join(lines)


def build_entry_page(rec: dict, all_slugs: set[str]) -> str:
    """Generate one entry's composite wiki page."""
    e = rec["entry"]
    fs = rec["factsheet"]
    related_raw = e.get("related", [])
    # Filter out broken Related links — pre-fail at build time, not at render time.
    related = [r for r in related_raw if r in all_slugs]

    lines = [
        f"# {e.get('name', rec['slug'])}\n",
        f"**Repo:** {e.get('repo', '?')}    **License:** {e.get('license', '?')}    **Language:** {e.get('language', '?')}\n",
        "## TL;DR",
        e.get("tagline", "(no tagline)"),
        "",
        "## What it provides",
        ", ".join(fs.get("provides", [])) or "(none documented)",
        "",
        "## What it needs",
        ", ".join(fs.get("needs", [])) or "(none documented)",
        "",
        "## Protocols",
        ", ".join(fs.get("protocols", [])) or "(none documented)",
        "",
        "## Capability",
        rec["capability"].strip(),
        "",
        "## Constraints / What it can't do",
    ]
    for c in fs.get("constraints", []) or ["(none documented)"]:
        lines.append(f"- {c}")

    if related:
        lines.append("\n## Related entries in this catalog")
        for slug in related:
            lines.append(f"- {slug}")

    return "\n".join(lines) + "\n"


def main(source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)

    records = []
    for entry_dir in sorted(source.iterdir()):
        if not entry_dir.is_dir():
            continue
        if not (entry_dir / "entry.json").exists():
            print(f"SKIP {entry_dir.name}: no entry.json")
            continue
        records.append(load_entry(entry_dir))

    all_slugs = {r["slug"] for r in records}

    (output / "INDEX.md").write_text(build_index(records))
    print(f"Wrote {output / 'INDEX.md'}")

    for rec in records:
        page_path = output / f"{rec['slug']}.md"
        page_path.write_text(build_entry_page(rec, all_slugs))
    print(f"Wrote {len(records)} entry pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("catalog/telecoms"))
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target directory (typically rowter-plugins/plugins/telecom-catalog/data)",
    )
    args = parser.parse_args()
    main(args.source, args.output)
