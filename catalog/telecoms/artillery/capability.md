Artillery is a cloud-native, open-source load and performance testing platform installed via npm. It supports HTTP, HTTPS, WebSocket, Socket.io, gRPC, GraphQL, and AWS Kinesis, enabling load tests against a broad range of service types. Tests run locally by default and can scale out to AWS Lambda, AWS Fargate, or Azure ACI without custom DevOps infrastructure.

## Load Generation

- Define virtual user scenarios in YAML, specifying phases (ramp-up, sustained load, spike) and per-request flows
- Override the target URL, select named environments, or inject variables at runtime without modifying test scripts
- Use CSV payload files to drive data-varied requests across virtual users
- Run a single virtual user in solo mode for smoke testing and debugging before scaling up

## Measurement and Observability

- Capture response latency percentiles (p50, p95, p99, p999), request rate, and virtual user lifecycle counts
- Record HTTP status code distributions and per-endpoint metric breakdowns
- Publish metrics to Datadog, New Relic, CloudWatch, Prometheus, Honeycomb, Dynatrace, Splunk, or any OpenTelemetry-compatible backend
- Compute Apdex scores to express user satisfaction thresholds as a single numeric value

## Assertions and SLO Enforcement

- Add HTTP response assertions (status codes, body content, headers) via the expect plugin
- Define SLO thresholds with the ensure plugin; the test process exits non-zero when thresholds are breached, integrating cleanly with CI/CD pipelines

## Test Composition

- Compose reusable test definitions from multiple input scripts merged at runtime
- Generate synthetic payload data for virtual users without maintaining external fixture files

## Constraints

- Distributed cloud runs require valid AWS or Azure credentials in the execution environment; no credential injection is provided by the sandbox.
- The gRPC and Kinesis engines are not bundled with the core package and must be installed separately before use.
- Cloud platform execution (AWS Lambda, Fargate, Azure ACI) uses multiply mode, which replicates the full scenario load per worker rather than dividing it, so total load scales multiplicatively with worker count.
- There is no built-in fault or chaos injection; latency simulation, forced error rates, and network partition testing require external tooling.
- No built-in dashboard UI is included; metrics visualization depends on external systems such as Grafana or a connected observability backend.
