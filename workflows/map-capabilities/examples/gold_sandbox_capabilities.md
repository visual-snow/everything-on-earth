# Sandbox Capabilities

The sandbox is a Dockerized 5G SA core (Open5GS) with a simulated RAN (UERANSIM).
It runs a complete control plane and user plane — no real radio hardware.
Subscriber data is stored in MongoDB. An iperf3 server is available for throughput testing.

Two modes:
- Pre-configured: the network boots ready to use with default subscribers and configs.
- Agent-configured: network functions wait for the agent to provide configurations before starting.

## Connectivity

- UEs can register to the core and establish PDU sessions.
- Data plane connectivity is verifiable by pinging through the GTP tunnel from the UE.
- Multiple UEs can attach simultaneously.

## Measurement

- Round-trip latency is measurable between UE and the data network via ping through the GTP tunnel.
- Uplink and downlink throughput are measurable per UE using iperf3 against a server running inside the sandbox.
- Packet loss is derived from ping statistics.
- Prometheus collects metrics from AMF, SMF, and UPF (registrations, sessions, packet counts).

## Configuration

- Network function configs are YAML files (Open5GS format for core, UERANSIM format for RAN).
- Subscriber profiles are managed in MongoDB — IMSI, authentication keys, QoS parameters (5QI, ARP, GBR/MBR), slice assignment (SST/SD), and AMBR.
- In agent-configured mode, the agent writes configs before network functions start.
- In pre-configured mode, configs can still be modified at runtime.

## Traffic Shaping & Fault Injection

- QoS behavior is simulated using Linux tc/netem on the user plane.
- Configurable impairments: delay, jitter, packet loss, corruption, reordering, and duplication.
- Bandwidth can be capped using token bucket filtering.
- Impairments are defined in a YAML file read at boot.

## Contention

- Background UEs can generate concurrent traffic to simulate resource contention.
- Up to 4 background UEs can run alongside the primary UE.
- Load levels are configurable as a fraction of spare slice capacity.

## Constraints

- No real radio — all RF is simulated, so radio-layer evaluations (handover, beam management, interference) are not possible.
- Backhaul is limited to ~100 Mbit by the Docker bridge network.
- QoS simulation approximates 3GPP behavior but does not replicate a real gNB scheduler.
- All containers share a single host — there is no true geographic distribution or transport latency.
