The towards5GS Helm Charts repository, maintained by Orange, provides Helm charts for deploying a complete 5G Standalone core network on Kubernetes using Free5GC and UERANSIM. It bundles every major 5G network function as a reusable chart, enabling cloud-native 5G research and integration testing without physical radio hardware. Deployment is a single Helm install that brings up both the core and a simulated RAN simultaneously.

## Core Network Functions

- Access and Mobility Management Function handles UE registration and mobility
- Session Management Function controls PDU session establishment and UPF association
- User Plane Function forwards user traffic through GTP tunnels
- Supporting core functions cover network repository, authentication, subscriber data, policy, and slice selection

## RAN Simulation

- Simulated base station connects to the AMF over the NGAP interface
- Simulated user equipment performs NAS registration, authentication, and PDU session setup
- End-to-end data path exercises GTP-U tunneling between the simulated RAN and UPF

## Protocols Exercised

- NAS carries signaling between the simulated UE and AMF
- NGAP carries signaling between the simulated base station and AMF
- PFCP carries session rules between SMF and UPF
- GTP-U carries user-plane traffic through the data path
- Service-Based Interfaces over HTTP/2 interconnect all core network functions

## Configuration Surface

- Each network function exposes its own values file for PLMN, TAC, and slice identifiers
- Subscriber identity, security keys, and slice subscriptions are set in the UE simulator values
- Secondary network interfaces are declared via Multus CNI network attachment definitions
- GTP tunnel handling is configured through a kernel module on worker nodes

## Constraints

- Multus CNI must be installed on the cluster before deployment; without it, secondary interfaces required by the UPF and simulated RAN cannot be created
- The GTP tunneling kernel module must be loaded on every worker node that will run the UPF
- Only 5G Standalone mode is supported; Non-Standalone mode with an LTE anchor is not available
- No observability stack is included; metrics, tracing, and dashboards must be added separately
- No fault injection or traffic generation tooling is provided beyond the built-in UE simulator
