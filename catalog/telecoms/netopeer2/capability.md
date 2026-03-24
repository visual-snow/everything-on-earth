# Sandbox Capabilities

Netopeer2 is a NETCONF server and CLI client toolset backed by a sysrepo YANG datastore. It provides a standards-compliant reference implementation of NETCONF for network configuration management tasks. The sandbox does not include traffic generation, fault injection, metrics export, or a web interface — management is exclusively through NETCONF sessions and a command-line client.

## Protocol Support

- NETCONF 1.0 and 1.1
- NETCONF over SSH and TLS transports
- NETCONF Call Home (server-initiated connections to a client)
- NETCONF Event Notifications, including subscription and push models
- NETCONF monitoring and YANG module library introspection

## Configuration Management

- SSH public key and keyboard-interactive authentication
- TLS mutual certificate authentication
- NACM access control rules governing read and execute permissions per user
- Additional YANG modules installable into the datastore at runtime
- Server operates in daemon mode, interactive CLI client mode, or Call Home mode

## Observability

- NETCONF session state inspectable via the IETF NETCONF monitoring YANG module
- Code coverage instrumentation available for test and validation workflows

## Constraints

- TLS transport and Call Home require manual XML configuration and are not active out of the box
- NACM is enabled by default; non-recovery users are restricted to read and execute operations until access control rules are explicitly modified
- No fault injection, network impairment, or load simulation capabilities are present
- No metrics export interfaces — there is no Prometheus endpoint, SNMP agent, or equivalent
