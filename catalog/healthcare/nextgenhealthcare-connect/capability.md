# Mirth Connect Capabilities

Mirth Connect is an open-source healthcare integration engine that translates, filters, routes, and transforms messages between disparate health information systems. It models integration workflows as configurable channels with source connectors, transformation steps, and destination connectors. Source code for versions 4.6 and later is no longer publicly available; the last open-source release is 4.5.2.

## Message Processing

- Channels receive messages from source connectors, apply JavaScript or rule-based transformations, and deliver results to one or more destination connectors
- An internal message queuing engine manages channel execution and delivery guarantees
- In-process channel-to-channel messaging allows pipeline composition without network hops

## Protocol Support

- HL7 v2.x over MLLP framing and raw TCP
- HL7 v3 and DICOM
- HTTP and HTTPS, WebSocket, SMTP, JMS, SFTP, and local file system
- EDI/X12 and NCPDP for pharmacy transactions
- JDBC/SQL for direct database read and write operations

## Administration

- A Swing-based administrator GUI provides channel design, deployment, and monitoring
- A command-line interface enables scripted administration and remote management
- A server manager handles service lifecycle, configuration editing, and log viewing
- A REST API exposes all administrative operations programmatically

## Monitoring

- Per-channel dashboards display received, filtered, queued, sent, and errored message counts
- An event log provides an audit trail of administrative actions
- Real-time server log viewing is available in the administrator interface

## Persistence

- An embedded database provides zero-configuration single-node operation out of the box
- External database backends support MySQL, PostgreSQL, Oracle, and SQL Server for production deployments
- A read-write split mode separates read-only query traffic to a secondary connection pool

## Constraints

- Source code for versions 4.6 and later is not publicly available; the last open-source release is 4.5.2 under MPL 2.0
- Default JVM heap is 256 MB and must be raised for production workloads
- Default administrator credentials have no enforced password policy; all policy minimums default to zero
- The embedded database is not suitable for multi-node or high-availability deployments
- The administrator GUI requires a Java Web Start launcher; plain-browser access is limited to the launch page
- No FHIR R4/R5 connector in the open-source codebase; available as a commercial extension only
- No built-in horizontal scaling or clustering; high availability requires external load balancing and a shared database
