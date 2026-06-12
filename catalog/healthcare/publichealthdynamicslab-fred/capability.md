# FRED Capabilities

FRED (A Framework for Reconstructing Epidemiological Dynamics) is a C++17 agent-based modeling framework for simulating the spread of infectious diseases through synthetic, geolocated populations. It was developed at the University of Pittsburgh and models individual-level transmission dynamics across households, schools, workplaces, and other mixing locations. The public repository is licensed for non-commercial use only.

## Agent-Based Simulation

- Individual agents carry demographic attributes (age, sex, race, income) and per-condition disease states
- Agents move through typed locations (households, neighborhoods, schools, classrooms, workplaces, offices, hospitals, group quarters)
- Disease conditions are defined with configurable transmissibility, state spaces, and transition rules

## Transmission Modes

- Proximity-based transmission occurs between co-located agents within places
- Network-based transmission operates over social contact networks
- Environmental transmission models indirect routes of infection
- Multiple conditions can be simulated simultaneously with independent transmission dynamics

## Population

- Synthetic U.S. populations based on 2010 Census and American Community Survey data are downloadable by county or state FIPS code
- Each synthetic person is geolocated and assigned to household, school, and workplace locations

## Execution

- Multi-run ensemble mode launches replicate stochastic simulations in parallel for uncertainty quantification
- OpenMP threading enables within-run parallelism for large populations
- Helper scripts manage job submission, statistics aggregation, and gnuplot-based time-series visualization

## Spatial Visualization

- A configurable grid overlay collects per-patch case counts and population sizes
- Visualization data is written at regular intervals for external mapping or animation tools

## Constraints

- No Docker images; requires manual C++17 compilation on macOS or Linux; Windows is unsupported
- Maximum thread count must be set at compile time; cannot be increased at runtime
- Synthetic populations cover U.S. geographies only (2010 Census); non-U.S. populations must be constructed externally
- Licensed for non-commercial, educational, or research use only; commercial use requires the separate Epistemix product
- The public repository lags behind the private University of Pittsburgh version
- Perl, Python, and gnuplot runtimes are required for run management and plotting scripts
- No vaccination module is present in the public source code
