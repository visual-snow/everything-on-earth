Stratum is an open-source, silicon-independent switch operating system built for software-defined networks. It exposes next-generation SDN interfaces that enable programmable, hardware-agnostic control of network forwarding pipelines. Stratum supports physical ASICs from multiple vendors as well as software-based switch backends, making it usable without dedicated hardware.

## Forwarding Pipeline Control

- Programs the data-plane forwarding pipeline using P4Runtime over gRPC
- Allows arbitrary pipeline definitions to be pushed, activated, and updated at runtime
- Supports both fixed-pipeline Broadcom switches and fully programmable Tofino-based ASICs

## Device and Interface Management

- Configures network devices and interfaces via gNMI
- Uses OpenConfig YANG models for structured, vendor-neutral configuration
- Manages chassis-level configuration through a protobuf-based abstraction layer

## Telemetry and Observability

- Streams operational state via gNMI subscribe, covering counters and interface state
- Tracks configuration state through a dedicated monitoring service
- Exposes documented gNMI paths for observable metrics and operational data

## CLI and Operational Tools

- Provides command-line interfaces for gNMI interaction, hardware abstraction layer inspection, and platform monitoring
- Offers a software switch backend for development and integration testing without physical hardware
- Includes a stub backend for unit testing and CI environments

## Constraints

- Tofino hardware mode requires the Barefoot SDE, which is not freely distributable and requires a vendor agreement
- Broadcom SDK6 requires a direct Broadcom relationship or vendor SLA to obtain
- Hardware support is limited to explicitly listed platforms; unsupported ASICs require porting effort
- No support for sFlow, NetFlow, IPFIX, or any packet-sampling telemetry protocol
- No in-band network telemetry support
- Routing protocols such as BGP and OSPF are out of scope; control plane logic must be delegated to an external SDN controller
