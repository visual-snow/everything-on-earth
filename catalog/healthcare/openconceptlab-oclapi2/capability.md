# OpenConceptLab/oclapi2

OCL API v2 is a Python/Django REST service that manages health terminology resources — concepts, sources, collections, code systems, and value sets — with FHIR R4 compatibility and full-text search. It exposes a browsable REST API, supports OpenID Connect single sign-on via Keycloak as an alternative to token-based Django Auth, and offloads bulk imports and scheduled tasks to Celery workers backed by Redis.

## Terminology Resource Management

- Create, version, and retire concepts with arbitrary custom attributes and mappings
- Organize concepts into sources (authoritative lists) and collections (curated subsets)
- Map between concepts across sources using typed relationships
- Query concepts by code, name, or custom attributes via Elasticsearch full-text search
- Export sources and collections as bulk downloads

## FHIR R4 Interface

- Serve CodeSystem and ValueSet resources through FHIR-compliant endpoints
- Validate FHIR resources via a required FHIR Validator sidecar before ingestion
- Support concept lookup and subsumption operations on CodeSystem resources

## Import and Background Processing

- Bulk-import concepts, mappings, sources, and collections via Celery workers
- Separate worker queues for bulk imports, indexing, and general tasks
- Celery Beat handles scheduled background jobs such as index refreshes
- Bulk-import worker concurrency is intentionally limited to one to protect database integrity

## Authentication and Access Control

- Standard mode uses Django token-based authentication
- SSO mode delegates authentication to an external Keycloak instance via OIDC
- CI mode disables authentication checks for automated test pipelines
- Per-object permission model scopes read and write access to organizations and users

## Observability

- django-silk profiler available in profiling mode for per-request SQL and timing analysis
- Sentry integration for error tracking and exception capture
- Healthcheck endpoints for liveness and readiness probing

## Constraints

- Elasticsearch host requires `vm.max_map_count` set to 262144 or higher
- Redis memory is capped at 2048 MB; exceeding this limit drops cached entries
- FHIR Validator sidecar must be running for any import that includes FHIR resources
- Bulk-import workers are capped at single concurrency; parallel bulk jobs are queued, not parallelized
- No built-in reverse proxy, metrics exporter, or database migration orchestration service
