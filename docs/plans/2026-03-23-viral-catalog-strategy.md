# Viral Catalog Strategy

> Ship pre-built catalogs as SEO magnets. Each catalog is a landing page, a demo, and proof the tool works.

## The Thesis

Occasional-use tools go viral when **the output is the marketing**. awesome-selfhosted has 282k stars not because people run a curation script — they star it for the data. We ship 20 pre-built catalogs on the hottest developer topics. People find the catalogs through Google, star the repo for the reference, discover the tool, and run it for their own topics.

## Why This Beats Awesome-Lists

| | awesome-lists | everything-on-earth catalogs |
|---|---|---|
| **Coverage** | Human-curated, 50-200 entries | Machine-discovered, 500-2000+ entries |
| **Freshness** | Stale within weeks in fast domains | Re-runnable, timestamped |
| **Discoverability** | Single markdown file | explorer.html with search/filter + catalog.json for agent retrieval |
| **Metadata** | Name + description | Stars, language, license, last_activity, score, tags, category, capability docs |
| **Agent-ready** | No | catalog.json loads directly into LLM context |

## Success Metrics

| Metric | 3-month target | 6-month target |
|--------|---------------|---------------|
| GitHub stars | 500 | 5,000 |
| Catalogs shipped | 10 | 20 |
| Organic search impressions | 10k/month | 100k/month |
| Community-submitted catalogs | 0 | 10 |

## Distribution Channels (per catalog)

1. **GitHub** — each catalog lives in `/catalogs/{topic}/` with its own README
2. **Reddit** — post to relevant subreddit (r/selfhosted, r/LocalLLaMA, r/devops, etc.)
3. **Hacker News** — "Show HN: I cataloged every {topic} repo on GitHub ({N} repos)"
4. **Twitter/X** — thread with explorer.html screenshots, top 10 repos, stats
5. **Dev.to / Hashnode** — article per catalog with analysis and highlights

## Catalog Production Cost

Per catalog (estimated):
- LLM tokens: ~$15-30 (6-8 Sonnet agents discovering)
- Firecrawl: ~$5-10 (searches + scrapes)
- Enrichment: ~$0.50 (Haiku tags/categories)
- Map-capabilities: ~$10-20 (optional, for top entries)
- **Total: ~$30-60 per catalog**
- **20 catalogs: ~$600-1,200**

## Catalog Lifecycle

```
1. Run /massive-crawl "{topic}"     → raw catalog
2. Review + tune pruning thresholds → curated catalog
3. Run /map-capabilities (top 50)   → deep docs for best entries
4. Write catalog README             → context, stats, highlights
5. Commit to /catalogs/{topic}/     → discoverable on GitHub
6. Distribute on social channels    → traffic
7. Re-run quarterly                 → freshness (badge: "Last updated: YYYY-MM")
```

## Repo Structure After Catalogs

```
everything-on-earth/
├── README.md                       ← links to all catalogs
├── catalogs/
│   ├── ai-agent-frameworks/
│   │   ├── README.md               ← topic intro, stats, highlights
│   │   ├── catalog.json            ← machine-readable (847 entries)
│   │   ├── explorer.html           ← browse in browser
│   │   ├── RESULTS.md              ← domain breakdown, top repos
│   │   └── capabilities/           ← deep docs for top entries
│   │       ├── langchain_capability.md
│   │       ├── crewai_capability.md
│   │       └── ...
│   ├── self-hosted-software/
│   ├── local-llm-tools/
│   └── ... (20 topics)
├── skill/                          ← the tool itself
├── pipeline/
├── hooks/
└── install.sh
```

## Key Risk: Catalog Staleness

Catalogs in fast-moving domains (AI agents, MCP servers) go stale in weeks. Mitigation:
- Badge in each catalog README: "Last crawled: YYYY-MM-DD"
- Quarterly re-runs for top 10 catalogs
- GitHub Action to auto-badge staleness
- Community contribution model (PRs to add missed repos)
