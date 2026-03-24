gNMI Gateway is a distributed, highly available service for connecting to multiple gNMI targets and proxying streaming telemetry subscriptions to downstream consumers. It decouples consumers from direct target connections through a local cache, and supports pluggable target loaders and exporters. The service can run as a single instance or in a coordinated cluster.

## Target Loaders
- JSON file-based loader for static target definitions
- Netbox integration for dynamic target discovery
- Simple file-based loader for lightweight setups

## Exporters
- Debug exporter that logs raw notifications to standard output
- Kafka exporter for real-time gNMI notification streaming
- Prometheus exporter that extracts metric values from OpenConfig paths

## Protocols and Data Models
- gNMI Subscribe RPC over gRPC
- OpenConfig data models for structured telemetry paths
- TLS for all target connections

## Cluster Coordination
- Standalone mode requires no external coordinator
- Clustered mode uses Apache Zookeeper for instance coordination and target locking
- Per-target flags control TLS verification behavior and cluster lock participation

## Constraints
- Pre-release and experimental status — API and behavior may change without notice
- Only the gNMI Subscribe RPC is supported; Get and Set operations are not implemented
- TLS is mandatory per the gNMI specification; plaintext connections are not supported
- Zookeeper timing constraints make geographically distributed deployments impractical
- No built-in time-series storage; metric persistence requires an external Prometheus or Kafka deployment
