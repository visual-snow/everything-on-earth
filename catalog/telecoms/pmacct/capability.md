pmacct is a passive network monitoring suite that collects both data-plane and control-plane telemetry. It ingests IP traffic flows, BGP routing state, BMP monitoring data, and streaming telemetry, then exports to message brokers, SQL databases, or flat files. It does not modify traffic and has no built-in web UI or REST API.

## Data-Plane Collection

- Captures per-flow IP accounting: source and destination host, port, protocol, byte and packet counts
- Collects NetFlow v5/v9, IPFIX, and sFlow v2/v4/v5 from routers and switches
- Captures raw packets via libpcap in promiscuous mode (Linux and cross-platform)
- Captures packets via Linux Netlink NFLOG on Linux hosts
- Classifies traffic by application using deep packet inspection when compiled with the ndpi option
- Enriches flows with GeoIP data when compiled with the geoipv2 option

## Control-Plane Collection

- Acts as a passive iBGP or eBGP neighbor to collect full RIB dumps and real-time update/withdrawal logs
- Collects BMP adjacent-RIB-in data including peer IP, AS path, communities, prefixes, and route distinguisher
- Collects streaming telemetry via TCP, UDP, and gRPC/gNMI using OpenConfig, Cisco, and Huawei YANG models

## Export and Output

- Exports to Apache Kafka and AMQP (RabbitMQ) for downstream processing pipelines
- Writes to MySQL, PostgreSQL, and SQLite3 when the corresponding plugins are compiled in
- Supports in-memory table plugin for interactive CLI queries, suited to prototyping only
- Can re-export captured packets as NetFlow v5/v9, IPFIX, or sFlow via probe plugins
- Replicates incoming flows to third-party collectors via the tee plugin

## Aggregation and Filtering

- Aggregates flows by configurable primitives: source host, destination host, port, protocol, and more
- Applies per-plugin BPF-style filters for selective aggregation
- Correlates data-plane flows with BGP next-hop and AS path from the control plane

## Constraints

- The NFLOG-based daemon is Linux-only; the libpcap-based daemon works cross-platform
- SQL, Kafka, AMQP, Avro, nDPI, ZMQ, and Redis support are all disabled by default and require compile-time flags to enable
- The tee replication plugin cannot run alongside other plugins in the same daemon instance
- The probe and sfprobe export plugins apply only to the libpcap and NFLOG daemons, not to NetFlow or sFlow collector daemons
- gRPC/gNMI streaming telemetry and YANG Push/UDP-Notif each require an external collector dependency compiled in at build time
- There is no native Prometheus or InfluxDB output; Kafka or AMQP are the recommended integration bridges
- No flow deduplication across replicated collectors is provided out of the box
