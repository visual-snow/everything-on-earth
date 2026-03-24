The YANG Catalog platform is a centralized repository that aggregates YANG configuration models alongside validation services, a module search interface, and a web-based admin UI. It supports both local development and production deployment modes, with additional targets for Kubernetes and OpenShift environments. The platform integrates with OpenSearch for indexing, RabbitMQ for messaging, Redis for caching, and Nginx as a reverse proxy.

## Components

- Backend API server handling module storage, search, and catalog operations
- Frontend Angular web UI and admin UI for browsing and managing modules
- YANG regex validation tool (yangre-gui) for testing YANG pattern expressions
- YANG file validation application (yangvalidator) for schema conformance checks
- Module compilation scripts for YANG file analysis and pre-processing

## Protocols

- HTTP and HTTPS for web UI and API access
- NETCONF and RESTCONF for network device configuration model interactions
- YANG as the data modeling language throughout

## Configuration

- OpenSearch connectivity: AWS-managed or self-hosted, configurable host and port
- RabbitMQ credentials for message queue authentication
- TLS certificate files for secure communication
- System user and group identities for service isolation
- Git user identity for module repository integration
- Software version pins for ConfD, yanglint, and xym tooling

## Observability

- All service logs collected in a configurable log directory
- Admin UI provides log filtering and review across components
- Cron failure alerts delivered via configurable email recipient

## Deployment Modes

- Local development: fully containerized stack with embedded OpenSearch
- Production: external AWS OpenSearch Service integration
- Kubernetes: alternative orchestration via dedicated deployment guide
- OpenShift: multi-tenant Kubernetes variant with non-root security constraints

## Constraints

- ConfD (Tail-F proprietary software) is required but cannot be freely distributed and must be acquired separately before deployment
- Development environments require at least 10 GB RAM and 45 GB of module data capacity
- Production environments require at least 24 GB RAM and 250 GB of data capacity
- IPv4 connectivity is required for pulling images from Docker Hub
- A shared volume must be mounted for inter-container data exchange
