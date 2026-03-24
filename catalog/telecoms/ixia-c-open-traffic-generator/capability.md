# Ixia-c (Open Traffic Generator)

Ixia-c is an API-driven, multi-component traffic generator that implements the Open Traffic Generator (OTG) standard for programmatic generation and measurement of L2–L7 network traffic. It is used to test network devices by sending configurable traffic flows and collecting per-port and per-flow statistics. It does not include protocol state-machine emulation (such as BGP, OSPF, or IS-IS), built-in fault injection, or a graphical interface.

## Traffic Generation

- Continuous and burst transmission modes
- Rate specified as packets-per-second or as a percentage of line rate
- Supports point-to-point (two-arm), one-arm, and three-arm mesh topologies
- Up to 256 flows per port in the community edition

## Supported Protocols

- Layer 2: Ethernet, VLAN
- Layer 3: IPv4, IPv6, GRE, ICMP, ICMPv6
- Layer 4: TCP, UDP
- Tunneling: VXLAN, GTPv1, GTPv2

## Measurement and Observability

- Per-port statistics: transmitted and received frame counts, byte counts, and rates
- Per-flow statistics: transmitted and received frame counts, byte counts, and rates
- One-way latency per flow: minimum, maximum, and average
- Packet capture with filtering, exportable as a standard capture file

## Control Interface

- REST API over HTTPS accepting OTG JSON payloads
- Python SDK (snappi) and Go SDK (gosnappi) for programmatic control
- All interaction is API-only; no GUI is provided

## Constraints

- Community edition is limited to 256 flows per port; higher flow counts require the commercial variant
- Throughput is bounded in the community edition; Tbps-scale testing requires the commercial Keysight KENG variant
- Requires a minimum of 2 x86_64 CPU cores and 7 GB RAM per deployment
- Traffic engine processes must run with elevated privileges to access the network interface at the packet level
- Protocol headers beyond the 12 built-in types are not natively supported; custom frame construction requires external tooling
- No fault injection, packet delay, or packet loss emulation is available in the provided environment
