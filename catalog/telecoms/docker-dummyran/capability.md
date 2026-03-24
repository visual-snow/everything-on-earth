This sandbox provides a simulated 4G LTE Radio Access Network (RAN) environment designed for testing and development of LTE core network components without physical radio hardware. It acts as an eNodeB simulator capable of initiating the control-plane handshake with a Mobility Management Entity (MME). The environment is useful for validating MME behavior, S1 interface connectivity, and LTE signaling workflows in isolation.

## RAN Simulation

- Simulates an eNodeB (base station) on the S1 interface toward a real or simulated MME
- Initiates the S1 Setup Request procedure to establish a control-plane connection
- Uses S1AP (S1 Application Protocol) carried over SCTP as the transport

## Configuration

- Target MME address and port are configurable at runtime
- Supports connection to either a live MME or another simulated core network component

## Constraints

- Simulates only the control-plane MME handshake (S1 Setup); user-plane (GTP-U) traffic and full E-UTRAN functionality are not supported
- No User Equipment (UE) simulator is included — the environment cannot model end-to-end subscriber sessions
- No built-in traffic generation, load testing, or measurement collection capability
- Source repository metadata was unavailable at catalog build time; capability details are derived from known LTE S1AP conventions and available entry metadata
