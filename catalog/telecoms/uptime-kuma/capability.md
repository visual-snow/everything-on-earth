Uptime Kuma is a self-hosted monitoring tool that tracks uptime and latency across a wide range of protocols and services. It provides a reactive web interface, persistent state via an embedded database, and dispatches alerts through more than 90 notification integrations. It serves as a self-hosted alternative to managed uptime services.

## Monitoring Protocols
- HTTP and HTTPS endpoint polling, including keyword match and JSON query variants
- TCP port reachability checks
- WebSocket connection probing
- ICMP ping with round-trip time charting
- DNS record resolution verification
- Docker container health status via socket
- Steam game server query protocol
- Passive push mode where an external agent sends heartbeats to Uptime Kuma

## Measurement Capabilities
- Up/down status per monitor
- Response time in milliseconds with historical charts
- Ping round-trip time with trend visualization
- SSL/TLS certificate expiry countdown
- DNS record resolution results

## Configuration Options
- Per-monitor check interval (default 20 seconds)
- Per-monitor notification channel assignment
- Per-monitor proxy settings
- Two-factor authentication for the web interface
- Custom public status pages with custom domain mapping
- Multi-language locale selection and light/dark UI theme

## Constraints
- Network File System volumes are explicitly unsupported as a data store
- FreeBSD, OpenBSD, NetBSD, Replit, and Heroku are unsupported deployment platforms
- No built-in fault injection or synthetic failure simulation capability
- No native SLA calculation, uptime percentage reporting, or alert history timeline
