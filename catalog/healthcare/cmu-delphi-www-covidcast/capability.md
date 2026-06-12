# COVIDcast Dashboard Capabilities

The COVIDcast Dashboard is a Svelte-based interactive web application that visualizes COVID-19 epidemiological signals and predictions across US geographic regions. It serves as the front end for the COVIDcast website, consuming data from the Delphi Epidata API. It is a pure client-side application with no backend component of its own.

## Visualization

- Displays interactive maps and charts of COVID-19 indicators including cases, deaths, symptom surveys, claims-based illness estimates, and mobility signals
- Supports geographic drill-down across counties, states, metropolitan areas, and other US geographic aggregations
- Temporal navigation allows exploration of signal trends and model predictions over time

## Development

- A local development server enables iterative development with hot reloading
- End-to-end tests using Cypress validate dashboard functionality against the running application
- A CI pipeline runs linting, unit tests, and builds on each commit
- A one-click cloud development environment is available for contributors

## Deployment

- Production builds are deployed to a static hosting platform
- Separate stable and development deployment branches are maintained

## Constraints

- Requires Node.js and npm for development and builds
- End-to-end tests require the development server to be running in a separate process
- US geographic coverage only; no international data visualization
- No containerized deployment configuration
- No documented environment variable or data-source configuration in the repository
