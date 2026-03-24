# Sandbox Capabilities

FRRouting (FRR) is a free, open-source routing protocol suite for Linux and BSD that implements a broad set of IGP and EGP protocols through individual per-protocol daemons coordinated by a central routing engine. It exposes a unified CLI, a RESTCONF API, and a YANG northbound interface for configuration and operational state queries. It does not include a data-plane forwarder, traffic generator, or graphical interface.

## Routing Protocols

- BGP (IPv4 and IPv6) with neighbor management and prefix policy
- OSPFv2 and OSPFv3 for intra-domain link-state routing
- IS-IS for link-state routing in carrier and data-center topologies
- RIPv1, RIPv2, and RIPng for distance-vector routing
- PIM-SM and MSDP for IPv4/IPv6 multicast routing
- LDP for MPLS label distribution
- BFD for sub-second failure detection across sessions
- VRRP for first-hop redundancy
- Policy-Based Routing and SR-TE path steering
- Babel and OpenFabric (additional IGP options)

## Configuration

- Per-protocol configuration via individual daemon config files
- Unified CLI shell spanning all active daemons
- RESTCONF API for programmatic configuration mutation
- NETCONF interface available when an external NETCONF server is integrated
- Route maps and prefix lists for routing policy
- VRF instances for traffic isolation
- BFD session parameters including timers and detection multipliers

## Observability

- BGP neighbor state and advertised/received prefix counts
- OSPF and IS-IS adjacency state and link-state database contents
- BFD session state and packet-level counters
- PIM neighbor table and multicast routing entries
- Per-VRF routing table inspection
- Interface-level statistics via the core routing engine
- YANG-modeled operational state queryable via RESTCONF or NETCONF

## Constraints

- Does not implement a data-plane forwarder — packet forwarding relies on the Linux kernel or an external data plane; software forwarding only, no hardware offload
- NETCONF and YANG northbound require external sysrepo and netopeer2 services that are not bundled with FRR
- EIGRP and NHRP implementations are alpha-quality and not suitable for production or reliable test scenarios
- No built-in traffic generation, packet injection, or fault injection capability
- Multi-node topology orchestration requires an external tool; FRR alone cannot define or manage lab topologies
