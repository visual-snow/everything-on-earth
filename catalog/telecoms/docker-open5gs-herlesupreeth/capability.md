# Sandbox Capabilities

The sandbox is a containerized 4G/5G telecom network stack combining Open5GS core network functions with simulated radio access via UERANSIM and srsRAN. It supports both 4G EPC and 5G Standalone configurations, and optionally IMS voice services (VoLTE/VoNR) and WiFi calling. No real radio hardware is required for standard use — all RF is simulated over a software transport layer.

## Core Network

- Full 4G Evolved Packet Core: mobility management, session management, user plane, policy, and subscriber data functions.
- Full 5G Standalone core: access and mobility management, session management, user plane, and all supporting service-based interface functions.
- Both generations can be deployed independently or together depending on the selected scenario.

## Radio Access

- 4G eNodeB and UE simulation via srsRAN.
- 5G gNodeB simulation via srsRAN and UERANSIM.
- 5G UE simulation via UERANSIM.
- Single-host and multi-host topologies supported — radio and core can run on the same or separate machines.

## IMS and Voice Services

- VoLTE and VoNR call routing through an IMS core (Kamailio or OpenSIPS).
- IMS subscriber management via a dedicated Home Subscriber Server.
- WiFi calling supported through an ePDG gateway with IKEv2 authentication.

## Charging

- Online charging system for real-time credit control and quota enforcement during data sessions.

## Observability

- Real-time dashboards displaying network function metrics.
- Metrics collected continuously from all core network functions.
- Subscriber state and IMS data queryable through dedicated management interfaces.

## Configuration

- Mobile network identity (country and network codes) configurable at deployment time.
- Subscriber IP address pools adjustable per scenario.
- Radio mode switchable between software simulation and over-the-air SDR hardware.
- Over 19 named deployment scenarios covering 4G-only, 5G SA, IMS, ePDG, and hybrid topologies.

## Constraints

- IPv6 subscriber addressing inside containers is not supported — all UE sessions use IPv4 only.
- No built-in fault injection, chaos tooling, or automated test harness — scenario execution is fully manual.
- No packet capture service included in the deployment stack.
- No O-RAN interfaces or RAN Intelligent Controller component — RAN is not disaggregated.
- Over-the-air radio mode requires specific SDR hardware models and is not available in software-only environments.
