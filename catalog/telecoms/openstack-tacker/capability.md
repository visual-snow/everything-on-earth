OpenStack Tacker is an NFV Orchestrator service that follows the ETSI MANO Architectural Framework for deploying and operating Virtual Network Functions. It provides end-to-end lifecycle management for VNFs running on OpenStack or Kubernetes infrastructure. The service exposes a REST API aligned with ETSI MANO NFV Orchestration standards and integrates with core OpenStack services for compute, networking, and orchestration.

## Orchestration
- Deploy, update, and terminate VNFs through the NFV Orchestration API
- Manage VNF lifecycle states including instantiation, scaling, healing, and termination
- Coordinate with OpenStack Heat for stack-based resource provisioning

## Infrastructure Targets
- Use OpenStack as a VIM for VNF workload placement
- Use Kubernetes as an alternative VIM for containerized VNF deployments
- Query and register VIM credentials for multi-site orchestration

## Management Interfaces
- Issue commands through the CLI client for all orchestration operations
- Interact with the Horizon web UI plugin for browser-based VNF management
- Authenticate and authorize all API calls via Keystone integration

## Deployment Modes
- Run in all-in-one mode with a full Devstack stack on a single machine
- Run in standalone mode with only the mandatory OpenStack services, suitable for CI environments

## Constraints
- Requires a minimum of 4 CPU cores, 16 GB RAM, and 80 GB storage
- Supported only on Ubuntu LTS; only the two most recent Ubuntu LTS releases are supported by Devstack
- Kubernetes VIM support is limited to Ubuntu host environments
- No built-in metrics collection or fault injection — external OpenStack telemetry services are needed for observability
