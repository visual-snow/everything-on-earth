This sandbox provides a three-node Arista containerized EOS lab arranged in a triangle topology with EBGP pre-configured between all peers. Each node runs as a separate autonomous system, giving operators a realistic multi-AS environment on a single host. The lab is managed entirely through a Makefile that handles bring-up, teardown, and interactive CLI access.

## Network Topology

- Three Arista cEOS switches connected in a full triangle (each node peers with the other two)
- Each switch operates in its own BGP autonomous system (65001, 65002, 65003)
- Dedicated out-of-band management network separate from the three point-to-point data-plane links

## Management Interfaces

- eAPI (HTTP JSON-RPC) available on all three nodes for programmatic command execution
- SSH access to each node's EOS CLI for interactive troubleshooting and configuration
- NETCONF available through EOS on all nodes (not pre-configured in demo startup configs)
- gNMI available through EOS on all nodes (not pre-configured in demo startup configs)

## Routing and Protocol Support

- EBGP sessions established at startup between all three node pairs
- BGP adjacency state inspectable via standard EOS show commands
- Per-device startup configurations stored as flat files and applied at container launch

## Observability

- BGP session state readable through eAPI queries or interactive CLI
- No streaming telemetry or gNMI Subscribe configuration included
- No pre-built dashboards or time-series database integrations present

## Automation Layer

- Single Makefile drives all lifecycle operations: bring-up, teardown, and per-node CLI access
- Startup configurations are version-controlled flat files, editable before launch

## Constraints

- The cEOS image must be downloaded manually from the Arista support portal, which requires a registered account; it is not bundled with the lab
- The image version is pinned and cannot be changed without editing the Makefile
- A mandatory 120-second delay follows bring-up before the topology becomes usable
- No fault injection, link-failure simulation, or high-availability topology variants are included
- No automated test harness or CI/CD integration is present
