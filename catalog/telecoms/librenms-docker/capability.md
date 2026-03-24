# Sandbox Capabilities

The sandbox is a containerized LibreNMS deployment — an auto-discovering network monitoring system backed by a relational database, a cache layer, and an SMTP relay. It supports a broad range of network vendors and device types via SNMP and syslog. It does not include packet capture, flow-based telemetry, streaming telemetry, or an external visualization layer.

## Discovery and Topology

- Automatic device discovery using neighbor protocols (CDP, LLDP)
- Network topology mapping derived from link-layer adjacency data
- BGP and OSPF neighbor visibility via SNMP

## Measurement

- Device availability and reachability status
- Interface traffic throughput, error counts, and drop rates
- CPU and memory utilization per device
- SNMP-polled metrics across supported vendor device types
- Inbound syslog events (TCP and UDP)
- Inbound SNMP trap events

## Alerting and Notification

- Alert rules configurable against any collected metric or event
- Email notification delivery via an integrated SMTP relay

## Deployment Modes

- Standalone mode: single instance handles both the web interface and polling
- Multi-dispatcher mode: polling workers scaled horizontally, coordinated through a shared cache
- Sidecar mode: syslog collection and trap reception run as isolated workers alongside the main instance

## Constraints

- Each librenms container requires NET_ADMIN and NET_RAW Linux capabilities — the application will not function without them.
- Volume ownership must be explicitly configured (PUID/PGID) — incorrect ownership prevents the application from starting.
- Multi-dispatcher mode requires a running cache service; without it, dispatcher sidecars cannot coordinate.
- All sidecar containers (dispatcher, syslog, trap receiver) must share the same data volume as the main container.
- No NetFlow, sFlow, or IPFIX collection — flow-based traffic analysis is not available.
- No streaming telemetry support (gNMI/gRPC) — all device data relies on SNMP polling or syslog push.
- No agent-based monitoring — devices must support SNMP or syslog to be observable.
- No built-in device configuration backup facility — no TFTP or FTP server is included.
