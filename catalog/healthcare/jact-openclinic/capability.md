# OpenClinic Capabilities

OpenClinic is an open-source PHP/MySQL web-based medical records system for private clinics, surgeries, and individual doctors. It manages patient demographics, clinic history, problem reports, staff, users, themes, and audit logging through a browser interface. Passwords are stored as unsalted MD5 hashes; the application should not be considered secure by modern standards.

## Patient Records

- Patient demographic data with searchable index
- Clinical history tracking with dated problem reports
- Medical test records with file attachment support (MIME type and file path stored)

## Administration

- Staff and user management with three fixed profile levels (Administrator, Administrative, Doctor)
- Clinic configuration settings including name, address, hours, phone, and session timeout
- Internationalization via portable object translation files

## Audit and Logging

- Per-user access log recording login events and timestamps
- Record-level audit trail tracking table name, operation type, affected row, and acting user
- Optional SQL debug tracing and console error output via configuration flags

## Deployment

- An install wizard handles initial database creation and configuration
- An upgrade script detects schema version mismatches and applies migrations automatically
- A demo mode restricts write operations for public demonstrations

## Constraints

- PHP 5.3 or later required; incompatible with PHP 4
- MySQL 5.1 or later is the only supported database; all tables use MyISAM with no foreign-key enforcement
- Passwords stored as unsalted MD5 hashes; no modern password hashing
- Only one clinic configuration is supported; no multi-site or multi-tenant capability
- Default credentials ship in seed data; login attempt limiting requires explicit configuration
- No REST, FHIR, or HL7 API; no appointment scheduling, billing, DICOM viewer, or Docker support
