LiveKit SIP is a SIP-to-WebRTC bridge that connects telephony networks to LiveKit rooms via SIP trunking. It runs alongside a LiveKit server instance, enabling standard phone callers to participate in real-time audio rooms as full room participants. The service uses Redis for session state and inter-service coordination between the SIP bridge and the LiveKit server.

## Inbound Calls
- Accepts incoming SIP INVITE requests from external telephony endpoints
- Routes callers into LiveKit rooms according to configurable SIP Dispatch Rules
- Dispatch Rules must be provisioned via the LiveKit server API before inbound routing is active

## Outbound Calls
- Sends SIP INVITE requests to external SIP endpoints
- Outbound SIP Trunks must be configured via the LiveKit server API before use

## Protocol Support
- Speaks SIP for call signaling and RTP for media transport
- Supports DTMF tone signaling via RFC 2833
- Encodes audio using the Opus codec

## Authentication
- Supports SIP Digest Authentication for trunk-level credential validation

## Observability
- Exposes a Prometheus metrics endpoint for operational monitoring
- Provides an HTTP health check endpoint for liveness probing
- Supports configurable log verbosity levels

## Constraints
- Requires a publicly reachable IP address so remote SIP peers can initiate connections; deployments behind NAT must enable the external IP discovery setting
- Redis must be the same shared instance used by the LiveKit server — a separate Redis instance will break session coordination
- SIP Trunks and SIP Dispatch Rules must be provisioned before any calls can be routed; the service has no built-in default routing
- Audio only — no video support; the bridge does not transcode video media
- No built-in SRTP or TLS transport security for SIP signaling
