# MITRE FHIR Server Capabilities

MITRE FHIR Server is a lightweight Go-based HL7 FHIR DSTU2 server using MongoDB as its storage backend. It acts as a thin wrapper around the intervention-engine/fhir library and was designed to support specific MITRE projects including Intervention Engine, eCQM Engine, Patient Matching Test Harness, and SyntheticMass. It is not a general-purpose FHIR server.

## FHIR API

- Serves FHIR DSTU2 resources over HTTP with MongoDB as the persistence layer
- Leverages the intervention-engine/fhir library for FHIR model definitions and server logic

## Constraints

- Implements FHIR DSTU2 only; no STU3, R4, or R5 support
- Not a complete FHIR implementation; tuned to the needs of specific upstream projects
- Requires a Go toolchain and a running MongoDB instance
- No authentication, authorization, or access control layer documented
- No FHIR capability statement or conformance endpoint documented in the README
- No Docker, containerized deployment, CI configuration, or test instructions
