# LinuxForHealth HL7v2-FHIR Converter Capabilities

The LinuxForHealth HL7v2-FHIR Converter is a Java library that converts HL7v2 messages to FHIR R4 Bundle resources using a declarative, YAML-template-driven approach. It uses HAPI HL7v2 for message parsing and HAPI FHIR for resource modeling. It is an embedded library with no REST API or HTTP server; the calling application must handle I/O and transport.

## Conversion

- Converts HL7v2 messages from ADT, DFT, MDM, OMP, ORM, ORU, PPR, RDE, VXU, and OML message families to FHIR R4 JSON Bundles
- YAML message templates define which segments map to which FHIR resources for each message type
- YAML resource and datatype templates define field-level mappings from v2 segments and datatypes to FHIR resource properties
- Concept map YAML files translate v2 vocabulary codes to FHIR coding systems
- Computed field values are supported via an embedded expression engine

## Template Customization

- Default templates ship with the library and are used when no custom path is configured
- Custom template directories override or extend the bundled templates for site-specific requirements
- Supplemental templates can be merged on top of base templates without replacing them entirely

## Configuration

- A timezone setting controls ISO 8601 offset formatting when HL7 fields lack timezone information
- A message-type filter restricts which HL7v2 message types are accepted for conversion
- Runtime options allow per-call timezone and variable injection for multi-tenant scenarios

## Constraints

- Requires JDK 11 or later
- OML_O21 support is partial: repeating ORDER groups and OBX observations are not converted
- DFT_P03 does not convert the financial transaction segment
- Debug log statements are stripped at build time to prevent protected health information leakage
- No REST, HTTP, or messaging interface; single-message conversion as an embedded library only
- No HL7v3 or CDA document support
