The srsRAN O-RAN SC RIC sandbox provides a containerized Near-RT RIC based on the O-RAN Software Community i-release, deployable without Kubernetes or Helm. It integrates with a srsRAN Project gNB over the E2 interface and ships with example KPM and RC xApps, enabling end-to-end O-RAN control-loop experimentation in a self-contained environment.

## RIC Platform Services

- E2 Termination accepts inbound E2 connections from gNB agents over SCTP
- E2 Manager maintains E2 node state and connection lifecycle
- Subscription Manager handles xApp subscription registration and teardown via REST
- Application Manager oversees xApp deployment and lifecycle events
- Routing Manager Simulator provides static RMR message routing across all services
- Redis-backed Shared Data Layer stores shared RIC state across components

## E2 Service Models

- E2SM-KPM supports Report Styles 1–5 for per-UE and E2-node-level performance metrics
- E2SM-RC enables PRB quota adjustment and handover control via E2 control messages
- E2SM-CCC supports O-RRMPolicyRatio configuration on the E2 node

## Measurement and Observability

- Per-UE downlink and uplink throughput reported via E2SM-KPM subscriptions
- Subscription-based periodic metric reporting triggered by the KPM xApp
- RC xApp logs control outcomes for PRB and handover operations

## Operational Modes

- Monitoring mode: KPM xApp subscribes to periodic reports and prints UE and node metrics
- Control mode: RC xApp sends E2SM-RC messages to adjust radio resource allocation
- Local simulation mode: srsRAN gNB and UE connected over a ZMQ RF link within the sandbox
- Remote E2 agent mode: E2 termination SCTP port can be exposed to accept external gNB connections

## Constraints

- Routing is static only; dynamic routing requires a real Routing Manager with Kubernetes and Helm
- Multi-xApp isolation relies on Subscription ID filtering, not true per-xApp RMR routing isolation
- A 60-second time-to-wait timer is enforced before the RIC accepts E2 agent reconnections after disconnection
- xApp may require a manual restart to correctly receive indication messages after the initial connection
- Locked to O-RAN SC i-release with no documented upgrade path to later releases
- No authentication or security mechanisms are present in this deployment
