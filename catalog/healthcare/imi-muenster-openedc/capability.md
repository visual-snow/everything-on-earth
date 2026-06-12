# OpenEDC Capabilities

OpenEDC is a browser-based electronic data capture system for medical research studies, built on the CDISC ODM-XML standard with no third-party framework dependencies. It supports offline-first operation with optional server synchronization for multi-user, multi-site projects. This repository is an archived, unmaintained prototype; the production-ready successor is hosted separately.

Two deployment modes:
- Standalone: fully offline, data stored locally on the device with AES encryption
- Server-connected: syncs with an OpenEDC Server backend for multi-user and multi-site collaboration

## Study Design

- A metadata design module allows researchers to create study forms and define data elements
- Forms follow the CDISC ODM-XML standard for portability and regulatory alignment

## Data Capture

- Clinical data entry runs in the browser with real-time field-level validation
- Conditional skip patterns adapt visible fields based on prior responses
- Data is captured directly into CDISC ODM-XML format

## Offline and Sync

- A service worker enables full offline operation; data entry continues without connectivity
- In server-connected mode, synchronization triggers automatically on reconnection
- Client-server communication uses end-to-end encryption

## Administration

- User and site management is available in server-connected mode only
- Internationalization support covers multiple display languages

## Constraints

- Archived and read-only as of March 2025; no active maintenance or updates
- Unmaintained prototype; not GCP-compliant or validated for production clinical use
- Administrative features require a running OpenEDC Server instance
- No containerized deployment, build step, or bundler
- No published REST API specification for the client-server protocol
