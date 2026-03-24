# free5GC Sandbox Capabilities

free5GC is an open-source 5G core network implementation conforming to 3GPP Release 15 and later, written in Go. It provides the full set of standard 5G core network functions and is intended for research, development, and testing of 5G infrastructure. It does not include a radio access network (RAN), a packet capture stack, an observability stack, or IMS/VoNR support.

## Core Network Functions

- Access and Mobility Management (AMF), Session Management (SMF), and User Plane (UPF) functions
- Authentication (AUSF), subscriber data management (UDM, UDR), and policy control (PCF)
- Network slice selection (NSSF), network function repository (NRF), and charging (CHF)
- Non-3GPP interworking via N3IWF and Trusted Non-3GPP Gateway (TNGF)
- Web-based subscriber management console backed by MongoDB

## Protocols and Interfaces

- NAS signaling between UE and AMF; NGAP over SCTP for RAN-to-AMF (N2 interface)
- PFCP for SMF-to-UPF control (N4); GTP-U tunneling for user-plane traffic (N3/N9)
- HTTP/2-based Service Based Interface (SBI) for inter-NF communication; optional TLS

## Configuration and Traffic Steering

- Per-network-function YAML configuration for all NFs
- Network slice definitions managed through NSSF and SMF configuration
- Multi-UPF topology and Uplink Classifier (ULCL) mode for traffic path selection
- Subscriber provisioning via web console or direct database insertion

## Observability and Testing

- Per-NF logging to stdout or file with configurable log levels
- Test coverage for multi-UPF and ULCL scenarios
- No built-in metrics exporter or Prometheus endpoint

## Constraints

- Requires a Linux kernel with the GTP5G module loaded on the UPF host; does not run natively on macOS or Windows
- The UPF requires kernel 5.4 or later and privileged host networking; standard container isolation is not sufficient
- No RAN is included — a separate gNodeB simulator such as UERANSIM must be supplied to exercise the full attach-to-data-plane flow
- MongoDB is a hard runtime dependency; no alternative data store is supported
- N3IWF requires a dedicated network interface and kernel IPsec support, making it difficult to sandbox
