NetXMS is an open-source, enterprise-grade network and infrastructure monitoring system that provides performance and availability monitoring with event processing, alerting, reporting, and graphing across all layers of IT infrastructure. The sandbox runs a fully operational multi-service deployment backed by PostgreSQL, exposing the management server, a local monitoring agent, and a web-based console.

## Monitoring and Measurement

- Collects network and I/O performance metrics, CPU and memory consumption, and process-level metrics
- Reads hardware sensor data and monitors network service availability
- Analyzes log file content in real time and supports application-level custom metrics
- Tracks business service availability and SLA compliance
- Gathers routing table, ARP cache, VLAN, switch forwarding database, and wireless access point data

## Protocol Support

- Communicates via SNMP v1/v2c/v3, ICMP, SSH, WMI, LLDP, CDP, STP, and RADIUS
- Receives and forwards syslog messages and SNMP traps
- Exposes a REST API over HTTP/HTTPS and supports LDAP for directory integration

## Deployment Modes

- Single-server mode with all components on one host
- Distributed zone-based mode using proxy agents per network zone, supporting overlapping subnets
- High-availability mode with multiple proxy agents per zone, automatic failover, and load balancing
- Agent inbound mode (server connects to agent) and agent outbound mode (agent connects to server, firewall-friendly)

## Scripting and Automation

- Built-in scripting language (NXSL) runs inside an isolated VM on the management server
- NxShell provides a Python/Java scripting interface for external automation
- Database management operations (integrity check, schema upgrade, lock release) are available as one-shot commands

## Constraints

- The version environment variable must be set before any service starts; containers will not launch without it
- The management agent address must point to a running agent instance for web service checks and SSH proxy queries to function
- The database service must pass a health check before the server or initialization containers are allowed to start
- Schema upgrade via the background-upgrade profile must be invoked manually and is excluded from the default startup sequence
- NXSL scripts run in isolated VMs with controlled access and cannot reach the host filesystem directly
- No built-in packet capture, NetFlow, or sFlow analysis is available in this environment
- No native Kubernetes or container orchestration monitoring is provided out of the box
