TRex is a DPDK-based open-source traffic generator capable of producing L2–L7 traffic at up to 200 Gbps line rate. It supports stateless, stateful, and advanced stateful modes, making it suitable for benchmarking routing and switching hardware, testing firewalls and NAT devices, and emulating realistic application workloads. Control is available through an interactive console, a Python scripting API, or a desktop GUI.

## Traffic Generation Modes

- Stateless (STL): packet-based L2–L4 generation for routing and switching benchmarks, up to 10–30 Mpps per core
- Stateful (STF): connection-aware traffic with L7 application profiles for firewall, IPS, and NAT testing
- Advanced Stateful (ASTF): full TCP/UDP emulation with L7 application layer for realistic per-flow behavior
- EMU mode: client-side L3 protocol simulation including ARP, DHCP, neighbor discovery, IGMP, and BGP via BIRD

## Protocol Support

- L3/L4: IPv4, IPv6, TCP, UDP, ICMP, ICMPv6, MPLS, GRE, VXLAN, NSH
- Routing: BGP (eBGP/iBGP), OSPF v2/v3, RIP v1/v2/RIPng, RPKI
- Application: HTTP/HTTPS, DNS, DHCP v4/v6, IGMP v1/v2/v3, MLD/MLDv2, IPv6 Neighbor Discovery

## Traffic Configuration

- Field engine for dynamic per-packet field modification (source IP ranges, port ranges, etc.)
- Packet sizes from 64 bytes to 9 KB (jumbo frames)
- Rate specified as Mpps, L1 bandwidth, L2 bandwidth, or link percentage
- Traffic modes: continuous, burst, and multi-burst with inter-stream triggering
- Up to 10,000 parallel streams in stateless mode; millions of concurrent flows in stateful modes
- PCAP file import for traffic replay, including files up to 1 TB for deep packet inspection testing
- Multiple simultaneous L7 application profiles (HTTP, Citrix, and others)

## Measurement and Observability

- Per-stream and per-interface throughput statistics (hardware and software counters)
- Latency and jitter measurement per stream
- Packet loss detection and flow ordering validation
- BPF filter-based live traffic capture with Wireshark/PCAP export
- NAT/PAT dynamic translation learning and validation

## Fault Injection

- Arbitrary and malformed packet construction via Scapy field engine
- TCP SYN sequence randomization for connection tracking stress testing
- NAT/PAT translation table exhaustion simulation

## Constraints

- Requires a DPDK-compatible NIC; the kernel driver is bypassed and the interface is bound exclusively to DPDK
- Supported NIC vendors are limited to Intel, Mellanox, Broadcom, Cisco VIC, Napatech, and Amazon ENA — not all NICs are supported
- Runs on x86 or ARM server platforms only; concurrent flow capacity is memory-limited, not CPU-limited
- ASTF TCP implementation is a pragmatic approximation, not a full kernel-grade TCP stack
- Cross-flow L7 protocol fault injection is partial, covering only specific protocols such as RTSP and SIP
- No native HTTP/2 or gRPC protocol stacks; no built-in horizontal scaling across multiple generator nodes
