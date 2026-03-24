CORE (Common Open Research Emulator) is a network emulation tool that uses Linux network namespaces to run multiple emulated nodes and links on a single machine. It supports both graphical and scripted workflows, and can bridge emulated topologies to live physical networks for hybrid experiments.

## Topology Design
- Build and edit network topologies visually through the graphical interface
- Define topologies programmatically using the Python scripting API
- Connect emulated nodes to live physical networks for hybrid emulation

## Routing Protocols
- Emulate standard unicast protocols including BGP, OSPF, and RIP
- Support for mobile and wireless protocols including OLSR and MANET
- Integrate with EMANE for RF channel and electromagnetic maneuver emulation
- Configure OSPF MDR for multicast designated router scenarios

## Execution Modes
- Run topologies interactively via the GUI for visual inspection and control
- Automate topology creation and execution through Python scripts
- Operate in hybrid mode with emulated nodes peering with real network infrastructure

## Measurement and Monitoring
- No built-in measurement or telemetry pipeline is included
- External measurement tools can be attached via hybrid live-network connectivity

## Constraints
- Requires a Linux host; Linux network namespaces are not available on macOS or Windows
- Python 3.9 or higher must be present on the host system
- EMANE-based wireless emulation requires a separate EMANE installation
- No built-in fault injection capability is documented
