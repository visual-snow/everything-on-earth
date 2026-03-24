ncclient is a Python library for client-side NETCONF scripting and application development. It provides a high-level API for connecting to and managing network devices via NETCONF over SSH, supporting both synchronous and asynchronous RPC dispatch.

## Connection and Session Management
- Establishes and manages NETCONF sessions to remote devices over SSH
- Supports password and key-based authentication
- Reads OpenSSH configuration files for connection settings
- Controls SSH host key verification behavior
- Configures session timeouts and other manager-level parameters

## NETCONF Operations
- Executes standard NETCONF RPCs: get, get-config, edit-config, copy-config, delete-config, lock, unlock, commit, discard-changes, close-session, kill-session
- Supports NETCONF 1.0 and NETCONF 1.1 protocol versions
- Dispatches RPCs synchronously by default or asynchronously when configured

## Vendor Device Support
- Selects vendor-specific handlers for Juniper, Cisco, Huawei, and other network device families
- Adapts RPC behavior and response parsing to device-specific quirks

## XML and Data Handling
- Constructs and parses NETCONF XML payloads
- Provides utilities for working with YANG-modeled data returned in XML form

## Constraints
- Requires a live NETCONF-capable device or server at connect time — no built-in mock or simulator is provided
- SSH is the only supported transport — NETCONF over TLS and SOAP transports are not supported
- Mandatory runtime dependencies must be present; a minimum Python version and later require the updated async API introduced in a prior major release
- No built-in YANG schema validation or RESTCONF support
