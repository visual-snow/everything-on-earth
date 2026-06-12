# Hades Capabilities

Hades is a lightweight read-only FHIR R4 terminology server written in Clojure. It wraps the hermes SNOMED CT library to expose SNOMED CT concepts, descriptions, and relationships via standard FHIR terminology REST operations. It does not support write operations, authentication, or codesystems beyond SNOMED CT.

## Terminology Operations

- CodeSystem lookup returns concept properties, descriptions, and relationships for a given SNOMED CT code
- Subsumption testing determines whether one SNOMED CT concept subsumes another
- ValueSet expansion resolves intensional value set definitions into enumerated concept lists
- All operations are served over FHIR R4 REST endpoints in JSON or XML format

## Architecture

- A pluggable codesystem provider interface allows additional terminology backends to be registered
- The hermes library provides the SNOMED CT index and query engine; a pre-built SNOMED CT database must exist before the server starts
- The hermes library version must match the hades version series for compatibility
- Runs on an embedded HTTP server with no external dependencies beyond the SNOMED CT database file

## Constraints

- SNOMED CT is the only supported codesystem; LOINC, ICD-10, and other terminologies are not yet available
- The SNOMED CT database must be pre-built using the hermes tool before hades can start
- No write or mutate operations; the server is immutable by design
- No authentication or authorization layer
- Several FHIR terminology operations are not yet implemented, including ConceptMap translate, closure, and code validation
- No container or cloud-native deployment configuration is provided
