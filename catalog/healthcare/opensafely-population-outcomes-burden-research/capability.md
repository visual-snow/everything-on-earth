# OpenSAFELY Population Outcomes Research Capabilities

This repository contains study-specific analytic code for an OpenSAFELY research project examining changes in rates of cardiometabolic and pulmonary events during the COVID-19 pandemic using NHS primary and secondary care records. It is not a reusable framework; it is a reproducible research pipeline producing pre-approved aggregated outputs.

## Study Design

- Measures monthly rates of stroke, myocardial infarction, deep vein thrombosis, pulmonary embolism, acute kidney injury, heart failure, ketoacidosis, and all-cause mortality
- Study window spans February 2019 through October 2020 in monthly snapshots
- Population is NHS patients aged 18 to 110 with at least one year of continuous registration

## Pipeline

- A three-action OpenSAFELY pipeline generates cohorts, calculates measures, and produces visualizations
- Cohort and variable definitions use the OpenSAFELY cohortextractor framework
- Clinical outcomes are defined via CTV3 Read codes for primary care and ICD-10 codes for secondary care
- Time-series plots display monthly event rates with 95% confidence intervals as stacked bar charts

## Privacy

- All analysis executes within the OpenSAFELY secure server; patient-level data never leaves NHS infrastructure
- Aggregated outputs require OpenSAFELY review and approval before public release
- Small-number redaction masks numerator and denominator values between 1 and 5

## Constraints

- Must execute within the OpenSAFELY secure analytics platform; cannot be run against arbitrary databases
- Aggregated outputs require manual review and approval before release
- Study window and population criteria are fixed; not parameterized for reuse on different cohorts
- No individual-level patient data is present in the repository by design
- No multivariable regression or adjustment; rates are unadjusted counts stratified by COVID-19 status only
- No SNOMED CT codelists; primary care outcomes use CTV3 Read codes throughout
