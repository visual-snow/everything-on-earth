# Sandbox Capabilities

netlab is an infrastructure-as-code tool that converts declarative YAML topology descriptions into fully configured virtual networking labs. It automates addressing plans, device configuration deployment, and lab lifecycle management across VM-based and container-based runtimes. It does not include a built-in hypervisor, container engine, or network device images — these must be supplied separately.

## Topology Definition

- Labs are described in YAML, specifying nodes, links, protocols, and addressing
- IPv4 and IPv6 address plans are generated automatically from the topology
- Topology graphs can be produced for visualization in external tools
- System-wide and per-device defaults can be overridden

## Lab Lifecycle

- Labs can be started, stopped, and restarted through the CLI
- Device configurations are deployed automatically via Ansible at startup
- Configurations can be collected from running devices for inspection
- Interactive access to individual devices is supported

## Protocol Support

- IGPs: OSPF (v2/v3), IS-IS, EIGRP, RIP (v2/ng)
- BGP: base BGP, BGP-LU, L3VPN (VPNv4/VPNv6), 6PE
- Overlay and tunneling: EVPN, VXLAN, MPLS, SR-MPLS, SRv6
- Switching: VLANs, VRFs, VRRP, LACP, LAG, MLAG, STP
- Auxiliary: LLDP, BFD, DHCP, DHCPv6, static routes, route redistribution

## Observability and Reporting

- Routing reports show BGP, IS-IS, and OSPF adjacencies and prefix tables
- Packet capture is available on VM and container interfaces
- Topology graphs are generated in standard graph description formats

## Fault Injection

- Link impairment can be applied per-link: delay, packet loss, and bandwidth limiting

## Constraints

- A lab runtime must be present: either KVM with Vagrant or Docker with containerlab — neither is bundled
- Network device images (vendor OS, router firmware) are not included and must be obtained and installed independently
- Ansible is required for configuration deployment; without it, configs can be generated but not applied to devices
- Link impairment relies on Linux kernel facilities and is not functional on non-Linux hosts
- There is no real-time telemetry, SNMP collection, or web dashboard — observability is limited to CLI reports and packet captures
