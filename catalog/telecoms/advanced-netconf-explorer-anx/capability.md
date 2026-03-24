Advanced NETCONF Explorer (ANX) is a graphical web application and Java client library for interacting with NETCONF/YANG device models and gNMI/gRPC telemetry streams. It connects to network devices or orchestrators, retrieves all supported YANG models, and presents them in an interactive tree browser with search and live data viewing.

## YANG Model Discovery and Browsing

- Connects to a NETCONF-capable device and retrieves all supported YANG models via NETCONF Monitoring (RFC 6022)
- Renders the full YANG model tree in a browsable, searchable web interface
- Supports bulk export of discovered YANG models as a ZIP archive

## Live Operational Data

- Fetches real-time operational data for any selected YANG node from the connected device
- Displays live gNMI/gRPC telemetry feeds for devices that support gNMI streaming

## Query and Subscription Tooling

- Generates subtree filters for use in NETCONF get/get-config queries based on selected YANG nodes
- Generates sensor paths for telemetry subscriptions from selected YANG nodes
- Supports editing of IOS XR sensor groups for configuring telemetry subscriptions

## Protocols Supported

- NETCONF and NETCONF 1.1 over SSH
- YANG schema retrieval via NETCONF Monitoring
- gNMI and gRPC for streaming telemetry
- IOS XR 64-bit JSON telemetry encoding

## Constraints

- Requires a minimum of 2–3 GB RAM allocated to the runtime environment; insufficient memory causes instability
- Initial YANG model parsing after connecting to a device may take 1–2 minutes depending on model count
- Live gNMI/gRPC telemetry streaming is limited to IOS XR devices with 64-bit JSON encoding
- NETCONF transport is SSH only; TLS and plain TCP are not supported
