ONOS (Open Network Operating System) is an open-source SDN controller platform designed to manage both legacy brown-field and modern green-field networks from a single control plane. It provides high availability through clustering, distributed state management, and a pluggable southbound architecture that supports a wide range of network device protocols.

## SDN Control and Flow Management
- Supports proactive flow setup with pre-programmed forwarding rules
- Supports reactive flow setup with on-demand rule installation triggered by packet-in events
- Exposes a northbound intent framework with a global network view, network graph, and application-level intents

## Protocol Support
- OpenFlow, P4Runtime, gNMI, NETCONF, RESTCONF, OVSDB southbound drivers
- BGP interworking with legacy IP networks via the SDN-IP application
- IP-Optical use case modules for multi-layer network control

## Scalability and High Availability
- Clustered multi-node mode with device control sharding for horizontal scalability
- Standalone single-node mode for development and testing
- Distributed state management engine for consistent cluster-wide network view

## Configuration and Management
- Network configuration pushed via REST API using a JSON-based network config subsystem
- CLI available for runtime configuration, debugging, and operational queries
- Graphical UI with multi-layer topology viewing

## Observability
- REST API can be polled for current topology state and installed flow rules
- gNMI southbound support enables device-level telemetry subscriptions
- No built-in streaming telemetry aggregation pipeline

## Constraints
- Southbound protocol support is driver-dependent — not all protocols are available for all device types
- No built-in fault injection or chaos testing framework; cluster failure scenarios require manual network partitioning
- High-availability clustering requires manual cluster formation and explicit node address configuration
- No built-in network traffic measurement or telemetry aggregation pipeline
