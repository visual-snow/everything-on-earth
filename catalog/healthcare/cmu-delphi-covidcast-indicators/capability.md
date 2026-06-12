# COVIDcast Indicators Capabilities

COVIDcast Indicators is a collection of Python pipelines that ingest heterogeneous COVID-19 data streams (medical claims, EMR, lab tests, surveys, search trends, official reports), compute aggregate epidemiological signals at fine geographic granularity, and upload them to the COVIDcast Epidata API. Each indicator runs as an independent module; there is no single monolithic entrypoint.

## Data Ingestion

- Per-source indicator pipelines fetch raw data from SFTP feeds, REST APIs, BigQuery, and Socrata endpoints
- Each pipeline produces standardized CSV files with signal value, standard error, sample size, geographic identifier, and date
- NaN codes encode the reason a value is missing rather than leaving fields blank

## Signal Processing

- A shared utilities library provides geographic aggregation (county to MSA, HRR, state) using population-weighted averaging
- Signal smoothing is available for temporal noise reduction
- An archive differ compares new exports against an S3 or git cache to produce incremental issue files for backfill tracking

## Validation

- A validator checks daily CSV outputs against recent API data to detect anomalous spikes, missing signals, and lag violations
- Configurable lag bounds per signal allow tuning for slowly-updating sources
- A dry-run mode executes the full pipeline without treating validation failures as fatal
- Known false-positive errors can be suppressed via configuration

## Monitoring

- A Slack bot monitors for missing expected data across all indicator runs and alerts the operations team
- Structured logging captures pipeline execution details

## Constraints

- Each indicator must be installed and run from its own directory; no unified CLI or single entrypoint
- Cross-resolution geographic aggregation requires the shared geomap utility
- Backfill tracking requires S3 or git archive access; without an archive backend, incremental issue files cannot be produced
- Weekly indicators use CDC epiweek format (Sunday-Saturday); consumers must parse time values accordingly
- No containerized deployment; pipelines run on bare Python virtualenvs managed by Jenkins and Ansible
- No built-in visualization, streaming ingestion, or API server; those are separate projects
