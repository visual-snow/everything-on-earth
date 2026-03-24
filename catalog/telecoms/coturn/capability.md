Coturn is a free, open-source TURN and STUN server used for WebRTC and VoIP NAT traversal. It acts as a media relay gateway, enabling peers to communicate through firewalls and NATs when direct connections are not possible. It supports the full STUN, TURN, and ICE RFC families and is widely deployed in production WebRTC infrastructure.

## Transport Protocols
- UDP, TCP, TLS 1.0/1.1/1.2/1.3, and DTLS 1.0/1.2 client-to-server transports
- SCTP transport (experimental)

## Operating Modes
- STUN-only mode for NAT address discovery without relaying
- TURN relay mode with UDP relay (RFC 5766) or TCP relay (RFC 6062)
- Secure mode using TLS or DTLS
- Multi-tenant mode via the Origin field

## Authentication
- No-auth mode for open relays
- Classic long-term credential mechanism
- TURN REST API with time-limited HMAC-SHA1 shared-secret tokens
- oAuth third-party authentication

## User and Session Management
- Administration CLI for user creation, quota management, and live session queries
- Test client utilities for STUN and TURN connectivity verification
- Telnet CLI and HTTPS management interface for live stats and configuration

## Observability
- Redis-based status and statistics storage
- Telnet CLI for querying live session and allocation data
- HTTPS management interface for server statistics

## Fault Simulation
- ALTERNATE-SERVER redirection (RFC redirect code 300) can simulate server unavailability to test client failover
- Relay port range restriction can simulate resource exhaustion scenarios
- No built-in network fault injection; traffic-level faults require external tooling at the host level

## Scalability and Backend Storage
- Supports SQLite, MySQL/MariaDB, PostgreSQL, Redis, and MongoDB as user and statistics backends
- DNS SRV records, ALTERNATE-SERVER, and external load balancers supported for horizontal scaling
- Multi-threading model configurable for full CPU utilization

## Constraints
- RFC 5780 NAT behavior discovery requires at least two listening IP addresses of the same address family
- Prometheus metrics support requires building from source; it is not available in standard distribution packages
- SCTP support is experimental and not suitable for production workloads
- No built-in clustering or state replication between instances; external coordination via Redis or DNS/load balancer is required
- No native web dashboard; management is limited to the telnet CLI and HTTPS API
