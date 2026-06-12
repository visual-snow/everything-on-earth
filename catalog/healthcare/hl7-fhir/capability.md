# HL7/FHIR Specification Capabilities

HL7/FHIR is the authoritative source repository for the FHIR specification. It is used by core HL7 editors to build and publish the official FHIR standard. It is a specification publisher, not a runtime implementation; it produces no server, API, or SDK.

Three build modes:
- Full publish: generates the complete specification archive and web publication.
- Validation-only: runs the specification validator without producing output artifacts.
- Web publication: renders the HTML publication surface without generating the archive; restricted to core editors.

## Specification Build

- A Gradle-based build system drives the full pipeline from source data to publishable output.
- Source data contains all FHIR resource definitions, profiles, value sets, and narrative content.
- The build compiles, validates, cross-links, and formats the specification into a coherent publication.
- An archive generator packages the complete specification for distribution.
- A web publication formatter produces the HTML rendering of the standard.

## Validation

- The validation runner checks specification source for conformance and internal consistency.
- Validation can run independently of the full publish step to catch errors earlier in the authoring cycle.
- The validator operates on the specification itself, not on FHIR resources produced by external systems.

## Change Workflow

- All substantive changes to the specification follow the HL7 Jira workflow; direct pull requests to the repository are not the intended contribution path.
- The `-web` and `-noarchive` build flags are restricted to core editors with publishing authority.

## Constraints

- Building the full specification requires a minimum of 16 GB RAM; lower-memory machines cannot complete the build.
- A full publish takes approximately 20 minutes on adequate hardware.
- The repository contains no runtime server, API endpoint, or FHIR resource processing engine.
- No SDK, client library, or reference implementation is included.
- No packaging for container runtimes is provided.
