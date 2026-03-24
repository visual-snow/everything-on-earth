Yanger is an extensible YANG module validator written in Erlang that parses and validates YANG data models against RFC 7950. It supports format conversion and schema transformations through a plugin architecture, making it useful for tasks that involve verifying, converting, or restructuring YANG modules.

## Validation

- Parses and validates YANG modules, reporting errors and warnings with line numbers and error codes
- Supports strict compliance mode to enforce tighter YANG rules beyond the default checks
- Warnings can be promoted to errors, and individual warning categories can be suppressed or enabled
- Applies deviation modules to a base schema before validation

## Format Conversion

- Converts YANG modules to tree, YIN (XML), Swagger/OpenAPI 2.0 JSON, or canonical YANG output
- Accepts YIN (XML) as input in addition to standard YANG syntax
- Writes output to a file or to standard output

## Schema Transformation

- Applies expand transform to inline groupings and typedefs before output
- Applies restconf transform to produce RESTCONF-compatible schema representations
- Filters schema nodes by YANG status: current, deprecated, or obsolete

## Feature and Conformance Control

- Enables or disables named YANG features per module before validation or conversion
- Sets module conformance to implement or import, affecting which checks apply
- Supports SMIv2 module input via a dedicated plugin

## Constraints

- Validates schema structure only; does not validate JSON or XML instance documents against a schema
- Operates exclusively as a CLI batch tool with no daemon mode, REST API, or interactive interface
- Not all output format and transform combinations are valid; restconf transform requires a subsequent format plugin to produce output
- Module resolution depends on a correctly configured search path; missing path entries cause resolution failures
- Feature flag syntax requires the module name prefix; unrecognized features produce warnings unless explicitly ignored
- Plugin discovery requires plugins to be on the Erlang code path or provided via the plugin directory flag at invocation time
