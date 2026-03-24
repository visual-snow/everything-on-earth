Aether SD-Core is an open-source 5G standalone core network developed under the Open Networking Foundation and Linux Foundation Aether platform. It provides a full suite of both control plane and user plane functions, deployed through Kubernetes Helm charts and integrated with the Aether-OnRamp framework for end-to-end 5G packet forwarding. Only 5G Standalone mode is supported; no 4G-anchor or Non-Standalone mode is available.

## Control Plane Functions

- Access and Mobility Management Function handles UE registration, authentication coordination, and mobility procedures
- Session Management Function manages PDU session establishment and lifecycle
- Network Repository Function provides service discovery and registration for all network functions
- Policy Control Function enforces per-session and per-slice policy rules
- Authentication Server Function processes EAP-AKA and 5G-AKA authentication
- Unified Data Management and Unified Data Repository store subscriber profiles and credentials
- Network Slice Selection Function selects appropriate network slices based on UE requests

## User Plane

- User Plane Function performs GTP-U encapsulation and packet forwarding on the N3 and N6 interfaces
- Supports DPDK and hugepage configuration for high-performance data-plane operation
- Static IP address pools are configurable for UE address management

## Subscriber Provisioning

- Web UI provides a graphical interface for adding and managing subscriber records
- Subscriber provisioning service exposes an API for programmatic subscriber management
- Network slice parameters, including slice type and differentiator values, are configurable at provisioning time

## Protocols Supported

- NAS over N1 for UE-to-core signaling
- NGAP over SCTP on the N2 interface for RAN-to-AMF communication
- PFCP between SMF and UPF for session control
- GTP-U on N3 for user plane tunneling
- HTTP/2 REST service-based interfaces between all core network functions

## Deployment Modes

- Kubernetes-only deployment via Helm charts; no compose-based alternative is provided
- Aether-OnRamp managed deployment for guided setup at enterprise or edge sites
- Per-interface IP address overrides required for N2, N3, and N6 network attachment

## Constraints

- A Kubernetes cluster with macvlan or equivalent CNI support is required; high-performance UPF additionally requires SR-IOV or DPDK-capable hardware
- Default Helm values do not produce a functional deployment without operator-supplied IP address and network interface configuration
- No fault injection or chaos-engineering tooling is included in the project
- No built-in observability stack is bundled; Prometheus and Grafana integration is not confirmed in available documentation
- No RAN simulator is included; an external gNB simulator must be provided separately
