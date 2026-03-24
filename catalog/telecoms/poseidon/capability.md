Poseidon is an SDN-based network situational awareness tool that uses machine learning to automatically classify devices on a network. It integrates with the FAUCET SDN controller to capture traffic via port mirroring, extract IP header features, and dynamically reconfigure mirroring and apply access control rules based on ML-derived device roles. It exposes Prometheus metrics and a REST API for monitoring and interaction.

## Orchestration and Control
- Core orchestrator coordinates traffic capture, ML classification, and FAUCET reconfiguration
- Standalone mode connects to a separately-managed FAUCET instance; full mode manages FAUCET alongside itself
- Remote deployment mode allows the orchestrator and FAUCET to run on separate hosts

## Traffic Capture
- Captures raw network traffic from a designated collector interface receiving mirrored switch traffic
- Supports centralized mirroring across multiple switches using FAUCET stacking with tunnel VLANs
- Per-host capture files accumulate over time and are used as input to the ML classification pipeline

## ML Classification
- Spawns per-capture ML worker jobs that classify devices based on IP header features
- Periodic re-classification cadence is configurable; a fast polling interval detects new hosts quickly
- Device roles derived from classification can trigger automated ACL application when enabled

## Event and Metrics Integration
- Receives real-time switch events from FAUCET via a message broker bridge
- Tracks event receipt timing via a Prometheus gauge to detect pipeline stalls
- Remote FAUCET configuration is managed over an authenticated gRPC channel

## Constraints
- Requires a FAUCET SDN controller running OpenFlow 1.3; no other SDN controllers are supported
- The collector interface must be up and connected to the switch mirror port before the system starts — hosts will not be detected if the interface is down at startup
- Only one collector interface is supported per instance; mirroring multiple switches requires FAUCET stacking
- Approximately 10 GB of free disk space is required for pcap storage
- TLS certificates for the gRPC config channel must be provisioned before the orchestrator becomes healthy
- No built-in traffic replay or pcap injection mechanism; live traffic from a real or external switch is required
