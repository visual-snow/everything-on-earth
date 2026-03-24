The Cisco XR NETCONF Lab is a Jupyter-based hands-on environment for learning NETCONF/YANG and building Python NETCONF clients against a live Cisco IOS-XR device. It pairs interactive notebook exercises with a model-driven telemetry stack so that interface statistics streamed from the router can be visualised while exercises run. The lab targets network engineers and developers who need practical experience writing NETCONF RPCs and consuming real-time telemetry data.

## NETCONF Operations

- Send NETCONF RPCs over SSH using the ncclient Python library
- Retrieve and filter configuration and operational data using YANG-modelled requests
- Edit device configuration via `edit-config` operations from notebook cells
- Execute notebook exercises interactively, one cell at a time

## Model-Driven Telemetry

- Receive gRPC telemetry streams pushed by the IOS-XR device at 10-second intervals
- Collect interface operational statistics via YANG-modelled sensor paths
- Store all incoming telemetry in a time-series database for historical queries
- Visualise live and historical interface traffic through a pre-built dashboard

## Traffic Generation

- Generate synthetic network traffic on demand using iperf between the Linux host and the IOS-XR device
- Observe the effect of generated traffic in real time through the telemetry dashboard

## Constraints

- An external physical or virtual IOS-XR device is mandatory; the lab does not include a simulated or containerised XR instance
- The IOS-XR device must run version 7.0.x; compatibility with other versions has not been verified
- The telemetry stack uses an unencrypted gRPC transport; no TLS is configured for the telemetry path
- iperf must be installed independently on both the Linux host and the IOS-XR device before traffic exercises can run
- The lab covers NETCONF/YANG only; RESTCONF, gNMI, and gNOI are not documented or supported
