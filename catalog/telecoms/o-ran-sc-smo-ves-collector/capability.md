The O-RAN SC SMO VES Collector is a Service Management and Orchestration component that receives Virtual Event Streaming events from O-RAN network elements and pipelines them through an internal message broker into a time-series database for persistence and a dashboard for visualization. It implements the ONAP VES collector interface, targeting performance measurement and event data from O-RAN compliant nodes. The stack is self-contained and bootstraps its own message bus, storage, and visualization layers automatically on startup.

## Event Ingestion

- Accepts VES events via HTTP or HTTPS depending on whether TLS certificates are provided at startup
- Supports direct VES posting to the collector endpoint as the primary ingestion path
- Bridges DMaaP message bus traffic into the internal Kafka topic via a dedicated adapter component
- Forwards all received events to a single internal Kafka topic consumed by downstream services

## Data Pipeline

- Kafka consumer reads from the event topic and writes performance measurement data to InfluxDB
- InfluxDB operates with unlimited series and tag-value cardinality, suitable for high-cardinality PM telemetry
- An initialization service configures InfluxDB databases and Grafana dashboards automatically on first run
- Kafka topic browser is included for runtime observability of message flow

## Configuration

- Collector, DMaaP adapter, and InfluxDB connector are each configured independently via environment variables
- Log verbosity is configurable per service to support fault investigation
- Assertion checks can be enabled on the collector and DMaaP adapter for testing scenarios
- Grafana is initialized with a default admin credential that can be overridden via environment variable

## Constraints

- TLS certificates must be created and placed on the host before starting the stack; the collector does not generate them automatically
- The InfluxDB hostname must be resolvable on any client machine used to access Grafana dashboards, which requires a manual hosts file entry
- Kafka is configured as a single broker with single-replica storage and is not suitable for high-availability or multi-node deployments
- External Kafka access is hardcoded to localhost, requiring reconfiguration for any non-local client
- The stack uses the the time-series database uses a legacy query API
- No data is persisted across container restarts as no persistent volumes are defined for Kafka, Grafana, or InfluxDB
