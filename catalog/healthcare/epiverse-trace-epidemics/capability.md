# epiverse-trace/epidemics Capabilities

epiverse-trace/epidemics is an R package that collects published deterministic and stochastic compartmental epidemic models under a unified interface. It provides first-class classes for demographic structure, non-pharmaceutical interventions, and vaccination regimes so that analysts can compose and compare outbreak scenarios programmatically. It is not a general ODE solver, a Bayesian inference engine, or a spatial transmission model.

## Models

- A deterministic SEIR-V model solved via ODE integration serves as the general-purpose baseline
- A deterministic model parameterised for COVID-19 includes explicit vaccine and waning compartments
- A stochastic discrete-time SEIR model handles Ebola-like haemorrhagic fever dynamics
- A disease-specific compartmental model covers diphtheria outbreaks

## Scenario Composition

- A population class defines contact matrix, age groups, and initial compartment sizes
- An intervention class represents NPIs as time-bounded reductions in transmission or contacts
- A vaccination class encodes dose schedules and coverage fractions over time
- Baseline vs intervention comparison by passing or omitting intervention and vaccination objects to any model function
- Multiple scenarios can be run and collected for side-by-side analysis

## Simulation Modes

- Deterministic ODE integration for the SEIR-V, Vacamole, and diphtheria models
- Stochastic discrete-time simulation for the Ebola model with replicate runs to characterise uncertainty
- Output is a tidy data frame of compartment sizes over time

## Constraints

- Directly transmitted infections only; vector-borne or environmental transmission routes are not supported
- API is under active development and may change between releases; not yet stable for long-lived production pipelines
- No spatial or network transmission models; population is treated as a single well-mixed group per demographic stratum
- No Bayesian or MCMC parameter fitting; parameter values must be supplied externally
- No surveillance data ingestion; observed case counts cannot be fed directly into model calibration
- Requires R with a C++ toolchain; Windows users need RTools installed
