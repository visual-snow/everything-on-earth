OpenSIPS IMS Community Edition is a 3GPP-compliant IP Multimedia Subsystem stack built on OpenSIPS, providing a complete Proxy, Interrogating, and Serving CSCF chain for VoLTE SIP signaling. It integrates with an Open5GS 4G Evolved Packet Core and includes a Python-based Home Subscriber Server, a media relay engine, and an SMS-over-IMS path. The environment can be deployed as a standalone IMS layer dropped into an existing 4G core, or as a full-stack setup with the embedded EPC included.

## IMS Signaling

- Full P-CSCF, I-CSCF, and S-CSCF chain handling SIP registration, authentication, and session routing per 3GPP TS 124 228
- NAT traversal and security association management at the P-CSCF entry point
- HSS-CSCF interaction over Diameter Cx for user authentication and registration data
- HSS-AS interaction over Diameter Sh for supplementary service data

## Media Handling

- RTP and SRTP media relay with transcoding support via the integrated media relay engine
- Configurable UDP port range for media streams

## Subscriber Management

- REST API on the Python HSS for querying and modifying subscriber records and session state
- Web UI for subscriber provisioning backed by the Open5GS subscriber store
- MySQL database for IMS routing and subscriber data; MongoDB for Open5GS subscriber records

## Observability

- Prometheus metrics endpoint exposed by a dedicated metrics service
- Grafana dashboards for real-time visualization of IMS and EPC metrics
- Centralized log volume shared across all services for unified log inspection

## SMS Path

- SMS-over-IMS routing through OsmoMSC, OsmoHLR, and a Kamailio SMSC gateway
- SMPP interface available for external SMS gateway integration

## 4G Core (Full-Stack Mode)

- MME, SMF, UPF, SGW-C/U, and PCRF components forming a complete 4G EPC
- GTP-U user-plane and GTP-C control-plane tunneling
- S1-MME interface over SCTP; PCRF policy control over Diameter Gx

## Constraints

- Requires elevated kernel capabilities (NET_ADMIN) for the P-CSCF, user-plane function, and media relay engine; not compatible with unprivileged sandbox environments
- No built-in fault injection or chaos engineering tooling; resilience and failure-mode testing depends entirely on external tools
- The Open5GS EPC depends on a custom base image that must be built locally before first use, adding setup overhead
- All 24 services share a single flat internal subnet with no network segmentation between the IMS and core planes
- No 5G standalone core integration; only the 4G non-standalone path is supported
- No call-detail-record or billing interface; Diameter Rf and Ro are absent
