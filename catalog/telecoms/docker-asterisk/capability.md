This sandbox provides a fully functional Asterisk PBX environment configured for residential and small-office VoIP deployments. It bundles the PrivateDial configuration suite, a WebSMS HTTP-to-SMS bridge, and AutoBan intrusion detection, running under a multi-service init scheme with lifecycle hooks for clean startup and shutdown.

## Telephony Engine
- SIP signaling over UDP, TCP, and TLS using the PJSIP channel driver
- RTP and SRTP media with SDES or DTLS key exchange for encrypted audio/video streams
- Support for voice calls, video calls, instant messaging, and voicemail-to-email delivery

## Dialplan and Configuration
- PrivateDial suite provides a pre-built dialplan covering common residential and small-office call flows
- Configuration files are seeded on first start and left untouched on subsequent upgrades, preserving local changes
- Logging verbosity is tunable at runtime through an environment variable

## SMS Gateway
- WebSMS bridge exposes an HTTP API that translates web requests into SIP MESSAGE delivery
- Intended for SIP trunks that do not natively support SIP MESSAGE; can be disabled when not needed

## Security
- AutoBan monitors the Asterisk Manager Interface event stream for repeated authentication failures
- Offending source addresses are blocked at the network layer using nftables rules
- TLS signaling with self-signed or Let's Encrypt certificates; certificates are automatically refreshed before expiry

## Deployment Modes
- Four image variants available: minimal engine only, standard with security and SMS, full with host audio, and extended with all available packages
- Host audio passthrough supported via PulseAudio socket sharing for interactive testing scenarios

## Constraints
- ICE, STUN, and TURN are explicitly out of scope; NAT traversal requiring these mechanisms is not supported
- TLS encrypts signaling hop-by-hop only; end-to-end media encryption depends on SRTP being negotiated by both endpoints
- AutoBan's nftables integration requires elevated Linux capabilities, which may be incompatible with hardened container security policies
- No built-in metrics exporter is available; observability relies on log output and AMI event consumption
- Multi-node clustering and high-availability configurations are not documented or supported
