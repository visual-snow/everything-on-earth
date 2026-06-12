# iMSTK Capabilities

iMSTK (Interactive Medical Simulation Toolkit) is a C++ toolkit for rapid prototyping of real-time multi-modal surgical simulation scenarios. It integrates haptics, rendering, computational mechanics, and virtual reality in a single framework. The project was discontinued in May 2025 and is no longer actively maintained.

Three rendering modes:
- Full rendering: GPU-accelerated pipeline for interactive simulators with visual feedback
- Offscreen rendering: runs without a display or GPU, suited for headless testing
- Renderless physics-only: strips the renderer entirely for biomechanical computation or custom renderer integration

## Device and Haptics Integration

- Haptic devices are abstracted via VRPN; any VRPN-compatible device appears as a unified input stream
- VRPN device configuration must be edited manually to match device addresses
- OpenHaptics SDK integration covers force-feedback for PHANToM-class devices
- Haply Inverse3 support is included but requires the Haply SDK to be acquired separately

## Simulation

- Real-time computational mechanics engine for deformable tissue and rigid body interactions
- Collision detection and response between simulation objects
- Multi-modal input combining haptic feedback with visual rendering

## Build System

- CMake Superbuild pulls and compiles all dependencies in one pass
- Requires CMake 3.15 or later
- On Windows, Visual Studio 2017, 2019, or 2022 is supported

## Constraints

- Discontinued May 2025; no active upstream maintenance or support
- Debug builds carry a significant performance penalty and are not suitable for real-time loops
- No Python bindings; C++ API only
- No REST, gRPC, or network interface; not designed for networked services
- No container or cloud-native deployment path
- No built-in benchmarking or performance instrumentation
- VRPN device configuration requires manual file editing per deployment
