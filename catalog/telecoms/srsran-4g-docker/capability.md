This sandbox provides a complete end-to-end LTE (4G) network running entirely in software, with the radio interface emulated over a message-passing library rather than physical hardware. It comprises three independently running services — an Evolved Packet Core (MME and SPGW), an LTE base station, and a user device — each isolated in its own container and communicating over virtual RF and core networks. The environment is designed for protocol-level experimentation, configuration testing, and fault injection without requiring any radio equipment.

## Radio and Protocol Stack

- LTE 4G air interface emulated over a message-passing library TCP sockets between base station and user device
- S1-MME signaling between base station and core network (MME)
- GTP-U user-plane tunneling between base station and SPGW
- RRC state machine active: device transitions to IDLE after one minute of inactivity and performs random access on next transmission

## Network Configuration

- EPC, base station, and user device each configurable via their respective configuration files
- Subscriber provisioning controlled through a CSV-based IMSI database; additional subscribers added by appending rows
- a message-passing library sample rate fixed at 23.04 Msps, corresponding to a specific LTE channel bandwidth
- Multi-UE operation supported by enabling an optional second user device service and adding a corresponding subscriber entry

## Measurement Capabilities

- UE attachment confirmation and IP address assignment observable after successful registration
- ICMP round-trip latency measurable from core network to user device (typically 20-25 ms over emulated LTE)
- Uplink scheduling latency observable (~20 ms above direct container routing baseline)
- RRC state transitions (connected to idle and back) traceable through log output

## Fault Injection

- Base station exits automatically if the RF link to the user device drops (fail-on-disconnect behavior)
- RRC idle can be triggered deterministically by allowing the data inactivity timer to expire
- Removal of NAT masquerade on the core network interface disrupts user device internet routing

## Constraints

- Requires a Linux kernel with TUN device support and elevated network capabilities; does not run natively on macOS without a Linux virtual machine
- Only the emulated RF backend is configured; no software-defined radio hardware passthrough is available
- User device internet routing through the core network requires manual post-startup commands and is not automated
- No persistent log or configuration storage; configuration changes require rebuilding the container image
- No metrics or monitoring stack included; all observability is through raw process logs
- No 5G NR components; the environment is strictly LTE (4G) only
