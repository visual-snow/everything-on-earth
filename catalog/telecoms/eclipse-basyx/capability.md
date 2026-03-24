Eclipse BaSyx Java V2 SDK is an Industry 4.0 platform that provides off-the-shelf Asset Administration Shell server components fully compliant with DotAAS Part 1 and 2 V3. It enables digital twin infrastructure through composable, containerised services for AAS and Submodel storage, discovery, and registration. The platform ships client SDKs alongside each server component for programmatic access.

## Asset Administration Shell Services

- Hosts AAS Repository, Submodel Repository, and Concept Description Repository as independent services or as a single aggregated environment
- Exposes all components through a DotAAS Part 2 V3 REST API with auto-generated OpenAPI specifications and interactive Swagger UI per component
- Supports pre-loading of AAS environments from XML, JSON, and AASX files at startup
- Provides an AAS Registry and Submodel Registry for lifecycle-aware endpoint tracking, with event output modes routed to structured logs or Kafka topics
- Offers an AAS Discovery Service for asset-ID-to-AAS-descriptor resolution
- Includes a browser-based Web UI for human-readable inspection of shells and submodels
- Supports MQTT eventing on AAS and Submodel Repositories for real-time change notifications

## Persistence and Configuration

- Runs in volatile in-memory mode or durable MongoDB-backed mode, switchable via a single property
- All Spring Boot configuration properties are overridable through environment variables, requiring no file edits at runtime
- Auto-registration and auto-discovery integration URLs are configurable per repository component
- CORS policy, MongoDB connection, and MQTT broker settings are all externally configurable

## Observability

- Health status available on every component via Spring Boot Actuator health endpoint
- MongoDB and MQTT infrastructure containers include dedicated readiness probes

## Constraints

- Only DotAAS V3 AAS formats are supported; V1 and V2 formats are incompatible with this SDK generation
- Upload file size is capped by Spring multipart limits (1 MB per file, 10 MB per request by default) and must be raised explicitly for large environments
- Duplicate Identifiable IDs across pre-loaded environments cause startup errors; Concept Descriptions are silently deduplicated as an exception
- OPC-UA server integration is not wired up in the default stack and requires additional custom configuration
- No built-in authentication or authorization is enabled in the minimal setup; OAuth2 or Keycloak must be configured separately for secured deployments
- No simulation or device-emulator component is included; AAS data must be supplied through file pre-configuration or REST API calls
