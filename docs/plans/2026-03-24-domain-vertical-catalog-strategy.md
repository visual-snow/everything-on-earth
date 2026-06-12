# Domain-Vertical Catalog Strategy

## Goal

Make everything-on-earth the definitive reference for open-source tools in 20 industry domains. Each catalog should be the first result when someone searches "open source {domain} tools github" — and comprehensive enough that they star the repo and never need to look elsewhere.

## Success Criteria

A catalog is DONE when:
1. It contains every discoverable open-source repo in the domain (not a curated subset — everything)
2. Every entry has real GitHub API signals (stars, forks, last commit, contributors, license)
3. Entries are ranked by a composite quality score — best first, long tail preserved
4. The explorer.html lets anyone search, filter, and sort without leaving their browser
5. The catalog.json is machine-readable and loadable into any LLM context window

The project is SUCCESSFUL when:
- 500 GitHub stars in 3 months, 5,000 in 6 months
- 10k organic search impressions/month in 3 months, 100k in 6 months
- Community members submit their own domain catalogs

## Why Domains, Not Tech Categories

Horizontal tech catalogs ("every RAG framework") compete with awesome-lists that already have 84k-282k stars. Domain-vertical catalogs ("every open-source cybersecurity tool") have 10-100x weaker catalog competition because they require domain expertise to curate — which is what our multi-agent pipeline automates.

## The 20 Domains

Ranked by: (community size x ecosystem depth x catalog gap x churn x shareability).

### Priority 1: Ship First

| # | Domain | Why this domain |
|---|--------|----------------|
| 1 | **Cybersecurity & Hacking** | 2.5M+ Reddit audience, tool-sharing culture, awesome-hacking 88k proves demand but is stale |
| 2 | **Gaming & Game Dev** | 2.0M r/gamedev, Godot 80k stars, high emotional shareability |
| 3 | **Quant Finance & Trading** | 1.8M r/algotrading, money-motivated audience that shares obsessively |
| 4 | **Geospatial & GIS** | Leaflet 44.7k stars but best catalog only 4.2k — 10x gap |
| 5 | **Autonomous Vehicles** | openpilot 60.1k stars but best catalog only 2.3k — 26x gap |

### Priority 2: Ship Second

| # | Domain | Why this domain |
|---|--------|----------------|
| 6 | Robotics | Humanoid boom (Figure, Tesla Bot, LeRobot) creating uncataloged churn |
| 7 | Bioinformatics & Genomics | AI+genomics intersection producing new tools faster than manual curation |
| 8 | Healthcare & Medical AI | Medical LLMs and FHIR tools uncataloged, $300B health IT market |
| 9 | Energy & CleanTech | $500B clean energy investment driving new tools, catalog at only 2.5k stars |
| 10 | Climate & Environmental Science | 1.6M r/environment, emotional shareability, near-zero catalog competition |

### Priority 3: Ship Third

| # | Domain | Why this domain |
|---|--------|----------------|
| 11 | Aerospace & Satellite | 25M r/space audience, catalog at only 2.1k stars |
| 12 | Drones & UAV | ArduPilot 11k stars, zero dedicated catalog competition |
| 13 | Education & EdTech | Best catalog has 173 stars — 38x gap vs ecosystem |
| 14 | Manufacturing & IIoT | ThingsBoard 14.7k stars, Industry 4.0 wave, no dedicated catalog |
| 15 | Telecommunications & 5G | 166 entries already cataloged in task-designer, awesome-telco only 868 stars |

### Priority 4: Ship Last

| # | Domain | Why this domain |
|---|--------|----------------|
| 16 | Music & Audio Production | 3.8M r/WATMM, AI music tools exploding |
| 17 | Agriculture & AgTech | Precision agriculture + drone + AI crop analysis niche |
| 18 | Legal & LegalTech | AI contract review wave, near-zero catalog competition |
| 19 | Construction & AEC | Digital twin boom, no existing catalog |
| 20 | Supply Chain & Logistics | AI demand forecasting, very low competition |

## Quality Philosophy

**No pruning. No star minimums. Everything stays.**

Instead of cutting repos, every entry gets a composite quality score from real GitHub API signals. The explorer sorts by score — best stuff first, long tail preserved.

**Hard cuts (data quality only):**
- No URL, no description, blank repo (0 commits/no README), fork with 0 additional commits

**Scoring signals:**

| Signal | Why it matters | Weight |
|--------|---------------|--------|
| README >100 words | Not a blank dump | Hard cut if missing |
| >1 commit | Not a one-off paste | Hard cut if 1 commit |
| License | Serious project | Bonus |
| Last commit recency | Actively maintained | High |
| Stars | Community validation | Medium |
| Forks | People building on it | Medium |
| Open issues / PRs | Community engagement | Low |
| Has releases | Production-ready | Bonus |
| Contributors >1 | Not a solo experiment | Bonus |

A 3-star government cybersecurity tool is just as valid as a 10k-star tool — it just sorts lower.

## Output Structure

```
catalog/
└── {domain-slug}/
    ├── catalog.json       ← machine-readable, scored, every entry
    ├── explorer.html      ← interactive browser, sort/filter/search
    └── RESULTS.md         ← stats and domain breakdown
```

## Cost

~$20-40 per catalog. ~$400-800 for all 20.

## Timeline

8 weeks. 5 catalogs per wave, 2 weeks per wave.
