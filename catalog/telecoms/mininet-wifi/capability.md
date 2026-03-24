Mininet-WiFi is a Mininet fork that adds wireless station and access point emulation for software-defined networking experiments over 802.11 links. It extends the standard virtual network framework with a wireless medium simulation daemon, enabling realistic signal propagation and interference modeling while retaining full OpenFlow and OpenvSwitch compatibility. Topologies are defined programmatically via a Python API or through a graphical editor.

## Wireless Emulation

- Emulates WiFi stations and access points backed by a wireless access point daemon within a single host
- Simulates the wireless medium including signal attenuation and interference between nodes
- Supports WPA/WPA2 authentication via wireless supplicant integration
- Optionally extends to IEEE 802.15.4 and 6LoWPAN for low-power wireless scenarios

## SDN and Switching

- Integrates OpenvSwitch for OpenFlow-capable virtual switching across wireless and wired segments
- Supports P4-based data plane programming as an optional extension
- Topology control and link manipulation follow the standard Mininet CLI and API conventions

## Measurement and Observation

- Collects wireless interface statistics and link-layer metrics via standard wireless tooling
- Measures throughput and latency using external traffic generators such as iperf and ping
- Exposes per-station and per-AP association state for monitoring experiments

## Fault Injection

- Configures degraded wireless conditions (attenuation, interference) through the medium daemon
- Applies additional link impairments such as packet loss and delay via standard Linux traffic control

## Constraints

- Requires Ubuntu 16.04 or higher; certain access point daemon features are broken on earlier Ubuntu releases
- Wireless emulation depends on a kernel module not available in all virtualized or container environments; the host kernel must expose this module for any deployment mode to function
- Network Manager must be disabled on affected Ubuntu distributions to prevent interference with virtual wireless interfaces
- No built-in LTE or 5G radio access network emulation; wireless support is limited to 802.11 and optionally 802.15.4
