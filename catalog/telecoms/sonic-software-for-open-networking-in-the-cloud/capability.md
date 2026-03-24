SONiC (Software for Open Networking in the Cloud) is a free, open-source network operating system built on Linux that runs on vendor-agnostic switches and ASICs. It uses a modular service architecture where each network function operates as an independent unit, sharing a central Redis-based state store. The platform has been production-hardened in large cloud-provider data centers and supports both physical hardware and a virtual switch mode for development and testing.

## Routing and Protocol Support

- BGP routing with neighbor management, prefix advertisement, and ECMP path selection via an FRRouting-based routing service
- OSPF support alongside BGP for interior gateway routing
- LACP-based link aggregation and LAG management
- LLDP neighbor discovery for topology awareness
- VLAN segmentation and Layer 2 switching
- Priority Flow Control and QoS for lossless RDMA/RoCE traffic

## Observability and Measurement

- Interface counters and per-port statistics available through the CLI
- Routing table inspection and BGP neighbor/prefix status queries
- SNMP polling via a dedicated SNMP agent service
- sFlow packet sampling and export for traffic analysis
- gNMI/gRPC streaming telemetry for real-time state export
- PFC watchdog metrics for RDMA congestion detection
- System memory and process status checks

## Configuration

- JSON-based configuration loaded into the central Redis CONFIG_DB at startup
- Full CLI for runtime inspection and configuration changes
- YANG models for structured configuration validation
- Minigraph XML for datacenter-style topology provisioning

## Operating Modes

- Virtual switch mode for software-only simulation without physical ASIC hardware
- Bare-metal production deployment via ONIE-based installation
- VM/KVM mode for learning and integration testing

## Constraints

- Hardware support requires a Switch Abstraction Interface implementation from the ASIC vendor; not all switch hardware is supported
- The central Redis database service is a single coordination point that all other services depend on for shared state
- Virtual switch mode does not emulate full ASIC forwarding performance or all hardware-specific features
- Configuration changes to hardware-forwarding paths require a synchronization round-trip through the ASIC daemon, introducing latency compared to software-only stacks
- No built-in fault injection or traffic generation framework; external tools are required for load testing and chaos scenarios
