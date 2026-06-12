# OpenELIS Global Core (1.x) Capabilities

OpenELIS Global Core is an open-source laboratory information system for clinical and reference labs operating in resource-constrained environments. It covers the full lab workflow — order entry, specimen tracking, result entry, quality assurance, and reporting — with built-in support for analyzer hardware and health data exchange standards. The 1.x branch is no longer actively maintained upstream.

## Core Lab Workflow

- Accepts electronic lab orders via HL7 messaging and supports manual order entry
- Tracks specimens through configurable status stages from intake to result release
- Manages result entry with validation queues and non-conformity recording
- Enforces role-based access control across all lab functions

## Analyzer Integration

- Imports results directly from a range of clinical analyzers including hematology, flow cytometry, serology, and PCR platforms
- Uses a reader plugin architecture to add analyzer support without core changes

## Reporting

- Generates patient-level, workplan, QA, and aggregate indicator reports
- Sends aggregate and result reports to external systems over standard HTTP
- Produces barcode labels in ZPL-II format for Zebra printers; no other label formats are supported
- A background scheduler runs aggregate report transmission and other periodic tasks

## Data Exchange

- Ingests electronic lab orders via HL7 v2.5.1 OML_O21 messages; no other inbound message types are supported
- Emits result and aggregate reports outbound via HL7 v2.x

## Constraints

- Requires PostgreSQL; no alternative database backend is supported
- Background jobs do not persist across restarts
- No FHIR interface, REST API, or SOAP API
- No built-in TLS; transport security must be handled externally
- No multi-tenancy support
- No automated test suite or audit log export facility
