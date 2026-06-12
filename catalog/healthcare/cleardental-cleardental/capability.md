# ClearDental Capabilities

ClearDental is an open-source Linux desktop dental practice management suite built with Qt/QML. It organises a practice around roughly 60 application modules covering scheduling, clinical documentation, billing, imaging, and insurance claims. A background daemon handles time-sensitive tasks — SMS appointment reminders and insurance eligibility checks — without user interaction.

## Scheduling and Patient Flow

- Appointment scheduling across one or more providers.
- Patient demographics and contact management linked to scheduled visits.
- SMS appointment reminders dispatched through the VoIP.ms gateway.

## Clinical Documentation

- Hard tissue charting per tooth with procedure history.
- Periodontal charting per tooth.
- Clinical exam modules for structured visit documentation.
- Procedure-specific documentation modules for discrete treatment types.
- Radiograph and photograph acquisition and association with patient records.

## Billing and Insurance

- Insurance claims submitted electronically via the DentalXChange API.
- Alternate claim path through the EDS EDI clearinghouse REST interface.
- Pre-estimate and actual claim workflows handled as distinct modes.
- MassHealth patient eligibility checked by scraping the MassHealth web portal.
- Eligibility checks can run automatically via the background daemon on a schedule.
- Production and financial reports for practice revenue oversight.

## Audit and Data Integrity

- Git is used as the audit trail mechanism for data changes.

## Background Daemon

- Runs independently of the interactive desktop session.
- Handles SMS dispatch and eligibility polling on a cron-like schedule.
- Allows automated tasks to complete without the UI being open.

## Constraints

- Linux-only; macOS and Windows are not supported.
- A minimum display resolution of 1920x1080 is required.
- Qt 5.14 or later and libusb must be present on the host.
- Initial application setup must be completed before any module is accessible.
- No authentication or access-control layer is present.
- No DICOM support; no HL7 or FHIR interfaces; no X12 EDI.
- No automated test suite.
- Version 1.0 is in maintenance mode; version 2.0 is not production-ready.
