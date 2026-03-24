Toxiproxy is a TCP proxy framework that intercepts application connections and simulates adverse network conditions through programmable fault injection. Applications route traffic through it while a separate HTTP management API controls which faults are active at any given moment. It is designed for use in development and CI/CD environments where controlled network failure scenarios are needed to test application resiliency.

## Fault Injection

- Add latency with configurable jitter to upstream or downstream traffic
- Cap bandwidth to a specified throughput rate
- Delay TCP socket closure to simulate slow connection teardown
- Drop all data and close the connection after a timeout, or hold it open indefinitely
- Send a TCP reset after an optional delay to simulate abrupt disconnection
- Fragment packets into smaller chunks with inter-chunk delays
- Close the connection once a cumulative byte threshold is exceeded
- Disable a proxy entirely to simulate total service unavailability

## Configuration

- Each proxy is defined by a name, listen address, upstream address, and enabled state
- Each toxic is defined by type, stream direction, a toxicity probability, and type-specific attributes
- Multiple proxies can be created in a single bulk operation via the HTTP API
- Configuration can be applied from a JSON file or updated live through the HTTP API
- Ephemeral listen ports are supported for dynamic test environments

## Observability

- Baseline proxy overhead is under 100 microseconds without any toxics active
- Throughput capacity reaches approximately 1000 MB/s on typical developer hardware
- Prometheus-format metrics are exposed via an HTTP endpoint for monitoring integration

## Client Support

- Official client libraries are available for Ruby, Go, Python, .NET, PHP, Node.js, Java, Haskell, Rust, and Elixir

## Constraints

- Not intended for production traffic — designed exclusively for test and CI environments
- The HTTP management API has no built-in authentication; network-level access control must be applied externally
- Client libraries for server v2.x are incompatible with server v1.x due to a breaking API change
- MySQL defaults to Unix socket connections, which bypass the TCP proxy; the socket must be explicitly disabled in the MySQL configuration to route traffic through Toxiproxy
- Listen ports in the Linux ephemeral range (32768–61000) should be avoided to prevent conflicts with the OS port allocator
- UDP is not supported; the proxy operates on TCP only
- TLS termination and inspection are not supported; the proxy operates below the TLS layer
