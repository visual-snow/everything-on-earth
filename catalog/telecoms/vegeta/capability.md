Vegeta is a constant-rate HTTP load testing tool that issues requests at a user-specified rate per second while explicitly avoiding coordinated omission. It produces a binary result stream that can be piped into its own sub-commands for reporting, encoding, and visualization. It is also available as a Go library for programmatic orchestration.

## Attack

- Sends HTTP requests at a fixed rate or at maximum speed and writes results to a binary stream
- Supports constant-rate mode (exact N requests per second) and infinite-rate mode (as fast as possible with a worker cap)
- Runs for a finite wall-clock duration or indefinitely until the process is stopped
- Reads targets from stdin or a file in plain HTTP or JSON format; lazy streaming supports unlimited or dynamically generated target lists

## Protocols

- HTTP/1.1 and HTTP/2 (negotiated via ALPN by default)
- HTTP/2 cleartext over unencrypted connections
- HTTPS with mutual TLS using client certificate and key
- Unix domain sockets as an alternative transport

## Measurement and Reporting

- Latency percentiles: min, mean, 50th, 90th, 95th, 99th, and max
- Total request count, sustained rate, and throughput for successful requests only
- Bytes transferred in and out, both total and mean per request
- Success ratio, status code histogram, and unique error strings
- User-defined histogram buckets and HDR histogram output
- Report formats: text summary, JSON metrics, histogram, and interactive HTML latency chart
- Optional a metrics scraping system scrape endpoint exposing bytes, latency, and failure count during an active attack

## Configuration

- Rate, duration, worker counts, connection limits, and per-request timeout are independently tunable
- Custom request headers and a default body file can be applied to all targets
- TLS validation can be skipped; trusted CA certificates, session resumption, and mutual TLS are supported
- Custom DNS resolvers, static host overrides, and local bind address are configurable
- Result stream encoding can be converted between binary, JSON, and CSV after the fact

## Distributed and Library Use

- Distributed runs are supported by splitting the target rate across multiple independent instances and aggregating result files offline
- The Go library exposes attacker, metrics, and targeter types for embedding in custom Go programs

## Constraints

- File descriptor and process limits must be raised manually before high-rate attacks; exceeding available resources can crash the process
- The a metrics scraping system scrape endpoint is only live during an active attack and closes immediately on completion, making tail-end scrapes unreliable; remote-write is not supported
- Custom DNS resolvers are non-functional on Windows
- There is no built-in assertion or threshold enforcement; pass/fail logic must be implemented externally by parsing the JSON report
- No support for gRPC, WebSocket, cookie jars, session management, or built-in scenario scripting
