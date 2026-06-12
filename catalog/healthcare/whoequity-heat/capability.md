# WHO HEAT Capabilities

The WHO Health Equity Assessment Toolkit (HEAT) is an R/Shiny web application that visualizes within-country health inequalities through disaggregated data and over 20 summary inequality measures. It ships in two editions: HEAT with a built-in WHO Health Inequality Data Repository, and HEAT Plus which accepts user-uploaded datasets. Available as online and offline desktop editions.

## Inequality Assessment

- Computes absolute and relative inequality measures across demographic dimensions (wealth quintiles, education, sex, region, subnational area)
- Ordered measures include the Absolute and Relative Concentration Index, Slope and Relative Index of Inequality
- Non-ordered measures include Between-Groups Variance, Coefficient of Variation, Mean Log Deviation, and Theil Index
- Simple measures include Rate Difference and Rate Ratio between best and worst performing subgroups
- Population-level measures include Population Attributable Risk and Population Attributable Fraction
- Confidence intervals are computed via Monte Carlo simulation with parallel processing

## Exploration Modes

- Explore Inequality mode examines a single country's health indicators over time with interactive charts and maps
- Compare Inequality mode benchmarks multiple countries for a selected indicator and disaggregation dimension

## Data Sources

- The built-in edition provides read-only access to the WHO Health Inequality Data Repository
- HEAT Plus accepts user-uploaded CSV or Excel datasets conforming to the HEAT data schema
- An internal data processing package validates and converts uploads to an optimized columnar format

## Deployment

- Online editions are hosted by WHO with no installation required
- Desktop editions bundle a portable R runtime and Chromium browser for fully offline use
- HEAT Plus online supports Azure AD authentication for user data persistence

## Constraints

- Built-in WHO data is not licensed under AGPL and cannot be used for commercial promotion or political activities
- Ordered inequality measures only apply to subgroups with a natural ranking; they cannot be computed for unordered dimensions like region or sex
- HEAT Plus users must not upload personal data or data violating privacy law to WHO servers
- No Docker, REST API, or FHIR export; the application is Shiny-only with export limited to charts and CSV/Excel tables
- Desktop editions depend on a portable R runtime; no containerized deployment is provided
