pyang is a YANG validator, transformer, and code generator written in Python. It supports RFC 6020 and RFC 7950 and operates entirely as a static analysis tool with no runtime server component. All interaction is through the command-line interface or the Python library API.

## Validation and Linting
- Validates YANG module syntax and RFC compliance in the default mode
- Detects non-backward-compatible changes between two module revisions using the check_update plugin
- Performs stricter RFC 8407 style and guideline checks via the lint plugin
- Reports validation errors and warnings with counts emitted to stderr

## Format Conversion and Output
- Converts between YANG and YIN formats in either direction
- Generates compact ASCII tree diagrams of the data model
- Produces PlantUML class diagram source for UML visualization
- Creates skeleton XML instance documents from a YANG module
- Translates to DSDL (RELAX NG, Schematron, DSRL) for XML instance validation
- Generates schema-aware YANG-to-JSON translation via jtox and jsonxsl plugins
- Outputs an HTML/JavaScript tree browser for interactive browsing
- Produces SID files for YANG module identifiers used in CoAP and COMI
- Prints module dependency lists and flattens groupings and augments into a single view
- Generates NETCONF capability URI lists

## Protocol and Standard Support
- YANG (RFC 6020, RFC 7950), YIN (RFC 6020), NETCONF (RFC 6241), RESTCONF (RFC 8040)
- DSDL (RFC 6110) and SMIv2 (RFC 6643) via the smi plugin
- Bundled IANA and IETF standard YANG modules available out of the box

## Configuration
- Module search paths and installation prefix configured through environment variables
- Plugin directory extensible via a CLI option
- Output format selected with a CLI flag; all options are per-invocation

## Constraints
- Requires Python 3.7 or later; an XML processing library is the only runtime Python dependency
- YANG-to-DSDL translation requires an XSLT processor and an XML validator system binaries to be present at runtime
- Standard YANG modules will not be resolved when installed to a non-default prefix unless search path environment variables are set correctly
- SMIv2 translation depends on the external an SMI library system library
- No built-in metrics export, GUI, or network server; output is textual diagnostics only
