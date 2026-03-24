Sysrepo is a YANG-based configuration and operational state data store for Unix/Linux applications. It provides ACID-like transaction guarantees and serves as the backend data layer for management agents such as NETCONF and RESTCONF servers. Applications subscribe to change events and read or write structured configuration data through a shared in-process library with inter-process coordination handled via shared memory.

## Data Store Management

- Four distinct datastores: startup (persists across reboots), running (active configuration), candidate (staging area), and operational (runtime state published by applications)
- Import, export, and edit datastore content using the configuration CLI tool
- Install, remove, and update YANG modules and set per-module permissions using the module management CLI tool
- Default storage backend uses JSON files; MongoDB and Redis backends are available as plugins
- Replay support for stored notifications via the subscription subsystem

## YANG Modeling and Protocols

- Full YANG 1.1 support including schema mount for inline mount points sharing the parent context
- NETCONF (RFC 6241) and RESTCONF (RFC 8040) integration through compatible server projects
- NETCONF Access Control Module (NACM) for user-based access control on datastores
- Subscribed notifications and YANG push supported via standard IETF models
- Custom RPC and event notification definitions supported

## Testing and Measurement

- Performance measurement tool benchmarks common use-cases against large YANG instance data sets
- Unit test suite built on the cmocka framework with optional Valgrind memory analysis
- Code coverage reporting available via CMake build flag using gcov, lcov, and genhtml

## Constraints

- No centralized enforcement of access control; security relies entirely on filesystem permissions, making sysrepo unsafe against malicious local processes that can manipulate shared files
- Native API is C only; Python and C++ bindings are maintained as separate external projects
- Maximum supported path length is 256 characters
- No encryption at rest for stored datastore data and no built-in audit logging capability
- Schema mount inline mount points must share the parent YANG context; cross-context mounts are not supported
- Default permissions block all users except the recovery account from writing data until access is explicitly configured
