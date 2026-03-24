# Sandbox Capabilities

The sandbox provides an open-source 5G RAN stack (srsRAN Project) paired with a 5G core network. It covers the full CU/DU layer stack — control plane, user plane, and physical-to-network layers — operating in RF simulation mode with no physical radio hardware. No UE simulator and no traffic generation tools are included.

Two deployment modes:
- Monolithic gNB: the CU and DU run as a single combined process, simplifying configuration.
- Split architecture: CU-CP, CU-UP, and DU run as separate instances, reflecting real disaggregated RAN deployments.

## RAN Architecture

- Full CU/DU stack is available, including control-plane and user-plane centralized units plus the distributed unit.
- Both Split-7.2 and Split-8 fronthaul configurations are supported.
- The RAN connects to the 5G core over standard interfaces: NGAP toward the AMF, GTP-U for user-plane tunneling.
- Inter-component interfaces (E1AP between CU-CP and CU-UP, F1AP between CU and DU) are active in split mode.

## RF Simulation

- RF is simulated using ZMQ-based virtual radio — no SDR hardware is required.
- The simulation allows RAN bring-up and protocol-layer testing without physical spectrum.

## Configuration

- The gNB is configured via a single YAML file covering AMF connectivity, cell parameters, and architecture selection.
- Architecture mode (monolithic vs. split) and fronthaul split (7.2 vs. 8) are selected at configuration time.
- AMF address and core connectivity parameters are adjustable per deployment.

## Constraints

- No UE simulator is bundled — a separate UE emulator must be provided externally to complete an end-to-end path.
- No built-in metrics export or KPI collection is available; RAN-side performance observability is absent.
- No fault injection or traffic impairment features are present.
- The codebase is archived as of late 2025; active development has moved to a successor project.
- RF simulation approximates channel behavior but cannot replicate real radio propagation, interference, or mobility effects.
