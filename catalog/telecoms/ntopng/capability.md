ntopng is a web-based network traffic monitoring application that performs deep packet inspection using the nDPI library. It supports real-time flow analysis, alerting, and host behavioral analysis, and can ingest traffic either by capturing live packets from a network interface or by receiving flow telemetry from external probes. The system stores state and flow records in Redis and exposes its interface through a web UI backed by a Lua scripting layer.

## Packet and Flow Capture

- Captures live traffic from a network interface using libpcap or eBPF kernel-level capture
- Operates as a flow collector, receiving NetFlow v5, NetFlow v9, IPFIX, and sFlow from upstream probes
- Classifies traffic at the application layer via nDPI deep packet inspection
- Supports SNMP for device and interface discovery

## Traffic Measurement

- Records per-flow statistics: bytes, packets, and duration in real time
- Produces top-talker rankings and application-layer protocol breakdowns
- Stores historical flow data with a configurable retention window
- Generates interface-level and aggregate throughput graphs over time

## Alerting and Behavioral Analysis

- Fires alerts on threshold breaches, traffic anomalies, and security events
- Scores host reputation and tracks behavioral patterns across flows
- Alert thresholds and behavioral checks are defined in editable Lua scripts

## Configuration

- Input source (live interface or flow probe) selected at startup
- Redis connection endpoint, HTTP/HTTPS listening port, and data retention period are all configurable
- Community edition is free under GPLv3; enterprise features require a license key

## Constraints

- A running Redis instance is required; ntopng will not start without one
- Enterprise features such as extended retention and advanced analytics are unavailable in the community build
- Standard libpcap becomes a bottleneck at multi-Gbps capture rates; high-throughput environments require PF_RING or eBPF
- No built-in traffic replay or fault injection mechanism is available
