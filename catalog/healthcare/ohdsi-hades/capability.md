# OHDSI HADES Capabilities

HADES (Health Analytics Data-to-Evidence Suite) is a collection of over 35 open-source R packages for large-scale observational health data research against the OMOP Common Data Model. It covers the complete analytic lifecycle from cohort definition through population characterization, causal effect estimation, patient-level prediction, and evidence synthesis. All packages require data in OMOP CDM format; MySQL is explicitly unsupported.

## Cohort Definition and Phenotyping

- An R-native DSL and JSON-based cohort expression language define inclusion criteria, qualifying events, and censoring logic
- Cohort diagnostic tools evaluate phenotype quality with sensitivity, specificity, positive predictive value, and negative predictive value
- A community-maintained phenotype library provides pre-defined cohort definitions
- Cohorts are instantiated against CDM databases via a dedicated generator package

## Population Characterization

- Descriptive statistics cover demographics, conditions, drugs, measurements, procedures, and costs across entire CDM databases
- Data quality rules evaluate completeness, conformance, and plausibility
- Incidence rate and proportion computations support time-at-risk analyses

## Causal Effect Estimation

- New-user cohort studies with large-scale propensity score matching and outcome modeling
- Self-controlled case series and self-controlled cohort designs for within-patient comparisons
- Meta-analytic evidence synthesis combines estimates across distributed sites
- Negative-control-based empirical calibration adjusts p-values and confidence intervals for systematic error

## Patient-Level Prediction

- Machine learning predictive models using regularized regression, gradient boosting, and other algorithms
- Deep learning and ensemble model variants extend the prediction toolkit
- Models report AUROC, calibration, and Brier score metrics

## Orchestration

- A study orchestration layer coordinates multi-package analyses across distributed CDM databases
- Interactive Shiny applications provide browser-based exploration of stored results

## Constraints

- MySQL is explicitly not supported; supported platforms include PostgreSQL, SQL Server, Oracle, Amazon Redshift, Google BigQuery, and Spark
- All source data must be transformed to OMOP CDM before any HADES package can run
- R 4.4.1 or later is the supported target; Java is required for database connectivity and regression
- Several packages are not on CRAN and require GitHub installation with a personal access token
- No Docker images, REST API server, or Python SDK; all analytics run in R
