GoFlow2 is a high-performance, modular network flow collector written in Go that ingests sFlow v5, NetFlow v5/v9, and IPFIX packets from network devices. It decodes incoming flow records and serializes them to JSON, protobuf, or plain text for delivery to Kafka or file-based transports. GoFlow2 is exclusively a pipeline entry point; storage, enrichment, aggregation, and alerting are handled by external systems.

## Collection

- Receives sFlow v5, NetFlow v5, NetFlow v9, and IPFIX over UDP
- Supports multiple parallel UDP listeners per protocol via a count parameter
- Exposes an HTTP endpoint for Prometheus metrics and health checks

## Flow Fields

- Per-flow measurements: bytes, packets, sampling rate, sequence number, flow start/end timestamps
- Transport-layer fields: protocol, source and destination ports, TCP flags, ICMP type and code
- IP metadata: type of service, TTL, IPv6 flow label, fragment ID and offset, forwarding status
- BGP and routing fields: source and destination AS, AS path, BGP communities, next hop
- Layer-2 and VLAN fields: source and destination MAC, VLAN IDs, EtherType
- MPLS fields: label and TTL

## Output Modes

- Stdout JSON lines (default) for interactive inspection
- File output for log-shipping integrations
- Kafka with protobuf encoding for high-throughput pipelines
- Raw producer mode for protocol-level debugging
- Enricher pipeline mode that annotates flows with GeoIP ASN and country data

## Constraints

- NetFlow v9 and IPFIX require Option Data Sets with sampling rate templates before flows can be decoded; there is a cold-start delay of several minutes until all templates arrive
- NetFlow v1, v7, and v8 are not supported
- JSON output is suitable only for low-volume consumption; protobuf is required for high-throughput workloads
- No built-in aggregation, flow stitching, alerting, authentication, or TLS on collection endpoints
