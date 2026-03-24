The Cisco NSO Docker (NID) sandbox provides a fully functional Cisco Network Services Orchestrator environment running inside containers, built from an official NSO installer. It supports NED and service package development, testing, and validation through a Makefile-driven workflow with ephemeral test environments. The environment includes a production runtime image and a development image with a complete Python and Java toolchain.

## Orchestration and Workflow

- Build targets create and tear down multi-container test environments per run
- CI mode tags images by NSO version and pipeline ID; master branch receives a bare version tag
- Project skeletons (NED, package, and system repository templates) are available to bootstrap new work
- Incremental package compilation runs inside a live container via helper scripts

## Device Simulation

- Network devices are simulated using netsim containers, each modeling YANG-defined device types via ConfD
- Simulated devices can be stopped and restarted independently from NSO to replicate device unreachability
- NSO syncs from simulated devices over NETCONF; configuration is pushed the same way as with real devices

## Management Interfaces

- NSO is accessible via its CLI in both J-style and C-style modes
- NETCONF is available for device synchronization and configuration push
- RESTCONF is exposed for programmatic access
- SSH is used for device management and netsim host-key retrieval

## Observability and Debugging

- A health check polls NSO phase status at regular intervals to confirm the daemon is fully started
- Package operational status is verified by inspecting package status through the CLI
- Python remote debugging is available via debugpy on a runtime-assigned host port
- A live NSO restart can be triggered without container recreation by sending SIGHUP to the run process

## Fault Injection

- Individual netsim containers can be stopped to simulate device loss while NSO continues running
- Packages can be force-reloaded via CLI command or a build-time variable during a clean rebuild

## Constraints

- The NSO installer binary must be obtained directly from Cisco and supplied before any image can be built; pre-built images are not redistributable due to licensing
- Stopping a netsim container with SIGINT kills the ConfD VM immediately without flushing its configuration database; always stop netsim cleanly to preserve state
- The health check start period may be insufficient for environments with a large number of packages, requiring an explicit increase
- IPv6 network prefixes are randomized on each test environment start; tests that depend on a fixed IPv6 address must set the prefix explicitly via a build variable
