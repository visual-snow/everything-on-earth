# CMU Delphi COVIDcast Capabilities

COVIDcast is a set of R and Python client libraries for accessing Delphi's COVIDcast Epidata API — a public epidemiological data service providing daily-updated COVID-19 indicators across US geographic regions. It does not compute or serve data; it provides structured programmatic access to an external API, plus tooling for forecast evaluation and model development.

## Data Access

- Retrieves COVID-19 signals including confirmed cases, deaths, symptom survey indices, insurance claims-based illness estimates, and mobility indicators
- Supports geographic granularities from county and state to metropolitan areas, hospital referral regions, DMAs, HHS regions, and national aggregates
- Supports daily and epiweek time resolutions
- Enables point-in-time historical snapshots via as-of queries, preserving the data as it existed on a given issue date
- Each signal observation carries an estimate value, standard error, sample size, issue date, and lag

## Forecast Support

- Provides R tooling for building hotspot prediction models and short-horizon forecasts
- Includes a probabilistic forecast evaluator with backfill-aware backtesting, accounting for data revisions between initial publication and later updates

## Visualization

- Generates choropleth and bubble maps of signal data across US geographies using native plotting integrations in both Python and R

## Constraints

- US geographic coverage only; no international geographies
- API enforces a maximum row limit per query; results beyond the threshold are silently truncated
- Anonymous access is rate-limited and restricts multi-valued query parameters; an API key removes those limits
- The original R client package is officially deprecated; the supported replacement is a separate package

## Out of Scope

- No data ingestion, indicator computation, or signal processing infrastructure
- No API server or backing database
- No real-time or streaming data delivery
- No built-in forecasting models
- No CLI tooling
