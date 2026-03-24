Nokia Service Router Linux (SR Linux) is a fully open network operating system (NOS) distributed as a free container image with no registration, licensing, or contract requirements. It is designed for learning, demonstration, testing, and CI environments, and supports a broad set of data-center routing and management protocols.

## Configuration

- NETCONF (RFC 6241) for structured configuration management
- gNMI SetRequest for programmatic, model-driven configuration
- JSON-RPC API for configuration and state queries
- CLI over SSH for interactive configuration sessions

## Routing and Control Plane

- BGP, OSPF, and IS-IS for IP routing
- EVPN and VXLAN for overlay and data-center fabric scenarios

## Telemetry and State Retrieval

- gNMI streaming telemetry for operational state and counters
- NETCONF get/get-config for point-in-time state retrieval

## Lab and Topology Integration

- Runs as a standalone containerized node for single-device testing
- Operates as a topology node in multi-node labs (e.g., via Containerlab)

## Constraints

- Not intended for production deployment; scoped to learning, demo, test, and CI environments only
- No Nokia support SLA is available through this container image distribution
- No fault injection or traffic generation tooling is bundled in this image
- Requires a Linux host with Docker and elevated network privileges due to NOS kernel requirements
