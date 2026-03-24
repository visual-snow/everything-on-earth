This sandbox provides a complete telemetry collection pipeline for Cisco NX-OS devices, combining a data collection agent, a time-series database, and a visualization layer with pre-built dashboards. It supports both dial-out mode, where the device initiates a gRPC stream carrying GPB-encoded data, and dial-in mode using gNMI subscriptions. The environment arrives with self-signed TLS certificates and example configurations ready for adaptation.

## Data Collection

- Collects interface counters and statistics from NX-OS devices
- Captures ARP and MAC address tables
- Gathers system capacity and utilization metrics via ICAM telemetry
- Measures fabric and endpoint metrics

## Protocols and Subscription Modes

- Dial-out: device-initiated gRPC with GPB encoding streams to the collector
- Dial-in via gNMI SAMPLE subscription mode
- Dial-in via gNMI ON_CHANGE subscription mode
- Supports both Native YANG and OpenConfig YANG models

## Configuration

- Credentials for gNMI access are supplied through environment variables; the account requires at minimum a network-operator role
- TLS for dial-out is optional and disabled by default; it can be toggled through configuration
- Certificate common name must match the value set in the collector configuration
- Separate example configuration files cover the primary collector and the gNMI plugin

## Constraints

- NX-OS versions before 10.1(1) cannot mix SAMPLE and ON_CHANGE subscriptions in a single gNMI connection; each mode requires its own collector instance
- Setup scripts rely on GNU sed and are incompatible with the BSD sed shipped by default on macOS
- Telemetry collection is limited to Cisco NX-OS devices; no multi-vendor formats are supported
- No built-in data retention or time-series cleanup policies are defined
