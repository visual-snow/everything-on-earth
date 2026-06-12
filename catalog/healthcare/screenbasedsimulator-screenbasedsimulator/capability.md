# ScreenBasedSimulator Capabilities

ScreenBasedSimulator is a screen-based clinical simulation platform for medical students to practice emergency scenario response. It was built by Carnegie Mellon University graduate students in partnership with WISER and integrates the BioGears human physiology engine for realistic patient modeling. The project is an MVP-stage prototype last updated in 2015.

## Simulation

- Scenario-based emergency training presents clinical situations requiring real-time decision-making
- The BioGears physiology engine provides realistic patient physiological responses to interventions
- Self-paced remote practice allows students to train outside of clinical settings

## Architecture

- A Java backend server handles simulation logic and scenario management
- A Unity-based client provides the user-facing simulation interface
- Patient and scenario data is stored in a MySQL database

## Constraints

- Requires a Java runtime and MySQL database
- The Unity client requires a Unity runtime to operate
- The BioGears physiology engine is an external dependency not bundled in the repository
- MVP-stage prototype with no formal releases; last commit in 2015
- No scenario authoring tooling, assessment/scoring system, or API documentation
- No authentication, multi-user management, containerized deployment, or CI pipeline
