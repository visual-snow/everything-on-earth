# NetBox Docker — Sandbox Capabilities

NetBox Docker is a community-maintained compose packaging of NetBox, a network source-of-truth application covering IP address management (IPAM) and data-center infrastructure management (DCIM). The stack runs the NetBox web application, a background task worker, a relational database, and two separate cache instances. It does not include TLS termination, metrics export, log aggregation, or pre-loaded seed data.

## Data Modeling and IPAM/DCIM

- Create, read, update, and delete IP prefixes, addresses, VLANs, VRFs, and ASNs
- Model physical and virtual infrastructure: sites, racks, devices, device roles, interfaces, cables, and power feeds
- Manage virtual machines, clusters, and virtual interfaces alongside physical assets
- Organize resources with tenants, tags, and custom fields

## API Access

- Full REST API with CRUD operations across all object types
- GraphQL endpoint available for flexible, query-based data retrieval
- Web UI accessible over HTTP for interactive management
- Automated admin account provisioned on first run via environment variables

## Background Jobs

- Asynchronous job processing for webhooks, custom scripts, and scheduled reports
- Worker liveness monitored independently from the main application

## Integration and Customization

- LDAP authentication available through environment-based configuration
- Override compose pattern allows local customization without modifying base files
- Configuration injected entirely through environment files — no in-container edits required

## Fault Simulation

- Database-unavailable scenario reproducible by stopping the database service; the application returns errors on all data operations
- Job-queue failures observable by stopping the cache/queue service while the worker is running
- Network partitions between services can be simulated by removing the shared internal network

## Constraints

- No port is exposed to the host in the default configuration; external access requires a reverse proxy or a compose override
- The image version tag must match the checked-out repository tag exactly; mismatches cause database migration errors
- No metrics endpoint or Prometheus exporter is included; application health is verified only through internal health checks
- Data is stored in named volumes and is not portable without explicit backup and restore procedures
- The housekeeping scheduler is not included in the default compose file and must be added manually
