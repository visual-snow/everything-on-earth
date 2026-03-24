Gradiant 5G Charts is a collection of Helm charts maintained by Gradiant for its Lab5G platform, packaging deployable 5G and 4G network functions and simulators on Kubernetes. It supports both standalone 5G core deployments and LTE/EPC setups, with interchangeable core and RAN components drawn from Open5GS, Free5GC, UERANSIM, srsRAN, PacketRusher, and OpenAirInterface.

## Core Network Functions

- Open5GS 5G SA core, including AMF, SMF, UPF, UDM, UDR, AUSF, PCF, NRF, NSSF, BSF, SCP, and SEPP
- Free5GC 5G SA core with equivalent network function coverage and a subscriber management WebUI
- Open5GS EPC components (HSS, MME, PCRF, SGWC, SGWU) for 4G/LTE deployments
- MongoDB as a shared datastore for both Open5GS and Free5GC subscriber data
- Subscriber provisioning via an init container using add, add-with-APN, and add-with-slice subcommands

## RAN Simulators and Radio Access

- UERANSIM gNodeB and UE simulators for 5G SA, with configurable UE count for multi-UE scenarios
- srsRAN 5G gNB with support for real RF hardware via UHD/USRP or software-only operation over virtual RF transport
- srsRAN 4G eNodeB and UE charts for LTE scenarios, with hardware or virtual RF options
- OpenAirInterface gNB supporting Ettus USRP hardware via a Kubernetes device plugin
- OpenAirInterface eNodeB for 4G RAN coverage

## Load Testing and Traffic Generation

- PacketRusher multi-UE 5G load tester with configurable UE identity, data network name, and gNB parameters
- iperf3 sidecar for active throughput and latency measurements between UE and data network

## Protocols

- 5G NR in Standalone mode; NAS for UE registration and session management
- NGAP for N2 control-plane signaling between AMF and gNB
- GTP-U for N3 user-plane tunneling
- PFCP for N4 session management between SMF and UPF
- SBI using HTTP/2 for communication between 5G core network functions
- S1AP for LTE control-plane signaling; ZMQ virtual RF transport for software-only RAN simulation

## Observability

- PacketRusher exposes an optional Prometheus metrics endpoint with ServiceMonitor and VictoriaMetrics scrape support
- srsRAN 5G ships a monitor sidecar for metrics scraping
- Kubernetes liveness and readiness probes on srsRAN 5G provide health signals
- Open5GS and Free5GC WebUIs provide subscriber and session visibility

## Configuration

- MCC/MNC defaults to 999/70; TAC defaults to 0x0001; slice SST defaults to 1 with SD 0x111111 — all overridable per chart
- AMF hostname, RF device driver, sample rate, downlink ARFCN, band, channel bandwidth, subcarrier spacing, and TX/RX gain are tunable
- UERANSIM UE authentication uses Ki, OPC/OP, and MSISDN; PacketRusher UE identity uses MSIN, key, and OPC

## Constraints

- All charts require a running Kubernetes cluster; no Docker Compose or bare-metal deployment path is provided
- Charts with real RF capability or load-testing functions require privileged pod security context and NET_ADMIN capability, which clusters enforcing restricted Pod Security Admission will block
- SBI communication between core network functions is plain HTTP/2 with no built-in inter-NF encryption or service mesh
- No built-in observability stack is included; Prometheus and Grafana must be deployed separately to collect metrics
- No packet capture or PCAP tooling is bundled in any chart
- srsRAN 5G has a 600-second startup probe initial delay, making automated readiness checks slow in CI pipelines
- MongoDB authentication is disabled by default, making the datastore unsuitable for production use without additional hardening
