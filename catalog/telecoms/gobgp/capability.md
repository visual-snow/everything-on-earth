GoBGP is an open-source BGP daemon written in Go, designed for modern environments with a rich policy engine based on the IETF vendor-neutral model. It exposes a gRPC API for programmatic management and supports a wide range of BGP address families and extensions. The daemon and CLI client together provide a full BGP control plane without requiring traditional vendor tooling.

## Supported Protocols
- eBGP, iBGP, BGP-4
- BGP-LS (Link-State)
- BMP (BGP Monitoring Protocol)
- EVPN / L2VPN-VPLS
- FlowSpec (IPv4 and IPv6)
- MRT dump and injection
- RPKI (Route Origin Validation)
- SR-Policy (Segment Routing Policy)
- L3VPN (IPv4/IPv6 unicast), MUP (Mobile User Plane)
- Graceful Restart and Long-Lived Graceful Restart
- Add-Paths, BGP Confederation, TTL Security, Unnumbered BGP, RT Constraint

## Operating Modes
- Standard eBGP/iBGP router
- Route Server (per-neighbor route-server-client)
- Route Reflector (per-neighbor route-reflector-client)
- Embedded Go library (no daemon required)
- gRPC-only management (config file optional)

## Configuration
- Config formats: TOML (default), YAML, JSON, HCL
- Supports peer-groups and dynamic neighbors (accept peers from a prefix range)
- Per-neighbor and global import/export policy with defined prefix, community, AS-path, and ext-community sets
- VRF support with RD and RT import/export for L3VPN
- RPKI server integration for Route Origin Validation
- BMP server forwarding with pre-policy or post-policy route monitoring
- MRT dump on a configurable interval; config reload via SIGHUP or auto-reload flag
- Zebra/FRR FIB integration via UNIX socket

## Observability
- Prometheus metrics endpoint (disabled by default, enabled via CLI flag)
- Per-peer FSM state, route counts (received/accepted/advertised), message counters, flap count, queue depth, and uptime
- Grafana dashboard available externally (dashboard ID 22061)

## Constraints
- TTL Security and eBGP Multihop are mutually exclusive on the same neighbor
- Zebra integration version must match the Quagga/FRR version installed on the system
- No native NETCONF/YANG, RESTCONF, or web UI — programmatic access is gRPC only
- No IS-IS, OSPF, or other IGP support; BGP-only daemon
- Prometheus metrics endpoint is disabled by default and must be explicitly enabled
