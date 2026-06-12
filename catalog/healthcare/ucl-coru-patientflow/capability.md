# PatientFlow Capabilities

PatientFlow is a Python package for real-time prediction of short-term hospital bed demand. It converts patient-level EHR snapshots into aggregate probability distributions over bed counts, helping bed managers anticipate capacity needs within an operational time horizon. It assumes independence between individual patient journeys and is not intended for individual clinical decisions.

## Prediction

- Generates probability distributions over the number of beds needed at configurable prediction times throughout the day
- Computes patient-level admission probability per specialty within a configurable prediction window
- Calculates time-varying arrival rates for patients not yet in the system at configurable time intervals
- Supports hierarchical aggregation from specialty through division to hospital level

## Model Training

- Trains admission and discharge predictive models using XGBoost and scikit-learn from historical EHR snapshots
- Models are trained on point-in-time snapshot extracts, not time-series data
- A synthetic data generator produces fake emergency department records for development and testing without access to real patient data

## Evaluation

- Scoring and comparison functions assess model performance across prediction times and patient subgroups
- Visualization functions produce probability distribution plots and model performance summaries

## Data

- An anonymised dataset of emergency department records from a major London hospital is published on Zenodo for reproducible research
- A conversion utility transforms raw hospital data into the published dataset format

## Constraints

- Requires Python 3.10 or later; not tested on Windows
- Assumes independence between individual patient journeys; correlated admissions violate the Bernoulli sum model
- Designed for short-term operational horizons only (minutes to approximately 24 hours); not for multi-day capacity planning
- Patient-level predictions must not be used to influence clinical decisions about individual patients
- Input must be point-in-time snapshot structures; time-series formats are not accepted
- No REST API, streaming interface, or containerized deployment
