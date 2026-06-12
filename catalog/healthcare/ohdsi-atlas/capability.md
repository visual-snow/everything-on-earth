# OHDSI Atlas Capabilities

Atlas is an open-source web application for the OHDSI research stack. It provides a graphical interface for defining cohorts, running characterizations, incidence-rate analyses, population-level effect estimation, and patient-level prediction against observational health data stored in the OMOP Common Data Model v5. Atlas has no persistence or computation backend of its own; it communicates exclusively with a separate WebAPI service.

## Cohort Definition

- A visual cohort expression builder constructs inclusion criteria, qualifying events, and censoring logic without writing SQL
- Cohort definitions are serializable as JSON expressions for sharing across sites
- Attrition reporting shows how each criterion affects the cohort size

## Analytics

- Characterization computes prevalence, means, and distributions of features across cohort populations
- Incidence-rate analysis calculates event rates within configurable time-at-risk windows relative to cohort entry
- Population-level estimation runs comparative effect analyses with empirical calibration
- Patient-level prediction builds and evaluates predictive models with AUROC and calibration metrics

## Vocabulary and Search

- A concept search interface browses the OMOP vocabulary across all standard terminologies
- Concept sets can be assembled and reused across multiple cohort definitions

## Authentication

- Supports multiple identity providers including OAuth 2.0 with OpenID Connect, SAML 2.0, Kerberos, LDAP, Active Directory, and database-local credentials
- Entity-level read and write permissions can be managed through the administration interface

## Constraints

- Requires a running OHDSI WebAPI instance; Atlas has no database or computation backend of its own
- Source data must be in OMOP CDM v5 format; no ETL or data-loading capability is included
- Google Chrome is the only officially supported browser
- All R-based analyses execute server-side in WebAPI; Atlas renders results only
- No built-in TLS termination; HTTPS must be provided by an upstream proxy
- No FHIR, HL7, or offline mode
