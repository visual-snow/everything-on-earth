oha is a Rust-based HTTP load generator that sends configurable bursts of requests to a target URL. It provides a real-time terminal dashboard with live latency histograms and status code tracking, and an async engine with keep-alive connection pooling. Results can be emitted as text, JSON, or CSV, and optionally persisted to a an embedded database for post-run analysis.

## Protocols

- HTTP/0.9, HTTP/1.0, HTTP/1.1, and HTTP/2
- HTTP/3 (experimental, requires a pure-Rust TLS backend)
- HTTPS via rustls (default) or native-tls
- Unix domain sockets (non-HTTPS only)
- HTTP/HTTPS through a proxy (HTTP/1.1 and HTTP/2 to proxy)

## Load Modes

- Fixed-count mode: run until N total requests complete
- Duration mode: run for a fixed wall-clock period
- Rate-limited mode: cap throughput at a global queries-per-second ceiling
- Burst mode: send N requests every D seconds on a repeating schedule
- Coordinated-omission-corrected mode: adjusted latency accounting when rate limiting is active
- Debug mode: single request with full request and response dump

## Request Configuration

- Total request count or duration as the termination condition
- Concurrent connection count and parallel streams per HTTP/2 connection
- Per-request timeout and TCP connect timeout
- Custom HTTP method, headers, and request body (string, file, or multipart form)
- Random URL generation per request using regex syntax, or URLs read from a file
- Basic auth and AWS SigV4 request signing
- TLS certificate overrides and insecure mode
- DNS resolution restricted to IPv4 or IPv6, and per-host DNS/port overrides
- Proxy host, headers, and protocol version

## Measurements

- Total duration and aggregate requests per second with full percentile distribution (p10–p99.99)
- Response time and first-byte time histograms with percentile breakdowns
- DNS dialup and DNS lookup times (average, fastest, slowest)
- Status code distribution and error distribution
- Total body data transferred, size per request, and throughput in bytes per second
- Optional success/failure breakdown histograms

## Output

- Real-time TUI dashboard (can be disabled for headless or higher-throughput runs)
- Text, JSON, CSV, or quiet output formats
- Per-request results optionally persisted to a an embedded database

## Constraints

- HTTP/3 is experimental and only functions with the a pure-Rust TLS backend
- Redirect following is not supported for HTTP/2
- Keep-alive cannot be disabled for HTTP/2 connections
- Burst-delay and burst-rate settings are ignored when a global QPS rate limit is active
- Coordinated-omission correction is silently ignored when no rate limit is set
- Unix socket connections only work with non-HTTPS target URLs
- Total concurrency with HTTP/2 equals connections multiplied by parallel streams, which can be unexpectedly high
- Large connection counts may require raising the OS open-file limit
- No built-in server or external target is provided; oha requires an independently running HTTP service to test against
- No scripting, scenario DSL, or persistent configuration file is supported
