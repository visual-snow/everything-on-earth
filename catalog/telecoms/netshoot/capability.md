# Sandbox Capabilities

Netshoot is a network diagnostics container that bundles over 30 CLI and TUI tools for inspecting, measuring, and tracing network behavior across Docker and Kubernetes environments. It operates inside a target container's or host's network namespace, enabling deep observation without modifying the production environment. It does not include any fault injection, automated remediation, or persistent metric storage.

## Reachability and Path Tracing

- ICMP reachability testing between any two network endpoints
- Traceroute-style path discovery with per-hop latency tracking
- Animated and continuous traceroute visualization for monitoring route stability
- TCP-level path tracing to distinguish network and transport layer reachability

## Traffic Capture and Inspection

- Full packet capture on any visible interface
- Protocol-aware packet inspection with terminal-based UI
- Pattern-matched traffic filtering across live network streams
- Packet crafting for custom protocol testing and edge-case simulation

## Throughput and Latency Measurement

- Bandwidth and throughput measurement between two endpoints
- Latency and jitter tracking with continuous sampling
- Packet loss rate observation
- HTTP and gRPC load testing with percentile latency reporting
- Per-flow bandwidth utilization monitoring in real time

## Protocol Testing

- DNS resolution queries and timing across resolver configurations
- HTTP and HTTPS request and response inspection
- gRPC service endpoint verification
- WebSocket connection testing
- SMTP transaction testing
- BGP routing daemon observation and interaction

## Connection and Routing State

- Active connection enumeration and socket state inspection
- Firewall rule and connection tracking table visibility
- IP routing table and interface configuration inspection
- IPVS load-balancing and IP set inspection
- Container resource metrics alongside network state

## Deployment Modes

- Interactive shell with access to all bundled tools
- Single-command execution for scripted diagnostics
- Sidecar mode sharing a pod's network namespace continuously
- Ephemeral debug container attached to a running Kubernetes pod
- Background batch capture writing to file

## Constraints

- Packet capture and network namespace manipulation require elevated privileges — basic diagnostics are available unprivileged, but capture and namespace switching are not.
- The tool is read-only: it cannot modify application configuration, network rules, or remediate any observed issue.
- All captured data and metrics are ephemeral — there is no persistent storage, log aggregation, or time-series retention across sessions.
- Container resource monitoring requires access to the Docker socket, which may not be available in all deployment environments.
