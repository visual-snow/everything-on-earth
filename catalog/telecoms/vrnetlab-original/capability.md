vrnetlab runs full KVM-based emulations of commercial virtual routers, packaging vendor disk images into isolated environments suitable for automated network testing. It was originally developed for Deutsche Telekom's TeraStream project and is designed primarily for CI/CD workflows rather than interactive labbing. Supported platforms include Arista vEOS, Cisco CSR1000v, NX-OS Titanium, XRv, XRv 9000, Juniper vMX, vQFX, and Nokia VSR.

## Routing Protocols
- BGP, OSPF, IS-IS, and MPLS are available through the emulated router platforms
- Protocol behavior matches the vendor's actual software stack, not a simulation

## Management and Configuration
- Routers are accessible via SSH and NETCONF for programmatic configuration and retrieval
- Serial console access is available for low-level troubleshooting
- YANG-modeled data can be queried and pushed over NETCONF
- SNMP polling is supported for basic monitoring

## Inter-Router Connectivity
- Point-to-point links between router instances are established through vr-xcon, a TCP socket bridge
- Multi-router topologies are assembled by wiring vr-xcon connectors between interfaces

## Operational Modes
- CI/CD automated testing is the primary design target
- Programmatic network emulation for scripted test scenarios; not intended for manual lab sessions

## Constraints
- Users must supply their own vendor-licensed disk images; no pre-built router images are distributed due to commercial license restrictions
- Requires a Linux host with KVM and nested virtualization support; incompatible with xhyve and standard VirtualBox
- No configuration persistence across restarts; container state is intentionally discarded for stateless CI workflows
- Resource consumption is equivalent to running full virtual machines, not lightweight containers
- No built-in topology orchestration, fault injection, or GUI; users must script startup and wiring manually
