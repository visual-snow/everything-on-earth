BMv2 is the reference software switch for the P4 language, designed to interpret compiler-generated JSON files and implement packet-processing pipelines in software. It serves as a development and testing platform for P4 programs written in both P4_14 and P4_16, supporting multiple target architectures. The toolset includes a runtime CLI for table population, a debugger for packet-level inspection, and a nanomsg client for real-time event consumption.

## Switch Targets

- Primary target implementing the v1model architecture for P4_16 programs
- gRPC-enabled variant that supports dynamic module loading at runtime
- Experimental target implementing the PSA architecture
- Example targets demonstrating multicast engine configurations

## Control Plane

- Thrift RPC server for runtime table population and multicast programming
- gRPC interface available through the grpc-enabled variant
- Runtime CLI for interactive table management and multicast group programming

## Observability

- Event logger that broadcasts table hits, misses, and parser transitions over nanomsg IPC
- Integrated debugger for runtime packet-level inspection
- Nanomsg client interface for consuming real-time switch events

## Configuration

- Thrift RPC server port is configurable at launch
- Event logging, the debugger, and dynamic module loading are each individually toggleable via flags
- Switch ports are bound to host network interfaces at startup
- Build-time flags control optional subsystems including gRPC, Thrift, debugging support, and stack features

## Constraints

- Not suitable for production use; throughput and latency are significantly lower than hardware switches
- P4_14 direct registers are not supported
- PSA architecture implementation is experimental and not fully mature
- Variable-length fields wider than 32 bits were only recently introduced
- No auto-generated per-program code, which limits runtime efficiency by design
