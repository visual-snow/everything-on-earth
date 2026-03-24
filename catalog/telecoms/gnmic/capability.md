# Sandbox Capabilities

gNMIc is a gNMI CLI client and telemetry collector that communicates with network devices over gRPC. It supports on-demand queries, streaming telemetry subscriptions, and configuration changes against any gNMI-capable target. It does not include a built-in dashboard, SNMP support, or NETCONF/RESTCONF interfaces.

## Telemetry Collection

- Streaming telemetry is available via Subscribe RPC, delivering continuous state updates from target devices.
- On-demand state and configuration retrieval is available via Get RPC.
- Device capability discovery is available via Capabilities RPC.
- Collected data can be exported to Prometheus, InfluxDB, NATS, or Kafka backends.

## Configuration and Targeting

- Targets are configurable via CLI flags, environment variables, or a declarative file-based configuration.
- Bulk operations against multiple targets simultaneously are supported.
- Dynamic target discovery allows the collector to adapt to changing inventory without restarts.
- Data pipeline transformations can be applied before output is written to backends.
- Transport is configurable as TLS or non-TLS gRPC.

## Operation Modes

- Operates as a standalone CLI tool for single commands or as a persistent collector.
- An interactive prompt mode provides YANG-aware autocomplete for path exploration.
- Can run as a single-instance collector or in a clustered, high-availability configuration.
- Supports a dial-out tunnel server for targets that initiate the gRPC connection.

## Constraints

- All targets must expose a reachable gRPC endpoint with gNMI support; devices lacking gNMI cannot be managed.
- The dial-out server is vendor-specific and is not universally applicable across device types.
- No built-in visualization — external tooling is required to render collected telemetry.
- No SNMP, NETCONF, or RESTCONF protocol support.
