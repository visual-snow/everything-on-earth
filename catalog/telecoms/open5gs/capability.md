# Open5GS

Open5GS is an open-source implementation of a 5G Core (5GC) and 4G Evolved Packet Core (EPC), written in C and compliant with 3GPP Release-17. It covers both 5G Standalone and 4G LTE deployments, providing all standard core network functions in a single integrated stack. It does not include a RAN emulator, UE simulator, traffic generator, IMS/VoLTE support, or a charging system.

## Network Functions

- Full 5G SA core: AMF, SMF, UPF, NRF, SCP, SEPP, AUSF, UDM, UDR, PCF, NSSF, BSF
- Full 4G EPC: MME, SGW-C/U, PGW-C/U, HSS, PCRF
- NSA (Non-Standalone) partial support via EPC coexistence

## Protocols

- 5G control plane: NGAP (N2), NAS-5GS, PFCP (N4), SBI (HTTP/2 REST)
- 4G control plane: S1AP, NAS-LTE, GTP-C, Diameter (S6a, Gx, Gy)
- User plane: GTP-U tunneling (kernel TUN device)

## Configuration

- Each network function is configured independently via YAML files
- Subscriber records are provisioned through a web UI backed by MongoDB
- Network slices (S-NSSAI, TAI), APNs/DNNs, and IP pools are all configurable
- IPv4 and IPv6 dual-stack supported in the user plane

## Observability

- Per-NF logging with configurable verbosity levels
- Subscriber session state and data usage queryable through the web UI
- Subscriber records accessible via standard MongoDB tooling
- No built-in Prometheus or metrics endpoint

## Fault Injection

- Individual network functions can be stopped and restarted independently to simulate NF failures
- Network-level faults (packet loss, delay, drops) can be introduced via Linux traffic control and firewall rules against GTP-U or SBI interfaces
- SCTP multi-homing failures can be simulated by manipulating network namespaces or dropping SCTP packets

## Constraints

- Requires a Linux host with TUN/TAP device access and the NET_ADMIN capability; does not run natively on macOS or Windows
- MongoDB is the only supported subscriber data store; no SQL or alternative backend is available
- No built-in RAN emulator — an external software RAN (e.g., srsRAN, UERANSIM) is required to form a complete testbed
- User plane throughput is limited to kernel-space GTP-U via TUN device; DPDK or hardware-accelerated fast-path is not included
- Licensed under GNU AGPL v3.0; commercial use requires a separate license
