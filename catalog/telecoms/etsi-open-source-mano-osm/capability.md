## ETSI Open Source MANO (OSM)

OSM is an ETSI-hosted, Apache-licensed NFV Management and Orchestration stack that implements the ETSI NFV MANO architecture. It orchestrates the full lifecycle of Virtualised Network Functions (VNFs) and Network Services across heterogeneous cloud and container infrastructure. The platform does not include a built-in SDN controller, fault-injection framework, or VNF package validator.

### Orchestration and Lifecycle Management

- Instantiate, scale, heal, and terminate Network Services and VNFs through a SOL005-aligned northbound API
- Allocate compute, network, and storage resources across multiple VIM backends including OpenStack and Kubernetes
- Manage Kubernetes-native network functions using Helm-based packaging

### Configuration Management

- Deliver Day-1 configuration to VNFs via Juju charms attached to descriptors
- Execute Day-2 operational primitives against running VNFs through the northbound API
- Override Helm values at instantiation time for Kubernetes-based network functions
- Enforce multi-tenant access control through role-based project and user scoping

### Monitoring and Policy

- Collect VNF and VIM telemetry and aggregate metrics at the orchestration layer
- Drive autoscaling decisions from threshold-based rules defined in VNF descriptors
- Trigger self-healing workflows automatically or manually via policy enforcement
- Expose orchestration-layer metrics for external scraping

### Fault Simulation (Limited)

- Rebuild or migrate virtual deployment units to exercise failure-recovery workflows
- Manually trigger healing policies to validate self-healing paths
- No native chaos or fault-injection module is included

### Constraints

- Day-2 configuration primitives require outbound access to a Juju controller; environments without this access lose Day-2 capability entirely
- Multi-site WAN stitching requires an external SDN controller; OSM does not bundle one
- Helm v3 is required for Kubernetes network function support; Helm v2 is unsupported
- SOL004 VNF package format validation requires external tooling; OSM does not ship a native validator
- OpenVIM and VMware vCloud Director VIM drivers are deprecated and may be removed in future releases
