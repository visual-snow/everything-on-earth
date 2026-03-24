Clixon is a YANG-based configuration manager that exposes network device configuration through interactive CLI, NETCONF, and RESTCONF interfaces. It couples an embedded XML datastore and a transaction mechanism with auto-generated interfaces derived directly from YANG schema definitions, making it well suited for tasks that require standards-compliant configuration management on network devices.

## Configuration Management
- Read and write device configuration via standard NETCONF get and edit operations
- Manage resources over RESTCONF using HTTP GET, PUT, PATCH, and DELETE against YANG-defined paths
- Work with a dual-datastore model — candidate and running configurations — supporting staged commits
- Interact through an auto-generated CLI whose command tree reflects the loaded YANG models

## Schema and Validation
- Author or load YANG models (RFC 7950) to define the configuration schema before any interface is usable
- Validate configuration changes against YANG constraints before committing to the running datastore
- Use XPath expressions for filtering and querying configuration and state data

## Protocol Support
- Exercise NETCONF (RFC 6241) sessions over SSH for full protocol compliance scenarios
- Exercise RESTCONF (RFC 8040) over HTTP or HTTPS for REST-style configuration workflows
- Encode and decode configuration payloads in XML

## Constraints
- No built-in fault injection or chaos engineering tooling is available; failure scenarios must be simulated externally
- No native streaming telemetry interface (such as gRPC or gNMI) is present; telemetry-focused tasks are out of scope
- A YANG model must be provided before any configuration interface — CLI, NETCONF, or RESTCONF — becomes operational
- The CLIgen library is a required external dependency; CLI functionality is unavailable without it
