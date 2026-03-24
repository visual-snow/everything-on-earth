hey is a lightweight CLI HTTP load generator designed as a modern replacement for ApacheBench. It sends a configurable number of concurrent requests to a target URL and reports latency and throughput statistics. Written in Go, it ships as a single self-contained binary with no runtime dependencies.

## Load Generation Modes

- Fixed-count mode runs exactly N requests, defaulting to 200 total
- Duration mode runs for a specified wall-clock time window, overriding the request count
- Rate-limited mode caps requests per second per worker to control throughput precisely
- CSV reporting mode emits one row per request for offline analysis

## Protocol Support

- HTTP/1.1 and HTTPS with TLS out of the box
- HTTP/2 available as an opt-in flag
- HTTP proxy forwarding supported via a host and port argument

## Request Configuration

- Concurrency level (number of parallel workers) is independently configurable from total request count
- HTTP method, headers, body string or body file, and Content-Type are all settable per run
- Basic authentication credentials can be supplied as a single argument
- Host header override is supported for virtual hosting scenarios
- Keep-alive, compression negotiation, and redirect following can each be disabled independently
- Number of CPU cores used by the process is configurable

## Measurement and Output

- Reports total requests, success count, and failure count
- Calculates requests per second and response latency distribution including mean, min, max, and percentiles
- Breaks down response status codes across the run
- Provides per-phase timing: DNS lookup, TCP connection establishment, and time to first byte

## Constraints

- The concurrency level must not exceed the total request count; the tool exits with an error if it does
- hey is a pure HTTP client and cannot load-test non-HTTP protocols such as gRPC, WebSocket, or raw TCP
- All load originates from a single process on one machine; there is no distributed or multi-node mode
- Output goes to standard out only; there is no built-in persistence, dashboard, or real-time progress display
- There is no warm-up phase, ramp-up concurrency control, think time between requests, or request sequencing
