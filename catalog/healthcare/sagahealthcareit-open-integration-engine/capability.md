# Open Integration Engine Capabilities

The Open Integration Engine is an open-source fork of Mirth Connect, a healthcare integration engine for connecting disparate clinical systems through channel-based message routing, transformation, and monitoring. It was forked under the Mozilla Public License after the upstream project's licensing changed to proprietary. FHIR is supported as a connector and transformation target, not as a built-in server.

## Message Processing

- Channel-based pipelines receive messages from source connectors, apply JavaScript transformations and filters, and deliver results to one or more destination connectors
- Global scripts and code templates can be shared across channels
- Messages can be re-processed from error queues without channel restart

## Protocol Support

- HL7 v2.x over MLLP and TCP
- HL7 FHIR R4
- C-CDA and CCD document exchange
- DICOM
- HTTP and HTTPS (REST), FTP, SFTP, SMTP, and JDBC for database connectivity

## Administration

- A web-based administrator UI provides channel design, deployment, and real-time monitoring
- Per-channel dashboards display received, filtered, queued, sent, and errored message counts
- Configurable alert thresholds notify operators of channel status changes and error rate spikes
- User roles and permissions are managed through the administrator interface

## Persistence

- An embedded database provides zero-configuration single-node operation for development
- External database backends support PostgreSQL and MySQL for production deployments

## Constraints

- Requires a Java runtime
- Forked from Mirth Connect after the upstream licensing changed to proprietary; ongoing divergence from the original codebase
- No native Kubernetes operator; container images are available but orchestration is manual
- No built-in high-availability clustering; must be handled externally
- HIPAA and GDPR compliance responsibility falls on the deploying organization
- No built-in FHIR server, terminology service, or IHE ATNA audit logging
