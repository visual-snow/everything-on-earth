Kamailio is an open-source SIP server (RFC 3261) designed for high-scale real-time communications including IP telephony, instant messaging, and presence. It operates as a core routing engine extended by loadable modules, capable of serving millions of users across a range of deployment roles. Configuration is driven by a routing script that controls every aspect of call and message handling.

## Operational Modes
- SIP registrar and location server
- Stateless and stateful SIP proxy
- Session Border Controller and edge proxy
- IMS (IP Multimedia Subsystem) server
- Presence server
- Load balancer and dispatcher

## Protocol Support
- SIP (RFC 3261) and SIP-T
- WebSocket and WebRTC gateway
- TLS for encrypted signaling
- HTTP via embedded server
- IPv4 and IPv6
- XML-RPC and JSON-RPC

## Core Components
- Modular plugin architecture with per-startup module loading
- Registrar, dialog, dispatcher, and presence server modules
- Database abstraction layer supporting MySQL, PostgreSQL, SQLite, and Redis
- EVAPI interface for third-party event integration
- RPC interface for runtime introspection and control

## Observability
- Statistics module exporting counters via RPC
- JSON-RPC and XML-RPC introspection endpoints
- Syslog-based logging with configurable severity levels
- SIP traffic capture and Homer integration via sipcapture module

## Constraints
- No built-in fault injection primitives; failure simulation requires external tooling or custom routing script logic
- No native Prometheus metrics endpoint; a third-party exporter is required for scraping
- Configuration language is a custom routing script DSL, not a standard format like YAML or JSON, which presents a steep learning curve
- Shared-memory architecture means horizontal scaling requires multiple independent nodes; there is no native state synchronization between instances without an external database
