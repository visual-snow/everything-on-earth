Telegraf is a plugin-driven server agent for collecting, processing, aggregating, and writing metrics, logs, and traces. It ships as a standalone static binary with no external runtime dependencies and supports over 300 plugins across inputs, outputs, processors, and aggregators.

## Input Collection

- Collects system metrics including CPU, memory, disk, and network statistics
- Supports network telemetry protocols: SNMP, SNMPv3, gNMI, OpenConfig, NetFlow v5/v9, IPFIX, sFlow, and Cisco TelemetryMDT
- Reads from messaging systems: MQTT, Kafka, AMQP, and HTTP endpoints
- Accepts Prometheus scrape targets and OpenTelemetry ingestion
- Supports industrial protocols: Modbus and OPC-UA
- Executes arbitrary commands or tails log files as input sources

## Output Forwarding

- Writes to InfluxDB, Kafka, MQTT, HTTP endpoints, Prometheus remote write, and OpenTelemetry collectors
- Supports many additional output destinations via the plugin ecosystem

## In-Flight Processing

- Processor plugins transform, filter, and enrich metrics before they reach outputs
- Aggregator plugins compute statistical summaries (min, max, mean, percentiles, histograms) over configurable time windows

## Measurement and Timing

- Collection and flush intervals are independently configurable (default 10 seconds each)
- Each measurement carries key-value tags for metadata and typed fields for values
- Supports metrics, logs, and traces within the same agent

## Operating Modes

- Daemon mode runs continuously at configured intervals
- Test mode collects one cycle and prints to standard output without writing to any output
- Once mode collects and flushes exactly one cycle then exits
- Config validation mode checks configuration syntax without running the agent

## Configuration

- Configured in TOML format with separate sections for inputs, outputs, processors, and aggregators
- Supports per-plugin filtering on tag names, measurement names, and field names
- Environment variable substitution is supported in configuration files
- Configuration can be split across multiple files in a directory

## Constraints

- Windows-specific plugins (Event Log, WMI, Performance Counters) are unavailable on Linux and macOS
- The metric buffer is bounded; metrics are silently dropped when the buffer fills before a flush completes
- Configuration format is TOML only; YAML and JSON are not supported natively
- Not all plugins support all field and tag filtering options — behavior varies by plugin
- There is no built-in UI, dashboard, or alerting; visualization and alerting must be handled by downstream tools
