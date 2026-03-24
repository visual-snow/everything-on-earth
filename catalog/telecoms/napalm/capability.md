NAPALM is a Python library that provides a unified, vendor-agnostic API for connecting to, configuring, and retrieving operational state from network devices. It abstracts vendor-specific CLIs and management APIs behind a single consistent interface, supporting Arista EOS, Cisco IOS, IOS-XR, NX-OS, Juniper JunOS, and other platforms. Agents can use NAPALM to automate multivendor network tasks without learning each platform's native tooling.

## State Retrieval

- Retrieve device facts: hostname, vendor, model, OS version, uptime, serial number, and interface list
- Query interface status, IP assignments, and traffic counters
- Inspect BGP neighbor relationships, neighbor detail, and BGP configuration
- Discover LLDP neighbors and their details
- Perform routing table lookups for specific prefixes
- Read ARP tables, IPv6 neighbor tables, and MAC address tables
- Retrieve NTP server, peer, and statistics information
- Collect SNMP community and configuration details
- Sample environment health: CPU load, memory usage, temperatures, power draw, and fan status
- Fetch system log entries
- Retrieve running, startup, or candidate configurations
- Execute active connectivity probes via ping and traceroute

## Configuration Management

- Load a full candidate configuration to replace the running configuration
- Load a partial candidate configuration to merge into the running configuration
- Generate candidate configurations from Jinja2 templates
- Compare a candidate configuration against the running configuration to produce a diff
- Commit a candidate configuration to make it active
- Discard a candidate configuration without applying changes
- Roll back a device to its previous configuration state

## Transport and Integration

- Connect to devices over SSH, NETCONF, or HTTP-based APIs depending on the vendor driver
- Invoke NAPALM from the command line using the bundled CLI client
- Integrate with Ansible via dedicated NAPALM modules
- Integrate with SaltStack and StackStorm using built-in or packaged support

## Constraints

- A real or emulated network device must be reachable; NAPALM has no built-in simulation or mock mode
- Getter method support varies by vendor driver; not every retrieval operation is available on every platform
- Some platforms require manual feature enablement before connections succeed (for example, the XML agent on IOS-XR or NXAPI on NX-OS)
- Atomic configuration replace and candidate-config workflows are not uniformly supported across all platforms
- Streaming telemetry via gNMI or gRPC is not available in the core library
- No fault injection, traffic generation, or chaos engineering capabilities are provided
