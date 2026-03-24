Anteon (formerly Ddosify) is an eBPF-based Kubernetes monitoring and load-testing platform. It auto-generates service maps of Kubernetes clusters without code instrumentation and runs scenario-based performance tests through a no-code scenario builder. The platform combines a CLI load engine with a self-hosted web UI backed by time-series metrics storage and async task workers.

## Load Testing

- Sends HTTP, HTTPS, and HTTP/2 requests against one or more target endpoints
- Supports linear, incremental, and waved load profiles to simulate constant, ramping, or oscillating traffic
- Runs multi-step scenario flows with correlation between steps, CSV test data injection, cookie handling, and assertions
- Parameterizes URLs, headers, bodies, and auth fields with dynamic random variables
- Debug mode executes a single iteration with verbose curl-like output for request inspection

## Measurement and Observability

- Reports total iteration count, pass/fail rate, average request duration, and per-step response times and status codes
- Captures real-time Kubernetes cluster CPU, memory, disk, and network usage
- Maps service-to-service latency via eBPF instrumentation without modifying application code
- Detects slow SQL queries from observed cluster traffic
- Exposes Prometheus metrics scraped from all backend services with a 10-day time-series retention window

## Configuration

- CLI accepts flags for target URL, iteration count, duration, HTTP method, request body, headers, auth, timeout, proxy, output format, and load type
- Accepts a JSON scenario config file for multi-step flows, enabling reuse and version control of test definitions
- Environment shared across all backend services via a single env file

## Constraints

- Protocol support is limited to HTTP, HTTPS, and HTTP/2; gRPC and WebSocket are not supported
- eBPF-based service mapping requires a Linux kernel with eBPF support and is unavailable on Windows or macOS nodes
- Kubernetes monitoring requires the Alaz eBPF agent to be deployed separately into the target cluster
- CLI output is limited to standard text and JSON formats; no native HTML or PDF reporting is available
- No built-in distributed tracing integration (OpenTelemetry, Jaeger, or Zipkin)
- No authentication or access controls are documented for the self-hosted web interface
