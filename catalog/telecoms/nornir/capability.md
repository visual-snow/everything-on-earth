Nornir is a pure-Python, pluggable automation framework for network devices that handles inventory management and concurrent task dispatching across many devices. It exposes no domain-specific language — all automation logic is expressed as ordinary Python functions. An extensible plugin architecture covers connections, runners, and inventory backends.

## Protocols

- SSH and CLI access via connection plugins based on Netmiko, Paramiko, or Scrapli
- NETCONF via Scrapli or NAPALM connection plugins
- RESTCONF via NAPALM or custom HTTP task functions
- gNMI via Scrapli-gNMI or custom plugins
- SNMP via custom task plugins
- HTTP/REST via requests-based task functions

## Inventory Management

- Hosts file defines per-device entries including hostname, platform, groups, and arbitrary data fields
- Groups file holds shared defaults for device families
- Defaults file provides global fallbacks across all hosts
- All inventory values are overridable at runtime through initialization arguments
- Dynamic inventory requires a custom plugin; static file-based inventory is the default

## Execution Modes

- Threaded runner executes tasks across all hosts in parallel with a configurable worker count
- Serial runner executes one host at a time, isolating per-device failures
- Dry-run support is protocol-dependent and delegated to the connection plugin

## Results and Observability

- Each task run returns a structured result object per host containing output, status, and exception details
- Failed-host tracking is available on the aggregated result after any run
- No built-in metrics or timing — instrumentation must be added inside task functions

## Constraints

- Python 3.10 or higher is required; older Python versions are not supported
- All connection and inventory plugins must be installed separately; none are bundled with the core framework since version 3.0.0
- Concurrency is thread-based and subject to the GIL — CPU-heavy tasks do not scale linearly with worker count
- Inventory is static at runtime by default; reflecting live changes requires a custom inventory plugin
- No built-in secret or credential vault integration; external wiring is required
- No built-in test or assertion framework; correctness checks must be written inside task functions
