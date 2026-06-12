# DHIS2 Analytics Capabilities

DHIS2 Analytics is a shared React component and utility library that powers the analytics applications within the DHIS2 health information platform. It provides reusable UI components for data dimensions, period selection, organization unit trees, pivot tables, visualization options, and interpretation workflows. It is a front-end library with no standalone server or backend of its own.

## Dimension Management

- Data, period, and organization unit dimension selectors with drag-and-drop panel layout
- Dynamic dimension support beyond the three fixed dimensions
- Period selector covers daily, weekly, monthly, quarterly, and yearly granularities including fiscal-year variants and alternative calendar systems

## Visualization

- Supports column, bar, line, area, pie, radar, gauge, and bubble chart types
- Year-over-year comparison, single-value display, scatter plot, and outlier table modes
- Pivot table rendering for tabular data exploration
- Line listing mode for individual-level record display
- Font styles, color sets (including color-blind-safe palettes), and legend display are configurable per visualization

## Collaboration

- Interpretation and comment workflows allow users to annotate and discuss saved analytics objects
- File management dialogs support save, rename, delete, and sharing link operations
- Rich-text formatting for interpretation content

## Layout

- Layout objects define which dimensions appear in columns, rows, and filters
- Visualization type constants and layout type constants standardize configuration across consuming applications

## Constraints

- Host application must supply all peer dependencies including React, the DHIS2 application runtime, and the DHIS2 UI framework
- Chart rendering delegates entirely to Highcharts; Highcharts license terms apply to any deployment
- API helpers require a live DHIS2 instance reachable via the application runtime context
- No standalone server, backend component, or authentication logic; all are provided by the host application
- No Docker or containerized deployment; distributed as an npm package only
