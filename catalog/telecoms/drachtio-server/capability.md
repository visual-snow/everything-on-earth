drachtio-server is a high-performance SIP signaling engine built on the sofia-sip stack, designed to be controlled programmatically by Node.js applications. It handles all SIP protocol mechanics while delegating call logic entirely to application code over a dedicated management connection. The server supports multiple SIP transports simultaneously and exposes optional Prometheus metrics for observability.

## SIP Transport
- Handles SIP over UDP, TCP, TLS, WebSocket, and Secure WebSocket
- Supports multiple simultaneous SIP contacts with independent transports and addresses
- NAT traversal via external IP configuration per contact or globally
- Outbound proxy forwarding for upstream SIP routing

## Application Control
- Inbound mode: application connects to the server and receives SIP events
- Outbound mode: server queries an external HTTP service to route each incoming request, returning reject, redirect, proxy, or route instructions
- Management connection supports shared-secret authentication and TLS

## Observability
- Prometheus scrape endpoint with counters for inbound and outbound SIP requests and responses
- Gauges for active dialogs, registered endpoints, proxied call setups, and connected applications
- Histograms for call answer time and post-dial delay, for both inbound and outbound legs
- Build info and uptime gauges; sofia stack internals exposed as separate metrics

## Deployment Modes
- Daemon mode for background operation
- Cloud-aware mode that auto-resolves local and public IPs from cloud metadata APIs on GCP, AWS, Azure, DigitalOcean, Scaleway, and Exoscale
- Configurable via XML config file, CLI arguments, or environment variables (CLI and env vars take precedence over config file)

## Security
- TLS for both the management listener and SIP transport
- Spammer and scanner rejection by matching User-Agent header values, with reject or silent-discard actions
- SIP timer overrides (T1, T2, T4) and MTU size control to force TCP for oversized UDP packets

## Constraints
- No native media or RTP handling; a separate media server is required for audio and video
- No built-in registration database; registration state must be managed by the application layer
- No built-in clustering or load balancing; horizontal scale requires external orchestration
- Outbound request-handler mode supports HTTP GET only, not POST
- Management port uses TCP or TLS only; plain UDP management connections are not supported
- Wire protocol version 0.9.0 and later is incompatible with older client library versions prior to 5.0.0
