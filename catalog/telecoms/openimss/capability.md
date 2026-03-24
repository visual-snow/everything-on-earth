openIMSs is an open-source, containerized IP Multimedia Subsystem (IMS) platform that integrates Open5GS, OpenSIPS IMS, srsRAN, and UERANSIM into a full 4G/5G core and IMS stack. It supports voice, video, RCS, and instant messaging services across both Non-Standalone (NSA) and Standalone (SA) 5G deployment modes. The platform spans over 40 microservices covering the full 3GPP network function stack, making it suitable for practical telecommunications development and research.

## Core Network Functions

- Full 5G Core (5GC): AMF, SMF, UPF, UDM, UDR, AUSF, NSSF, PCF, BSF, NRF, SCP
- 4G EPC components: MME, SGWC, SGWU, HSS, PCRF
- Legacy GSM support via OsmoHLR and OsmoMSC

## IMS Signaling

- SIP-based call session control via OpenSIPS P-CSCF, I-CSCF, and S-CSCF
- Home Subscriber Server for IMS via FHOSS
- Media plane handled by RTP Engine with RTP/SRTP transport
- Voice codec support through Asterisk with AMR

## RAN and Simulation

- 4G eNB and 5G gNB radio support via srsRAN
- 5G NR UE and gNB simulation via UERANSIM
- ZMQ-based radio emulation available for simulation without physical SDR hardware
- OpenAirInterface (OAI) integration supported

## Protocols

- SIP/IMS for multimedia session signaling
- Diameter for 3GPP AAA and policy signaling
- S1AP and NG-AP for 4G and 5G RAN-to-core interfaces
- GTP-U for user-plane tunneling; SCTP as transport for control-plane interfaces
- HTTP/2 REST for 5GC Service-Based Interface (SBI) communications

## Deployment Modes

- Co-located: RAN and core on the same network
- Distributed: RAN on a separate host with explicit inter-network routing
- NSA: 4G/5G hybrid using srsRAN
- SA: Pure 5G NR deployment

## Observability

- Metrics collection and visualization via Prometheus and Grafana
- Log aggregation and time-series storage via qryn, Vector, and ClickHouse
- Infrastructure monitoring via Coroot
- SIP capture and call-flow analysis via HEPify Server

## Subscriber Management

- MongoDB stores 5GC subscriber data; MySQL stores IMS subscriber data
- Subscriber provisioning available through a web-based management UI
- Network identity (MCC/MNC) and host addressing are configurable via environment variables

## Constraints

- IPv6 is not supported in the sandbox environment
- The platform has been tested exclusively on Ubuntu 22.04; behavior on other platforms is untested
- Physical radio operation requires Ettus USRP B210 SDR hardware
- No fault injection or chaos engineering framework is included
- No load-testing or traffic-generation tooling is available
