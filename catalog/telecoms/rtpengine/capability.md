rtpengine is a high-performance RTP and UDP media proxy designed as a drop-in replacement for rtpproxy, primarily used alongside the the SIP proxy SIP proxy. It supports in-kernel packet forwarding for performance-critical deployments and handles a wide range of media protocols including encrypted and WebRTC traffic.

## Protocols

- RTP and RTCP proxying and forwarding
- SRTP via SDES and DTLS-SRTP for encrypted media
- ICE in relay and lite-peer modes for NAT traversal
- RTCP multiplexing and demultiplexing
- WebSocket (plain and TLS) for WebRTC signaling transport
- T.38 fax over IP
- Legacy rtpproxy protocol and OpenSER mediaproxy protocol

## Forwarding Modes

- Kernel-space forwarding via the a dedicated kernel module kernel module for maximum throughput
- Userspace forwarding as automatic fallback when the kernel module is unavailable
- Media forking in publish-subscribe mode for parallel stream delivery
- Transcoding mode supporting audio codec conversion, DTMF translation, and T.38 conversion
- Recording mode with SRTP decryption for offline analysis

## Configuration

- Configurable UDP port ranges for media streams
- IPv4/IPv6 bridging and per-interface binding
- SRTP cipher selection across AES-CM, AES-F8, and AES-GCM profiles
- RTP profile selection covering AVP, AVPF, SAVP, and SAVPF variants
- ICE mode selection and NAT traversal address advertisement
- TOS/DSCP quality-of-service field settings
- Multi-threaded worker count tuning

## Measurement

- Per-call statistics exposed via the ng control protocol
- RTCP packet inspection and reporting
- Silence detection metrics
- Media recording for offline analysis

## Constraints

- Runs on GNU/Linux only; macOS and Windows are not supported
- ZRTP-encrypted packets pass through unmodified without decryption or inspection
- The kernel module is required to reach maximum forwarding performance; without it the daemon falls back to userspace processing
- Janus protocol compatibility is limited and not fully supported
- No built-in SIP signaling handling; an external SIP proxy such as the SIP proxy is required
