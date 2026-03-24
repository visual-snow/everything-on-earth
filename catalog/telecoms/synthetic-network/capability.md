The Synthetic Network sandbox provides a programmable network environment where traffic conditions can be manipulated at runtime without restarting the container. It bridges containers onto a virtual interface governed by a userspace packet-processing proxy, allowing tests to experience controlled bandwidth, latency, loss, jitter, and reordering. Both ingress and egress directions are independently configurable, and all parameters can be updated live via a REST API or JavaScript client library.

## Traffic Shaping

- Bandwidth cap settable per direction as an integer bit-rate
- Latency added uniformly to every packet crossing the synthetic interface
- Jitter applied on top of base latency with a configurable strength factor
- Packet loss expressed as a probability between 0 and 1, applied independently to ingress and egress
- Packet reordering toggled as a boolean per direction

## Per-Flow Rules

- Default link block applies conditions to all traffic traversing the interface
- Flows array allows per-protocol overrides, enabling different rules for UDP versus TCP
- All rule changes take effect immediately after a commit call, with no container restart required

## Measurement

- Ingress and egress traffic profiles record per-flow packet counts
- Profiles are readable at runtime through the JavaScript API
- Standard network diagnostic tools are available inside the container for manual inspection

## Modes of Operation

- Scripted mode: conditions controlled programmatically through the JavaScript client library
- Interactive mode: shell session inside a container on the synthetic network for manual exploration
- Browser mode: Chromium running inside a VNC session, subject to the same network conditions
- Minimal/headless mode: no GUI; conditions must be supplied via a pre-baked configuration file or a reload signal

## Constraints

- The container must run in privileged mode; the entrypoint relies on kernel networking utilities to wire up the virtual interface and routing
- Only traffic routed through the synthetic network interface is conditioned; API and VNC control-plane traffic uses a separate interface and is unaffected
- Minimal image variant has no live scripting capability; runtime updates require the full image with the frontend component
- No IPv6 support is provided; the environment is designed exclusively for Linux-based Docker networking with no Kubernetes or Windows container support
