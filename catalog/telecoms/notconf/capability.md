Notconf is a NETCONF/RESTCONF device simulator built on Netopeer2, Rousette, and Sysrepo. It exposes standard network management interfaces without performing any real network functions, making it a drop-in replacement for Cisco NSO netsim in test and automation environments. Pre-built profiles are available for Cisco IOS XR, IETF models, Juniper JUNOS, and Nokia SROS.

## Protocols

- NETCONF over SSH
- RESTCONF over HTTP/2
- YANG data modeling for module definitions

## Configuration

- YANG modules loaded automatically from a designated directory at startup
- Optional YANG features enabled via a CSV file listing module-name and feature-name pairs
- Startup datastore seeded from XML files at container initialization
- Operational data loaded from XML files at startup with hot-reload on file change
- A single shared credential set is used for all access; no per-user or role-based authentication is available

## Operating Modes

- Standard mode: normal NETCONF/RESTCONF service
- Debug mode: verbose logging variant for troubleshooting

## Observability

- No built-in metrics or telemetry collection
- Debug image variant emits verbose logging for inspection

## Constraints

- Exposes management interfaces only — no actual network functions are performed; no packet forwarding or routing protocol execution occurs
- Single credential set for all access; no per-user or role-based credential configuration is supported
- State is not persisted across restarts unless a volume is mounted externally
- No fault injection, chaos simulation, or failure mode capability
- No support for gNMI or gRPC-based management protocols
