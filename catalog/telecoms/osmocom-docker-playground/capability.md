The Osmocom Docker Playground is a containerized test infrastructure for the Osmocom open-source cellular telecommunications stack, covering GSM and UMTS core network components. It provides over 126 container definitions and integrates TTCN3 test suites to validate protocol behavior across signaling and data-plane interfaces. The environment supports both development (bleeding-edge) and stable release tracks, and can run individual test cases in isolation or full multi-config test sweeps.

## Protocol Coverage
- SS7 signaling stack including SIGTRAN, M3UA, and SCCP layers
- GSM and UMTS core network protocols
- SCTP transport
- GTP-U user-plane tunneling for GPRS

## Core Network Components Under Test
- Signaling Transfer Point
- Base Station Controller
- Base Transceiver Station
- Mobile Switching Center
- Media Gateway
- Home Location Register
- GPRS Gateway Support Node
- Serving GPRS Support Node
- Packet Control Unit

## Test Execution
- TTCN3 test suites validate each component against its protocol interface
- Single test case isolation is available to narrow failures to one scenario
- Multi-config runs exercise the same component across several parameter sets

## Performance and Diagnostics
- Kernel-level performance profiling via bpftrace, enabled per test run
- Crash diagnostics with automated backtrace collection through gdb integration
- QEMU-based kernel module validation for userspace-vs-kernel GTP-U comparison

## Configuration and Versioning
- Stack version is selectable between development and stable tracks at run time
- Per-component git branch overrides allow mixing release and pre-release code
- Container rebuilds and remote pulls can each be suppressed independently
- Custom kernel source, branch, and build behavior are fully configurable

## Constraints
- No real radio hardware is present; all air-interface testing is emulated or stub-based
- TTCN3 suite locations are actively being reorganized into a consolidated repository, so suite paths may shift between runs
- Kernel module testing via QEMU is only practical for the GPRS Gateway component and is not generalized across the stack
- There is no fault injection, traffic impairment, or packet loss simulation capability
- No persistent metrics storage or time-series monitoring is available
- HTTP-based layer cache invalidation can produce stale builds when upstream package content changes without a file-size change
