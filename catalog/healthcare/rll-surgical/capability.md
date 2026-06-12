# rll/surgical (DOOSim) Capabilities

rll/surgical is a research simulator for deformable one-dimensional objects (DOOs) - surgical suture, rope, and hair - using the Discrete Elastic Rods (DER) physical model. It targets robotic surgical assistant research and provides a simulation environment, motion planners, and hardware interfaces for the Raven II robot. The project was abandoned in 2011 and carries no license.

Two rod models are supported:
- Isotropic: uniform bending stiffness in all radial directions.
- Anisotropic: direction-dependent bending stiffness for materials such as braided suture.

## Physics Simulation

- The DiscreteRods engine implements the DER model, capturing bending, twisting, and stretching of slender elastic rods.
- Collision objects allow rods to interact with scene geometry.
- Simulation is limited to 1D thread-like structures; no tissue, organ, or surface deformation is included.

## Motion Planning

- An RRT planner samples configuration space and builds a tree of collision-free rod states.
- An SQP optimizer runs closed-loop control by solving a sequence of constrained quadratic programs to track a target rod configuration.
- Both planners operate on the rod state produced by the physics engine.

## Haptic Teleoperation

- A haptic device interface accepts operator input over UDP sockets, allowing a human to manipulate the simulated rod in real time.
- Raven II robot commands and state feedback are exchanged over a separate UDP socket channel.

## Vision Tracking

- A stereo vision thread tracks the rod in real-world camera frames, providing state estimates that can feed back into the controller.

## Recording

- StateRecorder captures rod state snapshots at runtime.
- TrajectoryRecorder logs full motion trajectories for later analysis or replay.

## Constraints

- Builds on Ubuntu 10.10 or later and Mac OS X only; the build system is a raw Makefile with no package manager support.
- Depends on Eigen2, OpenCV 2.1, GLUT, GLE, Bullet Physics, and Boost; exact versions from 2011 are required.
- No license is present; redistribution and derivative use are legally ambiguous.
- No ROS integration; robot communication relies entirely on raw UDP sockets.
- No unit tests and no continuous integration.
- Simulation covers 1D rods only; there is no 2D surface, volumetric mesh, or rigid-body anatomy model.
