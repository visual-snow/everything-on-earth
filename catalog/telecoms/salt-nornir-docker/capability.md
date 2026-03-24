This environment provides a self-contained SaltStack network automation platform with a Nornir Proxy Minion pre-wired to always-on Cisco DevNet sandbox devices covering IOS-XE, IOS-XR, and NX-OS. All control-plane services — master, REST API, and proxy — run together in a single container, making the stack immediately usable without manual installation or device provisioning.

## Management Protocols

- SSH connectivity via Netmiko, Scrapli, NAPALM, and PyATS drivers
- NETCONF via ncclient and scrapli-netconf
- RESTCONF over HTTPS transport
- REST API via Salt-API (CherryPy)
- CLI access via the salt command-line interface

## Operational Modes

- Full mode: master, API, and proxy all active simultaneously (default)
- Master-only mode: API and proxy disabled, master runs standalone
- Proxy-only mode: proxy connects to an external master

## Observability

- Proxy minion runtime statistics available through the CLI
- Full inventory inspection showing all managed hosts and their connection parameters
- Managed host enumeration and reachability checks
- Minion key management for verifying enrollment state

## Configuration

- SaltStack version, logging level, and proxy minion ID are all environment-variable controlled
- Master, API, and proxy processes can each be independently enabled or disabled at startup
- Nornir host inventory and connection options are defined in pillar files
- External authentication uses a shared-secret username and password

## Constraints

- Single-container design: no multi-node or multi-master clustering is supported
- Pillar changes require a full container restart; hot-reload is not available
- Salt-API runs without TLS by default; HTTPS requires manual reconfiguration
- Managed devices are external Cisco DevNet always-on sandboxes, so task execution depends on third-party network availability
- No built-in fault injection; misconfiguration and connectivity-loss scenarios must be simulated manually
