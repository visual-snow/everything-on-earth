libyang is a YANG data modelling language parser and toolkit written in C, providing APIs for parsing, validating, and converting YANG schemas and instance data. It serves as a foundational library for network management projects including libnetconf2, Netopeer2, and sysrepo. The toolkit ships both a C library for embedding in applications and a feature-rich command-line validation tool.

## Protocol Support
- YANG 1.0 (RFC 6020) and YANG 1.1 (RFC 7950)
- YIN format schemas
- XML instance data encoding (RFC 7950)
- JSON instance data encoding (RFC 7951)
- Default values (RFC 6243), YANG Metadata (RFC 7952), Schema Mount (RFC 8528), and YANG Structure (RFC 8791)

## Modes of Operation
- Library mode — embedded in C applications via the public API
- CLI mode — interactive and non-interactive use through the yanglint validation and conversion tool
- Release build — optimised with optional test suite
- Debug build — default build with full assertions enabled

## Measurement and Testing
- Built-in performance measurement tool included in the repository
- Unit test suite using the cmocka framework covering core library behaviour
- Code coverage instrumentation available via a CMake build option
- Regression fuzzing harness for continuous robustness testing

## Configuration
- Compiler and install prefix configurable at build time
- Runtime plugin directory overridable via environment variable
- Schema caching and optimisation behaviour toggleable
- Unit tests can be enabled independently in Release mode

## Constraints
- Extension and plugin support is unavailable on Windows
- On Windows, the CLI tool operates in non-interactive mode only
- On Windows, YANG date-time values with unspecified timezone are converted to UTC
- Requires a C compiler and build system
- Requires a compatible regular expression library
- No built-in language bindings — Python, C++, and Rust bindings are maintained as separate projects
- No NETCONF or RESTCONF transport layer; schema and data handling only
