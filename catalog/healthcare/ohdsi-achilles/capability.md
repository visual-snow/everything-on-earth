# OHDSI Achilles Capabilities

Achilles (Automated Characterization of Health Information at Large-Scale Longitudinal Evidence Systems) is an R package that generates approximately 200 descriptive statistics analyses over an OMOP Common Data Model v5.x database. It produces pre-computed summary results consumed by ARES, Atlas, and other OHDSI tools for data characterization and quality assessment.

## Analyses

- Covers person demographics, visits, conditions, drugs, measurements, procedures, observations, death records, and optionally cost data
- Produces counts, prevalence proportions, distribution statistics, and temporal trend analyses stored in dedicated result tables
- A small-cell-count threshold suppresses low-count cells to protect patient privacy

## Execution Modes

- Single-threaded mode uses temporary tables and is compatible with all supported database platforms
- Multi-threaded mode uses permanent staging tables for parallel execution on massively parallel processing platforms
- SQL-only mode generates dialect-specific SQL files without executing against the database, enabling review or offline import
- Selective analysis mode allows targeted re-computation of specific analysis IDs without re-running the full suite

## Database Support

- Connects via JDBC through the OHDSI DatabaseConnector library
- SQL dialect translation handles differences across PostgreSQL, SQL Server, Oracle, Amazon Redshift, and other supported platforms
- Post-processing indices can be added to result tables to improve downstream query performance

## Export

- Generates JSON artifacts for the ARES data quality viewer
- Result tables integrate directly with Atlas for cohort characterization and data source profiling

## Constraints

- Requires R 4.0.0 or later and a Java runtime for JDBC connectivity
- Supports OMOP CDM v5.3 and v5.4 only; earlier versions are not supported
- Index creation is not supported on Amazon Redshift or IBM Netezza
- Multi-threaded mode requires a writable scratch schema accessible alongside the CDM and results schemas
- Oracle requires a temporary table emulation schema with CREATE and INSERT permissions
- Setting the small-cell-count threshold to zero disables suppression and may expose re-identifiable data
- No REST API, Docker image, or built-in data quality rule engine
