Floodlight is an open-source, Java-based OpenFlow SDN controller that manages network forwarding behavior through a modular architecture. It supports OpenFlow versions 1.0 through 1.5 and is designed to control physical and virtual switches, routers, and access points. A built-in REST API and read-only web dashboard provide programmatic and visual access to controller state.

## Network Control and Forwarding

- Reactive L2/L3 forwarding with configurable match fields (in-port, VLAN, MAC, IP, transport layer, flags)
- Shortest-path routing via topology graph computed from LLDP-based link discovery
- Proactive static flow entry management allowing pre-installed forwarding rules independent of traffic triggers
- Configurable flow idle timeouts and ARP flooding behavior

## Device and Topology Awareness

- Host and device tracking by MAC address, IP, VLAN, and switch port
- Per-link latency history maintained by the link discovery subsystem
- Network graph updated continuously as switches connect, disconnect, or change roles
- Support for up to 1.5 million paths with configurable path-computation limits

## Traffic Measurement and Statistics

- Periodic port-level statistics collection (transmit/receive bytes, packets, errors) with configurable polling interval
- Per-flow rule hit counts and byte totals available via REST queries
- Per-link latency measurements with configurable history size and update threshold
- Internal module-level event counters and packet-in processing latency instrumentation
- JVM heap usage and controller uptime exposed through REST endpoints

## Security and Access Control

- ACL-based packet filtering via the firewall module
- Virtual tenant network isolation through a virtual network filter
- Optional TLS encryption for OpenFlow control-plane connections

## High Availability and Clustering

- Active/standby controller roles switchable at runtime via REST
- Cluster state synchronization across multiple controller nodes
- Per-switch role assignment at startup to support split-brain testing scenarios

## Fault Simulation

- Controller role can be toggled between active and standby at runtime to exercise HA failover logic
- Static flow entries can be inserted or deleted via REST to simulate routing failures
- Live Python debug interface allows manual module manipulation, flow deletion, and state modification during a running session

## Constraints

- Statistics collection is disabled by default and must be explicitly enabled before any metrics are gathered
- All controller state is held in memory and lost on restart unless cluster-level persistence is separately configured; persistence is also disabled by default
- Link discovery relies on LLDP; switches that strip or block LLDP packets will not appear in the topology graph
- The upstream project has had no active commits since approximately 2020; OpenFlow 1.5 support may be incomplete for features introduced in newer switch firmware
- High-availability clustering requires external coordination and a pre-shared keystore; it is not functional out of the box
