Checkmk is an IT monitoring system for infrastructure and application observability across physical, virtual, containerized, and cloud environments. It supports both agent-based and agentless monitoring with over 2000 integrations and auto-discovery. The system provides a web-based UI alongside a REST API and can be deployed in several editions ranging from open-source to multi-tenant managed service.

## Monitoring Coverage

- Host and service state tracking (OK/WARN/CRIT/UNKNOWN) with associated performance data
- Metric time series stored in RRD files with ML-based predictive threshold computation
- Hardware inventory collection for CPU, memory, disk, and network interfaces
- Database metrics for MySQL, PostgreSQL, Oracle, DB2, MongoDB, and SAP HANA
- Container and Kubernetes workload metrics
- Network device metrics via SNMP (v1/v2c/v3)
- Log file monitoring and file integrity/stat monitoring

## Data Collection Methods

- Agent-based TCP pull from monitored hosts
- Push agent mode (Cloud edition — agent initiates connection)
- Agentless SNMP polling
- IPMI for hardware telemetry
- Special agents for vendor APIs (AWS, Azure, GCP, VMware, and others)
- Piggyback relay for hosts that cannot be reached directly
- Active checks for ping, HTTP, TCP, DNS, and certificate validation
- Syslog and SNMP trap ingestion via the event console

## Notification and Alerting

- Notification engine with configurable rule-based routing
- Alert delivery via SMTP using a configurable mail relay host
- Event console for syslog and SNMP trap processing

## Editions

- Raw: open-source, community plugins, single-site
- Enterprise: distributed monitoring, LDAP, automated agent management
- Cloud self-hosted: Kubernetes and major cloud provider integration, OpenTelemetry, push agents
- MSP: multitenancy with isolated customer environments

## Constraints

- Distributed monitoring and LDAP integration require Enterprise edition or higher; Raw edition is single-site only
- OpenTelemetry application metrics ingestion and push agent auto-registration require Cloud edition
- Livestatus TCP access is disabled by default and must be explicitly enabled at startup
- Site name is fixed at creation time and cannot be changed without re-creating the site
- Site data must be persisted to survive restarts; re-creation without a persistent volume resets all configuration
- No native Prometheus scrape endpoint in Raw edition
