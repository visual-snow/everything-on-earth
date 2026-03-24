PyHSS is a Python 3 Home Subscriber Server and subscriber data management solution for LTE (4G) Evolved Packet Core networks. It consolidates multiple 3GPP network functions—HSS, VoLTE HSS, EIR, PCRF, BSF, and GMLC—into a single deployable stack, exposed through both Diameter interfaces and a Swagger-documented REST API. Subscriber capacity has been tested beyond one million entries, making it suitable for realistic load scenarios.

## Subscriber Management
- Create, read, update, and delete subscriber records via REST API
- Manage subscriber authentication vectors and IMSI/MSISDN bindings
- Assign subscriber profiles for IMS/VoLTE services
- Provision emergency subscriber entries with configurable TTL

## Diameter Protocol Support
- S6a: MME authentication and location management (standard LTE attach/detach)
- Cx/Sh: IMS/VoLTE P-CSCF and S-CSCF authentication and routing
- S13: IMEI-based equipment identity verification (EIR role)
- Gx: Policy and charging rules exchange (PCRF role)
- SLh: Subscriber location discovery (GMLC role)
- Zh/Zn: Generic Bootstrapping Architecture credential generation (BSF role)
- Device-Watchdog-Request keepalives and Capabilities-Exchange handshakes

## 2G/3G Interoperability
- GSUP interface for OpenBSC and Osmocom core network peers
- Enables multi-generation (2G/3G/4G) subscriber data sharing from a single HSS

## Operational Modes
- Run as any single network function or as the full combined stack
- Trusting Diameter mode accepts connections from any peer without verification
- TCP transport (load-tested) or SCTP (experimental, multihomed)
- Database backend selectable: MySQL, PostgreSQL, or SQLite

## Observability
- Prometheus metrics exported by dedicated metrics service
- SNMP support retained for legacy monitoring integration
- Centralised log aggregation across all microservices

## Constraints
- Redis 7.0.0 or later is a mandatory runtime dependency for inter-service message queuing; the stack will not start without it
- Diameter operates in trusting mode by default with no peer certificate or shared-secret authentication, and no TLS/DTLS encryption for transport
- SCTP transport is experimental and has not been load-tested; only TCP is validated for production-scale use
- No built-in rate limiting or denial-of-service protection for Diameter or REST API endpoints
