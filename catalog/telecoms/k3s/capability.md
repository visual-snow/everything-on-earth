K3s is a fully conformant, production-ready Kubernetes distribution packaged as a single binary under 100 MB, designed for edge, IoT, CI/CD, and embedded environments. It reduces the memory footprint of upstream Kubernetes by roughly half by consolidating control-plane components, removing in-tree cloud and storage drivers, and defaulting to SQLite as the datastore. The distribution bundles everything needed to run a complete cluster — networking, ingress, DNS, storage provisioning, and load balancing — without requiring external tooling.

## Cluster Topology

- Operates in two modes: server mode runs the full control plane alongside a local agent, while agent mode registers a worker-only node against a remote server
- Multi-node clusters are formed by pointing agents at the server address and supplying a shared join token
- TLS certificates for all cluster communication are generated and managed automatically

## Networking

- Flannel provides pod-to-pod overlay networking across nodes
- Kube-router enforces Kubernetes network policies
- Traefik serves as the default ingress controller for HTTP and HTTPS traffic
- Klipper-lb fulfills LoadBalancer-type service requests without an external cloud provider
- CoreDNS handles in-cluster service discovery and DNS resolution

## Storage and Data

- Local-path-provisioner supplies dynamic persistent volume provisioning backed by node-local storage
- The datastore backend is selectable: SQLite (default), etcd, MariaDB, MySQL, or PostgreSQL
- Kine abstracts the datastore interface so non-etcd backends appear as etcd to the control plane

## Observability

- Metrics Server collects in-cluster CPU and memory resource metrics for pods and nodes
- Resource metrics are accessible through the standard Kubernetes metrics API

## Configuration

- Cluster join credentials are passed via environment variables shared between server and agent nodes
- Bundled components such as Flannel, Traefik, and CoreDNS can individually be disabled or replaced
- Kubernetes manifests placed in a designated local directory are applied automatically at startup
- System limits for open files and processes are raised to 65535

## Constraints

- Running K3s inside a container requires privileged mode and tmpfs mounts for runtime directories
- In-tree cloud provider and storage drivers are absent; out-of-tree Container Storage Interface and Cloud Controller Manager alternatives must be used instead
- The join token must be distributed to agent nodes through a separate, secure channel before cluster formation
- Inter-node traffic is not encrypted by default; network encryption requires an additional overlay configuration
- No built-in fault injection or chaos engineering primitives are included
