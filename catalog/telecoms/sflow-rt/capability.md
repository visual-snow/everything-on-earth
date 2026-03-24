This sandbox provides a real-time network telemetry stack combining an sFlow analytics engine, a time-series metrics store, and a visualization layer. It is purpose-built for collecting and analyzing live network traffic data through sFlow sampling. The stack arrives pre-wired so that metrics flow from the collector into storage and then into dashboards without additional configuration.

## Network Telemetry Collection

- Receives sFlow datagrams from network devices and computes real-time traffic statistics
- Exports derived metrics to the time-series store at scrape intervals
- Supports custom startup properties to tune collector behavior at launch time

## Metrics Storage

- Stores time-series metrics with a configurable retention window (default 30 days)
- Retains historical traffic data for trend analysis and retrospective queries

## Visualization

- Provides a dashboard layer pre-connected to the metrics store
- Enables graphing of traffic statistics without manual data source configuration

## Runtime Configuration

- JVM heap allocation for the analytics engine is tunable to accommodate high-volume traffic
- Retention window for stored metrics is adjustable via environment variable
- Container user mapping is configurable for filesystem permission compatibility

## Constraints

- No authentication or TLS is configured by default; all interfaces are plaintext
- Only the sFlow protocol is supported; IPFIX, NetFlow, and other flow formats are not accepted
- sFlow traffic must be actively directed at the collector; passive capture from a mirrored port is not available without explicit device configuration
- Single-node deployment only; no clustering or high-availability mode is provided
- No alerting rules are shipped; threshold-based notifications require manual setup
