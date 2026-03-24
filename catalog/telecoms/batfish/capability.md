# Sandbox Capabilities

Batfish is an offline network configuration analysis tool that builds a vendor-neutral model from device configuration files and performs correctness verification without accessing live devices. It supports routing protocols, ACLs, firewall policies, and compliance checks across multi-vendor topologies. It does not monitor live traffic, connect to real devices, or simulate a live data plane.

## Routing Analysis
- BGP session establishment validity and route advertisement correctness.
- OSPF, IS-IS, EIGRP, and RIP neighbor and propagation correctness.
- Route behavior under single-link or single-device failure scenarios.

## Access Control and Policy
- ACL permit/deny outcome verification for arbitrary source/destination pairs.
- Firewall policy traversal analysis.
- IPsec/VPN and iptables policy parsing and correctness checking.

## Reachability
- Host-to-host and subnet-to-subnet reachability across the modeled topology.
- Service availability analysis under failure conditions.

## Compliance and Drift
- Configuration compliance checking against operator-defined standards (AAA, NTP, logging, SSH, MTU).
- Detection of undefined or unreferenced configuration structures.
- Functional equivalence comparison between two configuration snapshots for change impact analysis.

## Analysis Modes
- Pre-deployment validation against candidate configurations before any push.
- Post-deployment analysis of current production configurations.
- Differential analysis comparing two snapshots to assess change impact.
- Compliance auditing against policy rules.

## Constraints
- Input is always static configuration files — live traffic, packet captures, and real-time telemetry are not supported.
- Analysis is point-in-time only; no continuous monitoring or streaming updates.
- Vendor support for Aruba, Dell Force10, and Foundry is partial — configuration parsing may be incomplete.
- No built-in graphical interface; all queries require Python or the REST API.
