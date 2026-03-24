Contiv-VPP is a Kubernetes CNI plugin that uses FD.io Vector Packet Processing as a userspace data plane to deliver high-performance pod networking. It replaces kube-proxy by implementing Kubernetes services and network policies entirely within the VPP engine, using DPDK for fast NIC access. All inter-node traffic travels over configurable overlay transports, with VXLAN as the default and SRv6 as an alternative.

## Networking

- Pod-to-pod, host-to-pod, and external-to-pod connectivity managed entirely in the VPP data plane
- VXLAN overlay for inter-node pod traffic by default; SRv6 segment routing available as an alternative
- TAP interfaces connect pods and the host kernel to VPP; high-speed shared-memory interfaces support pod-to-pod service chaining
- IPv4 and IPv6 both supported
- Dual-NIC mode (one NIC for data plane, one for control) and single-NIC steal-the-NIC mode available

## Kubernetes Integration

- Kubernetes services and network policies enforced inside VPP with no fallback to iptables or kube-proxy
- A Kubernetes State Reflector mirrors the API server state into a dedicated ETCD instance for VPP agent consumption
- A CNI binary forwards pod add and delete requests via gRPC to the VPP switch daemon on each node
- Custom Resource Definitions expose per-node IP and gateway configuration; a CLI tool provides live IPAM and VPP state inspection

## Observability

- REST endpoint on each node exposes VPP agent statistics and debug information
- Telemetry polling interval is configurable and can be disabled
- KVScheduler records a full transaction history with a configurable retention window
- Event history on the agent captures all init-period events permanently; subsequent events are retained by age limit
- Live IPAM assignments and VPP forwarding state are inspectable via the netctl CLI tool

## Configuration

- Inter-node transport, TAP version, MTU, NAT behavior, generic segmentation offload, and packet tracing are set via a central ConfigMap
- Pod, host, node-interconnect, and VXLAN subnets are all independently configurable CIDRs
- NAT session timeouts, idle cleanup, and local endpoint weights are tunable per service
- GoVPP health-check probe intervals, reply timeouts, and retry thresholds are independently configurable
- Ring buffer sizes for TAP interfaces are adjustable per node

## Constraints

- Each node requires a DPDK-compatible NIC dedicated to VPP; that NIC becomes invisible to the Linux host network stack
- Dual-NIC mode requires at least two network interfaces per node
- VPP runs in userspace and requires hugepage memory allocation on the host
- ETCD must remain healthy for VPP agents to receive configuration updates; loss of connectivity stalls control-plane changes
- Pod and overlay IP addresses are derived from node identifiers; reusing or reordering node IDs after removal can cause address conflicts
- MTU defaults to 1450 to account for VXLAN encapsulation overhead; mismatched MTU causes silent packet drops
- Network policies and services are enforced solely inside VPP, so misconfigured rules drop traffic without any Linux-level visibility
