Routr is a cloud-native SIP proxy, registrar, and location server designed for telephony carriers, communication service providers, and integrators. It provides programmable SIP routing with multi-tenant and multi-domain architecture, supporting load balancing across media servers such as Asterisk and FreeSWITCH.

## Routing

- Intra-domain routing between endpoints within the same domain
- Domain ingress routing for calls entering a domain from external peers
- Domain egress routing for calls leaving a domain toward external trunks
- Peer egress routing for traffic between peer networks
- Session affinity mode for sticky routing to specific media servers during load balancing

## SIP and Transport

- SIP signaling over UDP, TCP, TLS, WebSocket, and WebSocket Secure
- Endpoint authentication via JWT
- RTPEngine middleware integration for media proxying

## APIs and Management

- gRPC API server for programmatic control and health inspection
- Command-line management tool for administrative operations
- Node.js SDK for custom integration and automation
- Processor framework for custom feature logic
- Middleware framework for cross-cutting concerns such as authentication and rate limiting

## Configuration and Data

- JSON and YAML file-based configuration
- PostgreSQL as a relational data source
- Redis-backed location service for persistent endpoint registration
- Helm Charts for Kubernetes deployments

## Constraints

- Region-based routing is not yet implemented
- STIR/SHAKEN call authentication is not yet implemented
- Web application UI is not yet implemented
- The in-memory location service backend does not persist registrations across restarts; Redis is required for persistence
- No built-in metrics or observability stack; health state must be inferred via the gRPC API server
