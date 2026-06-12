# Epivizor Capabilities

Epivizor is a Flask-based web application for interactive genomic epidemiology data visualization, built by the Public Health Agency of Canada's National Microbiology Laboratory. It supports outbreak hypothesis generation through dashboard-style metadata exploration with interactive charts and a compare-and-contrast mode for filtered data subsets. It has no authentication layer; access control must be handled externally.

## Data Visualization

- Interactive Plotly charts render epidemiological metadata across multiple dimensions
- A compare-and-contrast mode enables simultaneous visual analysis of two filtered data subsets
- Statistical computations via SciPy support quantitative comparison between groups

## Data Ingestion

- Accepts tabular data from Excel files (XLSX format) via openpyxl and xlrd
- Pandas handles data transformation and filtering
- High-performance JSON serialization with orjson

## Caching and Sessions

- Filesystem-based caching reduces repeated computation for dashboard interactions
- Server-side session management tracks user filter state across requests
- Response compression reduces payload sizes for browser delivery

## Deployment

- A Docker container packages the application with a Flask development server
- A production uWSGI configuration runs multiple processes and threads with extended timeouts for large datasets

## Constraints

- No authentication or authorization layer; relies on network-level access control
- The session secret key is regenerated on each application startup; all active sessions are invalidated on restart or container recreation
- No HTTPS or TLS termination in the provided configuration; must be handled by an upstream proxy
- No docker-compose or multi-container orchestration provided
- No structured logging beyond uWSGI daemon log files
