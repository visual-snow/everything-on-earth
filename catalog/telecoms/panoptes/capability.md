Yahoo Panoptes is a Python-based network telemetry ecosystem designed for discovery, enrichment, and polling of network devices at global scale. It uses a plugin-driven, horizontally scalable architecture to collect SNMP metrics, transform them, and forward results to a time-series database for storage and visualization.

## Discovery

- Enumerates network resources through scheduled discovery plugins running as distributed workers
- Supports a static resource file listing devices when no external configuration management database is available
- Organizes resources into named sites representing physical or logical datacenter groupings

## Enrichment

- Collects and caches device metadata through enrichment plugins backed by a distributed in-memory store
- Enrichment dimension values are string-typed tags attached to metrics for filtering and grouping
- Cached enrichment data is shared across polling workers to avoid redundant device queries

## Polling

- Collects metrics via SNMP, supporting community-string-authenticated queries including bulk retrieval
- Measures interface throughput (bits and packets in both directions), CPU utilization, system uptime, and memory totals
- Converts raw 64-bit counters to rates before publishing, producing gauge-type metrics
- Attaches millisecond-resolution Unix epoch timestamps to every metric
- Publishes metrics onto a distributed message bus; a consumer writes them to a time-series database

## Coordination and Scheduling

- Each plugin type (discovery, enrichment, polling) runs as independent scheduler and worker pairs
- Distributed locking prevents duplicate execution of the same plugin against the same resource
- Per-plugin execution frequency configuration enforces a minimum interval between runs

## Resource Filtering

- Plugin configurations declare which resources they act on using a SQL-subset filter DSL
- Supported operators: equality, inequality, pattern matching, boolean logic, and set membership
- Nested parenthetical grouping is not supported in filter expressions

## Constraints

- Parenthetical grouping in resource filter expressions is unsupported; complex boolean logic must be restructured to avoid it
- Enrichment dimension values must be strings; non-string types are not accepted
- Plugin code runs with the full OS permissions of the service user — no process-level sandboxing is applied
- The all-in-one single-node deployment mode is not suitable for production use
- There is no REST API for querying resources or metrics; data access requires direct interaction with the underlying stores
- Output is limited to InfluxDB-compatible format; Prometheus and OpenMetrics output formats are not available
- Device metric collection is strictly pull-based; no push or streaming ingestion from devices is supported
- Grafana dashboard customizations do not persist when the single-node environment is restarted
