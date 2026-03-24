ExaBGP is a pure-Python BGP implementation that exposes a JSON/text API so external programs can inject, withdraw, and inspect BGP routes without touching the FIB. It is used for DDoS mitigation via FlowSpec, anycast management, traffic engineering, and network monitoring.

## Protocols

- BGP with 4-byte ASN support, IPv4/IPv6 unicast and multicast
- MPLS, VPLS, VPNv4/VPNv6 (L3VPN), EVPN, BGP-LS, SRv6, MUP
- FlowSpec (RFC 5575 / RFC 8955) for traffic rate-limiting, discard, and redirect
- Graceful Restart, Enhanced Route Refresh, Add-Path, Extended Next-Hop, AIGP

## Modes

- Server mode: runs the BGP daemon from a configuration file
- CLI mode: interactive interface to a running daemon
- Decode mode: offline parser for raw BGP UPDATE messages
- Healthcheck mode: built-in health probe with automatic route announcement and withdrawal
- Validate mode: checks configuration syntax without starting the daemon

## Measurement and Observation

- Emits JSON-formatted BGP UPDATE messages to stdout, including neighbor, direction, NLRI, and attributes
- Reports BGP session state events via the external process API
- Decode subcommand converts raw BGP UPDATE hex to JSON for offline analysis
- Healthcheck script reports service health and triggers route changes based on probe results

## Configuration

- Single INI-like configuration file; neighbor blocks define peers with AFI/SAFI, ASN, timers, and capabilities
- Process blocks wire external programs to the API via stdin/stdout pipes
- Environment variables override any configuration setting
- Extensive library of example configuration files covering unicast, multicast, L3VPN, EVPN, FlowSpec, BGP-LS, and API patterns

## Fault Injection

- Route announcement and withdrawal via stdin pipe commands to an external process
- FlowSpec rules applied dynamically for traffic manipulation or DDoS mitigation
- Healthcheck-driven route withdrawal on probe failure to simulate failover
- silence-ack API command disables ACK messages for testing programs that do not handle them

## Constraints

- ExaBGP does not manipulate the FIB; a separate dataplane such as FRRouting or the Linux kernel is required if kernel routing table changes are needed
- API communication is exclusively stdin/stdout; external programs must handle or suppress ACK messages, or use the silence-ack option for compatibility with older scripts
- No built-in route reflector or full routing table — ExaBGP is a BGP edge tool, not a full-featured router daemon
- No OSPF, IS-IS, or other IGP support — BGP only
- No NETCONF/YANG or gRPC interface — the API is stdin/stdout JSON/text only
