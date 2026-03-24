The SONATA MANO Framework is a microservices-based NFV orchestration platform that manages the full lifecycle of network services and virtual network functions across heterogeneous virtualization infrastructures. It serves as the MANO core of the SONATA/5GTANGO service platform, coordinating end-to-end service workflows through a set of loosely coupled, message-driven components. All inter-component communication is handled asynchronously over a RabbitMQ message broker.

## Orchestration Components

- Service Lifecycle Management handles end-to-end service workflow orchestration
- Function Lifecycle Management manages VNF-level orchestration independently
- Specific Manager Registry acts as the registry and dispatcher for runtime customization plugins
- Service-Specific Managers enable per-service behavior customization injected at runtime
- Function-Specific Managers enable per-VNF behavior customization injected at runtime
- Placement Plugin computes resource allocation and optimization decisions

## Supported Lifecycle Modes

- Service instantiation across connected virtualization infrastructure
- Horizontal scaling of running services
- Service migration between infrastructure targets
- Controlled service termination

## VIM Backend Options

- Local emulation backend available for development and testing scenarios
- OpenStack backend supported for production virtual machine workloads
- Kubernetes backend supported for containerized network function deployments

## Data Persistence

- Orchestration state backed by MongoDB
- Service and function descriptors managed through the SONATA Catalogue
- Instantiation records stored in the SONATA Repository

## Constraints

- RabbitMQ must be running before any component can communicate; the entire platform is inoperable without it
- Service-Specific Managers and Function-Specific Managers must be registered with the registry before they can be invoked during lifecycle events
- No built-in monitoring or telemetry pipeline is provided; external tooling is required for metrics collection
- Placement optimization is entirely plugin-driven; no default multi-constraint optimizer is included out of the box
