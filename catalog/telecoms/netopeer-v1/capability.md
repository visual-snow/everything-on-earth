Netopeer (v1) is the first-generation NETCONF Protocol Toolset developed by CESNET, built on the a NETCONF library library. It provides a server daemon, an interactive CLI client, and tooling for managing transAPI modules on NETCONF-enabled devices. This toolset is deprecated in favour of its successor, Netopeer2.

## Server and Client

- NETCONF server daemon that operates in daemon or foreground verbose mode
- Interactive CLI client for connecting to and issuing RPCs against NETCONF-enabled devices
- SSH transport enabled by default; TLS transport available only when enabled at compile time

## Protocol Support

- NETCONF v1.0 and v1.1 with Chunked Framing Mechanism (RFC 6241)
- NETCONF over SSH (RFC 6242) and NETCONF over TLS (draft standard)
- NETCONF Event Notifications (RFC 5277, RFC 6470)
- NETCONF Access Control / NACM (RFC 6536)
- NETCONF Call Home via Reverse SSH and TLS variants
- YANG data modelling (RFC 6020) processed through a YANG validation tool

## Module Management

- Module manager for adding, removing, enabling, and disabling transAPI modules at runtime
- First-run configurator with a text UI for setting up access control and module paths
- Bundled transAPI modules implementing the ietf-system data model and network interface management
- Per-module XML datastore files for persistent configuration state

## Access Control

- NACM default-write-action configurable; writes are blocked by default until explicitly relaxed
- Per-user unlimited-access grants configurable through the first-run configurator
- NACM denial of writes can be used to simulate access-control fault conditions

## Fault Injection

- No dedicated fault-injection facility; malformed or rejected RPCs sent via the CLI client test server error handling
- NACM write-denial configuration simulates access-control fault scenarios

## Observability

- No built-in metrics or telemetry export; server exposes configuration datastores only
- Logging verbosity adjustable across four levels: errors, warnings, verbose, and debug

## Constraints

- No longer maintained; migration to Netopeer2 is recommended by the original authors
- TLS support must be enabled at compile time and is not active in the provided build configuration
- NACM blocks all write operations by default and must be explicitly relaxed before configuration changes take effect
- No RESTCONF, gNMI, or gRPC interfaces are available; the toolset is NETCONF-only
- Requires specific minimum versions of a NETCONF library, an SSH library, a YANG validation tool, Python, and a configuration editing library at build time
- The graphical management interface is a separate project and is not included in this sandbox
