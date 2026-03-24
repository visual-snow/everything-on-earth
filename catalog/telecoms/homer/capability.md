# Sandbox Capabilities

HOMER is a carrier-grade packet and event observability framework for VoIP and real-time communications monitoring. It captures and correlates SIP, RTP, and RTCP traffic using the HEP/EEP encapsulation protocol, and surfaces call flow analysis, QoS metrics, and search through a web dashboard. It does not include a built-in storage engine or a native visualization layer.

## Traffic Capture and Correlation

- Passive capture of SIP signaling, RTP media streams, and RTCP control traffic
- HEP/EEP encapsulation enables capture agents to forward traffic to a central ingest server
- Correlation of signaling and media events into unified call flows
- Capture can be deployed as a standalone agent against a remote ingest server or co-located in an all-in-one setup

## Measurement and Observability

- QoS metrics derived from RTP and RTCP XR streams
- RTP statistics including packet loss, jitter, and delay indicators
- Call Detail Records (CDRs) for session-level accounting
- Syslog ingestion alongside VoIP-specific telemetry
- PCAP export for individual calls or sessions
- Unified collection of logs, metrics, and traces via the HEP pipeline

## Storage and Visualization Integration

- Storage backend is configurable — supported targets include PostgreSQL, Loki, Elasticsearch, and qryn
- API-only headless mode available when a separate visualization layer manages storage queries
- Grafana integration supported for dashboard rendering

## Constraints

- No built-in storage engine — an external database must be provisioned and connected before data can be persisted or queried
- Passive packet capture requires a separately deployed capture agent; the ingest server does not capture traffic on its own
- No native visualization engine — dashboards depend on Grafana or a compatible external tool
- Designed for Linux hosts only; no Windows-native deployment path is supported
