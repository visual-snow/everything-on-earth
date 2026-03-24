MaxiNet is a distributed SDN network emulator that extends Mininet across multiple physical machines, enabling large-scale topology experiments that exceed the capacity of a single host. A central coordinator partitions the topology graph using METIS and distributes subtopologies to worker nodes connected over inter-machine tunnels. An external OpenFlow controller drives the emulated switches via the standard SDN southbound interface.

## Topology & Partitioning
- Automatic METIS-based partitioning splits a single topology into per-worker subgraphs weighted by a configurable share value
- Static mapping mode lets experiments assign nodes to specific workers explicitly
- Dynamic topology modification allows adding hosts, switches, and tunnels while an experiment is running
- Link fault injection brings individual emulated links up or down at runtime

## Network Emulation
- GRE tunnels carry inter-worker data-plane traffic by default; STT tunneling is available as an alternative
- OpenFlow southbound protocol connects emulated switches to an external controller
- Host network interfaces support TCP Segmentation Offload deactivation and RSS load-balancing across multiple worker IPs
- Link bandwidth limiting and other traffic-control parameters are applied per emulated interface

## Node Modes
- Default mode uses standard Mininet hosts and Open vSwitch switches
- Optional Docker-container node mode replaces hosts with containers via the ContainerNet fork
- Optional libvirt node mode replaces hosts with hypervisor-managed virtual machines

## Measurement & Monitoring
- Per-worker CPU, memory, and network-interface utilisation logging activated through a single monitor call
- Post-experiment plotting of monitored resource data from collected logs
- Bandwidth measurement between emulated hosts via iperf
- Reachability and latency checks via ping and ICMP RTT

## Configuration
- Single INI-format configuration file shared across all nodes covers the coordinator, each worker, and shared secrets
- HMAC password authenticates remote procedure calls traffic between the coordinator and workers
- Threadpool size on the coordinator governs maximum cluster scale (each worker consumes dedicated threads)

## Constraints
- Requires Python 2; the codebase is incompatible with Python 3
- Installer and dependencies are validated only on Debian 8 and Ubuntu 14.04; other distributions are unsupported
- STT tunneling does not support bandwidth limiting or other traffic-control link parameters
- Physical network MTU must exceed 1500 bytes to carry GRE-encapsulated packets without MTU reduction
- No multi-tenancy isolation — the cluster must run on a trusted private network
- METIS must be installed separately; topology partitioning fails without it
- No built-in REST or gRPC management API; control is exclusively through the Python API or interactive CLI
