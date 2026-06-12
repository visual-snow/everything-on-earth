# CDC DEX FHIR Facade Capabilities

The CDC Data Exchange FHIR Facade is a proof-of-concept ASP.NET Core service that ingests HL7 FHIR R4 Bundle resources and stores them to cloud object storage. It provides JWT authentication via a cloud identity service, structured logging, and OpenTelemetry trace export. It is a write-only ingestion endpoint; no FHIR search or resource read operations are implemented.

## Ingestion

- Accepts FHIR R4 Bundle resources via a POST endpoint in JSON or XML format
- Parses and validates incoming bundles against the FHIR R4 specification before storage
- Maximum supported bundle size is 300 MB
- Stores validated bundles as objects in cloud storage

## Authentication

- JWT bearer token authentication validates required OAuth2 scopes per request
- Scope configuration defines which client identifiers, organizations, and data streams are authorized
- Partial scope matches are rejected; all configured scopes must be present in the token

## Observability

- Structured logs are written to a cloud logging service with per-request timestamps and correlation
- OpenTelemetry traces are exported via gRPC to a configurable collector endpoint
- Log batches are additionally persisted to cloud storage for long-term retention
- A health endpoint reports service availability and dependency status

## Metadata

- A FHIR CapabilityStatement endpoint describes the server's supported interactions

## Constraints

- FHIR R4 only; no R5 or STU3 support
- Write-only ingestion; no FHIR search, read-by-ID, or query operations
- Proof-of-concept status; not cleared for production PHI workloads
- Storage is flat-file cloud objects, not an indexed FHIR resource database
- No SMART on FHIR launch context or patient-level scopes; only system and organization scopes
- No FHIR Subscriptions, Bulk Data export, or CDS Hooks
