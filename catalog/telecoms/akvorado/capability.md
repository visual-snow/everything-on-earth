# Akvorado

Akvorado is a network flow collection, enrichment, and visualization platform developed by Free, a French ISP. It ingests NetFlow, IPFIX, and sFlow traffic from network devices, enriches the records with SNMP-derived interface names and IP geolocation data, and stores them in a columnar database for interactive analysis. It does not support alerting, threshold notifications, multi-tenant access control, or streaming telemetry protocols such as gRPC or NETCONF.

## Flow Collection

- Accepts NetFlow v5/v9, IPFIX, and sFlow from external network devices over UDP
- Flow reception is UDP-only; TCP-based flow collection is not supported
- SNMP polling enriches flow records with human-readable interface names from the originating device

## Storage and Query

- Enriched flow records are persisted in a columnar database (ClickHouse) for efficient aggregation queries
- Per-flow byte and packet counters are stored alongside geolocation and interface metadata
- A message bus (Kafka in KRaft mode) decouples the flow receiver from the storage ingestion pipeline

## Visualization

- Web console provides timeseries charts of flow volumes over configurable time windows
- Sankey diagrams show traffic distribution across autonomous system, interface, and geography dimensions
- Kafka topic consumer lag is inspectable through a browser-based topic viewer

## BGP Metadata

- An outlet component connects via BGP to exchange route and metadata state with external peers
- Flow state and metadata cache can be persisted to disk across restarts

## Configuration

- Central orchestrator distributes a single YAML configuration file to all other components at runtime
- Environment variable overrides allow per-deployment customization without modifying the base config
- Console branding, database DSN, and outlet persist paths are all configurable via environment variables

## Constraints

- Geolocation enrichment requires an external IPinfo.io license or database; without it, all geo fields are absent from flow records
- No built-in fault injection, traffic replay, or pcap import — the platform cannot simulate device failures or replay historical captures
- Schema and configuration migrations between versions are not automatic; the changelog must be reviewed before every upgrade
- The fixed internal network subnet used by the Kafka service may conflict with existing host or datacenter network ranges
- All HTTP-based services are accessible only through the reverse proxy; direct host exposure is limited to the proxy's two listener ports
