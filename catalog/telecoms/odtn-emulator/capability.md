The ODTN-emulator provides software-simulated optical transport network nodes for testing and developing network management applications without physical hardware. It models two complementary node types — OpenConfig-compliant terminal devices and a TAPI 2.1 optical line system — together forming a minimal but representative disaggregated optical network topology.

## OpenConfig Terminal Device Emulation
- Simulates Cassini-model terminal devices with line-side and client-side optical components
- Exposes 16 optical channel components per node, each reporting output and input power with instant, average, minimum, and maximum readings at 60-second intervals
- Accepts configuration of per-channel target output power via NETCONF edit-config operations
- Two independent terminal device instances run simultaneously, enabling multi-node management scenarios

## TAPI Optical Line System Emulation
- Models the optical line system components that sit between terminal devices in an Open Line System architecture
- Exposes a network topology of 2 devices, 64 ports, and 12 links via a REST interface
- Implements TAPI 2.1 schema for topology and connectivity service queries
- Serves static pre-loaded state; no runtime provisioning workflows are supported

## Protocol Interfaces
- NETCONF over SSH for all OpenConfig terminal device interactions
- HTTP REST for all TAPI optical line system interactions
- YANG data models underpin all OpenConfig and TAPI schemas

## Constraints
- All emulated state is loaded from static XML files at startup and does not change at runtime; power values are fixed and no degradation or failure simulation is available
- YANG schemas are patched at startup to work around datastore limitations, causing them to diverge from canonical upstream OpenConfig definitions
- The TAPI emulator has no NETCONF interface and no authentication; the OpenConfig emulators use hardcoded credentials with no hardening
- The third emulator variant (Lumentum) exists in source but is not wired into the default multi-node deployment
- No streaming telemetry, gNMI, SNMP, or fault injection interfaces are available
- State does not persist across restarts; each start re-initializes all nodes from static configuration files
