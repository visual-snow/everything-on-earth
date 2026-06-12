# Health Equity Tracker Capabilities

The Health Equity Tracker is an open-source data platform that aggregates and visualizes US health disparity data across race, ethnicity, sex, socioeconomic status, and geography. It covers COVID-19, HIV, chronic disease, maternal health, community safety, and social determinants of health. Data flows through batch ingestion pipelines into a cloud data warehouse; the public frontend has no authentication or access control.

## Data Ingestion

- Per-source ingestion classes fetch raw data from federal and state agencies (CDC, ACS, BJS, KFF, and others)
- A pipeline orchestrator sequences ingestion, staging to cloud storage, and loading into a data warehouse
- Data is stored in standardized metric types: raw counts, rates per 100,000, percentage shares, relative inequity percentages, age-adjusted ratios, and composite index scores

## Visualization

- Single-topic reports display one health metric for a selected US geography (national, state, county, or territory)
- Side-by-side comparison views contrast two geographies or two demographic groups on the same metric
- Choropleth maps show geographic disparity heatmaps at national, state, or county level
- Trend line charts display time-series disparities across available years

## Infrastructure

- Infrastructure is provisioned via declarative configuration for cloud compute, messaging, storage, and data warehouse resources
- CI pipelines run linting, unit tests, and nightly end-to-end browser tests
- PR preview deployments enable review of frontend changes against a test backend

## Constraints

- All data ingestion is batch-only; no real-time or streaming pipeline
- US geographic coverage only; no international data sources
- Environment files are checked into version control; no secrets may be stored in them
- Infrastructure deployment does not automatically detect code changes in containerized services; images must be explicitly rebuilt
- No authentication or access control on the public-facing frontend
- No full-stack local development environment outside of the pipeline orchestration layer
