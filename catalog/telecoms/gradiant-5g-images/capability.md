This sandbox provides a collection of containerized Cloud-Native Network Functions for building end-to-end 5G (and 4G/EPC) testbeds, maintained by Gradiant for its Lab5G platform. It supports two complete 5G core stacks — Open5GS and free5GC — alongside simulated radio access network components, enabling realistic mobile network emulation without physical radio hardware. Deployments range from a single base station with a handful of user devices to multi-slice, dual-base-station configurations.

## 5G Core Network Functions

- Full Open5GS core stack including access and mobility management, session management, user plane, network repository, authentication, unified data management, policy control, and network slice selection functions
- Full free5GC core stack with equivalent network function coverage
- Subscriber management web interfaces for both core stacks
- A shared document database for subscriber and session state

## Radio Access Network Simulation

- UERANSIM simulated 5G base station and user equipment, supporting multiple simultaneous UE tunnels per container
- PacketRusher simulated base station and UE with virtual routing and forwarding isolation per subscriber
- srsRAN support for both 4G and 5G configurations, including hardware-attached deployments with Ettus USRP radios

## Protocols and Interfaces

- 5G NR over simulated radio frequency
- N2 control plane (NGAP) between access management and base station
- N3 user plane (GTP-U tunneling) between user plane function and base station
- Service-Based Interface (HTTP/2) between 5G core network functions
- Non-Access Stratum signaling via simulated UE components

## Traffic and Measurement

- End-to-end UE connectivity verified via ping and traceroute over simulated tunnel interfaces
- Throughput measurement via a bandwidth testing tool executed within per-subscriber virtual routing contexts
- Multiple simultaneous UE tunnels observable as separate network interfaces

## Configuration

- Mobile country and network codes, tracking area code, and slice parameters set via environment variables
- UE credentials (key, operator code, IMSI, MSISDN) and APN/DNN configured per container
- AMF and base station addresses resolved by hostname within the deployment network
- Network and user plane bind interfaces selectable by name or explicit IP
- NAT on the user plane function can be disabled; SMF configuration overridable via volume mount
- Multi-UE count controlled by a flag on the UE container command

## Deployment Modes

- Single or dual base station with one or two network slices
- PacketRusher mode with VRF-based subscriber isolation
- Open5GS with OAI CN5G and UERANSIM
- Open5GS or free5GC with UERANSIM
- Open5GS with srsRAN (4G or 5G), including USRP hardware variants
- IMS stack integrated with Open5GS and srsRAN

## Fault Injection

- Individual network function containers can be stopped independently to simulate NF outages
- No dedicated fault injection tooling is included

## Constraints

- The user plane function container must run in privileged mode with access to a kernel TUN device on the host
- PacketRusher requires a host with a GTP kernel module and a privileged container
- USRP-based deployments require physical Ettus USRP hardware attached to the host machine
- Subscriber registration is a manual prerequisite that must be completed before any UE can attach
- Multi-slice operation requires manual override of NSSF and AMF configuration files via volume mounts
- No observability stack, automated provisioning, or traffic shaping is included
