FreeSWITCH is a software-defined telecom stack that replaces proprietary switching hardware with a flexible software implementation. It supports voice, video, and messaging workloads across a wide range of protocols and deployment scales. Its modular architecture allows individual codecs, endpoints, and application modules to be loaded at runtime without restarting the core engine.

## Protocols

- SIP (Session Initiation Protocol) for call signaling
- RTP and SRTP for media transport with optional encryption
- WebRTC for browser-based real-time communication
- MRCP for media resource control (speech recognition, TTS integration)
- SMS for text messaging

## Operating Modes

- Back-to-back user agent (B2BUA) — default SIP call handling mode
- SIP proxy mode for pass-through signaling
- Conference bridge mode for multi-party audio
- Interactive voice response (IVR) mode via the dialplan tools module
- Voicemail server mode

## Configuration

- XML-based configuration files govern all core and module settings
- Dialplan routing is defined in XML or via Lua and JavaScript scripts
- Each loadable module has its own configuration file
- Runtime reconfiguration is possible through the Event Socket Library without a restart
- Deployable via native packages on Debian and CentOS, or compiled from source

## Measurement and Observability

- Event Socket interface streams real-time call events and statistics to external consumers
- Call detail records written by dedicated CDR modules (CSV and SQLite backends available)
- SNMP monitoring available through an optional module

## Constraints

- No containerization manifests are included in the upstream repository; any container-based deployment requires user-supplied configuration
- Windows support lags behind Linux in feature parity and community testing coverage
- Cloud connectivity features require a valid SignalWire account token; they are unavailable in fully offline environments
- No built-in fault injection or chaos testing tooling is provided
