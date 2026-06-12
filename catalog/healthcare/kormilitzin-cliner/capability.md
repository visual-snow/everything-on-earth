# CliNER Capabilities

CliNER is an open-source Python NLP system for clinical named entity recognition in electronic health record text. It implements the i2b2 2010 shared task annotation schema, classifying each token into Problem, Test, Treatment, or None using IOB-style sequence labeling with CRF or LSTM models. The project has been unmaintained since 2018.

## Entity Recognition

- Identifies and classifies clinical named entities in free-text clinical notes
- Supports two model architectures: a CRF classifier with linguistic and domain-specific features, and an LSTM sequence classifier
- Entity types follow the i2b2 2010 schema: Problem, Treatment, and Test

## Knowledge Integration

- Optionally integrates UMLS Metathesaurus knowledge tables for enhanced feature extraction
- GENIA biomedical tagger integration provides part-of-speech and chunk features from the biomedical domain
- A pre-trained silver model built on MIMIC-II data is available for immediate use without i2b2 data access

## Workflow

- Train mode builds a model from paired plaintext and i2b2 annotation files
- Predict mode applies a trained model to new documents and produces annotation output files
- Evaluate mode scores predictions against gold-standard annotations with precision, recall, and F1 metrics

## Constraints

- A UMLS license from the National Library of Medicine is required for optimal CRF feature extraction; without it, recognition performance degrades
- i2b2 data licensing prohibits redistribution of models trained on i2b2 datasets; only the MIMIC-II silver model is publicly available
- The UMLS database is built from raw RRF tables on first run, requiring substantial disk space and processing time
- The GENIA tagger must be compiled from C++ source before CliNER can use it as a feature extractor
- Unmaintained since 2018; compatibility with current Python packaging ecosystem is not guaranteed
- Only the i2b2 annotation format is supported; no BRAT, CoNLL, or other NER annotation formats
- No REST API, web interface, or containerized deployment; CLI-only operation
