This sandbox provides a containerised instance of iperf3, a standard network bandwidth measurement tool. It operates in a client/server model where one container acts as the listener and another initiates test traffic. It is suited for tasks involving throughput benchmarking, latency measurement, and protocol-level performance analysis between networked endpoints.

## Bandwidth and Throughput Measurement
- Measures end-to-end throughput between a client and server in bits per second
- Supports both TCP and UDP protocols
- Allows parallel streams to simulate concurrent connections
- Configurable test duration to capture sustained performance

## Latency and Loss Measurement
- Reports round-trip time between client and server
- In UDP mode, captures jitter and packet loss percentage
- In TCP mode, reports retransmit counts as an indicator of congestion

## Test Configuration
- Supports reverse mode to measure server-to-client direction
- Allows target bitrate specification for UDP load testing
- Produces machine-readable JSON output for programmatic result parsing
- Port and stream count are configurable at runtime

## Constraints
- No built-in orchestration — the caller must establish network connectivity between client and server containers independently
- Single iperf3 process per container with no multi-session management layer
- No web interface, REST API, persistent storage, authentication, or native fault-injection capability
