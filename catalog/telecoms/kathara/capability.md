# Kathara

Kathara is a lightweight network emulation system that models full network topologies by running each virtual device as an isolated container interconnected through virtual Layer 2 segments. It is the successor to Netkit and supports both local single-host deployments and distributed Kubernetes-based scenarios. It does not include built-in traffic generation, packet capture, or a graphical topology editor.

## Routing and Protocol Support

- Emulates BGP, OSPF, RIP, and IS-IS routing protocols via pre-built router images
- Supports DNS configuration and resolution across emulated networks
- Enables software-defined networking scenarios using OpenFlow and P4

## Topology and Configuration

- Network topology defined declaratively through a single topology file per scenario
- Per-device startup scripts apply interface configuration and daemon setup at boot
- Python API available for programmatic scenario construction and automation
- Custom device images can be assigned per node within a scenario

## Operational Modes

- Local mode runs scenarios entirely on a single host using the local container engine
- Kubernetes mode (Megalos) distributes devices across a cluster for larger-scale emulation
- CLI commands manage full scenario lifecycle: start, stop, inspect, and clean
- Python library provides the same lifecycle control programmatically

## Constraints

- No native packet capture or traffic measurement tooling; any monitoring depends on tools pre-installed in device images
- No built-in fault injection primitives; link failures require manual interface removal or container termination
- Kubernetes mode requires a pre-configured cluster and is not suitable for offline single-host use without a container engine
- No REST API, web dashboard, or native controls for packet loss, latency, or jitter injection
