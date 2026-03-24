KubeEdge is a CNCF-graduated framework that extends Kubernetes orchestration and device management to resource-constrained edge hosts. It bridges a standard Kubernetes control plane with remote edge nodes through a persistent cloud-edge tunnel, enabling containerized workloads and IoT device state to be managed from a single Kubernetes API surface. Edge nodes continue running their workloads autonomously if the cloud connection is lost.

## Workload Orchestration
- Deploy and lifecycle-manage containerized workloads on edge nodes using standard Kubernetes pod and deployment semantics
- A lightweight kubelet-equivalent agent on each edge node handles local container scheduling, GC, and status reporting
- Node heartbeat and status updates flow back to Kubernetes at configurable intervals (default 15 s heartbeat, 10 s status)
- Supports cloud, edge, EdgeSite (standalone single-node), and high-availability multi-replica deployment modes

## Device Management
- Sync device metadata and live status between edge nodes and the cloud using Kubernetes custom resources
- Device state is cached locally at the edge and queryable by on-node applications without a live cloud connection
- Publish-subscribe messaging between edge devices and applications is handled via an MQTT broker integration

## Cloud-Edge Communication
- Primary tunnel uses an encrypted WebSocket connection initiated outbound from the edge node; QUIC is available as an alternative transport
- A service bridge allows cloud-side components to invoke HTTP servers running at the edge without direct inbound access
- Metadata processed by edge nodes is persisted locally in a lightweight embedded database for offline resilience

## Cluster Bootstrap and Management
- A CLI tool handles initializing the cloud-side components on a Kubernetes cluster and joining edge nodes to the cluster
- TLS certificates are generated during the init and join workflows; ongoing rotation is an operator responsibility
- The number of simultaneously connected edge nodes per cloud-side instance is configurable (default cap of 10)

## Constraints
- Requires an existing Kubernetes cluster; KubeEdge extends Kubernetes and cannot replace it
- Edge nodes must be able to initiate outbound tunnel connections to the cloud; the cloud cannot initiate direct inbound connections to edge nodes without the tunnel
- The embedded local metadata store is not suitable for high-throughput write workloads at the edge
- No built-in observability stack, metrics exporters, or fault-injection framework are included; resilience testing relies on the end-to-end test suite
