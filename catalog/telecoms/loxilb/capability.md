loxilb is an open-source, eBPF-based cloud-native load-balancer written in Go, targeting Kubernetes service-type LoadBalancer for on-prem, public-cloud, and hybrid environments. It is purpose-built for telco and 5G workloads, with native support for protocols such as GTP, SCTP multi-homing, PFCP, NGAP, SRv6, and SEPP. A CLI tool, a REST API server, and a Prometheus metrics endpoint are all included in the distribution.

## Load Balancing

- Distributes traffic across TCP, UDP, SCTP, QUIC, FTP, and TFTP services
- Supports NAT44, NAT66, and NAT64 address translation
- Provides per-LB, per-endpoint, and per-client QoS controls
- Can operate as a Kubernetes service proxy or full kube-proxy replacement
- Supports standalone mode (no Kubernetes required)

## Telco and 5G Protocol Support

- Handles GTP tunnels and PFCP sessions for mobile user-plane workloads
- Supports SCTP multi-homing required by NGAP and other 5G control-plane protocols
- Implements SRv6 segment routing and SEPP inter-PLMN proxy functions
- SIP load balancing is available for IMS and VoLTE traffic

## Routing and High Availability

- Integrates goBGP for dynamic route advertisement and anycast VIP distribution
- BFD-based hitless failover for clustered deployments
- Active and passive endpoint liveness probes detect unhealthy backends
- Cluster mode supports multiple nodes coordinated via a self-annotation index

## Observability

- Exports Prometheus metrics for traffic, connection, and health data
- CPU profiling support for performance analysis
- Extensive endpoint liveness probing in both active and passive modes

## Constraints

- Requires a privileged container running as root to load eBPF programs and manage host network interfaces
- Host kernel must support eBPF; validated on Ubuntu 20.04, 22.04, 24.04, and RedHat 9 — Windows is not supported
- eBPF sockmap L7 acceleration and several advanced options are marked experimental and may not be stable in production
- Kubernetes Network Policy enforcement is not yet implemented
- Multi-cluster support is planned but not yet available
