Predator is an open-source platform for managing the full lifecycle of API load testing, from authoring and scheduling tests through distributed execution and real-time reporting. It is built on Artillery as its load-test engine and can be deployed on Kubernetes, DC/OS, or Docker. The platform exposes a REST API and a web UI, making it suitable for both manual and CI/CD-driven workflows.

## Load Testing

- Generates load over HTTP and HTTPS
- Distributes load generation across unlimited runner instances
- Supports stress and performance testing modes
- Schedules recurring test runs using cron expressions

## Functional Testing

- Runs functional tests with assertions against HTTP endpoints
- Executes the same test definitions used for load runs

## Metrics and Reporting

- Measures latency at min, max, median, p95, and p99 percentiles
- Tracks requests per second and HTTP status code distribution
- Aggregates results across concurrent runner instances in real time
- Exports metrics to Prometheus and InfluxDB
- Sends notifications via Slack, Microsoft Teams, Discord, and generic JSON webhooks

## Fault Injection

- Integrates with Kubernetes Chaos Mesh to inject faults into the target environment during active load tests (available from v1.7.0 onward)

## Constraints

- Runner version must match the manager's major.minor version exactly; mismatches cause test failures
- Only tagged releases are supported; the latest tag is explicitly unsupported
- Cassandra is not a supported database backend (dropped in v1.5.0); supported engines are PostgreSQL, MySQL, MSSQL, and SQLite
- Chaos Mesh fault injection requires a Kubernetes deployment and is not available on plain Docker or DC/OS
- No support for gRPC, WebSockets, or non-HTTP protocols
