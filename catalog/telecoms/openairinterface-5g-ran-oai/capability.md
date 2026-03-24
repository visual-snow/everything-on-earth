## OpenAirInterface 5G RAN (OAI)

OpenAirInterface is an open-source, 3GPP-compliant software implementation of the full 4G LTE and 5G NR radio access network stack, maintained by the OAI Software Alliance. It covers gNB, eNB, and UE components across all standard protocol layers, and supports both real SDR hardware and a software-only RF simulator. It does not include a 5G core network, management APIs, or built-in fault injection.

### RAN Protocol Stack
- Full 5G NR (Rel-15+) and LTE (Rel-10/12) implementations from PHY through RRC
- CU/DU split over F1AP and CU-CP/CU-UP split over E1AP
- 5G N2 interface (NGAP) toward an AMF; 4G S1 interface (S1AP) toward an MME
- O-RAN RIC interface via E2AP

### Deployment Modes
- RF simulator mode: fully software, no SDR hardware required
- Standalone 5G SA and non-standalone NSA (LTE anchor + NR data)
- PHY-test loopback: validates the physical layer without a core network
- RAN-only mode (noS1/noNG): operates without any core network connection

### Measurement and Observability
- Per-UE PHY KPIs: block error rate, modulation-coding scheme, throughput
- RRC state machine tracing and MAC scheduling statistics
- Real-time event tracing via the T-tracer framework

### Configuration
- File-based configuration per network element; no REST or gRPC management API
- Runtime parameter changes require a process restart
- Numerology, bandwidth, and band selection are parameterized in config files

### Constraints
- Supported only on Ubuntu 22.04/24.04, RHEL 9, and Fedora 41; other Linux distributions are unsupported
- Production RF hardware deployments require a real-time kernel or high-priority scheduling; RF simulator mode works on standard kernels
- The OAI Public License V1.1 is not OSI-approved; commercial use requires a separate agreement with the OAI Software Alliance
- The UE simulator cannot connect to commercial 5G networks and does not pass 3GPP conformance tests
