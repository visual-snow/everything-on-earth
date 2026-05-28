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


# Translation: actual primary domain (entry.json `domain`) → one of WIKI_CATEGORIES keys
DOMAIN_TO_CATEGORY: dict[str, str] = {
    # 5G core variants
    "5g-core": "5g-core",
    "5g-core-network": "5g-core",
    "5g-standalone-core": "5g-core",
    "3gpp-core": "5g-core",
    "5g-core-interfaces": "5g-core",
    "4g-5g-core": "5g-core",
    "4g-5g-core-network": "5g-core",
    # 4G/EPC
    "4g-epc": "epc-4g-core",
    "4g-core": "epc-4g-core",
    "4g-lte": "epc-4g-core",
    "4g": "epc-4g-core",
    "epc": "epc-4g-core",
    "gsm": "epc-4g-core",
    # RAN / gNB / eNB
    "5g-ran": "gnb-ran-simulation",
    "5g-ran-simulation": "gnb-ran-simulation",
    "enb-simulation": "gnb-ran-simulation",
    "baseband": "gnb-ran-simulation",
    "baseband-processing": "gnb-ran-simulation",
    "o-ran": "gnb-ran-simulation",
    "e2ap": "gnb-ran-simulation",
    # Traffic / load
    "load-testing": "traffic-generation",
    "http-benchmarking": "traffic-generation",
    "api-load-testing": "traffic-generation",
    "api-stress-testing": "traffic-generation",
    "api-benchmarking": "traffic-generation",
    "call-flow-generation": "traffic-generation",
    # Observability / monitoring
    "infrastructure-monitoring": "packet-capture-observability",
    "kubernetes-monitoring": "packet-capture-observability",
    "docker-telemetry": "packet-capture-observability",
    "flow-monitoring": "packet-capture-observability",
    "flow-collection": "packet-capture-observability",
    "flow-analytics": "packet-capture-observability",
    "bgp-telemetry": "packet-capture-observability",
    "cisco-mdt": "packet-capture-observability",
    "model-driven-telemetry": "packet-capture-observability",
    "infrastructure-visibility": "packet-capture-observability",
    "deep-packet-inspection": "packet-capture-observability",
    "anomaly-detection": "packet-capture-observability",
    "fault-management": "packet-capture-observability",
    "distributed-alerting": "packet-capture-observability",
    # IMS / VoIP / VoLTE
    "asterisk": "ims-volte",
    "kamailio": "ims-volte",
    "call-processing": "ims-volte",
    "real-time-communications": "ims-volte",
    "cloud-native-telephony": "ims-volte",
    "rtp-media": "ims-volte",
    "rtp-proxy": "ims-volte",
    "media-processing": "ims-volte",
    "hep-protocol": "ims-volte",
    "ice": "ims-volte",
    # OSS/BSS
    "billing": "oss-bss",
    "inventory-orchestration": "oss-bss",
    # Slicing
    "5g-network-slicing": "network-slicing",
    # Fault / chaos
    "fault-injection": "fault-injection-chaos",
    "chaos-engineering": "fault-injection-chaos",
    "degraded-network-conditions": "fault-injection-chaos",
}


