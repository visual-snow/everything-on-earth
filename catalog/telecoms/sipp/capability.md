SIPp is an open-source SIP protocol test tool and traffic generator that drives and receives SIP calls using XML-based scenario definitions. It supports multiple transport modes, optional media playback via PCAP replay, and detailed statistics collection for both load testing and functional validation of SIP equipment.

## Modes

- Originates calls as a User Agent Client
- Receives calls as a User Agent Server
- Originates calls with RTP and RFC 2833 DTMF media replay
- Coordinates third-party call control across two remote endpoints
- Runs as a background daemon with graceful shutdown via signal
- Executes fixed-count regression runs where exit code signals pass or fail

## Protocols

- SIP over UDP, TCP, TLS, and SCTP in single-socket and multi-socket configurations
- IPv4 and IPv6
- RTP media streaming via PCAP file replay
- RFC 2833 DTMF digit delivery over RTP
- Third-party call control

## Measurement

- Call rate, successful and failed call counts, and granular failure reason counters
- Response time distribution with per-timer start and stop markers in scenario files
- Call length distribution with standard deviation
- Per-message sent, received, retransmitted, lost, and unexpected counts
- Configurable statistics snapshot frequency and ring-buffer log rotation
- Structured exit codes that signal all-pass, at least one failure, timeout, or fatal error

## Configuration

- Scenario behavior driven by XML scenario files or built-in scenario names
- Transport mode, call rate, simultaneous call limit, and total call count are all command-line parameters
- Per-call variable injection from CSV files
- TCP reconnect behavior and SCTP multihoming parameters are independently configurable
- TLS certificate validation, certificate revocation list checks, and session key logging are supported
- Multiple trace logs available for statistics, response times, messages, errors, call debug, and screen state

## Fault Injection

- Unexpected mid-call messages trigger automatic CANCEL or BYE based on call state
- UDP retransmission timers follow RFC 3261 with configurable T1 and optional global disable
- TCP disconnect simulation with controlled reconnection attempt limits
- Out-of-call message injection to handle unmatched Call-IDs
- Conditional branching in scenarios to exercise error response paths such as 403 mid-flow
- Regexp-based response validation with scenario branching on mismatch

## Constraints

- A single instance communicates with exactly one remote host; multi-leg scenarios require multiple processes
- PCAP media playback may not function correctly over IPv6
- SCTP transport is not available on Windows
- TLS requires certificate and key files present at startup; missing files prevent the process from starting
- TLS session key logging requires OpenSSL 1.1.1 or later and is not available with the WolfSSL build
- Multi-socket modes are bounded by OS file descriptor limits
- Scenario files must conform to the project DTD; invalid XML causes scenario load failure
