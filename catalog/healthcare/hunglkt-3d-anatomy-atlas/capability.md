# 3D Anatomy Atlas Capabilities

3D Anatomy Atlas is an open-source desktop anatomy reference application built on OpenSceneGraph with a MySQL backend and .NET Core API layer. It renders three-dimensional anatomical models for healthcare professionals and students. 3D models are authored in Blender from medical images and documentation. The project has been unmaintained since 2018 with no formal releases.

## Visualization

- Renders 3D anatomical models using OpenSceneGraph with Qt integration
- Supports interactive rotation, zoom, and exploration of body structures
- Anatomical metadata is stored in and served from a MySQL database

## Content Pipeline

- 3D models are created in Blender from medical images, documents, and X-ray data
- A .NET Core API layer provides backend services for model and metadata retrieval

## Constraints

- Windows 10 Enterprise only; no cross-platform build instructions documented
- Requires an NVIDIA GTX 1080-class GPU per the team's hardware specification
- Unmaintained since 2018 with no versioned releases or pre-built binaries
- Planned AR, VR, mobile, haptic feedback, and CPR simulation modes exist only on the project roadmap; no implementation code is present
- No Docker, CI/CD pipeline, test suite, or API documentation
- No data license for included anatomy models
