This sandbox deploys a complete 5G core network using Open5GS on Kubernetes, with each network function running as a separate microservice. It includes simulated radio access network components that generate real registration, session, and data-plane traffic against the core. Multi-slice support is built in, allowing configuration of independent network slices with dedicated session and user-plane functions per slice.

## Core Network Functions
- Access and Mobility Management (AMF) handles UE registration, authentication coordination, and mobility
- Session Management (SMF) establishes and manages PDU sessions, one instance per slice
- User Plane Function (UPF) forwards user traffic and terminates GTP tunnels, one instance per slice
- Network Repository Function (NRF) provides service discovery for all network functions
- Authentication Server Function (AUSF) and Unified Data Management (UDM) handle subscriber authentication
- Unified Data Repository (UDR) stores subscriber profiles and policies
- Policy Control Function (PCF) enforces session and access policies
- Network Slice Selection Function (NSSF) routes registration requests to the correct slice
- Service Communication Proxy (SCP) brokers HTTP/2 service-based interface calls between functions
- MongoDB stores subscriber records and network function profiles

## Radio Access Simulation
- Simulated base station (gNB) connects to the AMF over the N2 interface using NGAP
- Simulated user equipment (UE) instances register with the core and establish data sessions
- Two UE instances are active by default; additional UEs require manifest changes or use of the multi-slice deployment generator

## Observability
- AMF exposes Prometheus metrics for monitoring registration and session counters
- Optional Monarch overlay enables per-slice monitoring through a dedicated metrics overlay
- Per-pod log streaming is available for each network function in real time
- Packet capture on the UPF tunnel interface allows inspection of user-plane GTP traffic

## Configuration
- Each network function is configured via a dedicated ConfigMap holding its YAML configuration file
- Default deployment uses two network slices identified by S-NSSAIs with distinct slice differentiators
- Slice count and per-slice resources are adjustable through a generation script driven by a single config file
- Subscriber data is managed through a web UI or command-line scripts against the MongoDB store
- Kustomize overlays support standard, metrics, node-selector, and demo deployment variants

## Constraints
- Requires Ubuntu 22.04 LTS; the Kubernetes manifests are not directly usable on macOS or Windows hosts
- Requires Kubernetes with Multus CNI and OVS-CNI pre-configured, and OVS bridges for the N2, N3, and N4 interfaces must exist before deployment
- Minimum hardware is 2 vCPUs, 4 GB RAM, and 40 GB disk
- No fault injection, chaos tooling, or automated traffic generation beyond basic connectivity tests is included
- No pre-built Grafana dashboards are included; Monarch integration for visualization is external to the repository
