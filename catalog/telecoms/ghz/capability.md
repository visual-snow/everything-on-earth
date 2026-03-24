ghz is a command-line gRPC benchmarking and load testing tool written in Go. It sends configurable volumes of gRPC requests to a target server and reports latency distributions, error rates, and throughput metrics. The tool supports constant, step, and linear ramp load profiles as well as all four gRPC streaming modes.

## Protocols

- gRPC over HTTP/2 (the only supported transport)
- gRPC with mutual TLS authentication
- gRPC server reflection for automatic service discovery without a proto file
- Unary, client-streaming, server-streaming, and bidirectional streaming

## Load Profiles

- Constant load: fixed RPS or concurrency for a set request count or wall-clock duration
- Step load: RPS or concurrency increases or decreases by a fixed amount on a repeating interval
- Linear ramp load: RPS or concurrency changes linearly from a start value to an end value over a total duration
- Async mode: requests are dispatched without waiting for prior responses, maximising in-flight count

## Measurement

- Total request count, wall-clock duration, and requests per second
- Latency average, fastest, slowest, and percentile distribution (p10 through p99)
- Latency histogram bucket counts
- Error distribution keyed by error message string
- gRPC status code distribution
- Per-request detail records (timestamp, latency, status) available in JSON and CSV output formats
- InfluxDB line-protocol output for time-series ingestion

## Configuration

- Service definition supplied via a proto source file or a binary protoset
- Request payload accepted as inline JSON or from a file; pre-serialised binary protobuf payloads also supported
- gRPC metadata supplied as inline JSON or from a file
- Per-request timeout and dial timeout independently configurable
- First N requests can be excluded from statistics to skip warm-up
- Output format selectable: summary, CSV, JSON, pretty, HTML, or InfluxDB variants
- All settings can be stored in a JSON or TOML configuration file

## Output and Reporting

- Human-readable summary printed to stdout by default
- HTML report for sharing results without additional tooling
- Web UI sub-application stores historical runs in a database and serves a browsable report dashboard

## Constraints

- Only gRPC over HTTP/2 is supported; HTTP/1.1, REST, and other protocols are not available
- The number of connections cannot exceed the concurrency level; violating this is a fatal configuration error
- Binary payload mode and dynamic streaming messages are mutually exclusive
- When a time-boxed duration is set, the total request count parameter is ignored
- Step and linear ramp schedules require start value, end value, and step size or step duration to all be specified
- No built-in varied or randomised payload generation beyond Go template functions in the JSON data field
- ghz is a client-side tool only; the target gRPC server must be provided and managed separately
- All load originates from a single process; distributed multi-node load generation is not supported
