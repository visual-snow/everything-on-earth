This environment provides a containerized LTE research platform built around srsRAN, running an Evolved Packet Core and an LTE base station as separate privileged services on a shared host. It is designed for SDR-based LTE experimentation using BladeRF or SoapySDR-compatible hardware. The setup targets researchers who need isolated EPC and eNB components running against real or emulated radio hardware.

## LTE Core (EPC)

- Runs a full Evolved Packet Core implementing MME, HSS, and SGW/PGW functions
- Handles S1-MME control-plane signaling from the base station
- Supports GTP-U user-plane tunneling
- Exposes both control and user-plane ports to the host for standalone core testing

## LTE Base Station (eNB)

- Runs an LTE eNodeB capable of transmitting and receiving over a physical SDR device
- Reads device hardware through direct host device access
- Configured via standard srsRAN eNB configuration files installed at startup
- Operates on an isolated radio-access network segment

## Configuration and Observation

- EPC and eNB each load their configuration from files placed by an install service at startup
- Both services bind-mount large portions of the host filesystem to share libraries and system tools
- Inspection of running state requires attaching directly to the container process; no structured log output is configured
- No ZeroMQ virtual RF mode is configured, so software-only loopback radio is not available out of the box

## Constraints

- Both services require full privileged mode with unrestricted host kernel access; they cannot run in a restricted or unprivileged container environment
- The EPC and eNB are placed on separate isolated networks with no inter-container route, meaning the S1 interface between them is not routable as configured and must be manually bridged before the stack can function end-to-end
- No user equipment service is defined, so a complete attach procedure requires an external UE or additional configuration
- The base image is unpinned, so builds may produce different results as upstream packages change over time
- No example configuration files are included; valid epc.conf and enb.conf must be supplied before the services will start successfully
