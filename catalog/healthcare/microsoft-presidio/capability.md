# Presidio Capabilities

Presidio is a Python SDK and collection of REST microservices for detecting and anonymizing personally identifiable information (PII) in unstructured text, structured data, and raster images. It ships four independent modules — Analyzer, Anonymizer, Image Redactor, and Structured — that can run in-process, as HTTP services, or as batch workloads over Spark. It does not include a UI, an audit trail, or any data-at-rest storage.

## PII Detection

- Detects PII entities in free text using NLP models, regular expressions, rule-based logic, and checksum validators
- Returns a confidence score, entity type, and character offsets for each detected span
- Confidence scores can be boosted when context words surrounding an entity match a configurable list
- NLP backend is swappable between spaCy, HuggingFace Transformers, and Stanza
- Recognizer registry is pluggable — custom recognizers can be added via regex patterns, deny lists, checksums, or ML models
- Language support is per-recognizer and depends on the underlying NLP model

## Anonymization

- Applies operator-based transformations to detected spans: redact, replace, mask, hash, or encrypt
- Operator assignment is configurable per entity type, allowing mixed strategies in a single pass
- Deanonymization is supported only for encryption-based operators; redact, mask, and hash are irreversible
- Structured and semi-structured data (tabular, JSON, nested) is handled by the Structured module independently of the text pipeline

## Image Redaction

- Detects and redacts PII in raster images using OCR to locate text regions
- Supports DICOM medical image format in addition to standard raster formats
- Redaction accuracy is bounded by OCR quality; degraded or low-resolution images may produce missed detections

## Deployment

- Runs as an in-process Python library, as HTTP microservices, or as a PySpark batch workload
- Each of the four modules is independently deployable
- Kubernetes deployment is supported for scaled or production environments
- All services are stateless; no database or persistent storage is included

## Constraints

- Detection does not guarantee complete recall; automated PII identification must be supplemented with additional safeguards for regulatory compliance
- DICOM support is confined to the Image Redactor module; HL7 and FHIR formats are not parsed natively
- Deanonymization is unavailable for destructive operators (redact, hash, mask)
- Not all entity types are available in all languages; coverage depends on the NLP model selected for each recognizer
- No audit log or decision trail is produced for anonymization actions
- No synthetic data generation; the tool de-identifies existing data but does not fabricate replacement records
