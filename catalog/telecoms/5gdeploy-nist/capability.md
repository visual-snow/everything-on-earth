5gdeploy is a TypeScript/Node.js toolkit developed at NIST for emulating 5G standalone networks. It converts a JSON network-definition document (NetDef) into a fully-configured deployment with interchangeable Control Plane, User Plane, and RAN implementations. The environment supports end-to-end data path testing, traffic generation, fault injection, and metrics collection across a range of open-source 5G components.

## Network Definition and Topology

- Define network topology, slices, subscribers, and data networks in a single JSON NetDef document
- Select from pre-built scenario scripts covering cloud/edge, multi-slice, and multi-UPF topologies
- Deploy all network functions on a single host or distribute them across multiple machines via VXLAN bridges

## Control Plane, User Plane, and RAN Selection

- Control Plane implementations available: free5GC, OAI, Open5GS, Phoenix
- User Plane implementations available: free5GC UPF, eUPF, NDN-DPDK UPF, OAI, Open5GCore, Phoenix
- RAN simulators available: UERANSIM, PacketRusher, OMEC-gNBSim, OAI, srsRAN; core-only mode available for physical gNBs

## Deployment Modes

- Signaling-only mode: UE registration without PDU sessions (OMEC-gNBSim, PacketRusher)
- Full PDU session mode: end-to-end data plane with UE simulators (UERANSIM, PacketRusher, OAI, srsRAN)
- Multi-host mode: network functions distributed across machines using VXLAN bridging

## Traffic Generation and Measurement

- Throughput and latency measurement via iperf2, iperf3, netperf, sockperf, and D-ITG
- One-way and two-way active measurement via OWAMP/TWAMP
- UE reachability scanning and PDU session enumeration
- Per-container interface RX/TX counters via linkstat
- Prometheus and Grafana metrics for supported CP/UP implementations

## Fault Injection

- Apply tc-netem impairments (delay, loss, jitter, reorder, corrupt) to any named network segment between matched containers
- Mark packets with specific DSCP values to test QoS-differentiated forwarding behavior

## Supported Protocols

- 5G NR, GTP, GTP-U, NAS, NGAP, N4/PFCP, SBI, SCTP, NDN (via NDN-DPDK UPF)

## Constraints

- Maximum 253 network functions per deployment; maximum 64 virtual networks per deployment
- Only one scenario may run at a time on a host; other running scenarios must be shut down first
- QoS options (DSCP marking and netem impairment) are supported only on free5GC UPF, Open5GCore gNB and UPF, PacketRusher gNB, and UERANSIM gNB
- NDN-DPDK UPF requires DPDK-compatible hardware
- No Kubernetes or Helm support; deployment is Docker Compose only
- No built-in IPv6 UE data plane support
- Netem impairment rules are static at compose generation time; no automated fault injection scheduling
- Project is not under active development; only occasional maintenance updates are expected
