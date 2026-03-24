The SD-RAN RAN Simulator is a virtual radio access network environment from ONF's SD-RAN project that simulates CU/DU nodes and RU cells communicating over the O-RAN E2AP standard. It creates virtual gNodeB environments for testing xApps and E2 termination logic without physical radio hardware. The simulator integrates with a full SD-RAN control plane stack, enabling end-to-end validation of control-loop interactions at the RAN layer.

## Simulation Capabilities

- Simulates multiple gNodeB CU/DU nodes and RU cells defined by a YAML topology model loaded at startup
- Supports KPM service model for periodic UE and cell metrics reporting to connected xApps
- Supports RC service model for control-loop interactions between xApps and simulated nodes
- Generates PCI values per cell as part of the simulated radio environment
- Allows runtime topology and metrics mutations via gRPC API without restarting the simulator

## Protocol Support

- Communicates with E2 termination over O-RAN E2AP carried on SCTP transport
- Exposes a gRPC API for runtime control, dynamic scenario changes, and topology inspection
- Registers simulated nodes as standard gNodeB types for E2 subscription compatibility

## Operational Modes

- Integrated SD-RAN mode: full stack including E2 termination, subscription, and topology services
- Standalone simulation mode: loads YAML topology model and exposes gRPC API only
- Dynamic scenario mode: runtime gRPC calls mutate topology and metrics mid-run for live testing

## Constraints

- The released open-source snapshot cannot build functional binaries because it depends on private ONF repositories; active development branches require ONF membership access
- Deployment requires a running Kubernetes cluster and a package manager; no documented bare-metal or compose-based deployment path exists
- No fault injection, node failure simulation, or failure scenario modeling is supported
- No RRC or NAS layer is simulated — protocol coverage is limited to E2AP; no full radio protocol stack is present
- The public mirror is read-only and does not accept upstream contributions
