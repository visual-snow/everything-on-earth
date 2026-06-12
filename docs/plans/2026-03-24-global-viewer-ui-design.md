# Global Viewer UI/UX Design

## Overview

Redesign the everything-on-earth explorer from a single-page filterable card grid into a multi-page static site with knowledge graph visualization, unified brand identity, and per-repo detail pages.

## Architecture: Static Site Generator (Approach A)

Extends the existing Jinja2 pipeline. No new toolchain. All pages generated at build time.

## Pages

### 1. Landing Page (index.html)

DeepMind-inspired homepage. Dark background (#0d0d0d). Centered title "Everything on Earth" with node-graph globe logo. Subtitle with total repo count. Responsive grid of symmetric cards, one per catalog domain.

Each card:
- Domain-specific wireframe icon (shield for cyber, antenna for telecom, controller for gaming)
- Domain name + stats ("397 tools across 23 domains")
- "Explore" button
- Hover: subtle lift + glow

Scales naturally to N catalogs.

### 2. Graph Explorer (catalog/{slug}/index.html)

Two-column layout: fixed sidebar (280px) + graph canvas.

**Sidebar:**
- Breadcrumb: Home > {Domain}
- Search input (filters nodes in real-time)
- Collapsible sub-domain list (click to highlight cluster)
- Sort toggle (score / stars / activity)
- Stats footer (total repos, domains, avg score)

**Graph canvas:**
- Library: force-graph (WebGL, handles 1000+ nodes at 60fps, ~50KB CDN)
- Nodes: circles sized by quality_score (4px min, 20px max)
- Node colors: heat-mapped by quality score
  - Green (#3fb950): score >= 70
  - Amber (#d29922): score 40-69
  - Dim gray (#484f58): score < 40
- Edges: faint lines connecting repos with shared sub-domain or >= 2 shared tags
- Hover: tooltip (name, stars, score)
- Click: navigates to detail page
- Controls: scroll zoom, drag pan, double-click center

Edge list computed at build time in Python, embedded in page JSON.

### 3. Detail Page (catalog/{slug}/detail/{repo-slug}.html)

Same two-column layout as graph explorer.

**Sidebar:**
- Breadcrumb: Home > {Domain} > {Repo}
- Search input (typing navigates to graph with filter)
- "Nearby repos" list (repos connected in graph, max 10)
- "Back to graph" button

**Main content:**
- Header: repo name (h1), quality score badge (color-coded), stars, language, license pills, tags, last activity
- "View on GitHub" button
- Horizontal divider
- capability.md rendered as HTML (fallback: description field)

## Brand Identity

Unified "Everything on Earth" brand across all pages. Domains are sections, not separate identities.

**Design system: "Obsidian Monolith"** (validated via UI/UX Pro Max)

### Color Tokens (CSS Variables)

| Role | Hex | Variable |
|------|-----|----------|
| Background (landing) | `#0d0d0d` | `--bg-deep` |
| Background (pages) | `#0d1117` | `--bg-base` |
| Surface (cards/sidebar) | `#161b22` | `--bg-surface` |
| Surface elevated | `#21262d` | `--bg-elevated` |
| Border | `#30363d` | `--border` |
| Text primary | `#e5e2e1` | `--text-primary` |
| Text secondary | `#8b949e` | `--text-muted` |
| Link/accent | `#58a6ff` | `--accent` |
| Score high (>=70) | `#3fb950` | `--score-high` |
| Score mid (40-69) | `#d29922` | `--score-mid` |
| Score low (<40) | `#484f58` | `--score-low` |
| Destructive | `#f85149` | `--destructive` |

### Typography

- Headings/labels: Space Grotesk (700 for display, 600 for h1-h3, 500 for labels)
- Body: Inter (400 regular, 500 medium)
- Scale: 12 / 14 / 16 / 18 / 24 / 32 / 48
- Line height: 1.5 body, 1.2 headings
- Max line length: 75 characters

### Spacing & Radius

- Spacing scale: 4px increments (4 / 8 / 12 / 16 / 24 / 32 / 48)
- Cards: border-radius 8px
- Inputs: border-radius 6px
- Pills/tags: border-radius 4px
- Touch targets: min 44x44px

### Accessibility (WCAG AA)

- Text contrast: >= 4.5:1 (primary text on bg-base = 12.4:1)
- Focus states: 2px solid #58a6ff outline
- Keyboard navigation: full tab support on graph, sidebar, forms
- prefers-reduced-motion: disable graph animations, static layout
- SVG icons only (Lucide), no emojis
- cursor-pointer on all clickable elements

### Responsive Breakpoints

- Mobile: 375px
- Tablet: 768px (sidebar collapses to drawer)
- Desktop: 1024px
- Wide: 1440px

**Logo:** Node-graph wireframe globe (variant 3 — clean, fewer nodes, clear sphere silhouette). White on dark. Used as favicon + header logo.

**Domain icons:** Wireframe node-graph style, gradient dark background. Consistent line weight and node size across all domains:
- Cybersecurity: shield shape
- Telecom: antenna/tower shape
- Gaming: controller shape (PlayStation-style, variant 2)

Future domains get new icons in the same wireframe family.

## Generated File Structure

```
catalog/
  cybersecurity/
    index.html              <- graph explorer
    detail/
      sherlock.html          <- one per repo
      nmap.html
      ...
    catalog.json             <- existing, unchanged
  telecom/
    index.html
    detail/
      free5gc.html
      ...
    catalog.json
index.html                   <- landing page
assets/
  logo.png                   <- node-graph globe
  icons/
    cybersecurity.png
    telecom.png
    gaming.png
```

## Pipeline Integration

- `run_finalize()` generates index.html (graph explorer) + detail/{slug}.html per repo
- New Jinja2 templates: `landing.html`, `graph.html`, `detail.html`
- Replaces old `explorer.html` template
- Edge list computed in Python during finalize
- capability.md read from disk, rendered into detail pages
- Landing page generated separately, reads all catalog directories

## Dependencies

- `force-graph` via CDN (WebGL force-directed graph, ~50KB)
- No other new dependencies

## Navigation

Breadcrumb + sidebar for persistent navigation. Browser-native page transitions. Back button works naturally.

## Stitch Mockups

Generated in Stitch project `13542425217429128933`:
- Landing: screen `67daf1cd4ef34391a5125e8b8bb0545e`
- Cyber graph: screen `1d4c6f7b97344c61bd9cca32bebe1459`
- Telecom graph + detail: additional screens in same project

## Brand Assets (Generated with Nano Banana 2)

- Logo: `/tmp/eoe-logo-3.png` (selected)
- Domain icons: `/tmp/eoe-domain-icons-1.png` (cyber + telecom)
- Gaming icon: `/tmp/eoe-gaming-icon-2.png` (selected)

Assets to be copied into `assets/` during implementation.
