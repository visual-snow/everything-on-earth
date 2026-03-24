Locust is an open-source load and performance testing tool where test scenarios are written as plain Python classes. Each simulated user runs inside a lightweight gevent coroutine, allowing hundreds of thousands of concurrent users from a single process or a distributed cluster. Tests can be driven interactively through a browser-based dashboard or run headlessly in CI/CD pipelines.

## Protocols

- HTTP and HTTPS via a built-in requests-based client
- WebSocket and SocketIO via community-maintained clients
- Any custom protocol implementable through a Python client

## Load Configuration

- Total user count and spawn rate (users added per second) are independently configurable
- Run duration can be bounded by a time limit or left open-ended
- Wait time between tasks supports constant, random-range, constant-throughput, and constant-pacing strategies
- Custom configuration files allow repeatable test profiles

## Execution Modes

- Interactive web UI mode for live start/stop/adjust control and real-time metrics
- Headless CLI mode for fully scriptable, pipeline-friendly execution
- Distributed mode with one master coordinating multiple worker processes
- Single-process mode that combines master and worker roles for lightweight runs

## Measurement

- Requests per second (throughput)
- Response time percentiles: median, 95th, 99th, and maximum
- Failure count and failure rate
- Active user count and worker status in distributed runs
- Stats exportable to CSV for offline analysis

## Task Composition

- User behavior is defined in Python classes with weighted tasks and optional task groupings
- Tasks can be nested and composed to model realistic user journeys

## Constraints

- No built-in fault injection or chaos engineering primitives; failure scenarios must be hand-coded in task logic
- Non-HTTP protocols require a custom Python client written and wired in manually
- Distributed mode requires stable network connectivity between the master and all workers
- Worker processes must each be able to import the locustfile; shared in-memory state across workers is not automatic
- No built-in support for replaying recorded sessions or HAR files; all scenarios must be authored in Python
- No native SLA assertion framework; pass/fail thresholds must be enforced through external scripting
