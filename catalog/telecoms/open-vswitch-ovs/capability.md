Open vSwitch is a production-quality, multilayer software switch designed for virtual machine environments and capable of spanning multiple physical servers. It combines a Linux kernel module for high-performance flow-based switching with a fully userspace datapath option, and is managed through a transactional database (OVSDB) alongside an OpenFlow control plane.

## Switching and Forwarding

- Operates in standalone mode as a self-learning switch or in controller mode delegating decisions to an external OpenFlow controller
- Supports kernel datapath for production-grade throughput and a userspace DPDK datapath for kernel-bypass forwarding
- Implements OpenFlow 1.0 plus a broad set of extensions for flow table management

## Tunneling and Encapsulation

- Supports VXLAN, GRE, Geneve, ERSPAN, GTP-U, SRv6, and Bareudp tunnel types
- Handles 802.1Q VLANs on both trunk and access ports
- Supports LACP-based NIC bonding across physical uplinks

## Monitoring and Measurement

- Exports flow-level traffic data via NetFlow, IPFIX, and sFlow
- Port mirroring copies packets to a designated monitoring interface
- CLI tools expose live flow table entries and datapath statistics without external tooling

## Configuration and Control

- OVSDB serves as the sole configuration store, accessible through C and Python bindings
- Command-line utilities manage bridges, ports, tunnels, flow entries, and QoS policies
- Runtime daemon parameters such as log levels and revalidation behavior are tunable without restart

## Fault Injection and Testing

- Flow rules can be installed to drop, redirect, or override traffic at specific priorities
- A packet tracing utility simulates how a hypothetical packet traverses the pipeline without injecting real traffic
- A simple built-in OpenFlow controller supports basic drop and redirect scenarios for test use only

## Constraints

- The userspace datapath without DPDK is explicitly experimental and carries significant performance cost relative to the kernel datapath
- The kernel module must match the running kernel version; a version mismatch requires recompilation or fallback to the userspace datapath
- OVSDB and OpenFlow are the only native management interfaces; there is no built-in REST or gRPC API
- OpenFlow support is version 1.0 plus extensions, and full feature parity with later OpenFlow specification versions is not guaranteed
