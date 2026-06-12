# HL7 v2 to FHIR Capabilities

HL7 v2 to FHIR is an HL7 Implementation Guide that defines declarative ConceptMap mappings for converting HL7 v2.x messages, segments, datatypes, and vocabulary codes to FHIR R4 Bundles and resources. It is a specification artifact, not a runtime engine; implementers use the mappings as input to their own conversion tooling.

## Message Mapping

- Fifteen v2 message structures (ADT, OML, ORM, ORU, MDM, SIU, VXU families) are mapped to FHIR R4 Bundles
- Each message map specifies which segments produce which FHIR resources and how they are assembled into a Bundle

## Segment and Datatype Mapping

- Approximately 35 v2 segments (MSH, PID, PV1, OBR, OBX, ORC, RXA, DG1, IN1, SPM, and others) are mapped to one or more FHIR resources
- Approximately 40 v2 datatypes (CWE, CX, XPN, XAD, XTN, DTM, EI, PL, HD, and others) are mapped to FHIR primitive and complex types
- Context-dependent datatype variants use flavor qualifiers to select the correct mapping per usage site

## Vocabulary Mapping

- v2 table codes are mapped to FHIR CodeableConcept coding systems
- Code-system mappings cover the standard HL7 vocabulary tables used across v2.1 through v2.9

## Conditional Logic

- Mapping conditions use a formal grammar for expressing when a particular mapping row applies
- FHIRPath expressions provide an alternative condition language
- Error conditions can halt mapping when required v2 elements are absent

## Constraints

- Targets FHIR R4 (4.0.1) only; no R5 mappings are defined
- Mappings use v2.9 as the baseline; deprecated fields from earlier versions are included but flagged
- Cardinality mismatches between v2 and FHIR must be resolved by implementers; the guide provides guidance but no single required strategy
- Temporal fields must be reformatted to ISO 8601 using platform-specific utilities
- No runtime engine, reference implementation, or test harness is included; the ConceptMaps are declarative artifacts only
- Cross-resource references are the implementer's responsibility
