# Servando Capabilities

Servando is an open distributed telemedicine platform built on Android. It schedules patient-facing medical actions through a protocol-driven agenda engine and relays collected data between patient devices and hospital servers over a web services layer. The project has been inactive since 2015 and depends on a separate core library module.

## Patient Monitoring

- Patients execute scheduled medical actions on an Android device according to a declarative protocol definition
- An agenda engine manages the timing and sequencing of follow-up actions as defined in a protocol XML file
- A services layer encapsulates the logic for each type of medical action

## Data Exchange

- Collected patient data is transmitted from the Android client to hospital server endpoints via XML-serialized web services
- The server side exposes received data through a REST API for consumption by hospital systems

## Protocol Management

- Follow-up protocols are defined declaratively in XML, specifying which medical actions to perform and when
- The protocol engine interprets these definitions and drives the agenda execution on the patient device

## Constraints

- Requires Android for the client-side application; no iOS, desktop, or web client
- Depends on a separate servando-core library module that must be available as a dependency
- Last active in 2015; project was mid-migration from Google Code at the time of the last commit
- No authentication, security documentation, or observability instrumentation
- No automated tests, CI configuration, or containerized deployment
