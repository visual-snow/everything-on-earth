Icinga 2 is an open-source monitoring framework that can run as a standalone master node or as a satellite agent node connected to a parent master. The environment is fully configured through environment variables at container startup, supporting automated PKI enrollment and cluster federation out of the box.

## Monitoring Checks
- Execute host and service checks using Nagios-compatible monitoring plugins
- Perform ICMP ping checks to test host reachability
- Check SSL certificate validity and expiry dates
- Query PostgreSQL health metrics including connection counts and query performance
- Query MSSQL health metrics via a dedicated health plugin
- Collect network device health metrics via a dedicated network check plugin
- Retrieve structured check output and performance data with exit-code-based severity (OK, WARNING, CRITICAL, UNKNOWN)

## Cluster and Node Management
- Operate as a master node to coordinate a monitoring zone hierarchy
- Operate as an agent node that enrolls with a parent master using a PKI ticket
- Accept command execution and configuration distribution from a parent node
- Define zone names, endpoint addresses, and global zones through environment variables
- Override the node common name and bind address at runtime

## REST API
- Submit passive check results to simulate any host or service state
- Query and manipulate monitoring objects over an authenticated HTTP interface
- Use the API to inject fault conditions without altering container configuration

## Email Notifications
- Send outbound alert notifications over SMTP using a bundled mail transfer agent
- Inject mail transfer agent configuration at runtime through an environment variable

## Constraints
- A persistent volume and a stable hostname are required; without them, node identity and TLS certificates are lost on container restart, breaking cluster trust
- Node setup runs only once per container lifetime; re-enrollment requires a fresh or cleared volume
- Partial mounts inside the data directory will corrupt the symlink structure and render the installation unusable — the full directory tree must exist before mounting sub-paths
- Master and agent nodes must share the same certificate authority, and the cluster communication port must be reachable between them
