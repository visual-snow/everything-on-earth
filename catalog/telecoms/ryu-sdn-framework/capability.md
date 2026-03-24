Ryu is a component-based Software Defined Networking framework written in Python that provides well-defined APIs for building network management and control applications. It functions as an OpenFlow controller daemon that developers extend by loading custom application modules, and it supports a broad range of OpenFlow protocol versions alongside ancillary protocols for configuration and routing.

## Protocols

- OpenFlow versions 1.0, 1.2, 1.3, 1.4, and 1.5
- Nicira Extensions to OpenFlow
- NETCONF
- OF-config
- BGP with an interactive SSH console
- Zebra protocol with a SQL database backend

## Operation Modes

- Standalone controller mode running a single application or set of applications
- Component-based application mode where custom Python modules are loaded at launch

## Configuration

- Applications are specified as arguments at controller startup
- NETCONF support is enabled by installing the an SSH library package
- OF-config support is enabled by installing the an XML library and a NETCONF client library packages
- BGP SSH console requires the an SSH library package
- Zebra protocol database backend requires an ORM library

## Notable Absences

- No built-in measurement or telemetry collection
- No fault injection or chaos-testing utilities
- No performance benchmarking tooling
- No built-in high-availability or redundancy mechanisms

## Constraints

- Ryu is unmaintained and actively seeking new maintainers; security fixes and stability patches are not guaranteed
- The framework is Python-only with no compiled controller core, which limits raw packet-processing throughput
- NETCONF and OF-config functionality depend on optional third-party packages not installed by default
