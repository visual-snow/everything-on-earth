## SR Linux/SROS Streaming Telemetry Lab

This lab deploys a Containerlab-based Clos/DCI fabric using Nokia SR Linux leaf and spine nodes alongside Nokia SR OS DC gateways, wired to a complete streaming telemetry stack. It demonstrates gNMI dial-in telemetry collection, EVPN/eBGP underlay and overlay routing, and traffic-driven weathermap dashboards in Grafana.

### Network Fabric

- Four SR Linux nodes acting as leaves (IXR-D2L) and spines (IXR-D3L)
- Two Nokia SR OS DC gateway nodes (SR-1) via SR-SIM
- Six Linux client nodes with iperf3 servers for traffic generation
- eBGP underlay between leaves, spines, and DC gateways
- iBGP/EVPN overlay providing Layer 2 service across the fabric

### Telemetry Collection

- gnmic collector manages gNMI dial-in subscriptions to all NOS nodes
- Three subscription modes available: on-change, sample, and target-defined
- SR OS additionally supports dial-out telemetry (node initiates session)
- SR Linux exposes full YANG coverage of state and configuration data via gNMI
- Collected metrics stored in Prometheus and visualized in Grafana

### Observability

- Grafana preconfigured with anonymous access and the flow-panel (weathermap) plugin
- Weathermap dashboard displays live link utilization across the fabric
- Prometheus exposes all gnmic-scraped metrics for ad-hoc querying
- iperf3 traffic can be generated between client pairs or across all nodes via traffic.sh

### Constraints

- SR OS DC gateway nodes require an active SR-SIM license from the Nokia Support Portal; the lab cannot start those nodes without it
- The topology is Containerlab-native; no docker-compose equivalent exists and Containerlab must be installed on the host
- No fault injection or link failure scenarios are defined in the lab; failure modes must be introduced manually
- NETCONF and RESTCONF interfaces are not exposed or documented in this lab
