CGRateS is a real-time Online/Offline Charging System for Telecom and ISP environments, implemented in Go. It exposes rating, session charging, CDR processing, fraud detection, and least-cost routing as independent micro-services over a rich RPC API. All services run within a single engine process or across a clustered deployment.

## Charging and Rating
- Supports online (prepaid/pseudoprepaid) real-time session reservation and debit
- Supports offline (postpaid/rated) post-call CDR-based billing
- Tariff plan loading from CSV files via the loader service or loader tool
- Default request types: prepaid, postpaid, pseudoprepaid, rated
- Configurable max and min call duration per charging profile

## Session and Resource Management
- Session manager with reservation handles mid-call balance checks and debits
- Resource allocation and limiting enforces concurrent-session caps per account or destination
- Charging profile assignment maps sessions to the correct rating plan

## CDR and Event Processing
- Full CDR storage with support for interim (mid-call) records
- Event Reader Service ingests events from Kafka, AMQP, NATS, flat files, and HTTP
- Event Exporter Service publishes CDRs and events to configurable external targets
- Retry and dead-letter handling for export failures with configurable attempt counts

## Statistics and Thresholds
- Real-time metrics queues track ASR, ACD, TCD, ACC, TCC, PDD, DDC, and custom counters
- Event-driven threshold breach detection triggers configurable actions on metric violations
- Concurrent request monitoring with configurable sampling interval
- Performance target of 5000 or more requests per second on a single machine

## Routing and Protocol Agents
- Least-cost routing evaluates routes against cost and quality metrics
- Dispatcher routes requests across cluster nodes for horizontal scaling
- Protocol agents available: Diameter, RADIUS, HTTP, DNS, SIP (redirect-only), Asterisk, Kamailio

## Attribute Processing
- Attribute pipeline modifies session and CDR fields before rating or export
- Supports chained attribute profiles applied in configurable order

## Constraints
- A runtime data store (Redis or MongoDB) must be running and reachable before the engine starts; no embedded data store is provided
- A persistent store (MySQL, MariaDB, PostgreSQL, or MongoDB) is required for tariff plans and CDR storage; without it, rating cannot function
- Tariff plans must be pre-loaded before any rating or charging request can be processed
- Diameter and RADIUS agents require an external peer or client and are not self-contained
- Session charging requires an upstream VoIP platform to generate session events; the engine does not originate calls
- No built-in web UI or dashboard is provided; all interaction is through the RPC API
