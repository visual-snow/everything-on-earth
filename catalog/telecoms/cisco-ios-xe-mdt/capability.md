This sandbox provides a pre-configured telemetry collection stack designed to receive, store, and visualize streaming telemetry from Cisco IOS XE network devices. It supports three transport modes — gRPC Dial-Out, NETCONF Dial-In, and gNMI Dial-In — and stores time-series data for dashboard visualization. The environment targets Catalyst 9000-series switches and wireless controllers running IOS XE 16.10 or later.

## Transport Protocols

- gRPC Dial-Out: device initiates connection to the collector; subscriptions defined statically on the device
- NETCONF Dial-In: collector opens a session to the device and dynamically sends subscriptions
- gNMI Dial-In: collector subscribes using periodic sample or on-change mode
- TLS and mutual TLS secured transport available as an option for gRPC

## Telemetry Data Available

- Interface counters and admin/operational state changes
- CPU utilization and memory usage
- Temperature sensors, fan state, and power supply state
- System state, last boot time, and login/logout events
- OSPF neighbor state changes and BGP peer state changes
- Wireless AP radio operational data (requires IOS XE 17.7 or later)
- Storage and USB peripheral state change events

## Subscription Modes

- Periodic: data pushed at a configured interval (e.g., every 30 seconds)
- On-change: event-driven push triggered when monitored data changes
- YANG data models supported include Cisco-IOS-XE vendor models and OpenConfig models

## Fault and Event Injection

- On-change subscriptions can be configured to capture routing protocol flaps (OSPF, BGP)
- Interface state change events available for both admin and operational state
- System event notifications cover reboots, temperature faults, fan faults, flash faults, and SFP changes
- Configuration change events observable via on-change subscription on the native configuration tree

## Constraints

- IOS XE 16.10 or later is required for gRPC Dial-Out; gNMI secure mode additionally requires TLS certificates pre-loaded on the device
- NETCONF Dial-In requires AAA configured on the device with a privilege level 15 user
- Power supply state via the OpenConfig platform XPath is documented as non-functional on C9300 running IOS XE 17.3
- No device emulator or simulator is included; a real or lab IOS XE device is required to generate telemetry
- gNMI insecure mode does not support TLS; switching to secure mode requires a separate certificate generation workflow
- No data retention policy or time-to-live is configured for stored telemetry by default
