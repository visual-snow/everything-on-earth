OpenKilda is a web-scale Software-Defined Networking (SDN) controller built by Telstra, designed to manage tens of thousands of OpenFlow switches simultaneously and control millions of flows. It uses a distributed processing architecture built on Apache Kafka and Apache Storm, with a graph database for topology and flow state persistence.

## Switch and Flow Control
- Manages OpenFlow switches using dual Floodlight controller instances
- Programs flow rules across the network via the OpenFlow protocol
- Maintains flow-level statistics collection across all managed devices

## Topology and Path Computation
- Stores network topology and flow state in a graph database
- Computes routes using a dedicated Path Computation Engine with configurable cost functions
- Supports flow groups for backup route diversity across multiple paths
- Recalculates paths automatically in response to hardware change events

## Configuration Management
- Applies service configuration using template-based management with YAML variable files
- Operates in multi-table pipeline mode by default
- Supports blue-green deployment configuration for zero-downtime controller upgrades
- Enables remote debug configuration via JDWP

## Monitoring and Telemetry
- Collects sub-second network metrics and visualizes them through a built-in reporting component
- Supports traffic mirroring and data gathering for flow-level analysis
- Provides a REST API and web GUI for programmatic and manual network management

## Fault Injection and Testing
- Creates virtual topologies in test mode to simulate switch and link failures
- Validates failover behavior using flow groups with pre-configured backup routes

## Constraints
- Requires Linux kernel 4.18 or later for Open vSwitch meters support
- Requires Open vSwitch 2.9 or later
- Single-table switch mode is deprecated since release 1.126.2; new features are available in multi-table mode only
- Scale is validated up to tens of thousands of switches; behavior beyond that boundary is not documented
