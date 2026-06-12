# HAPI FHIR Capabilities

HAPI FHIR is a Java library and server framework for building HL7 FHIR clients and servers. It ships as a modular toolkit covering model objects, parsers, REST clients, and two distinct server modes — a lightweight plain/facade server and a full JPA server backed by a relational database — with support for FHIR versions DSTU2 through R5.

Two server modes:
- Plain/Facade server: delegates resource storage to application code; no built-in persistence layer.
- JPA server: manages full FHIR persistence on a relational database schema with search, versioning, and subscription.

## FHIR Parsing and Model

- Java model classes cover all FHIR resource types across DSTU2, DSTU3, R4, R4B, and R5.
- JSON and XML encoders and parsers handle serialization and deserialization of FHIR resources.
- A fluent builder API constructs and traverses resources programmatically.
- A context object caches parsed definitions for efficient repeated use.

## REST Clients

- A generic client issues typed FHIR operations against any conformant server.
- An annotation-driven client maps Java interface methods to FHIR REST calls.
- Both clients support synchronous and asynchronous ($export, batch) request patterns.

## Plain and JPA Servers

- The plain server routes incoming FHIR REST requests to provider classes written by the application developer.
- The JPA server stores resources, history, search parameters, and metadata in a relational schema; Elasticsearch can supplement full-text search but cannot replace the relational backend.
- The JPA server supports multitenancy via partitioning; all tenants share a single logical ID space within a partition.
- Referential integrity is enforced at the application layer; the database schema does not use foreign-key constraints for FHIR references.

## Clinical and Workflow Features

- MDM patient and practitioner matching links records across source systems using configurable rule sets.
- A subscription engine delivers resource change notifications over REST-hook and WebSocket channels.
- CDS Hooks integration exposes decision-support hooks callable from EHR launch contexts.
- International Patient Summary (IPS) generation assembles a cross-border summary document from stored resources.
- Async batch jobs run long-running operations ($export, reindex) outside the request cycle.

## Validation and Query

- The instance validator checks FHIR resources against base profiles and custom StructureDefinitions.
- HFQL provides a SQL-like query language over stored FHIR resources for ad-hoc data access.
- OpenAPI/Swagger documentation is generated automatically from server capability statements.

## Configuration and Integration

- Spring Boot auto-configuration wires HAPI FHIR beans into Spring application contexts with minimal boilerplate.
- A CLI tool supports development tasks including validation and server startup.
- The JAX-RS server adapter runs HAPI FHIR providers inside JAX-RS containers.

## Constraints

- A relational database (PostgreSQL, H2, MSSQL, Oracle) is required for the JPA server; Elasticsearch alone is not sufficient.
- MySQL and MariaDB are deprecated and not recommended for new deployments.
- Partitioned multitenant servers maintain a single shared ID pool across all tenants.
- External FHIR references are rejected by the JPA server by default unless explicitly allowed.
- No built-in OAuth2 or OIDC authorization server is included; token validation must be wired externally.
- Native GraphQL and Kafka-based subscriptions are not part of the core distribution.
