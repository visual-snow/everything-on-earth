FD.io VPP (Vector Packet Processing) is Cisco's open-source, production-grade packet-processing stack that runs on commodity CPUs using a vector-based processing model. It delivers switch and router functionality through a plugin-based, extensible dataplane with broad protocol support across L2 through L7.

## Protocols

- IPv4, IPv6, MPLS, GRE, VXLAN, VXLAN-GPE
- IPsec (AH + ESP per RFC 4301/4302/4303), IKEv2, WireGuard
- Segment Routing for IPv4, IPv6, and MPLS; SRv6 Network Programming
- GTPu, L2TP, LISP, LISP-GPE
- QUIC, HTTP/1, HTTP/2
- BFD, LACP, LLDP, VRRP, ARP, ND, ICMP, ICMPv6
- DNS, DHCP, IGMP, IPFIX

## Measurement and Observability

- Shared-memory statistics segment (statseg) with per-node counters and interface statistics
- Prometheus exporter via the prom plugin (experimental)
- IPFIX flow records exported via the flowprobe plugin
- Per-thread CPU performance counters via the perfmon plugin (PMU-based)
- Buffer utilisation monitoring via the bufmon plugin
- sFlow sampling exporter via the sflow plugin
- Binary API call tracing with configurable circular buffer

## Configuration

- Primary configuration via a startup configuration file covering CPU pinning, buffer sizing, plugin selection, memory, logging, and API socket settings
- CLI accessible over a UNIX socket or interactive terminal
- Binary API socket used by VPP agents and the VAT test tool
- Plugins individually enabled or disabled via the plugins stanza
- CPU pinning supports main-core, worker corelist, and scheduler policy (fifo, rr, other)
- Hugepage and memory layout configurable per NUMA node

## Fault Injection

- nsim plugin introduces per-interface configurable delay and packet loss fraction
- Packet generator (pg) injects high-speed traffic into arbitrary graph nodes and supports pcap replay

## Constraints

- DPDK dataplane operation requires privileged access and hugepages; falls back to a reduced buffer count when running unprivileged
- Worker threads each require dedicated shared-memory space; test workloads empirically need at least 2048 MB for 16 cores
- DPDK UIO drivers must be loaded before VPP starts and are not loaded automatically
- The Prometheus exporter is marked experimental and does not provide stable scrape guarantees
- nsim delay and drop-fraction settings apply per interface and must be explicitly enabled per interface via CLI
