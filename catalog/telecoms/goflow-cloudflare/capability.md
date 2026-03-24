GoFlow is Cloudflare's original network flow collector, written in Go, that receives and decodes flow telemetry from network devices and publishes structured records to Apache Kafka. It supports four major flow export protocols and exposes Prometheus metrics for operational visibility. This is the upstream implementation; the project is unmaintained and the goflow2 fork is the recommended successor.

## Protocol Support
- Receives NetFlow v5, NetFlow v9, IPFIX, and sFlow v5 traffic over UDP
- Handles sFlow sample types including RAW, IPv4, IPv6, Ethernet, Gateway, router, and switch samples
- Manages NetFlow v9 and IPFIX template state, including Option Data Sets for sampling rate tracking

## Decoding and Output
- Decodes raw flow packet payloads into structured records with 40+ fields per flow (source/destination IPs, ports, AS numbers, VLAN IDs, TCP flags, ICMP type/code, MPLS labels, byte and packet counts)
- Publishes decoded records as protobuf messages to Kafka topics via a Go client library
- Falls back to stdout console output when Kafka publishing is disabled

## Operational Modes
- Kafka mode (default): decodes flows and publishes protobuf to Kafka
- Console mode: decodes flows and prints records to stdout without a Kafka dependency
- Individual protocol listeners (NetFlow/IPFIX, sFlow) can be enabled or disabled independently

## Monitoring
- Exposes a Prometheus metrics endpoint covering decode latency, sample rates, payload counters, and NetFlow template tracking
- Worker concurrency is configurable to tune throughput

## Constraints
- Project is unmaintained; the upstream maintainer recommends migrating to the goflow2 fork for ongoing fixes and features
- No built-in flow storage or query capability — an external Kafka consumer is required for any persistence or analysis
- Template state for NetFlow v9 and IPFIX is held in memory; restarting the collector loses all learned templates until exporters re-advertise them
- No TLS support for Kafka connections is documented in the original repository
- Receive-only: the collector cannot export flow data back to network devices and has no replay or pcap ingestion capability
