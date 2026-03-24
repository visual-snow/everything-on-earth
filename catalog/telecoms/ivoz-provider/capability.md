IVOZ Provider is a multitenant VoIP telephony platform that pairs a SIP proxy and media relay engine with a full PBX application server, enabling operators to deliver hosted telephony across multiple brands and companies from a single deployment. The platform exposes a REST API and a layered set of web portals — one each for platform administrators, brand administrators, company administrators, and end users — backed by a relational database and an in-memory cache.

## Telephony and Signaling

- Handles SIP call routing, registration, and media relay for voice traffic
- Supports WebRTC in addition to conventional SIP endpoints
- PBX functionality (dial plans, IVR, call queues) is provided through an application server with a FastAGI interface

## Administration and Configuration

- Four-tier admin hierarchy: platform admin, brand admin, company admin, end user
- Each tier operates through its own dedicated web portal
- REST API available for programmatic provisioning and management

## Deployment Modes

- Can run with all components on a single machine or distributed across multiple machines
- Suitable for cloud or public-network deployments with appropriate network configuration

## Observability

- Health checks are defined for database and cache services
- No built-in metrics export or monitoring stack is included; external observability tooling must be added separately

## Constraints

- No metrics or observability stack is bundled — Prometheus, Grafana, or equivalent must be integrated independently
- No fault injection or traffic-generation tooling is included in the development environment
- Containers have no restart policies configured and will not auto-recover from crashes without additional orchestration
- No resource limits are applied to any service, so runaway processes can exhaust host memory or CPU unchecked
- The backend service has a 120-second startup delay before it reports healthy, which can slow automated pipeline runs
