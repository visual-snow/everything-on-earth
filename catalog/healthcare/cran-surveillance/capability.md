# cran/surveillance Capabilities

cran/surveillance is an R package for statistical surveillance of infectious disease count data. It covers temporal and spatio-temporal modeling, prospective outbreak detection, and reporting-delay adjustment. It operates entirely within an R session; there is no web interface, REST API, or standalone service.

## Outbreak Detection
- Prospective monitoring algorithms flag when observed case counts exceed alarm thresholds derived from historical baselines.
- Multiple detection algorithms are available, suited to different distributional assumptions and data sparsity conditions.
- Categorical and count-based detection approaches are both supported.

## Endemic-Epidemic Modeling
- A multivariate regression framework decomposes case counts into endemic, autoregressive, and neighbourhood-spread components across regions and time.
- A self-exciting spatio-temporal point process model captures event clustering in continuous space and time.
- A fixed-population event-history model handles individual-level transmission data.

## Nowcasting
- Reporting-delay adjustment produces corrected case counts and prediction intervals for the most recent, incompletely reported time periods.
- Backprojection is available for reconstructing past incidence from delayed observations.

## Evaluation and Scoring
- Probabilistic forecast quality is assessed via proper scoring rules: Dawid-Sebastiani Score, Log Score, and Ranked Probability Score.
- Calibration tests evaluate whether predictive distributions are consistent with observed outcomes.
- One-step-ahead predictive distributions support rolling forecast evaluation.

## Visualization
- Temporal, spatial, and spatio-temporal plots summarize surveillance time series and spatial case distributions.
- Animation of outbreak spread over time is supported.

## Constraints
- Runs only within R; no Python bindings, command-line binary, or network interface.
- The multivariate endemic-epidemic model requires at least one prior time point; the first observation cannot be modeled.
- Bayesian nowcasting requires a separately installed external sampler.
- No contact tracing, phylogenetic, genomic, or clinical record analysis.
- No built-in dashboard or web UI.
