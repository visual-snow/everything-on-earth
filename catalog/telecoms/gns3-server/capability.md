# Sandbox Capabilities

GNS3 Server is a network emulation backend that orchestrates multiple underlying emulators — including Dynamips, Qemu/KVM, VirtualBox, Docker, and VPCS — to create multi-node virtual network topologies. It exposes a REST API used by external GUI clients to build, configure, and run emulated networks. It does not emulate protocols directly, does not include a graphical interface, and does not bundle any router images or appliance firmware.

## Topology Management
- Create, connect, and tear down virtual network nodes across heterogeneous emulator backends
- Add and remove links between nodes to mutate topology at runtime
- Support for lightweight virtual PCs alongside full router and appliance nodes

## Protocol Support
- Emulated devices can run routing protocols including BGP, OSPF, EIGRP, IS-IS, RIP, and MPLS
- Layer-2 features including VLANs and STP are available through emulated switches
- DHCP, DNS, and SNMP are reachable within emulated topologies via device configuration

## Fault Injection
- Stop or remove individual emulated nodes to simulate device failure
- Reconfigure device settings via API without restarting the topology
- Inject link changes to simulate network partitions or path failures

## Deployment Modes
- Runs as a foreground process for development or interactive use
- Supports daemon mode for persistent background operation
- Can be managed as a system service or run in a container

## Constraints
- No router or appliance images are included — disk images must be sourced and supplied separately
- External emulator binaries (Dynamips, Qemu, VirtualBox) are required but not bundled
- Docker-based nodes and IOU nodes are supported on Linux only; these features are unavailable on other platforms
- No native packet capture interface — traffic inspection requires an external tool
- No metrics or observability endpoint exposed by the server itself
