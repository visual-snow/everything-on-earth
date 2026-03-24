This sandbox provides Cisco's pyATS (Python Automated Test Systems) framework running in a pre-configured Python virtual environment. It is designed for network test automation workflows, supporting device connectivity via SSH, Telnet, and ICMP. The full image variant includes the Genie and unicon libraries for richer device interaction and parsing.

## Test Execution

- Run pyATS job files using the easypy test runner from the command line
- Execute jobs directly or drop into an interactive Python shell for ad-hoc scripting
- Capture pass/fail results from job output; no built-in metrics export

## Device Connectivity

- Connect to network devices over SSH, Telnet, or ICMP
- Full variant includes Genie parsers and unicon connection libraries for structured device interaction
- Base image provides clients only; no simulated or virtual devices are bundled

## Environment Customization

- Auto-install additional Python packages by supplying a requirements file at container start
- Run custom initialization logic (repository clones, key scanning, dev installs) via a bash init script
- Initialization runs once per container lifecycle, guarded by a sentinel file

## Execution Modes

- Interactive Python shell (default)
- Bash shell for manual exploration
- Direct job execution for automated test runs
- Alpine-based variant available for lighter footprint; ARM64 variant available for compatible hardware

## Constraints

- Initialization scripts run only once per container lifecycle; starting a fresh container is required to re-trigger them
- No simulated network devices are included — real or separately provisioned devices must be reachable for end-to-end test execution
- No pre-built multi-service topology is provided; multi-container orchestration is the user's responsibility
- No built-in test result export integrations (such as JUnit XML or time-series formats) are available out of the box
