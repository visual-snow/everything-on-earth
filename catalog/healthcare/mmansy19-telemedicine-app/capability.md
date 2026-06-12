# Telemedicine App Capabilities

This Telemedicine App is a platform built with Next.js and Node.js that connects patients with certified doctors for online consultations. It supports video conferencing, appointment booking, secure messaging, and medical record management across patient, doctor, and admin roles. A Flutter mobile client is also provided.

## Consultations

- Real-time video consultations between patients and doctors via WebRTC
- Appointment booking for both online and in-person visits
- Secure asynchronous messaging for follow-up communication between consultations

## User Roles

- Patients can search for doctors, book appointments, and access their medical records
- Doctors manage their availability, conduct consultations, and update patient records
- Administrators oversee platform-wide user and content management

## Medical Records

- Patient medical records are stored and accessible through the platform
- Records are linked to consultation history

## Constraints

- No containerized deployment; the frontend deploys via a static hosting platform only
- The video conferencing provider is ambiguously documented between two different technologies
- No authentication provider is explicitly named despite role-based access being implemented
- No automated test suite, CI/CD pipeline, or linting configuration documented
- No API documentation or OpenAPI specification published
- No HIPAA or data-privacy compliance documentation
- No observability stack for logging, tracing, or alerting
- The backend repository is not publicly linked
