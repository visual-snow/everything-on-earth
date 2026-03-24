The Ligato VPP Agent is a Go-based control and management plane for FD.io VPP (Vector Packet Processor), built on the CN-Infra framework. It translates model-driven northbound API calls — delivered over gRPC, REST, etcd, or Kafka — into VPP Binary API operations via GoVPP. The agent provides transactional configuration, runtime observability, and fault-tolerant state reconciliation for high-performance userspace networking.

## Networking Configuration

- Manage VPP and Linux interfaces (loopback, VETH, TAP, VXLAN, GRE, and others)
- Configure L2 bridge domains, cross-connects, and FIB entries
- Configure L3 routes, ARPs, and proxy ARP ranges on both VPP and Linux
- Apply ACL rules and NAT44/NAT64 policies
- Configure IPsec security associations and security policies
- Configure WireGuard tunnels and Segment Routing policies
- Allocate and reference IP and MAC addresses symbolically via the netalloc plugin
- Configure punt rules, STN (steal-the-NIC) entries, and IPFIX flow export

## Observability and Telemetry

- Export Prometheus metrics for VPP runtime, memory, and node counters via the telemetry plugin
- Query per-node counters and statseg data at configurable polling intervals
- Retrieve KVScheduler transaction history and dependency graph state
- Dump current northbound and southbound state for any object type via REST or agentctl
- Publish interface status updates to etcd or Redis

## Configuration and Management

- Apply full or partial northbound configurations via REST PUT or agentctl update
- Validate configuration before applying it via the REST validation endpoint
- Inspect live agent status, plugin health, and KVScheduler state via agentctl
- Distribute configuration across multiple agents using etcd as the KV store
- Enable API tracing to capture and replay VPP Binary API call sequences

## Fault Injection and Resilience Testing

- Stop VPP independently to test agent recovery and supervisor restart behavior
- Disconnect etcd to simulate KV store unavailability and observe resync behavior
- Trigger KVScheduler full resync to force state reconciliation against live VPP state
- Inspect pending transactions caused by unresolved object dependencies

## Constraints

- The agent requires privileged container capabilities for VPP to access kernel networking resources and hugepages; unprivileged execution is not supported.
- Agent and VPP must share access to the same Unix sockets; they must run in the same process namespace or have the sockets volume-mounted to both.
- For etcd-backed deployments, etcd must be reachable before the agent starts — there is no built-in retry loop beyond the configured dial timeout.
- The DPDK plugin is disabled by default; hardware NIC passthrough requires host-level DPDK configuration and hugepage allocation outside the container.
- KVScheduler enforces strict dependency ordering — objects with unresolved dependencies are held in a pending state, not silently applied or skipped.
- Redis status publishing requires explicit endpoint configuration; it is not included in the default dev image setup.
