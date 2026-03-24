my5G-RANTester is a Go-based tool that emulates the control and data planes of 5G user equipment and base stations, enabling stress testing and protocol study against a live or emulated 5G core network. It implements the full NAS/NAS-5GS stack alongside NGAP and GTP-U interfaces, allowing large numbers of virtual UEs to register and attach without any radio channel simulation.

## Operational Modes

- Attach a single UE or a single gNB using static YAML configuration
- Register N UEs sequentially to stress-test core scalability
- Send a configurable number of registration requests per second for a fixed duration to load the AMF
- Measure average per-UE registration latency over a set number of requests
- Continuously probe AMF availability over a configurable time window

## Protocols

- NGAP over SCTP for gNB-to-AMF control plane signaling
- NAS and NAS-5GS for UE mobility and session management
- GTP-U over UDP for user-plane tunnel establishment

## Measurements

- Per-UE registration latency in milliseconds
- AMF response count over a timed interval
- AMF availability status over a timed interval
- Successful UE attach verified by presence of a tunnel interface

## Configuration Surface

- gNB and AMF bind addresses, PLMN list (MCC, MNC, TAC, gNB ID), and network slice descriptors (SST, SD)
- UE SIM credentials (MSIN, KEY, OPC, AMF field, SQN), home PLMN, DNN, and slice descriptor
- Log verbosity level

## Constraints

- The wireless channel is not implemented; the tool tests the 5G core only and cannot simulate radio conditions, handover, or RF interference
- Requires elevated network privileges to create tunnel interfaces for user-plane traffic
- Depends on an externally provided 5G core such as free5GC or Open5GS — no core is bundled
- All UEs in a load test share a single gNB instance; multi-gNB distribution is not supported
- SIM credentials must match subscriber records provisioned in the target core's database
- No HTTP/2 or Service Based Interface support — only RAN-to-core NGAP, NAS, and GTP-U
