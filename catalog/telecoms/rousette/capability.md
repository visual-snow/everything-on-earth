Rousette is a RESTCONF server (RFC 8040) built on top of sysrepo, providing standards-based HTTP/2 access to YANG-modeled datastores. It supports XML and JSON encoding, NACM access control, and NETCONF notification streams. The server is designed to run behind a reverse proxy that handles TLS termination.

## Protocols and Standards

- RESTCONF over cleartext HTTP/2 (prior-knowledge)
- YANG module library access per RFC 8525
- NMDA datastore operations per RFC 8527
- YANG Patch support per RFC 8072
- NACM access control per RFC 8341
- NETCONF notification streams and IETF Subscribed Notifications per RFC 8639

## Authentication and Access Control

- HTTP Basic authentication via PAM
- Anonymous access mode available when no Authorization header is presented, subject to NACM rules
- NACM rules configured through the ietf-netconf-acm YANG model in sysrepo

## Datastore Operations

- Read and write access to running, candidate, startup, and operational datastores via sysrepo
- YANG Patch for atomic multi-edit operations
- YANG module library introspection endpoint

## Logging and Observability

- Structured logging to stdout, syslog, or systemd journal via spdlog
- Sysrepo operation timeout configurable at startup via CLI flag
- No built-in metrics or health-check endpoint

## Constraints

- TLS termination is not implemented; a reverse proxy is required for HTTPS
- TLS certificate-based client authentication is not supported
- Last-Modified and ETag collision-prevention headers are not implemented
- with-operational-default and with-origin NMDA capabilities are not implemented
- Binds only to the IPv6 loopback address by default; external access requires a reverse proxy
- Requires Linux; PAM integration and test isolation rely on Linux-specific kernel features
- Anonymous access requires carefully ordered NACM rules to function correctly
