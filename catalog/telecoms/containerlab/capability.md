# Containerlab

Containerlab is a CLI tool that orchestrates container-based network labs by parsing declarative topology files and automatically wiring virtual links between nodes. It supports over 50 network operating system kinds from vendors including Nokia, Arista, Cisco, and Juniper, covering both containerized and VM-backed platforms. It does not include a built-in traffic generator, telemetry stack, or graphical interface.

## Topology Definition and Deployment

- Define multi-node topologies in YAML, specifying nodes, kinds, links, and management settings
- Deploy or destroy an entire lab with a single command
- Inject per-node startup configurations at deploy time for most supported platforms
- Snapshot running node configurations back to the filesystem
- Generate static topology diagrams from definition files without deploying

## Protocol and Management Plane Support

- Routing protocols available across supported NOS kinds: BGP, EVPN, IS-IS, OSPF, MPLS, Segment Routing
- Management access via SSH, NETCONF, RESTCONF, gNMI, gRPC, and SNMP
- Automated TLS certificate provisioning for nodes that require it

## Lab Scaling and Automation

- Built-in CLOS/fabric topology generator for scaled spine-leaf lab creation
- Non-interactive mode suitable for integration into CI/CD pipelines
- Node labels and groups allow selective operations across subsets of a topology

## Traffic and Measurement

- No native traffic generation or packet capture
- External traffic generators can be added as nodes within the topology
- Node status and management addressing are inspectable via the inspect command

## Constraints

- Requires a Linux host with Docker; does not run natively on macOS or Windows without a Linux VM
- VM-backed router images must be built separately by the user from vendor-supplied ISOs; images are not redistributed
- Containerized NOS images require vendor-specific licensing and image pull agreements
- Concurrent topologies share the host kernel network namespace; interface name collisions must be managed by the operator
- Fault injection and link impairment are not natively supported and must be applied through host-level tools outside Containerlab
