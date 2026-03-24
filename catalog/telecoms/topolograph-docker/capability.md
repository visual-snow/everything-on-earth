Topolograph is a network topology visualization and what-if analysis platform that collects Link State Database (LSDB) information from routers running OSPF or IS-IS and renders an interactive graph. It exposes a REST API and an MCP server so agents can query topology, calculate paths, and monitor routing events programmatically.

## Topology Collection
- Collects LSDB data from routers via OSPF (OSPFv2, OSPFv3) and IS-IS using NAPALM device login
- Persists topology snapshots to a MongoDB store for historical comparison and repeated queries
- Resolves OSPF Router IDs to human-readable hostnames via a configurable DNS server

## Path Analysis
- Calculates shortest paths between any two nodes in the stored topology graph
- Computes backup paths including loop-free alternates and failover routes
- Supports what-if analysis to evaluate topology behavior under simulated link or node failures

## Event Monitoring
- Detects and records OSPF and IS-IS link-state change events
- Queries current node and edge connectivity status across the graph

## Agent Integration (MCP)
- Exposes an MCP server endpoint that LLM agents connect to for structured network queries
- Supports topology queries, path calculations, and event lookups via the Model Context Protocol
- API access is authenticated by token; source IP whitelisting must be configured before requests succeed

## Web Interface
- Provides a browser-based interactive graph for manual topology exploration and what-if scenarios
- Swagger UI available for REST API discovery and manual testing

## Constraints
- NAPALM-based collection requires active SSH or API access to each monitored router with valid credentials; no passive or SNMP-only collection path is available
- API source IP whitelisting must be explicitly configured; misconfiguration silently blocks all API access
- MCP server token provisioning is manual and not automated in the default setup
- BGP-LS is listed as a supported protocol in project documentation but has no collector or configuration present in the environment
- NetBox integration for hostname enrichment is deprecated; hostname resolution depends solely on DNS
- No TLS configuration is provided for the web UI or MCP endpoint in the default setup
