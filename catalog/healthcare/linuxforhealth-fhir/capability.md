# LinuxForHealth/FHIR Capabilities

LinuxForHealth/FHIR (formerly IBM FHIR Server) is a modular Java FHIR server implementing FHIR R4 and R4B on OpenLiberty. It exposes a standards-conformant REST API with multi-tenancy, pluggable persistence, and optional clinical intelligence extensions.

Four deployment modes:
- Single-tenant Derby: embedded database for local development and evaluation only.
- Multi-tenant PostgreSQL: recommended production topology with per-tenant schema isolation.
- Citus (experimental): sharded PostgreSQL for high-volume horizontal scale.
- Payload offload: stores large resource payloads in S3 or Azure Blob while keeping metadata in the database.

## FHIR REST API

- All standard FHIR R4 and R4B interactions are supported: read, vread, create, update, patch, delete, search, and history.
- Extended operations include `$validate`, `$everything`, `$export`, `$import`, `$convert`, `$reindex`, and terminology operations.
- Server-side search supports all standard search parameter types, including chained and reverse-chained parameters.
- Conformance is declared via CapabilityStatement and TerminologyCapabilities resources.
- Notification of resource changes can be delivered over WebSocket subscriptions.

## Persistence

- JDBC persistence uses a versioned, normalized schema with a CLI tool for schema creation, upgrade, and migration.
- The schema tool requires an admin database user separate from the runtime user.
- PostgreSQL is the supported production backend; Derby is available for development only.
- Payload offloading to S3-compatible or Azure Blob storage must be configured before any data is ingested; it cannot be applied retroactively to existing data.

## Bulk Operations

- Bulk export and import follow the FHIR Bulk Data Access specification using asynchronous HTTP polling.
- Bulk operations run outside the standard interceptor chain and do not trigger event notifications.
- Export targets can be configured to write to S3-compatible or Azure Blob storage.

## Security and Authorization

- A built-in SMART-on-FHIR interceptor enforces token-based authorization for FHIR API requests.
- An OAuth2 authorization server is not included; an external provider must supply tokens.
- CADF-format audit events record FHIR API interactions for compliance and traceability.

## Terminology and Quality

- A terminology service handles CodeSystem and ValueSet lookup, validation, and expansion.
- A FHIRPath engine evaluates path expressions used in search, validation, and profiles.
- A CQL evaluation engine supports clinical quality measure execution.
- Conformance profiles for US Core, mCODE, and related IGs are bundled and can be activated per tenant.

## Multi-Tenancy

- Each tenant receives an isolated schema within the shared database instance.
- Per-tenant configuration controls which FHIR resource types, search parameters, and profiles are active.

## Constraints

- Java 11 is required; newer JVM versions are not supported.
- Derby must not be used in production environments.
- Payload offload configuration must precede any data ingestion; migration of existing payloads is not supported.
- Bulk export and import skip interceptors and change notifications.
- The schema CLI requires a database admin user distinct from the application user.
- No OAuth2 authorization server, Kafka broker, NATS broker, CDS Hooks service, topic-based Subscription, or administrative UI is included.
