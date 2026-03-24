This sandbox provides a self-contained internet reliability and performance monitoring stack built around Prometheus and Grafana. It continuously probes external targets over HTTP, HTTPS, ICMP, and TCP, and runs periodic bandwidth tests to measure real-world download and upload speeds. Dashboards are auto-provisioned on startup, giving immediate visibility into connection health and host system metrics.

## Probing and Reachability

- Sends HTTP and HTTPS probes to configurable external targets, recording status codes and response latency
- Performs ICMP ping checks against named targets with routing and switch labels for structured reporting
- Supports TCP banner probing for services such as SSH, POP3S, and IRC
- Probe targets and their human-readable names are defined in a plain-text host list

## Bandwidth Measurement

- Runs Ookla-based download and upload speed tests on a configurable schedule (default every 30 minutes)
- Records latency alongside throughput so degradation events can be correlated with speed drops

## Host System Metrics

- Collects CPU, memory, disk I/O, and filesystem utilization from the host running the stack
- Metrics are scraped at the global default interval and available alongside network probe data in the same dashboards

## Dashboarding

- Grafana loads a pre-built internet monitoring dashboard without manual import steps
- Prometheus is the sole datasource and is wired up automatically at startup

## Optional Extensions

- Local network targets (routers, switches) can be enabled by uncommenting entries in the host list
- Starlink dish monitoring and smart-plug power tracking are available when a companion configuration is supplied

## Constraints

- The repository is archived; no further development occurs here — active maintenance has moved to the successor project
- Grafana and Prometheus endpoints have no authentication or TLS — the stack is intended for isolated or home networks only, not public-facing deployments
- Each bandwidth test consumes real upstream bandwidth; the default 30-minute interval may exhaust data caps on metered connections
- Prometheus is pinned to a 2021 release while Grafana tracks the latest image, creating a version-mismatch risk when upgrading
- IPv6 probing is not supported; HTTP probes are forced to IPv4
- No alerting rules are wired up out of the box despite an alert rules file being referenced in the configuration
