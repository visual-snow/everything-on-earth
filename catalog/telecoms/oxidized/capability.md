Oxidized is a network device configuration backup tool that automatically retrieves and versions configurations from over 130 network operating system types. It serves as a modern replacement for RANCID, combining Git-based version history, a REST API, and syslog-driven change detection. The hook system enables integration with external notification and automation targets.

## Configuration Retrieval

- Continuously polls devices on a configurable interval using a parallel threading engine
- Supports on-demand fetches and priority queuing for individual nodes via the REST API
- Connects to devices over SSH or Telnet depending on model handler requirements
- Reads the device inventory from sources including CSV files, SQLite, MySQL, or an HTTP endpoint

## Versioning and Change Tracking

- Stores retrieved configurations in a Git repository, preserving full version history
- Exposes version diffs and history for any node through the REST API
- Attributes configuration changes to specific users via Git blame integration
- Captures change events in real time through a syslog listener that records timestamps and user identity

## Device and Model Support

- Includes handlers for 130+ network OS types covering a wide range of vendors and platforms
- Applies credentials and privileged-mode access settings per device model or group
- Merges system-wide and user-specific YAML configuration files in a defined order

## Event Hooks and Integration

- Fires hooks on configurable events including fetch completion and configuration changes
- Supports hook types for running external commands, posting to HTTP endpoints, and sending notifications to messaging platforms
- Synthetic syslog messages can be directed at the listener to simulate change events for testing

## Constraints

- Must be run as a dedicated non-root user; running as root is not supported
- Requires a pre-initialized Git repository accessible by the service user when using Git-backed output
- Thread count must be manually tuned to ensure the retrieval interval is met; no automatic hard concurrency cap is enforced
- The REST API does not support TLS natively; securing the endpoint requires an external reverse proxy
- No built-in metrics or monitoring endpoint is provided; observability relies on external tooling or log parsing
