# FAUCET

FAUCET is an OpenFlow 1.3 SDN controller built on the Ryu framework that programs multi-table L2/L3 pipelines on both hardware and software switches. It manages VLANs, ACLs, and IPv4/IPv6 routing through a single declarative configuration file and exposes operational metrics through a bundled Prometheus and Grafana stack. The environment does not include a software dataplane (such as Open vSwitch or Mininet), a BGP daemon, or a packet-capture facility.

## Network Control

- Programs OpenFlow datapaths with multi-table pipelines covering L2 switching, VLAN segmentation, and ACL enforcement
- Routes IPv4 and IPv6 traffic statically or via BGP-learned routes (requires external ExaBGP process)
- Supports link aggregation (LACP) and neighbor discovery and loop detection (LLDP)
- Manages stacked/distributed topologies with automated failover across multiple datapaths
- Handles port authentication (802.1x) and DHCP relay signalling, delegating the actual service to external processes

## Observability

- Exports per-port byte, packet, and error counters via Prometheus
- Collects per-flow match and action statistics through the companion gauge controller
- Exposes controller health and event-loop latency as Prometheus metrics
- Streams structured JSON events over an event socket for external consumers
- Ships preconfigured Grafana dashboards for switch, port, and flow-level views

## Configuration and Reload

- All datapaths, VLANs, ACLs, routers, and interfaces are declared in a single YAML file
- Monitoring polling intervals and storage backends are configured in a separate gauge YAML file
- Supports hot-reload: faucet detects config file changes and reloads policy without restarting the controller process

## Constraints

- Requires OpenFlow 1.3 with multi-table pipeline support; switches limited to OpenFlow 1.0 are not compatible
- Hardware switches must implement all pipeline matches defined in faucet's spec and pass integration tests — not all vendor ASICs qualify
- BGP routing requires ExaBGP deployed as a separate process; faucet does not embed a BGP daemon
- 802.1x and DHCP functions require external processes (hostapd, dhcpd); faucet only handles the OpenFlow signalling side
- The gauge monitoring controller and the main controller must share a consistent topology configuration; mismatched configurations cause silent monitoring gaps
- No native fault-injection API; fault scenarios require external tooling such as Mininet or manual switch commands
