# README Redesign — Design Document

Date: 2026-03-23

## Decisions

1. **Kill both "Why" sections.** No "Why I Built This", no "Why It Works". Lead with value prop, go straight to install.
2. **Both skills visible, pipeline internals and troubleshooting collapse** behind `<details>` blocks.
3. **Keep ASCII pipeline diagram + add tables** for outputs and requirements.
4. **Centered hero block** with repo name as H1, one-line value prop, hero image, install command. No badges.
5. **"Product Page" structure** — each section has one job, reads top-to-bottom.
6. **No closing tagline.**

## Theme

Max the fuck out of your Claude subscription by doing a massive parallel crawl that searches everything on earth about whatever you want.

## Structure

```
Section 1: Hero (centered div)
  - H1: everything-on-earth
  - Value prop (one sentence, the theme)
  - Hero image
  - Install command
  - Nav links

Section 2: Getting Started
  - Clone + install (3 lines)
  - First crawl example
  - One-line flow summary
  - Requirements in > [!NOTE] block
  - Uninstall one-liner

Section 3: How It Works — /massive-crawl
  - ASCII pipeline diagram (3 phases with timing)
  - Brainstorm: recon scouts + user approval (no awesome-list details)
  - Discover: 6-8 Sonnet swarm, self-claiming tasks
  - Pipeline: deterministic Python, no LLM merge
  - > [!TIP] about pruning pause
  - <details> Pipeline internals (dedup, prune, enrich, finalize)

Section 4: /map-capabilities
  - One-line summary
  - Three-phase pipeline (Researcher, Writer, Judge)
  - Batched waves of 15
  - > [!NOTE] about resumability

Section 5: What You Get
  - Output table (catalog.json, explorer.html, RESULTS.md, *_capability.md)
  - > [!IMPORTANT] experimental warning + token cost framing

Section 6: Troubleshooting (collapsed)
  - Commands not found
  - Firecrawl errors
  - Pipeline fails

Section 7: License
  - MIT, no tagline
```

## Formatting Techniques

- `<div align="center">` for hero block
- `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]` GitHub alert blocks
- `<details><summary>` for pipeline internals and troubleshooting
- Tables for outputs
- Fenced code blocks for install and commands
- ASCII box-drawing for pipeline diagram

## What Was Removed

- "Why I Built This" section (opinionated, repetitive)
- "Who This Is For" section (preachy, no info)
- "Why It Works" section (3 subsections repeating same ideas)
- "Heads Up — Experimental" standalone section (merged into [!IMPORTANT])
- "Requirements" standalone section (merged into [!NOTE] in Getting Started)
- Closing tagline

## Estimated Length

~100-120 lines. Down from 155.
