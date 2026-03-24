# O-RAN Testbed Automation (NIST)

This environment deploys and configures a software-based 5G Open RAN research testbed following NIST TN 2311 blueprints, supporting both bare-metal and virtualized installations. It integrates a 5G core, one or two gNodeB implementations, Near-RT and Non-RT RICs, and a set of xApps into a reproducible end-to-end testbed. It does not include RF hardware or SDR integration, fault injection, or traffic impairment capabilities.

## RAN and Core Components

- Two gNodeB options: srsRAN and OpenAirInterface, selectable per scenario
- Two UE software options, compatible with the respective gNodeB selections
- Open5GS 5G core for full control and user plane processing
- FlexRIC as an alternative RIC stack when paired with the OAI gNodeB

## Intelligent RAN Control

- O-RAN SC Near-RT RIC (Kubernetes-based) supporting E2AP, E2SM-KPM, and E2SM-RC service models
- O-RAN SC Non-RT RIC available as a minimal prototype (no rApp support)
- KPM Monitor, Traffic Steering, QoE Predictor, Cell Anomaly Detection, and RIC Control xApps pre-integrated
- Hello World xApps available in Go, Python, and Rust for development reference

## Observability

- KPM metrics collected across MAC, RLC, PDCP, and GTP layers
- Metrics include PRB allocation, RSRP, UE throughput, RLC delay, and KPM indication latency
- Grafana dashboards for real-time KPM visualization
- Network flow visibility via Cilium Hubble UI
- Metric export to console, CSV, or InfluxDB

## Lifecycle Management

- Idempotent installer resumes from the point of interruption on failure
- Single-command startup, status check, and shutdown scripts
- Software versions pinned via a locked commit manifest

## Constraints

- Requires Ubuntu 20.04, 22.04, or 24.04 LTS; no other operating system is supported
- Minimum 57 GB storage, 6 GB RAM, and 2 CPU cores; 6 or more cores recommended for stable operation
- Stable internet access is required throughout installation; interruption requires a full restart
- Near-RT RIC runs in Kubernetes and may enter a crash loop if hardware resources are insufficient
- Non-RT RIC is a minimal prototype with no rApp support
- Not all component pairings are verified; only combinations documented in the official diagrams are confirmed to interoperate
