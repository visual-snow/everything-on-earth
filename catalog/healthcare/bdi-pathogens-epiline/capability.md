# EpiLine Capabilities

EpiLine is an R package for simultaneously estimating epidemic curves and symptom-to-report delay distributions from case time-series and line list data. It uses Bayesian inference via Stan, correcting for right-censoring, reporting lags, and underlying infection dynamics. It operates entirely within an R session with no web interface or API.

## Epidemic Curve Estimation

- Models daily symptom-onset counts with a Gaussian-process growth rate that varies over time
- Reported case counts are modelled with a negative binomial distribution allowing for overdispersion
- Symptom-to-report delay is parameterised as a time-varying Johnson SU distribution with four parameters each following a Gaussian process

## Simulation

- A simulator generates synthetic reported case counts and line list data under the model assumptions
- Simulated data can be used to validate the fitting procedure and explore sensitivity to parameter choices

## Inference

- Full Bayesian posterior sampling via Stan MCMC produces credible intervals for all model parameters
- Posterior quantiles of the delay distribution are tracked over the reporting period
- A static-tail mode freezes delay distribution parameters after a configurable cutoff day to handle right-truncation at the end of the observation window

## Visualization

- Plot methods on the fitted object display symptom-onset curves, growth rate trajectories, delay distribution evolution, and delay quantiles over time

## Constraints

- Line-list report dates must fall within the supplied reporting period; out-of-range values are not handled
- Cases with only a report date and no symptom date must be excluded from the line list but included in daily totals
- Requires Stan code compilation at package install time along with rstan and related dependencies
- Default MCMC settings are insufficient for reliable inference; production runs need substantially more iterations and chains
- No incubation period or infection-to-symptom delay modelling; only symptom-to-report delay is estimated
- No multi-pathogen, multi-region, or hierarchical modelling capability
