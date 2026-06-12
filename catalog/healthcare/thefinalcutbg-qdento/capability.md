# QDento Capabilities

QDento is a free, open-source cross-platform dental practice management desktop application built with Qt6 and C++. It is the international fork of DinoDent, stripped of Bulgaria-specific healthcare integrations, and intended as a clean baseline for country-specific customization. All data is stored in a local SQLite database with no cloud or network backend.

## Patient Records

- Patient demographics, contact details, and clinical history
- Dental status charting with per-tooth procedure recording
- Periodontal status tracking per tooth
- Patient history log across visits

## Scheduling and Finance

- Appointment scheduler for managing patient visits
- Invoice generation, debit notes, and credit notes for patient billing
- Financial document management and reporting

## Constraints

- Requires Qt6 version 6.8 or later; Qt5 is not supported
- All data stored in a local SQLite file; no cloud sync, remote database, or multi-user networked mode
- No country-specific billing, insurance claim submission, or regulatory integration; intended as a customization base
- No REST, HL7, or FHIR API
- No DICOM or radiograph viewer
- No e-prescription workflow
- Desktop-only; no web or mobile client
