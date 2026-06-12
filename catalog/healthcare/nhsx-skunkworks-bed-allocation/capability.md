# NHS Bed Allocation Capabilities

NHS Bed Allocation is a proof-of-concept machine learning tool developed by the NHS AI Lab for Kettering General Hospital. It suggests optimal bed assignments for incoming patients using constraint-based rules and a greedy allocation agent, presented through a web dashboard. No trained models or real patient data are included in the repository.

## Allocation

- A greedy allocation agent evaluates available beds against ward-level, patient-level, and room-level constraints to suggest placements
- A Monte Carlo Tree Search agent is implemented as an alternative but excluded from the UI due to performance limitations
- Constraints are expressed as binary satisfied/not-satisfied rules; no weighted or soft constraint balancing is supported

## Demand Forecasting

- A time-series model forecasts upcoming patient admissions from historical data
- Forecasts feed into the allocation agent to anticipate bed demand

## Virtual Hospital

- A ward and bed environment model represents the hospital's physical layout
- Several hospital characteristics are hardcoded in the prototype

## User Interface

- A web dashboard displays bed suggestions with constraint satisfaction detail per recommendation
- The UI is the only integration surface; no API layer is exposed

## Data

- A synthetic data generator produces fake admissions records for integration testing
- Real data mode requires user-supplied historical admissions data in the expected format

## Constraints

- Proof-of-concept only; not production-validated or deployed at scale
- Python 3.9 or later required; tested on macOS only
- No trained model artifacts or real patient data included
- MCTS allocation agent excluded from the UI due to performance issues
- No containerized deployment, API layer, or multi-hospital configuration
- Constraint rules are binary only; no weighted balancing or optimization
