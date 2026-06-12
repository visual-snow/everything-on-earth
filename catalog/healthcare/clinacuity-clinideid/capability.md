# CliniDeID Capabilities

CliniDeID is a Java desktop application that automatically de-identifies clinical text notes according to the HIPAA Safe Harbor method. It uses an ensemble of machine learning models (SVM, MIRA, and RNN) to detect protected health information and replaces identified entities with realistic surrogates that maintain consistency across an entire patient record. Pre-trained models must be downloaded separately and are licensed for non-commercial use only.

## De-identification

- Detects PHI entities in clinical text using an ensemble voting system across multiple model architectures
- SVM and MIRA classifiers are functional in the current release; the RNN component is disabled in the beta
- Identified entities can be replaced with generic category tags or with realistic surrogate values
- Surrogate replacement maintains consistency across all documents in a patient's record

## Input Formats

- Processes plain text clinical notes
- Supports HL7 CDA (Clinical Document Architecture) documents
- Can read from relational databases via JDBC (PostgreSQL, MySQL, DB2)

## Interfaces

- A JavaFX graphical interface provides interactive document review and de-identification
- A command-line runner enables batch processing without the GUI

## Validation

- Accuracy benchmarked against i2b2 2006, 2014, and 2016 de-identification challenge corpora
- Comparative performance studies published against other de-identification tools

## Constraints

- Requires Java JDK 17 or newer; Apple M1/M2 requires Azul Zulu OpenJDK builds
- 28 GB of JVM heap memory is required at runtime
- Pre-trained models are licensed for non-commercial use only and must be downloaded from external hosting before first run
- The RNN model component is disabled in the current beta due to Python environment issues
- No Docker, REST API, or service deployment mode; strictly local desktop operation
