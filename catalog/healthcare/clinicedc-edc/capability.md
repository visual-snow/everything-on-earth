# clinicedc/edc Capabilities

clinicedc/edc is a Django-based electronic data capture framework for building multisite, randomized longitudinal clinical trials. It runs in production for NIH-funded HIV, diabetes, and hypertension studies across Africa, collecting data at point-of-care into validated electronic CRFs. It does not include HL7/FHIR interoperability, CDISC export formats, or offline-first support.

## Participant Management

- Screens participants against protocol eligibility criteria before enrollment
- Manages informed consent with full version history; consent periods are coupled to data collection windows
- Generates unique participant identifiers per site and protocol

## Randomization

- Assigns participants to treatment arms using site-stratified randomization lists
- Supports treatment unblinding workflows for safety reviews
- Links randomization to pharmacy dispensing and visit schedules

## Visit Scheduling

- Enforces protocol-defined visit windows with configurable tolerance periods
- Flags missed, overdue, or out-of-window visits
- Supports both scheduled follow-up and unscheduled as-needed visits

## Data Collection

- Electronic CRFs with field-level validation at point-of-care entry
- Captures vitals, eGFR, and glucose measurements with reference-range checking
- Grades lab results against CTCAE and DAIDS toxicity scales
- Manages specimen requisitions and links results back to participant records

## Safety and Pharmacovigilance

- Records and tracks adverse events through resolution
- Produces QA reports highlighting data anomalies and protocol deviations

## Pharmacy

- Manages drug dispensing records per randomization arm
- Tracks stock and links dispensing events to visit data

## Reporting

- Generates PDF reports and participant-level summaries
- Exports data for statistical analysis
- Produces QA and monitoring reports for site auditors

## Constraints

- Requires Python 3.12+ and Django 5.2+; MySQL 8+ is the only supported database backend
- Asynchronous tasks require Celery backed by Redis; not designed for synchronous-only production use
- Field-level encryption keys must be backed up independently of the database; loss renders encrypted data unrecoverable
- No HL7/FHIR integration, CDISC ODM/SDTM export, or offline-first application support
- Deploys on bare-metal Ubuntu with systemd; no container or cloud-native deployment provided
