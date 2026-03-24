Pumba is a chaos testing and network emulation CLI tool for container runtimes. It targets running containers by name, name pattern, or label, and injects faults at the network, process, and resource levels. Both one-shot and recurring chaos schedules are supported.

## Fault Injection

- Injects egress network delay with configurable jitter, correlation, and statistical distribution (uniform, normal, Pareto, Pareto-normal)
- Drops egress packets by Bernoulli probability, 4-state Markov model, or Gilbert-Elliot good/bad channel model
- Duplicates or corrupts egress packets by probability
- Limits egress bandwidth in configurable units with optional overhead and cell size parameters
- Drops ingress packets using random or nth-packet matching rules
- Sends signals to container PID 1 (kill), stops, pauses, restarts, or removes containers
- Stresses CPU, memory, and I/O inside a container using the stress-ng utility

## Container Targeting

- Selects containers by exact name, regular expression, or Docker label (Docker runtime only)
- Supports random selection from a matched set each interval
- Applies network chaos to a specific network interface, with optional IP/CIDR and port filters

## Scheduling

- Runs chaos once for a configured duration
- Repeats chaos at a fixed interval with duration shorter than the interval

## Constraints

- Network egress faults use Linux traffic control (netem); ingress faults use iptables — both are required together for bidirectional fault injection
- Network chaos requires the helper container to have NET_ADMIN capability and access to the host Docker socket
- Container filtering by label is available in Docker runtime mode only; containerd mode requires container ID or name
- No built-in metrics export, observability endpoint, web UI, or REST API — CLI only
- No DNS fault injection or HTTP-layer fault injection; operates at L3/L4 only
- No native network chaos support on non-Linux hosts, as netem and iptables are Linux kernel features
