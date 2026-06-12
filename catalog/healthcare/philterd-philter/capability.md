# Philter Capabilities

Philter is a self-hosted REST service for detecting and de-identifying PII and PHI in plain text and PDF documents. It wraps the Phileas redaction engine and exposes HTTP endpoints for filtering content and managing named filtering policies. It ships a web UI, optional NER model servers for person names and medical conditions, and optional search-backed span storage. It does not include an audit log, a FHIR endpoint, or built-in API authentication.

## PII and PHI Detection

- Detects PII and PHI entities in free text and PDFs using named filtering policies
- Policies control which entity types are active, which detection strategies apply, and what transformation is applied per type
- Person-name detection uses a dedicated NER model server that must be reachable at startup
- Medical-condition detection uses a second NER model server, separately addressable
- Policies can be stored on disk or in S3 and are resolved by name at request time

## De-identification Strategies

- Supports redact, mask, replace, and shift transformations, configurable per entity type within a policy
- Date shifting displaces dates by a consistent offset to preserve temporal relationships while obscuring absolute values
- Mixed strategies are supported within a single policy pass — different entity types can use different transformations
- PDF filtering returns either a redacted PDF or a ZIP of redacted page images, depending on the endpoint called

## Policy Management

- Named policies are the primary configuration unit; each request references a policy by name
- Multiple policies can coexist, allowing different sensitivity profiles for different data classes
- Policy changes take effect without restarting the service

## Observability

- Exposes a health and status endpoint for liveness checks
- Prometheus metrics are available for request counts and latency
- JMX metrics are available as an alternative to Prometheus
- Datadog metrics integration is optionally configurable
- An optional search and span storage backend can record detected spans for later inspection

## Deployment

- Runs as a standalone Java service; requires Java 17 or later
- Web UI is included and served by the same process
- NER model servers are separate processes that must be reachable before the main service accepts traffic
- Redis can be enabled as a response cache; it is disabled by default
- GPU acceleration for NER inference requires an NVIDIA runtime on the host
- All state beyond policies is held in memory or in the optional external backends; the core service itself is otherwise stateless

## Constraints

- No built-in API authentication or rate limiting; network-layer controls must be applied externally
- No audit log or redaction provenance; there is no record of which spans were transformed or by which policy
- No FHIR or HL7 endpoint; input is plain text or PDF only
- The bundled search security configuration is not production-ready and must be hardened before exposure
- Detection recall is bounded by the NER models and regex patterns in the active policy; automated de-identification must be supplemented with additional safeguards for regulatory compliance
- Deanonymization is not supported for any transformation strategy; all operations are irreversible
