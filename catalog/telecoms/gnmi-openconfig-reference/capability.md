This environment provides a reference repository for OpenConfig-based network management, containing protobuf specifications, YANG data model definitions, and supporting tooling for gNMI. It is a specification and documentation resource rather than a runnable simulation, intended for tasks that involve reading, analyzing, or working with OpenConfig standards and gNMI RPC definitions.

## Protocols and Interfaces

- gNMI (gRPC Network Management Interface) — the primary protocol defined in this repository
- gRPC — the underlying transport protocol for gNMI operations
- YANG — the data modeling language used to define configuration and state schemas
- OpenConfig path conventions — standardized path addressing for network element attributes

## Telemetry and Measurement

- gNMI Subscribe RPC specification for streaming telemetry from network devices
- gNMI Get RPC specification for retrieving configuration and state data

## Configuration

- gNMI Set RPC specification for pushing configuration changes to devices
- OpenConfig YANG model paths for targeting specific configuration nodes

## Tooling

- Python scripts for OpenConfig-related processing and validation tasks
- Shell scripts for supporting utility operations
- RPC definitions and protobuf specifications organized under a dedicated directory
- IETF content and OpenConfig-to-IETF mappings

## Constraints

- No runnable network simulation or emulated devices are included; this is a specification repository and cannot be used to simulate live device behavior
- Requires an external gNMI-capable target — either a real network device or a separate emulator — to actually exercise the RPC definitions
- No versioned releases or packages are published; any dependent tooling must pin to a specific commit
- No gNMI server implementation is present; only client-side specifications and tooling are included
