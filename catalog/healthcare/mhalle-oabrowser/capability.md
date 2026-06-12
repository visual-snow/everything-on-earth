# Open Anatomy Browser Capabilities

The Open Anatomy Browser (OABrowser) is a browser-based 3D viewer for anatomy atlases. It renders surface meshes and volumetric slices from a structured JSON atlas descriptor using WebGL. It is a purely static front-end application with no server-side component; atlas data must be served over HTTP.

## 3D Rendering

- Displays anatomy models from VTK, STL, and OBJ surface mesh formats
- Renders volumetric data from NRRD files as composited coronal, sagittal, and axial slices
- WebGL-based rendering with trackball camera controls for rotation, zoom, and pan

## Atlas Navigation

- Parses a JSON atlas descriptor defining the hierarchical structure of anatomical regions
- Allows selection and isolation of individual anatomical structures within the hierarchy
- Supports undo and redo for view state changes
- Provides screenshot capture of the current 3D scene

## Collaboration

- Shared view state synchronization via a real-time database backend
- Collaborative sessions are accessible via shareable URLs
- Authentication supports OAuth providers including Google, GitHub, Twitter, and Facebook

## Constraints

- Requires WebGL support in the browser; displays a fallback message if absent
- Atlas data must be served over HTTP or HTTPS; direct local file access is not supported
- The real-time database SDK is pinned to a legacy version with hard-coded project credentials
- The 3D rendering library is pinned to a legacy version; mesh loaders are bundled locally rather than managed as packages
- No server-side component, test suite, CI/CD configuration, or containerized deployment
- Last updated in 2018; no active maintenance
