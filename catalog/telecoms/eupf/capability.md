eUPF is an open-source 5G User Plane Function that uses eBPF XDP hooks for high-performance packet forwarding between the 5G core and external data networks. It separates into a userspace control plane handling PFCP session management and an in-kernel forwarding plane processing packet detection, forwarding action, and QoS enforcement rules. It has been validated alongside Free5GC, Open5GS, and OpenAirInterface 5G core deployments.

## Control Plane

- Manages PFCP sessions over the N4 interface, receiving rules from a Session Management Function
- Exposes a REST API for inspecting active sessions, rules, and associations
- Exposes a Prometheus metrics endpoint reporting PFCP counters, latency histograms, and active session gauges
- Supports UE IP address allocation and F-TEID allocation when the corresponding features are enabled
- Accepts configuration via YAML file, environment variables, or CLI flags with explicit precedence ordering

## Data Plane

- Attaches XDP programs to configured network interfaces for in-kernel packet processing
- Forwards GTP-U encapsulated traffic on the N3 interface between the gNB and the UPF
- Supports N9 interface for uplink classifier and anchor UPF chaining in multi-UPF deployments
- Performs kernel FIB lookup for routing decisions; unresolvable routes fall back to the kernel networking stack
- Reports per-protocol receive counters (ARP, ICMP, IPv4, IPv6, TCP, UDP) and per-XDP-action counters

## Observability

- PFCP receive and transmit counters, per-message error counters with cause codes, and processing latency histograms
- XDP action counters covering aborted, dropped, passed, transmitted, and redirected packets
- GTP receive counters distinguishing echo, PDU, other, and error message types
- Active PFCP session and association gauges available for scraping at any time

## Operational Modes

- Generic XDP mode attaches at the kernel level and works with any NIC; validated for evaluation and testing
- Native XDP mode attaches at the driver level for higher throughput; requires driver support
- Offload XDP mode executes on the NIC itself; requires NIC hardware support
- Can replace the UPF component in an existing Open5GS, Free5GC, or OpenAirInterface deployment

## Constraints

- Requires Linux kernel 5.15.0-25-generic or later; earlier kernels are not supported
- Requires elevated Linux capabilities (NET_ADMIN and SYS_ADMIN) to load eBPF objects and configure memory limits
- Only IPv4 is supported for PFCP NodeID; IPv6 node addressing is not implemented
- Only one FAR rule, one QER rule, and one SDF filter per PDR are supported; multi-rule PDRs are not handled
- IPv6 data-plane forwarding is not implemented; IPv6 packets are counted but not routed
- No built-in packet capture or CLI debugging tooling; tcpdump integration is listed as a future roadmap item
