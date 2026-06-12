# ggsurveillance Capabilities

ggsurveillance is an R package providing ggplot2 extensions and tidy utility functions for infectious disease surveillance and outbreak investigation. It adds epidemic curve geoms, date-based aggregation helpers, and specialized epidemiological visualizations to the tidyverse ecosystem. It is purely a visualization library; no statistical modelling or data ingestion is included.

## Epidemic Curves

- A dedicated geom renders case-count bars binned by configurable date intervals (day, week, ISO week, month, quarter, year)
- Date-interval binning aligns to reporting-week boundaries for consistent surveillance reporting
- Annotation geoms add text labels and point markers to epidemic curves
- Year-boundary vertical lines are auto-detected and drawn

## Seasonal Analysis

- A date-alignment function overlays multiple seasons of surveillance data on a common axis
- Seasonal overlay plots show historical median, interquartile range, and min/max ribbons for comparison against the current season

## Contact Tracing Visualization

- A Gantt-style geom displays overlapping exposure intervals for individuals on a horizontal timeline
- Suitable for visualizing ward stays, exposure windows, and isolation periods in outbreak investigations

## Diverging Charts

- Diverging bar and area geoms produce population pyramids, vaccination-status breakdowns, and Likert-scale charts
- Label geoms and a symmetric diverging scale provide count or percentage annotations

## Utilities

- Reproducible age-group labeling, geometric mean computation, and count expansion helpers complement the visualization geoms
- Nested date axis guides display hierarchical year-month-day labels
- Composable theme modifier functions adjust legend position, axis rotation, and grid visibility

## Constraints

- Requires R with ggplot2 and the tidyverse; not available outside the R ecosystem
- Date binning depends on locale-correct ISO week definitions; mixing ISO weeks and epidemiological weeks can produce misaligned bins
- The Gantt geom requires data in long format with explicit start and end date columns
- Lifecycle status is experimental; the API may change between releases
- No data ingestion from surveillance databases, statistical modelling, interactive output, or spatial map geoms
