gNBSim is a 5G gNodeB and UE simulator from the Aether/SD-Core project that generates NAS and NGAP signaling to exercise a 5G Core Network end-to-end. It supports multiple configurable test profiles covering the full 3GPP registration, PDU session, and release procedure set. The simulator can run dozens of virtual UEs concurrently, each with its own per-IMSI state machine, and report per-procedure latency and pass/fail outcomes.

## Radio Access and Core Connectivity
- Simulates N2 control-plane signaling between a gNodeB and an AMF using NGAP over SCTP
- Simulates N3 user-plane tunnels between a gNodeB and a UPF using GTP-U
- Sends ICMP echo probes over established GTP-U tunnels to verify end-to-end data-plane connectivity
- Supports single-interface mode (shared IP for N2 and N3) and multi-interface mode (separate IPs requiring secondary network interfaces)

## UE Simulation
- Instantiates configurable pools of virtual UEs, each identified by a unique IMSI, with independent NAS state machines
- Executes standard 3GPP procedures: initial registration, PDU session establishment, UE-initiated deregistration, and service requests
- Supports parallel or sequential UE execution per profile
- Detects per-UE timeout conditions and reports them as failures

## Test Profiles and Automation
- Ships with named built-in profiles covering registration, PDU session, data-plane ping, deregistration, and service request flows
- Supports custom profiles composed of named iteration chains with user-defined step sequences
- Profiles can be enabled or disabled selectively to observe partial-flow behavior
- Optional HTTP API allows runtime profile triggering and step-by-step execution control when step-trigger mode is enabled

## Measurement and Observability
- Records per-transaction and per-procedure latency for each UE
- Produces per-profile pass/fail summary logs and aggregate error reports
- Exposes an optional Go runtime profiling endpoint for CPU and memory analysis

## Fault Injection
- Retransmission mode replays Service Request messages to simulate retry behavior
- Step-trigger mode in custom profiles pauses execution between steps for controlled fault injection via the HTTP API
- Per-UE timeouts treat stalled UEs as failures, simulating partial network outages

## Constraints
- GUTI-based registration is not yet implemented; only IMSI-based registration is supported
- GTP-U echo request/response handling and N2/Xn handover procedures are pending and not available
- Single-interface mode supports only one gNB instance per simulator process due to a fixed user-plane port conflict
- Custom profile iteration blocks are capped at seven actions per iteration
- There is no built-in application-layer traffic generator beyond ICMP echo; iperf or equivalent tools must be introduced separately
- Running profiles cannot be aborted, suspended, or resumed through the HTTP API once started
