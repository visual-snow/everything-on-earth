Fortio is Istio's open-source load testing tool that runs HTTP, gRPC, TCP, and UDP traffic at a target query rate, records latency histograms, and reports percentile breakdowns. It combines a load generator, echo server, web UI, and REST API in a single binary. Results are saved as JSON and can be visualized as comparative multi-run graphs.

## Load Generation
- Sends HTTP/1.0, HTTP/1.1, HTTP/2, gRPC, TCP, and UDP traffic at a configurable target QPS (0 = maximum speed)
- Controls concurrency through a configurable number of parallel connections
- Supports fixed-duration runs, fixed request-count runs, or open-ended runs
- Accepts custom headers, POST payloads (inline, file, or random-size), and connection reuse policies
- Distributes calls uniformly or with jitter to de-synchronize parallel clients

## Measurement and Reporting
- Captures latency histograms with configurable bucket resolution (default 1 ms)
- Reports configurable percentiles (default p50, p75, p90, p99, p99.9) plus min, avg, and max
- Tracks actual QPS achieved, total request count, error counts, and per-status-code breakdowns
- Saves results as JSON files and renders comparative graphs across multiple runs
- Optionally emits access logs in JSON or InfluxDB line format
- Resolves and measures DNS lookup latency on demand

## Fault Injection
- Injects response delays with probability distributions via echo server query parameters
- Returns non-200 HTTP status codes at configurable rates to simulate error scenarios
- Varies response payload size probabilistically to stress receiver-side processing
- Closes connections after a configurable fraction of requests to test reconnect behavior
- Aborts an entire load test run when a specific status code or socket error is encountered

## Proxy and Fan-out
- Fans out a single inbound request to multiple upstream targets in parallel (scatter-gather)
- Proxies raw TCP connections to a configured backend
- Supports serial fan-out mode for ordered upstream calls

## Scripting and Automation
- Provides an embedded scripting engine for ramp-up sequences and programmatic test orchestration
- Exposes a REST API for triggering runs, polling status, stopping runs, and querying DNS
- Supports live flag reconfiguration by watching a config directory without restarting

## Constraints
- HTTP/2 support requires a non-default client flag and runs slower than the fast HTTP/1.1 client; connection reuse and keepalive options are unavailable in that mode
- No built-in distributed load generation across multiple coordinated agents; all traffic originates from a single process
- Result files are stored flat in a single directory with no built-in database, time-series backend, or Prometheus scrape endpoint
- No native SLO pass/fail thresholds or CI result diffing; threshold logic must be scripted externally
- The embedded scripting engine is a simplified subset of Go and may not support complex orchestration requirements
- Maximum echo server response payload is capped at 256 KB by default
- Mutual TLS requires a custom CA certificate; standard public CAs are only valid for outbound client connections
