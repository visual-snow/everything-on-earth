VyOS is an open-source network operating system that combines a Linux kernel, FRR (Free Range Routing), and Netfilter into a unified, configurable router and firewall platform. It uses a hierarchical CLI modeled after Junos-style set/commit/rollback workflows, making it suitable for tasks that require realistic enterprise-grade routing and security policy configuration.

## Routing Protocols
- BGP, OSPF, IS-IS, and RIP via FRR
- Static routing and policy-based routing supported alongside dynamic protocols

## VPN and Tunneling
- IPsec via StrongSwan/libreswan
- OpenVPN for SSL-based remote access and site-to-site tunnels
- WireGuard for lightweight, modern VPN connectivity

## Firewall and NAT
- Stateful packet filtering via Netfilter
- Source and destination NAT, including masquerade rules
- Zone-based and interface-based firewall policies

## High Availability
- VRRP (keepalived) for gateway redundancy across multiple routers

## Observability
- Interface statistics available via CLI show commands
- Syslog output for event and error logging
- No native metrics exporter (e.g., Prometheus) is available

## Configuration Management
- Hierarchical CLI with set/delete/commit/rollback operations
- Configuration persisted in a structured text file, loadable at boot

## Constraints
- No fault injection or traffic simulation tooling is available; network failure scenarios must be constructed manually via configuration changes
- No GUI management interface; all interaction is CLI-only
- No native metrics or telemetry export; external monitoring requires additional tooling or log scraping
