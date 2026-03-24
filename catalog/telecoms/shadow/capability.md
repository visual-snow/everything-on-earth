Shadow is a discrete-event network simulator that runs real, unmodified application code as native Linux processes by intercepting system calls and routing them through a virtual simulated network. It is designed to scale to thousands of concurrent network-connected processes while producing deterministic, reproducible results across runs.

## Simulation Engine

- Discrete-event core advances virtual (simulated) time, not wall-clock time
- Intercepts over 150 Linux system calls to integrate processes into the virtual network
- Each simulation run operates on a private, fully isolated virtual network
- Same configuration always produces identical output, enabling reproducible experiments

## Process Execution

- Runs unmodified Linux binaries without recompilation or instrumentation
- Supports multiple virtual hosts within a single simulation, each with its own process tree
- Host and process definitions specify the executable, arguments, and hostname

## Network Support

- Simulates TCP and UDP traffic between virtual hosts
- TLS and HTTP are supported through the intercepted system call layer as used by real applications
- Network topology is specified via a graph; built-in and custom graphs are both supported

## Configuration

- Declarative YAML format controls all simulation parameters
- Network graph, host definitions, and process arguments are all specified in a single file
- Multiple virtual hosts can be co-located in one configuration

## Output and Measurement

- Per-host output directories capture stdout and stderr for each simulated process
- Simulation-wide logs are written to a top-level output directory on completion

## Constraints

- Runs on Linux only; the syscall interposition mechanism is not available on macOS or Windows
- Applications that depend on unsupported or partially implemented syscall behavior may fail or produce incorrect results
- Fault injection capabilities (packet loss, latency, jitter, bandwidth limits) are not confirmed in available documentation
- No built-in GUI, web dashboard, or containerized deployment configuration is provided
