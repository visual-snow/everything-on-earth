This sandbox provides a Telegraf, InfluxDB, and Grafana (TIG) observability stack for collecting and visualizing Cisco Model Driven Telemetry (MDT) from Catalyst and Meraki network devices. Metrics are streamed over gRPC using YANG Push subscriptions with KVGPB encoding, then stored in a time-series database and rendered in pre-built dashboards. Configuration is generated from a single YAML file using Jinja2 templates, which produces all required Telegraf, InfluxDB, and Grafana config files automatically.

## Telemetry Collection

- Receives periodic and on-change YANG Push subscription streams from Cisco devices
- Supports KVGPB (Key-Value Google Protocol Buffers) encoding over gRPC
- Collects PoE power consumption per switch port (Wh)
- Collects wireless client upload and download traffic (Kbytes)
- Collects wireless client connection counts and per-radio limits
- Collects switch port operational status
- Collects interface bytes transmitted and received

## Device and API Integration

- Targets Cisco Catalyst switches and Meraki wireless infrastructure
- Integrates with Meraki REST API for device management queries
- YANG subscription paths and update policies are configurable per device

## Configuration and Templating

- Single config file drives the entire stack: device identities, API keys, and storage credentials
- Jinja2 templates auto-generate all service configuration files from that single source
- Supports both periodic and on-change subscription modes per device

## Visualization

- Grafana provides pre-built dashboards for wireless and switching metrics
- InfluxDB stores all time-series data with configurable organization and bucket settings

## Constraints

- A manually populated configuration file must exist before the stack can start; there is no wizard or auto-discovery
- The Catalyst 9300 Sustainability dashboard is a non-functional placeholder; that metric set is not yet implemented
- Telemetry transport has no built-in encryption; an external gateway is recommended for any remote-access scenario
- No scalability guidance or multi-device performance limits are documented
