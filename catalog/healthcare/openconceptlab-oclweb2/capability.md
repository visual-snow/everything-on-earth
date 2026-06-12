# OCL TermBrowser v2 Capabilities

OCL TermBrowser v2 is a React-based web client for browsing, managing, and comparing health terminology concepts and mappings. It serves as the front end for the Open Concept Lab, targeting clinical terminologists and implementers working with FHIR, SNOMED, LOINC, and similar code systems. It requires a running OCL API server and has no offline or embedded mode.

## Terminology Browsing

- Searches and navigates concepts, sources, collections, and mappings across multiple terminology systems
- Displays concept relationships as interactive graph visualizations
- Supports side-by-side version comparison of concepts and sources
- Rich-text editing for concept descriptions and notes

## Management

- Drag-and-drop list management for organizing concept collections
- Internationalised interface supporting multiple display languages
- Raw JSON inspection and editing of terminology resources

## Authentication and Analytics

- Single sign-on via OpenID Connect with an external identity provider
- Session analytics and error tracking provide operational visibility into browser usage
- CAPTCHA integration for public-facing forms

## Deployment

- Ships as a containerized application serving a production build
- A development mode enables live-reload and a component design explorer for contributors
- Production deployments are managed through an external CI/CD pipeline

## Constraints

- Requires a running OCL API server reachable over HTTP; no offline or standalone mode
- Single sign-on requires an external identity provider with valid OIDC client credentials
- No bundled API server, database, or identity provider; all backend services must be provisioned separately
- No automated end-to-end test suite in the deployment configuration
