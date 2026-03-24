Polycube is an open source Linux software framework that provides fast, lightweight network functions built on eBPF and XDP kernel technologies. Network functions — called cubes — can be composed into arbitrary service chains and managed through a REST daemon or a CLI. All management operations are programmatic; there is no GUI or web dashboard.

## Layer-2 Switching
- Transparent and standard 802.1Q Layer-2 bridging with spanning-tree slow-path support
- Minimal single-bridge forwarding for low-overhead switching scenarios
- Policy-based and simple forwarding cubes for custom packet steering

## Layer-3 Routing and NAT
- IP router with longest-prefix-match forwarding
- Network Address Translation transparent cube for source and destination rewriting
- iptables-compatible packet filtering using an eBPF-based drop-in replacement

## Firewalling and DDoS Mitigation
- Stateful packet filtering transparent cube with per-connection state tracking
- DDoS traffic mitigation cube that drops attack traffic in the XDP fast path
- SYN flood detection monitor that exports TCP/IP ratios for external alerting

## Load Balancing
- Reverse-proxy load balancer that terminates and redistributes inbound connections
- Direct-server-return load balancer that bypasses the return path through the balancer

## Traffic Monitoring and Packet Capture
- Dynamic network monitor that injects arbitrary eBPF programs at runtime and exports metrics as JSON or OpenMetrics (Prometheus-compatible)
- Per-service statistics and cube state queryable at runtime through the REST API
- Packet capture transparent cube attachable to any existing port or network device

## Kubernetes Networking
- Full CNI plugin covering switching, routing, NAT, load balancing, and tunneling
- Kubernetes switching fabric and traffic dispatcher for pod-to-pod communication
- Network policy filter for enforcing Kubernetes NetworkPolicy objects

## Constraints
- Requires Linux kernel 4.15 or later; eBPF and XDP are Linux-only — macOS and Windows are not supported
- Only one daemon instance is allowed per host and the process must run as root; containers require privileged mode with host networking
- Topology persistence does not save YANG action-style rules (such as firewall or NAT rule appends), and transparent cubes attached to network devices are not restored on restart
- The dynamic monitor does not export struct or union map value types, and batch map operations are limited to hash and array map types
- No built-in fault injection, traffic generation, or distributed tracing capability is provided
