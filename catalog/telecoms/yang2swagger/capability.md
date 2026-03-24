Yang2Swagger converts YANG data models into RESTful API specifications compliant with the RESTCONF (RFC 8040) standard, producing OpenAPI 2.0 output in YAML or JSON format. It uses the OpenDaylight YANG parser internally and can return results as structured Java objects, making it suitable for both standalone use and programmatic integration.

## Invocation Modes

- Run as a standalone executable JAR from the command line
- Integrate into a Maven build lifecycle via the Maven plugin component
- Use programmatically as a Java library that returns a Swagger object

## Input Control

- Point at one or more directories containing YANG modules as input source
- Select which YANG element types to include: data nodes, RPCs, or both
- Enable or disable full CRUD path generation (read-only mode generates GET paths only)
- Control namespace inclusion in resource URIs
- Choose between standard RESTCONF path format and the OpenDaylight bierman-02 variant

## Output Customization

- Write output to a file or stream to stdout
- Set the API version string embedded in the generated specification
- Choose BASIC or no authentication definition in the output
- Override the content type used for request and response bodies
- Optionally reuse structurally identical grouping types to reduce output size
- Apply a simplified inheritance model for compatibility with standard code generators

## Server Scaffolding

- Generate a REST framework server stub code from YANG models via the codegen component

## Constraints

- Requires a supported runtime version to execute; a build tool is required to build from source
- Output targets OpenAPI 2.0 only — OpenAPI 3.x is not supported
- Large YANG models may exhaust the fixed JVM heap allocation and produce an out-of-memory error
- Maven plugin integration is noted as not thoroughly validated in the current release
- OpenDaylight Maven repository configuration may be needed to resolve build dependencies