def assign_category(rec: dict) -> str:
    """Multi-stage category assignment.

    1. Honor explicit wiki_category if present (editorial override).
    2. Translate entry.domain via DOMAIN_TO_CATEGORY.
    3. Substring match against entry.provides (e.g., '5g-core-*' -> '5g-core').
    4. Last resort: 'uncategorized' (listed in INDEX, not silently dropped).
    """
    entry = rec["entry"]

    if "wiki_category" in entry:
        return entry["wiki_category"]

    domain = entry.get("domain", "")
    if domain in DOMAIN_TO_CATEGORY:
        return DOMAIN_TO_CATEGORY[domain]

    provides = entry.get("provides", []) or []
    # Substring match: any '5g-core-*' tag means it's a 5G core component
    joined = " ".join(provides)
    if "5g-core-" in joined:
        return "5g-core"
    if "4g-epc-" in joined:
        return "epc-4g-core"
    if any(tag.startswith(("gnb-", "ran-", "enb-")) for tag in provides):
        return "gnb-ran-simulation"
    if any("ue-" in tag and "subscriber" not in tag for tag in provides):
        return "ue-emulation"
    if "ims-" in joined or "volte" in joined or "voip" in joined:
        return "ims-volte"
    if "fault-inject" in joined or "chaos" in joined:
        return "fault-injection-chaos"
    if "traffic-gen" in joined or "load-test" in joined:
        return "traffic-generation"
    if any(t in joined for t in ("pcap", "monitoring", "observability", "telemetry")):
        return "packet-capture-observability"
    if "diameter" in joined or "roaming" in joined or "ipx" in joined:
        return "roaming-interconnect"
    if any(t in joined for t in ("oss", "bss", "billing", "charging")):
        return "oss-bss"
    if "slicing" in joined:
        return "network-slicing"

    return "uncategorized"


def build_index(records: list[dict]) -> str:
    """Generate INDEX.md content."""
    by_category: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        by_category[assign_category(rec)].append(rec)

    def short_desc(rec: dict) -> str:
        desc = rec["entry"].get("description", "")
        # First sentence only for the bullet line
        short = desc.split(". ")[0].rstrip(".")
        if short and len(short) < len(desc):
            short = short + "…"
        return short

    lines = [f"# Telecom software catalog ({len(records)} entries)\n"]
    for cat_slug, cat_desc in WIKI_CATEGORIES.items():
        entries = by_category.get(cat_slug, [])
        lines.append(f"## {cat_slug}\n")
        lines.append(f"{cat_desc} ({len(entries)} entries)\n")
        for rec in sorted(entries, key=lambda r: r["slug"]):
            name = rec["entry"].get("name", rec["slug"])
            license_ = rec["entry"].get("github_metrics", {}).get("license", "?")
            lines.append(f"- **{rec['slug']}** ({license_}) — {short_desc(rec)}")
        lines.append("")

    # Unmapped entries get a fallback section so nothing is silently dropped.
    unmapped = by_category.get("uncategorized", [])
    if unmapped:
        lines.append("## uncategorized\n")
        lines.append(f"Entries pending category assignment ({len(unmapped)})\n")
        for rec in sorted(unmapped, key=lambda r: r["slug"]):
            lines.append(f"- **{rec['slug']}** — {short_desc(rec)}")
        lines.append("")

    return "\n".join(lines)


def build_entry_page(rec: dict, all_slugs: set[str]) -> str:
    """Generate one entry's composite wiki page."""
    e = rec["entry"]
    fs = rec["factsheet"]
    gh = e.get("github_metrics", {}) or {}
    # related_repos in entry.json is GitHub URLs, not catalog slugs — drop the
    # "Related entries in this catalog" section entirely rather than guess at
    # URL→slug extraction.

    # factsheet.protocols are richer ("Diameter (S6a, Gx, Gy — 4G EPC)") than
    # entry.protocols ("Diameter") — prefer factsheet, fall back to entry.
    protocols = fs.get("protocols") or e.get("protocols", [])

    lines = [
        f"# {e.get('name', rec['slug'])}\n",
        f"**Repo:** {e.get('repo_url', '?')}    **License:** {gh.get('license', '?')}    **Language:** {gh.get('language', '?')}\n",
        "## TL;DR",
        e.get("description", "(no description)"),
        "",
        "## What it provides",
        ", ".join(e.get("provides", [])) or "(none documented)",
        "",
        "## What it needs",
        ", ".join(e.get("needs", [])) or "(none documented)",
        "",
        "## Protocols",
        ", ".join(protocols) or "(none documented)",
        "",
        "## Capability",
        rec["capability"].strip(),
        "",
        "## Constraints / What it can't do",
    ]
    for c in fs.get("constraints", []) or ["(none documented)"]:
        lines.append(f"- {c}")

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
