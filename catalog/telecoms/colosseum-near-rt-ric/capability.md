The Colosseum Near-Real-Time RIC is a minimal O-RAN Software Community RIC (Bronze release) adapted for the Colosseum wireless network emulator as part of the OpenRAN Gym project. It provides E2 termination, E2 management, routing, and an in-memory state store, supporting concurrent connections from multiple base stations and multiple xApps. It is designed to run inside Colosseum LXC containers and is orchestrated entirely through shell scripts.

## Interfaces and Protocols

- E2AP over SCTP connects RAN nodes to the E2 termination component
- RIC Message Router handles inter-component messaging, keyed by message type identifiers
- Redis serves as the in-memory state store between the E2 manager and the database component
- Two deployment modes are supported: standard mode with network address translation for Colosseum, and a co-located mode for Arena environments where RIC and DU share the same machine

## Observability

- RIC Indication Messages are received from RAN nodes at a 250 ms default periodicity
- E2 termination logs expose gNB connection events and message processing latency at nanosecond resolution in debug mode

## Configuration

- The network interface for SCTP binding is selected at startup and determines which physical or virtual interface the E2 termination listens on
- A static routing table maps message type identifiers to component addresses and must be regenerated manually whenever xApp assignments change
- The gNB identifier and xApp identifier are injected at runtime through environment variables
- E2 termination behavior, including log level and trace mode, is controlled through a mounted configuration file

## Constraints

- The environment is designed exclusively for Colosseum; the base container images are only available to Colosseum users and cannot be used outside that platform
- The static routing table must be manually rebuilt and all affected components restarted whenever xApp network assignments or message type mappings change
- Only a single xApp IP slot is pre-allocated by default; running multiple xApps requires modifying the network setup and regenerating the routing table
- This is a Bronze release baseline and does not include the A1 interface, O1 management interface, xApp onboarding workflow, or a distributed shared data layer
