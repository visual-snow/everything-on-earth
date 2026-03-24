nfdump is a suite of command-line tools for collecting, storing, and analyzing network flow data from NetFlow, IPFIX, and sFlow sources. It combines high-performance capture daemons with a flexible filtering and aggregation engine, making it suited for post-hoc traffic analysis at scale.

## Collection

- Captures NetFlow v1, v5, v7, v9, and IPFIX streams via a dedicated collector daemon
- Captures sFlow v4 and v6 streams via a separate collector daemon
- Converts pcap files or live packet captures into flow records
- Supports NSEL and NAT Event Logging extensions carried over NetFlow v9

## Analysis

- Filters stored flow records using tcpdump-style filter expressions
- Aggregates flows on any flow element or combination of elements
- Generates statistics and summaries over arbitrary flow fields
- Outputs results as plain text, CSV, JSON, or user-defined format strings
- Exports metrics to InfluxDB and Prometheus

## Enrichment

- Annotates flows with IP geolocation and autonomous system number data
- Flags flows associated with Tor exit nodes
- Anonymizes IP addresses using the CryptoPAn algorithm
- Optionally fingerprints TLS sessions using JA4

## Replay and Maintenance

- Re-emits stored flow records to another collector for forwarding or testing
- Manages expiration and rotation of binary flow data files
- Supports multiple compression codecs for stored files

## Constraints

- NetFlow v5/v7 use 32-bit on-wire counters, which can overflow on high-bandwidth links; nfdump mitigates this with 64-bit internal storage but cannot recover already-lost precision
- Binary flow files are architecture-dependent and are not portable between big-endian and little-endian systems without explicit conversion
- Flow files written in the legacy 1.6.x format are readable only by the analysis binary, not by collector daemons
- Collector daemons require elevated privileges to bind to ports below 1024
- No built-in access control is provided for collector endpoints; isolation must be enforced at the network or OS level
