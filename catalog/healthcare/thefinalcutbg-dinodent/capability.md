# DinoDent Capabilities

DinoDent is a desktop dental practice management application for Bulgarian dentists. It runs entirely on a local workstation with a local SQLite database or an optional distributed rqlite backend; no cloud services or external accounts are involved unless explicitly configured for Bulgarian national system integrations.

## Patient and Clinical Records

- Dental status charted per tooth with procedure history and treatment notes.
- Periodontal status recorded per tooth.
- Patient demographics, contact details, and appointment scheduling.
- Google Calendar integration for appointment synchronization.
- SMS reminders dispatched through a configurable SMS gateway.

## Financial and Document Management

- Invoice and receipt generation for patient services.
- Financial aggregates and reporting across patients and time periods.
- Print and PDF output via the LimeReport engine.

## National System Integrations

- Electronic document submission to the National Health Insurance Fund (NHIF) via SOAP/XML.
- Prescription and referral submission to the Primary Information System (PIS) via SOAP/XML.
- NHIS service client for National Health Information System interactions using XML with C14N canonicalization.
- NRA XML service client for National Revenue Agency tax document submission.
- NHIF package counters tracked per patient and period.
- All official electronic submissions require a physical PKCS11 hardware token for document signing.

## Data and Configuration

- All data stored in a local SQLite database or a distributed rqlite SQL cluster for multi-workstation setups.
- Auto-update service checks for and applies new application versions.
- No data leaves the local environment except through explicit national system submissions.

## Constraints

- Bulgaria-only; national integrations are hard-coded to Bulgarian authorities and are not applicable outside Bulgaria; an international fork (QDento) exists separately.
- A physical PKCS11 hardware token is required for all official electronic submissions; the application cannot sign documents without one.
- Desktop-only; no web interface, mobile client, or REST API is present.
- No automated tests or CI pipeline.
- No multi-tenancy; designed for a single practice.
- No audit log for user actions.
