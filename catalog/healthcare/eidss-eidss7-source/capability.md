# EIDSS v7 Capabilities

EIDSS v7 (Electronic Integrated Disease Surveillance System) is an open-source multi-domain epidemiological surveillance platform used by public health and veterinary authorities. It covers human disease case reporting, animal health events, laboratory sample management, vector surveillance, and outbreak investigations. It is built on ASP.NET Core with a SQL Server backend and a Blazor/Razor web frontend. The repository README is a blank placeholder with no installation instructions.

## Surveillance Domains

- Human disease surveillance: individual case reporting, aggregate disease reports, active surveillance campaigns, ILI aggregate forms, weekly reporting, and WHO-formatted export
- Veterinary surveillance: animal disease case reporting, farm management, active surveillance sessions, and aggregate action reports
- Outbreak investigation: session-based investigation workflow with linked human cases and document management
- Vector surveillance: vector surveillance session recording and reporting

## Laboratory

- Sample and test management with specimen tracking through laboratory workflows
- Freezer and biobank management for specimen storage
- LOINC-to-EIDSS code mapping for standardized test identification

## Geographic Information

- Map-based visualization with a four-level administrative hierarchy
- Geocoding integration for address resolution

## Reporting

- Report viewer backed by a configurable report server with upload and download capabilities
- Aggregate reporting and analytics sub-schema for epidemiological summaries

## Administration

- Organisation, employee, site, user-group, and access-rule management
- System preferences and configuration management
- Multi-language support driven by per-language connection strings

## Authentication

- JWT bearer token authentication with configurable issuer, audience, and expiration
- OAuth 2.0 authorization and token endpoints
- Structured audit logging of user and system events

## Constraints

- Requires Microsoft SQL Server; no alternative database backend
- Three database connection strings must be supplied with no fallback defaults
- JWT secret must be configured explicitly; zero clock-skew enforcement means token expiration is strict
- The repository README is blank; no build, installation, or deployment instructions are documented
- No containerized deployment, CI/CD pipeline, or OpenAPI definition file is shipped
- External integration is limited to a single national patient identification service with no federated reporting adapters
