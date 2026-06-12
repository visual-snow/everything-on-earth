# Microsoft FHIR Server Capabilities

Microsoft FHIR Server is a .NET Core open-source implementation of the HL7 FHIR specification supporting STU3, R4, and R5. It is designed for the Azure ecosystem with pluggable persistence backed by either Cosmos DB or SQL Server. It does not include a built-in terminology server, DICOM support, or non-Azure export targets.

## FHIR API

- Exposes a RESTful FHIR API supporting standard CRUD operations, search, and history across all resource types
- Supports batch and transaction bundles
- Resource versioning is configurable per resource type
- Profile validation can be enforced on create and update operations
- FHIRPath is used for search parameter extraction

## Interoperability

- SMART on FHIR authorization via an Azure Active Directory proxy
- Data conversion from HL7v2 and C-CDA XML to FHIR resources using a Liquid templating engine
- Custom conversion templates can be hosted in a container image store

## Bulk Operations

- Bulk export produces NDJSON files written to Azure Blob Storage with configurable concurrency limits
- Bulk import ingests FHIR resources from external storage
- Reindex operations rebuild search indices in the background after search parameter changes

## Persistence

- Cosmos DB backend provides globally replicated, schemaless storage
- SQL Server backend provides schema-versioned relational storage with a migration CLI tool
- Schema upgrades can run automatically on startup or be managed externally via the CLI

## Authentication

- OAuth 2.0 with JWT bearer tokens issued by Azure Active Directory
- An in-process development identity provider is included for local testing without external AAD configuration

## Observability

- Application-level telemetry integrates with Azure Application Insights for request tracing and exception reporting
- A capability statement endpoint reflects the server's supported features and operations

## Constraints

- Bulk export destination is Azure Blob Storage only; no local filesystem or S3 target
- SMART on FHIR proxy requires Azure Active Directory; not compatible with arbitrary OIDC providers without customization
- SQL schema migrations must run in strict version order; skipping versions is unsupported
- Data conversion is disabled by default and requires a container image store for custom templates
- No built-in terminology server, DICOM support, GraphQL, or streaming change feed connector
