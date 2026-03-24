# Sandbox Capabilities

Nautobot is a web-based network infrastructure management platform that serves as a Network Source of Truth — a centralized inventory and automation hub for network operations. It provides structured storage for devices, IP space, circuits, racks, and their relationships, exposed through REST and GraphQL APIs. The sandbox does not include any live network devices, telemetry collection, or configuration push capability.

## Inventory and Data Modeling

- Device inventory with site, rack, and role assignments
- IP address management covering prefixes, VLANs, and address utilization
- Circuit and provider tracking with status
- Custom fields and user-defined relationships between any data objects
- Data validation rules for naming standards and object constraints

## API and Integration

- REST API for full CRUD operations on all data models
- GraphQL API for flexible, relationship-aware queries
- Webhook system for outbound HTTP callbacks on data changes
- Git-based loading of YAML configuration contexts into data models

## Automation and Jobs

- Background job execution with scheduling support
- Job and task execution history for auditability
- Change log providing a full audit trail of data modifications
- Plugin system for extending models, APIs, and the UI

## Observability

- Audit trail of all create, update, and delete operations
- Job execution history and status tracking
- IP prefix and VLAN utilization reporting
- Rack utilization tracking

## Constraints

- No built-in device communication — the platform cannot push configuration or poll devices over SSH, SNMP, or any CLI protocol; automation against live devices requires external tools or plugins.
- No telemetry or time-series storage — there is no native mechanism for ingesting or storing streaming metrics or operational state.
- No built-in alerting engine — notifications depend entirely on webhooks delivered to external systems.
- Plugin installation requires an application restart and may require database migrations, making plugin changes a disruptive operation.
- Git integration is limited to loading YAML files as configuration contexts; arbitrary file types are not supported.
