The QUIC Network Simulator is an ns-3-based test framework that evaluates QUIC protocol implementations by routing traffic between client and server endpoints through a simulated network. It enables controlled measurement of QUIC behavior under configurable link conditions including bandwidth, delay, and queue depth. Traffic is isolated across two separate internal networks, with each run producing logs for post-run analysis.

## Network Scenarios

- Point-to-point link with configurable bandwidth, delay, and queue size (simple-p2p)
- Point-to-point link with a competing TCP cross-traffic flow (tcp-cross-traffic)

## Link Condition Controls

- Bandwidth cap to simulate constrained or congested links
- One-way delay to simulate high-latency paths
- Queue depth to induce packet drops under saturation

## Fault Injection

- TCP cross-traffic competing with QUIC flows to simulate realistic congestion
- Queue saturation via reduced queue depth to trigger packet loss
- Artificial bandwidth and delay parameters to stress protocol behavior

## Protocol Support

- QUIC (primary focus)
- UDP and IPv4 as underlying transport and network layers
- IPv6 enabled across the topology
- TCP supported in the cross-traffic scenario only

## Logging and Observability

- Per-service logs written for the simulator, server, and client after each run
- All logs available for offline analysis; no real-time measurement tooling is included

## Constraints

- Client and server must be pre-built images conforming to the quic-interop-runner interface; arbitrary binaries cannot be used directly
- Only two scenarios are provided out of the box; additional scenarios require writing ns-3 C++ code and rebuilding the simulator image
- Network topology is fixed to a single bottleneck link; multi-path and multi-hop topologies are not supported
- No packet-loss rate or jitter parameters are exposed in the documented scenarios
- No built-in traffic capture, pcap export, or throughput measurement tooling is included
