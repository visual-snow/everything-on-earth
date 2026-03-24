Cisco YANG Suite is a web-based application for exploring YANG data models and performing network management operations against Cisco devices. It supports NETCONF, RESTCONF, gNMI, and gRPC model-driven telemetry protocols, making it suitable for tasks that require programmatic interaction with Cisco network equipment. The tool is oriented toward operations and exploration rather than simulation or fault injection.

## Protocol Support
- NETCONF over SSH for configuration and state retrieval
- RESTCONF over HTTPS for REST-style model-driven operations
- gNMI in both secure and insecure modes, covering IOS-XE and NX-OS targets
- gRPC model-driven telemetry (MDT) for streaming subscription data from IOS-XE devices

## YANG Model Management
- Browse and navigate YANG data models loaded into the suite
- Diff YANG model versions to identify schema changes between releases
- Load Cisco native YANG models, including large vendor model sets

## Telemetry and Streaming
- Configure and receive gNMI streaming telemetry subscriptions
- Configure and receive gRPC MDT subscriptions from supported devices

## Configuration and Extensibility
- Manage plugins through an admin interface without rebuilding the application
- Customize Django application settings for production deployments
- Automated periodic data backups via configurable cron schedule

## Constraints
- Requires approximately 3.5 GB of memory to load large Cisco native YANG model sets; memory-constrained environments may not support full model exploration
- No device simulator or emulator is included — a real or separately-provisioned Cisco device must be available as a target for NETCONF, RESTCONF, or gNMI operations
- Single superuser model at setup time; no role-based access control for multi-user scenarios
- Self-signed TLS certificates generated during setup are suitable for testing only and must be replaced with CA-signed certificates for production use
