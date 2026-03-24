ktranslate is a Kentik open-source network telemetry agent that collects SNMP metrics, flow records (NetFlow, IPFIX, sFlow), syslog messages, and streaming telemetry, then translates and forwards them to configurable observability sinks. It supports enrichment via GeoIP and DNS resolution, rollup aggregations, filtering, and sampling before export. Configuration is driven entirely by a YAML file and CLI flags with no web interface.

## SNMP Polling

- Polls network devices for interface counters and device metrics using SNMP v1, v2c, or v3
- Device inventory supplied via an external YAML file; discovery mode can auto-detect devices on a subnet
- Single-poll and walk modes allow targeted, one-shot queries against individual devices for testing or validation

## Flow Collection

- Receives NetFlow v5/v9, IPFIX, and sFlow records on a configurable UDP listener
- Captured fields include timing, bytes, packets, source and destination addresses and ports, protocol, interface indexes, VLAN tags, TCP flags, and autonomous system numbers
- Sampling rates are preserved and exported with each flow record

## Syslog Ingestion

- Accepts syslog messages over TCP, UDP, and Unix sockets
- Supports RFC3164, RFC5424, and RFC6587 framing variants

## Data Enrichment

- Resolves IP addresses to hostnames via a built-in DNS resolver
- Applies MaxMind GeoLite2 geographic data when a valid license key is available
- Supports custom tag maps and external enrichment webhooks for additional field decoration

## Output and Export

- Routes processed data to one or more sinks: Kafka, Prometheus, HTTP, file, S3, cloud storage, New Relic, or stdout
- Output serialization formats include JSON, flat JSON, Avro, Prometheus exposition, InfluxDB line protocol, Elasticsearch, and NetFlow
- Rollup aggregations (sum, topK) can be computed over configurable dimensions before forwarding
- Compression options include gzip, snappy, and deflate

## Operational Modes

- Flow-only mode disables SNMP polling for isolated flow pipeline testing
- AWS Lambda and VPC Flow log modes enable cloud-native ingestion
- A dry-run estimation flag records payload sizes for New Relic without transmitting data

## Constraints

- GeoIP enrichment requires a MaxMind license key provided at build time; without it geographic fields are unavailable
- No built-in fault injection, flow replay, pcap ingestion, or threshold-based alerting capabilities
- Rollup output and raw alpha flows cannot be routed to separate sinks independently without an explicit flag
- No native TLS termination for flow input; TLS applies only to HTTP serving endpoints
- SNMP device inventory must be maintained manually in an external file unless discovery mode is enabled
