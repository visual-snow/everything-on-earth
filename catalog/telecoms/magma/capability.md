# Sandbox Capabilities

Magma is an open-source mobile core network platform providing an evolved packet core (EPC), cloud orchestrator, and federation gateway for 2G/3G/4G and Wi-Fi access networks, with experimental 5G support. It is designed to let operators manage mobile core infrastructure without vendor lock-in using standard commercial radio hardware. The sandbox does not include a built-in RAN, IMS/VoLTE core, or standalone charging system.

## Core Network Functions

- Access Gateway implements the full EPC stack including mobility management, session management, and packet data gateway functions.
- Subscriber records, policy rules, and IP address pools are independently configurable.
- Session policy enforcement and dataplane traffic forwarding are handled by dedicated internal services.
- SMS and HTTP redirect services are available as optional functions.

## Orchestration and Management

- A cloud-hosted orchestrator provides centralized configuration, monitoring, and analytics across one or more gateways.
- A web-based NMS exposes traffic analytics and wireless user dashboards.
- A federation gateway enables integration with an existing operator core via standard 3GPP interfaces.

## Observability

- Gateway health status is continuously monitored and reported.
- User traffic flows and analytics are visible through the orchestrator dashboards.
- Call tracing and event reporting services capture per-session activity.
- Logs can be forwarded to external systems via a log aggregation agent.

## Configuration

- eNodeB configuration is managed through a dedicated daemon.
- Subscriber data and policy rules are stored and served by independent internal databases.
- Orchestrator connectivity is secured with TLS certificates.
- Development and debug modes can be activated via environment variables.

## Operating Modes

- LTE (4G) EPC mode for full evolved packet core operation.
- Federation mode for proxying through to an existing MNO core.
- Carrier Wi-Fi mode for Wi-Fi access network support.
- 5G mode with service-based interfaces is available but experimental.

## Constraints

- No built-in RAN is included — an external eNodeB or gNodeB is required for radio access.
- No standalone HSS is included in the gateway — subscriber federation relies on the federation gateway or a local subscriber store, not a 3GPP-compliant HSS.
- No built-in charging system is provided — billing and charging must be handled by an upstream MNO core via the federation gateway.
- The orchestrator requires a full Kubernetes cluster with supporting databases to operate; it cannot run as a standalone service.
- The access gateway is Linux-only and requires specific kernel and kernel module support; macOS and Windows hosts are not supported.
