Netdata is an open-source, real-time infrastructure monitoring platform that collects per-second metrics from systems, containers, applications, and hardware with minimal configuration. It runs an edge-based observability pipeline that includes ML-powered anomaly detection, tiered time-series storage, alerting, and a built-in web dashboard. Netdata operates as a passive observer and does not modify or interact with monitored systems.

## Metric Collection

- Collects host kernel and network stack metrics via the proc filesystem
- Tracks per-process and per-user resource usage through a dedicated process plugin
- Monitors cgroup-based containers including Docker and Kubernetes workloads
- Covers 800+ application integrations including databases, web servers, and message queues
- Ingests custom application metrics via the StatsD protocol
- Scrapes and exposes metrics in the OpenMetrics/Prometheus exposition format
- Maps live network sockets per process via the network viewer plugin

## Storage and Resolution

- Stores metrics at one-second resolution at the primary tier
- Automatically downsamples to per-minute resolution at the second tier and per-hour at the third
- Achieves roughly 0.5 bytes per sample using ZSTD compression
- Supports memory-only storage mode with no disk writes

## Anomaly Detection and Alerting

- Trains unsupervised per-metric ML models at the edge without sending data to external services
- Assigns an anomaly rate score to each metric, surfaced in the dashboard
- Correlates patterns across metrics using a scoring engine
- Supports customizable alert rules; notifications are pushed directly to integrations such as Slack, PagerDuty, and email

## Log Analysis

- Provides systemd journal log viewing and analysis through a dedicated plugin

## Deployment Modes

- Standalone: single agent with local dashboard and storage
- Parent mode: centralized agent receiving streamed metrics from child agents over TCP
- Child mode: agent streaming all metrics to a parent with optional local retention
- Cloud-connected: agent registered to Netdata Cloud for remote access and multi-node views
- Kubernetes: deployed via Helm chart with a per-node DaemonSet and a parent Deployment

## Constraints

- Requires host PID namespace and host network mode for full monitoring; omitting these disables container network interface mapping and host networking metrics
- Requires elevated Linux capabilities and an unconfined security profile; without them, local listener discovery and cgroup container name resolution are unavailable
- Must mount several host filesystems and sockets for complete visibility; partial mounts yield incomplete metrics
- Does not support running as a non-root user from startup; some features may break in that configuration
- Has no built-in fault injection or synthetic load generation; it is a passive observer only
- Has no native OpenTelemetry ingestion support at this time
