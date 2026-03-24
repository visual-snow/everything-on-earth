# Sandbox Capabilities

The sandbox is a containerized 5G SA core with MBS-enhanced network functions implementing 3GPP Release 17 Multicast-Broadcast Services (MBS). It includes a simulated RAN and UE alongside the core, enabling end-to-end testing of both point-to-multipoint (PTM) and point-to-point (PTP) MBS delivery. There is no real radio hardware and no observability stack.

Two deployment modes:
- Internal: complete end-to-end stack — core, gNB, and UE run together in a single environment.
- External: core only — accepts connections from an external gNB implementation.

## MBS Delivery
- The network supports MBS session establishment and delivery over the 5G user plane.
- A dedicated test Application Function/Application Server is available to drive MBS sessions.
- Both PTM (multicast) and PTP (unicast MBS) delivery modes can be exercised.

## Core Control Plane
- Full 5G SA control plane: registration, authentication, session management, and policy enforcement.
- MBS-enhanced AMF, SMF, and MB-SMF handle mobility and multicast session control.
- Subscriber and policy data are stored in a database accessible through a management UI.

## User Plane
- MBS-enhanced UPF and MB-UPF carry GTP-U tunnels for both unicast and multicast traffic.
- UEs can register, establish PDU sessions, and receive MBS content.

## Configuration
- Network function behavior is controlled via per-function YAML configuration files.
- Component versions are independently selectable for MBS-enhanced and standard core functions.

## Constraints
- No built-in traffic generation or load testing beyond the MBS test application container.
- No metrics or observability tooling — there is no Prometheus, Grafana, or equivalent.
- All components run on a single host network — there is no multi-host or distributed deployment.
- MBS-enhanced components are built from a development branch, not a stable upstream release.
- Linux host required; Windows and macOS are not supported.
