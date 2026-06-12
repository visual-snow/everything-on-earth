# OpenEMR Capabilities

OpenEMR is a full-stack open-source EHR and medical practice management system. It covers the complete clinical and administrative workflow — patient records, scheduling, billing, and patient-facing access — and exposes standards-based APIs for integration with external systems.

Two deployment postures:
- Production: versioned, stable release for live clinical environments.
- Development: flexible or nightly build variants for testing and customization.

## Clinical and Administrative Functions

- Clinicians can create, retrieve, and update patient records, encounters, and clinical documentation.
- Scheduling supports appointment management across a practice.
- Billing handles electronic claims and practice revenue workflows.
- Patients interact with their records and care team through a dedicated patient portal.
- Multiple sites can be hosted from a single instance using path-based multitenancy.

## Interoperability

- FHIR R4 resources are exposed over a REST API conforming to US Core 8.0 and USCDI v1.
- A SMART on FHIR v2.2.0 launch framework supports app authorization and context-aware EHR integrations.
- Bulk data export delivers large patient populations in NDJSON format over asynchronous HTTP.
- An OpenEMR-native REST API provides access to records and workflows beyond the FHIR surface.
- An interactive API explorer is available for developers to browse and test endpoints.

## Authorization

- OAuth 2.0 with OpenID Connect governs all API and portal access.
- PKCE is supported for public and single-page application clients.
- OAuth2 clients are registered with named scopes and redirect targets.
- FHIR resource access is controlled by granular per-scope permission flags and category filters.

## Measurement

- A token introspection endpoint allows callers to verify access token validity at runtime.
- A health readiness endpoint reflects overall system availability.

## Configuration

- REST and FHIR APIs can be enabled or disabled independently from administration settings.
- The site base URL must be set for OAuth2 and FHIR endpoint resolution to function.
- Multitenancy routing is path-based; each tenant shares the same database backend.

## Constraints

- All API and OAuth2 communication requires HTTPS; HTTP-only deployments cannot use these surfaces.
- MariaDB and MySQL are the only supported database backends.
- SMART app launch and OAuth2 flows require a publicly resolvable site address.
- The patient portal API is experimental and not production-stable.
- No DICOM imaging, telemedicine, lab instrument integration, or message broker is included.
