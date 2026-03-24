Ella Core is a production-oriented open-source 5G core network that consolidates all standard network functions into a single binary with an embedded database and eBPF-based data plane. It is designed for private network deployments in factories, warehouses, stadiums, ships, and remote sites, and exposes a REST API and web UI for full lifecycle management.

## Core Network Functions

- AMF handles UE registration, mobility, and NGAP signaling with the radio access network
- SMF manages PDU session establishment and lifecycle via PFCP toward the UPF
- UPF processes user-plane traffic using an eBPF/XDP data plane capable of 10+ Gbps throughput and sub-millisecond latency
- UDM/UDR stores subscriber profiles and credentials in an embedded SQLite database
- AUSF performs 5G authentication (5G-AKA and EAP-AKA')
- NRF provides internal network function registration and discovery over the Service-Based Interface

## Protocol Support

- NAS over N1 for UE registration, authentication, and session management signaling
- NGAP over N2 (SCTP) for gNB control-plane communication with the AMF
- PFCP over N4 for SMF-to-UPF session control
- GTP-U over N3 for user-plane encapsulation between the gNB and UPF
- SBI (HTTP/2) for internal communication between network functions
- 5G RedCap for reduced-capability IoT device support

## Configuration and Modes

- Configured via a single YAML file; log level (debug/info/warn/error) and output destination are independently settable for system and audit logs
- XDP attachment mode is selectable: generic (all NICs including virtual), native (requires driver support), or offload (NIC hardware)
- Telemetry export to any OTLP-compatible collector is toggled and endpoint-configured in the same file

## Observability

- Prometheus-compatible metrics endpoint for scraping by any metrics collector
- OpenTelemetry traces, metrics, logs, and profiles exportable via OTLP
- Structured audit log written to stdout or a file
- Real-time flow monitoring and usage reports available through the web UI

## Constraints

- Requires a Linux host with eBPF/XDP kernel support; non-Linux environments are not supported
- The container must run in privileged mode to access eBPF and network namespaces
- The N6 (external data network) interface must be reachable outside the container network; UE packets are silently dropped on isolated internal networks
- Minimum resource footprint is 1 CPU core, 1 GB RAM, and 10 GB disk
- Single-process architecture with no documented horizontal scaling or high-availability mode
- No built-in fault injection or chaos engineering capability
