# Sandbox Capabilities

The sandbox is a containerized Zabbix monitoring stack — a platform that collects metrics from hosts, processes SNMP traps, and exposes a web-based management interface. It includes a monitoring server, web UI, collection agents, proxies, a Java gateway, and an SNMP trap receiver. No pre-configured dashboards, alerting rules, or discovery policies are included — all monitoring configuration must be defined after the stack is running.

## Deployment Modes
- Minimal: server and database only — the default starting point.
- Full: all Zabbix components active, including agents, proxies, and the web reporting service.
- Extended: full stack plus supplementary tooling.
- Kubernetes: a manifest is available for orchestrated deployment outside of Compose.

## Monitoring Protocols
- SNMP v1/v2c/v3 polling and trap reception are supported.
- IPMI is available for hardware-level monitoring.
- JMX is supported via the Java gateway for Java application monitoring.
- HTTP checks are available for synthetic endpoint monitoring.

## Configuration
- Database backend is selectable: MySQL or PostgreSQL.
- Web server is selectable: Apache or Nginx.
- OS base image is selectable: Alpine, Ubuntu, CentOS, or Oracle Linux.
- Credentials are supplied through environment variable files, not hardcoded defaults.
- IPv6 network support is toggleable via environment variables.
- Each component — agent, proxy, server — is configured independently.

## Data Collection
- Agents collect host-level metrics from monitored targets.
- Agent2 provides an extended collection capability with additional plugin support.
- Proxies allow distributed data collection from remote network segments.
- SNMP trap receiver captures asynchronous device notifications.

## Constraints
- No pre-built dashboards or alerting rules — the web UI starts empty and must be configured manually before any monitoring is operational.
- The default Compose profile starts only the server and database; all other components must be explicitly activated via profile selection.
- No native Prometheus or OpenMetrics scraping endpoint is exposed by the server.
- No built-in TLS termination — encrypted external access requires a separately configured reverse proxy.
- Versions 7.0 and later are licensed under AGPLv3; commercial deployments require a support agreement with Zabbix LLC.
