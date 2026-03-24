k6 is a modern open-source load testing tool built by Grafana Labs that uses a JavaScript/ES6 scripting engine backed by a Go runtime. It is designed for developer-centric performance testing in DevOps workflows, supporting local CLI execution, CI pipeline integration, and distributed runs via Kubernetes or Grafana Cloud.

## Protocols

- HTTP/1.1 and HTTP/2
- WebSocket
- gRPC
- Browser automation via a Chromium-based browser module

## Execution Modes

- Local single-machine runs with pass/fail exit codes for CI integration
- Distributed cloud execution via Grafana Cloud k6
- Kubernetes operator-based distributed runs
- Browser performance testing mode

## Scenario Scheduling

- Open model, closed model, constant arrival rate, and fixed iteration executors
- Ramping stages to model traffic spikes, ramp-ups, and ramp-downs
- Per-scenario configuration allowing mixed workload shapes in a single test

## Metrics and Measurement

- Built-in HTTP metrics: response time (with p50/p90/p95/p99 percentiles), error rate, request throughput, bandwidth
- Virtual user concurrency tracking
- Custom metric types: Counter, Gauge, Rate, and Trend
- Threshold engine for declarative pass/fail assertions on any metric
- Output connectors for InfluxDB, Prometheus, Grafana Cloud, CSV, JSON, and StatsD

## Configuration

- Test options defined in the script itself and overridable via CLI flags
- Environment variable injection at runtime
- TLS settings including certificate configuration and verification control
- Reusable option sets via a config file

## Fault Simulation

- Think time and pacing via sleep calls in scripts
- Custom error rate simulation through deliberate bad requests and check assertions
- Traffic spike and drop modeling via ramping stages

## Constraints

- No built-in chaos or fault injection primitives; all fault simulation must be coded manually in JavaScript
- No native support for database protocols such as SQL, MongoDB, or Redis in core; requires community extensions
- JavaScript execution is single-threaded per virtual user, which limits achievable concurrency on a single machine for CPU-bound logic
- The browser module requires Chromium and consumes significantly more resources than protocol-level tests
- Distributed runs beyond a single machine require Grafana Cloud k6 or a self-managed Kubernetes operator; no built-in peer-to-peer coordination is available
