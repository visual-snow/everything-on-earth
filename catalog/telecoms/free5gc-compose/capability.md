# free5gc-compose Sandbox Capabilities

free5gc-compose is a containerized deployment of the free5GC open-source 5G standalone core network, implementing the full set of 3GPP Stage 3 control-plane and user-plane network functions. It bundles a gNB and UE simulator (UERANSIM) to emulate radio access, enabling end-to-end 5G SA testing without physical hardware. It does not include 4G/EPC interworking, built-in fault injection, or automated test suites.

## Control-Plane Network Functions

- Access and Mobility Management (AMF) — handles UE registration, mobility, and N2/N1 signaling
- Session Management (SMF) — manages PDU sessions and the N4 interface toward the user plane
- Authentication Server (AUSF), Unified Data Management (UDM), and Unified Data Repository (UDR) — subscriber authentication and data storage
- Policy Control (PCF) — provides policy rules to other NFs
- Network Repository (NRF) — NF registration and discovery
- Network Slice Selection (NSSF) — slice selection logic
- Network Exposure (NEF) — external API exposure
- Charging Function (CHF) — online/offline charging

## User-Plane and Non-3GPP Functions

- User Plane Function (UPF) — GTP-U tunneling and packet forwarding on the N3/N9 interfaces
- ULCL topology — optional split user-plane with I-UPF and PSA-UPF for uplink classifier testing
- Non-3GPP Interworking Function (N3IWF) and Trusted Non-3GPP Gateway Function (TNGF) — Wi-Fi and trusted non-3GPP access

## RAN Simulation

- UERANSIM gNB — simulates a 5G base station over NGAP (N2) and GTP-U (N3)
- UERANSIM UE — simulates one or more user equipment over NAS (N1)
- srsRAN can substitute UERANSIM as an alternative RAN simulator

## Subscriber Management

- Web interface for creating, editing, and deleting subscriber profiles
- MongoDB backend stores subscriber credentials, slice configuration, and policy data

## Observability

- Per-NF metrics endpoints exposed to an optional Prometheus collector
- Grafana dashboards available when the monitoring overlay is enabled

## Deployment Modes

- Standard mode — runs pre-built images with no compilation step
- Build mode — compiles free5GC from local source before running
- ULCL mode — activates split user-plane topology
- Monitoring mode — adds Prometheus and Grafana as an overlay

## Constraints

- The GTP5G kernel module must be installed on the host; the UPF cannot create tunnel interfaces without it
- UPF and N3IWF containers require privileged execution to manage tunnel network interfaces
- MongoDB versions above 4.4 require AVX CPU support; hosts lacking AVX must use a workaround
- Compose v2 is required; Compose v1 is not supported
- ULCL topology is validated only against a specific release tag and may not work on other versions
