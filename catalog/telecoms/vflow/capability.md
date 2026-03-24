vFlow is a high-performance network flow collector written in Go that ingests IPFIX, sFlow v5, Netflow v5, and Netflow v9 packets and publishes decoded JSON to a message queue. It is designed for enterprise-scale telemetry pipelines with support for replication, dynamic worker scaling, and Prometheus monitoring.

## Flow Collection

- Collects IPFIX (RFC7011), sFlow v5 raw headers and counters, Netflow v5, and Netflow v9 over UDP
- Each protocol can be independently enabled or disabled via configuration flags
- Per-protocol worker counts are tunable; dynamic worker scaling can be enabled automatically
- Template-based protocols (IPFIX and Netflow v9) cache received templates to disk for persistence across restarts

## Message Queue Integration

- Publishes decoded flow records as JSON to a message queue on per-protocol topics
- Supports Kafka as the default producer, with NSQ, NATS, and raw socket as alternatives
- Producer can be disabled to run in collect-only mode without publishing to a queue

## Mirroring and Replication

- IPFIX packets can be simultaneously replicated to a third-party collector while being processed locally
- Mirror destination is configured via address and port settings

## Monitoring and Statistics

- Exposes a Prometheus metrics endpoint and a RESTful stats API on the same HTTP port
- Per-protocol decode counters are available via the stats endpoint
- Stats format is switchable between Prometheus and RESTful modes

## Load Generation

- Includes a stress generator for producing synthetic flow traffic to test collector throughput

## Constraints

- Requires an external message queue to be running before the collector starts; no built-in queue is provided
- IPFIX and Netflow v9 data records cannot be decoded until the collector has received the corresponding templates; data arriving before templates are cached will be dropped
- UDP packet size defaults to 1500 bytes and must be manually tuned when jumbo frames are in use
- No authentication or encryption is provided on UDP listener ports or the HTTP stats endpoint; access control relies entirely on network-level controls
- IPFIX collection is UDP-only; TCP transport for IPFIX is not supported
