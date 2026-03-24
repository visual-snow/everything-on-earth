The Prometheus SNMP Exporter bridges SNMP-capable network devices and Prometheus by walking OID trees and exposing the results as standard Prometheus metrics. It operates as a proxy: Prometheus sends a scrape request with a target parameter identifying the SNMP device, and the exporter performs the walk and returns the collected metrics. A single exporter instance can serve thousands of devices in multi-target proxy mode, making it suitable for large-scale network monitoring.

## Protocol Support

- SNMPv1 using GETNEXT walk operations
- SNMPv2c using GETBULK walk operations
- SNMPv3 using GETBULK with configurable security levels: no authentication, authentication only, or full authentication and privacy
- UDP transport by default; TCP transport is available as an alternative

## Metric Collection

- OID tree walks are mapped to Prometheus gauge and counter metrics, with SNMP table indexes exposed as labels
- Standard IF-MIB interface metrics are supported, including octet counters, interface descriptions, indexes, names, and aliases
- Counter64 values are automatically wrapped at 2^53 to prevent float64 rounding loss
- Self-monitoring metrics for the exporter itself are available at a dedicated endpoint, covering scrape latency and error counts
- Multiple modules can be collected in a single scrape request with configurable per-module concurrency

## Configuration

- Module definitions specify which OID subtrees to walk along with retry counts, timeouts, and lookup mappings
- Authentication configuration supports separate credential blocks referenced by name, keeping credentials decoupled from module definitions
- Environment variable expansion is available for credential fields, allowing secrets to be injected at runtime without hardcoding
- Per-scrape overrides for authentication, module selection, SNMP context, and engine ID are passed as URL parameters
- TLS and HTTP basic authentication can be applied to all exporter HTTP endpoints via a web configuration file
- MIB-derived configurations are produced offline by a separate generator tool that compiles MIB files into the module configuration format

## Operational Modes

- Single-target mode: one instance handles requests for a specific device
- Multi-target proxy mode: one instance serves many devices via parameterized scrape URLs
- Multi-module mode: multiple module definitions collected in one HTTP request
- Generator mode: offline compilation of MIB files into module configuration (separate binary)

## Fault Tolerance Options

- Permissive OID ordering can be enabled per module to tolerate buggy agents that return out-of-order OID responses
- Maximum repetitions per GETBULK request can be reduced per module to accommodate devices that fail on large bulk requests
- Unconnected UDP socket mode works around multi-homed devices that respond from an unexpected source address

## Constraints

- MIB-derived module configurations must be produced by the generator tool; hand-editing those files is not supported
- Duplicate module or authentication block names in the configuration are invalid and will prevent the exporter from loading
- Counter64 wrap behavior is a global setting and cannot be disabled on a per-module basis
- Overlapping OID walks across modules in a multi-module scrape are not deduplicated, which can multiply traffic to the target device
- SNMPv1 and SNMPv2c community strings are transmitted in plaintext; SNMPv3 is required when confidentiality is needed
- The generator binary requires NetSNMP shared libraries and cannot be built or run as a self-contained binary
- The exporter is poll-only and has no support for receiving SNMP traps or issuing SNMP SET operations
- There are no built-in controls on label cardinality; SNMP tables with unbounded indexes can produce high-cardinality metrics
