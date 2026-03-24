KNE is a containerized network emulation framework built on Kubernetes that enables testing of network control planes using vendor-supplied device images without physical hardware. It exposes a standard gRPC interface for topology management and supports multi-vendor device emulation across a Kubernetes cluster. Topologies are defined declaratively using custom resource definitions and managed through a CLI tool or programmatically via the topology manager API.

## Routing Protocols

- BGP, IS-IS, and OSPF are supported for control plane testing across emulated devices
- OpenConfig, gNMI, and gRPC interfaces are available for device configuration and telemetry

## Link and Port Features

- LACP-based port aggregation is supported for multi-link emulation
- Automatic Protection Switching is available for resilience scenario testing
- Data plane connectivity between pods is handled by a per-host topology agent

## Measurement and Observability

- Transceiver state emulation is available on emulated devices
- Optical characteristics can be emulated on data plane wires
- Usage metrics reporting is supported but disabled by default

## Configuration

- Pod boot initial configuration can be applied at topology creation time
- Each pod can be exposed as an in-cluster or external service
- Topology creation and teardown are managed via CLI or gRPC API

## Constraints

- No native fault injection or traffic impairment primitives are built into the framework
- No built-in traffic generation capability; external tools are required for traffic workloads
- No packet capture or flow measurement is included; observability depends on vendor container capabilities
- Network devices must be provided as vendor-supplied container images; no built-in software router is available
- A running Kubernetes cluster is a prerequisite; there is no alternative deployment path
