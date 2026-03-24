ElastiFlow is a network flow data collection and visualization platform built on the Elastic Stack that ingests telemetry from routers, switches, and other network devices. It processes flow records into searchable indices and surfaces traffic patterns through pre-built dashboards, making it suitable for network operations, capacity planning, and threat investigation tasks.

## Flow Protocol Support
- NetFlow v5 and v9
- sFlow
- IPFIX, including Ziften ZFlow IPFIX records

## Traffic Measurement and Analysis
- Top talkers by source and destination
- Flow conversations between host pairs
- Service and application classification
- Autonomous System (AS) traffic breakdown
- Geographic IP distribution via GeoLite2
- Traffic locality patterns (internal vs. external)
- IP reputation and threat detection

## Platform Components
- Elasticsearch for data storage and indexing
- Logstash as the flow data processing pipeline
- Kibana for dashboards and visualization

## Operating Modes
- Legacy open-source mode targeting Elastic Stack 6.x/7.x (Logstash-based, deprecated)
- Current commercial mode via the ElastiFlow Unified Flow Collector (10x+ throughput)

## Constraints
- Local SSD storage is mandatory — HDD storage severely degrades indexing and query performance
- No built-in fault injection or synthetic traffic generation capabilities
- The legacy open-source version is no longer maintained and should not be used for new deployments
- Kibana dashboards are optimized for 1920x1080 monitor resolution; other resolutions may require layout adjustments
