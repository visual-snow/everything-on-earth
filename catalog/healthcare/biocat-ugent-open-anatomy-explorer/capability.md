# Open-Anatomy-Explorer

Open-Anatomy-Explorer is a web-based 3D anatomy atlas that lets students browse and quiz on anatomical models, and lets instructors upload, label, create quizzes, and share models across institutions. The frontend renders models in the browser via WebGL; the backend enforces role-based access through Keycloak OIDC and stores model data in MongoDB. There is no docker-compose for local development, no DICOM ingestion pipeline, and no CI/CD configuration included.

## Student Mode

- Browse a catalogue of published anatomical models rendered in 3D via WebGL
- Rotate, pan, and zoom models; select labelled structures to view their names
- Attempt quizzes that test structure identification against instructor-defined answer sets
- Access is scoped to the institution's Keycloak realm; cross-institution sharing requires explicit model export/import by an instructor

## Instructor Mode

- Upload 3D model assets and assign anatomical labels to individual structures
- Create quizzes from labelled models and configure pass/fail thresholds
- Export model packages for transfer to other institutions; import packages shared by peers
- Manage published models and student access through the Angular admin UI

## Authentication and Access Control

- All access flows through Keycloak OIDC; the application consumes ID tokens and enforces role claims
- Student and instructor roles must be assigned manually inside the Keycloak realm console
- OIDC client configuration in Keycloak requires the redirect URIs and client secret to be set before first use
- REST API endpoints on the Quarkus backend validate bearer tokens on every request

## Deployment

- Runs on Kubernetes; ingress controller and dynamic persistent volume provisioning are required
- Container images must be built from source before deployment; no pre-built images are distributed
- MongoDB is used for model metadata and quiz results; persistent volumes back model file storage
- No local development path exists outside a Kubernetes cluster

## Constraints

- DICOM ingestion is not supported; models must be prepared in a compatible 3D format before upload
- Keycloak realm, roles, and client configuration require manual setup with no automated provisioning
- No CI/CD pipeline or automated test suite is bundled with the repository
