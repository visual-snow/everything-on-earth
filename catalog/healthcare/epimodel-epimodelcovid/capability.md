# EpiModelCOVID Capabilities

EpiModelCOVID is an R package extending EpiModel to simulate SARS-CoV-2 transmission dynamics over dynamic contact networks using temporal exponential-family random graph models (tERGM). It provides modular, individual-based stochastic simulation for specific epidemiological settings such as cruise ships and corporate offices. It operates entirely within an R session with no web interface or API.

## Transmission

- Stochastic per-contact transmission across discordant edges in multi-layer bipartite networks
- Transmission probability is configurable per dyad type with relative infectivity multipliers for asymptomatic individuals
- Timed intervention parameters reduce transmission probability or contact rates at specified simulation steps to model non-pharmaceutical interventions

## Disease Progression

- An extended SEIR compartment chain tracks susceptible, exposed, asymptomatic, pre-clinical, clinical, recovered, and hospitalized states
- Transition rates between compartments are configurable with age-stratified clinical probability vectors
- Age-indexed mortality applies disease multipliers to clinically ill individuals

## Diagnosis

- A PCR diagnosis module supports symptomatic and surveillance testing arms with configurable sensitivity
- Rescreening of previously negative individuals can be toggled on or off

## Vaccination

- A two-dose vaccination module tracks uptake by age group with configurable dose intervals and immunity-onset lags
- Vaccine efficacy reduces the probability of clinical disease

## Network Dynamics

- Dynamic networks are resimulated at each time step using tERGM fitted from empirical contact data
- A lockdown time parameter switches the active network layer set mid-simulation to model structural contact reduction

## Setting Modules

- A ship module simulates closed populations of passengers and crew across six bipartite network layers with pre/post-lockdown switching
- A corporate module simulates office workforces with hospitalization compartments and two-dose vaccination

## Constraints

- Requires R 4.1.0 or later and EpiModel 2.4.0 or later with compatible Statnet packages
- No spatial or metapopulation structure; geographic heterogeneity must be encoded in separate network layers
- PCR sensitivity is uniform; no within-host viral-load trajectory or test-timing model
- Vaccination is limited to two-dose regimens with no waning immunity, reinfection, or booster support
- No variant-specific parameterization for fitness differentials
- No built-in parameter calibration, MCMC fitting, or containerized runtime
