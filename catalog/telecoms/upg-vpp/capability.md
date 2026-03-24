UPG-VPP is an out-of-tree user-plane plugin that implements a GTP-U user plane per 3GPP TS 23.214 and TS 29.244 Release 15, deployable as a 5G UPF, PGW-U, or TDF-U. It pairs a high-performance vector packet processor data plane with a PFCP session-control server and an application detection framework for L7 traffic classification. The project is used in production by telecom operators and includes a Go-based end-to-end test framework that drives PFCP signalling and live traffic within isolated network namespaces.

## Operating Modes
- PGW mode: GTP-U encapsulation and decapsulation between access and SGi interfaces, IPv4 and IPv6
- TDF mode: transparent traffic detection without GTP-U tunnelling, IPv4 and IPv6
- GTP Proxy mode: relay GTP-U between access and core network interfaces, IPv4 and IPv6
- Single-core and multicore scheduling, selectable at startup
- Debug and release build variants

## Supported Protocols
- GTP-U (3GPP TS 29.281) for user-plane encapsulation and decapsulation
- PFCP (3GPP TS 29.244) for session establishment, modification, deletion, and reporting
- IPv4 and IPv6 for both inner UE addressing and outer transport addressing
- HTTP L7 detection via regex-based TCP proxy
- IPFIX for flow telemetry export
- ICMP and ICMPv6, UDP

## Traffic Measurement and Reporting
- Volume-based and duration-based Usage Reporting Rules per PFCP session
- Volume quota enforcement with threshold-triggered session reports
- Periodic reporting via measurement period intervals
- Start-event triggered reporting
- IPFIX flow records exported to a configurable collector
- Live flow state inspection via the VPP CLI

## Application Detection
- L7 regex matching and IP filter rules for classifying application traffic
- TCP proxy with configurable MSS for URL-based detection
- Per-application rule sets managed through VPP CLI commands

## Session and Routing Control
- PFCP session establishment, modification, and deletion per 3GPP TS 29.244
- Packet Detection Rules, Forwarding Action Rules, and URR hot-swap mid-session
- Named VRF-backed network interface contexts for access, core, and SGi segments
- TDF uplink table for subscriber routing in transparent detection mode

## Fault Injection and Testing
- GTP-U extension header and corrupt datagram injection at configurable frequency
- Connection flood stress tests for PFCP and data-plane load
- PDR replacement mid-session to validate rule hot-swap
- MTU edge-case and fragmentation boundary tests
- NAT pool exhaustion tests (TDF mode, IPv4 only)
- Routing policy change tests mid-session
- Process pause and debugger attachment options for failure inspection

## Constraints
- Buffer Action Rules are not implemented
- QoS Enforcement Rules are not implemented
- Lawful Intercept FAR action destination is not implemented
- Ethernet bearer support is not implemented
- PFCP error handling is incomplete; errors in session procedures may not propagate correctly
- The data-plane heap cannot grow beyond its initial allocation; large deployments must pre-configure a larger heap at startup
- IP fragments larger than approximately 2 KiB cannot be produced unless buffer size is increased at startup
- IP reassembly is limited to 8 fragments; large PFCP datagrams may exceed this limit
- UDP datagrams over 1500 bytes are split by default rather than IP-fragmented; a startup configuration workaround is required
- Zero UDP checksum bug affects PFCP Session Modification Responses for IPv6 PFCP endpoints; the workaround is to use an IPv4 PFCP endpoint
- Built and tested on Linux only; no Windows support
