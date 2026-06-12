# DOME Capabilities

DOME is a transformer-based Python framework for de-identifying protected health information in German clinical documents. It uses encoder-based NER models to detect PHI entities and applies configurable per-entity actions: redact, replace with structured tags, shift dates and ages, or keep unchanged. Model weights are not included; users must supply their own fine-tuned HuggingFace-compatible model.

## De-identification

- Detects PHI entities in clinical free text using a transformer-based sequence labeling model
- Redaction replaces each character of detected PHI with a masking character
- Replacement substitutes PHI with a structured tag encoding the category and type
- Date and age shifting offsets values by a configurable integer to preserve temporal relationships while obscuring absolute dates
- Keep mode leaves specified PHI types untouched in the output

## Training

- Fine-tunes transformer models on annotated clinical datasets formatted as UIMA CAS XMI files
- Requires a typesystem definition conforming to the repository's schema

## Evaluation

- Computes token-level precision, recall, and F1 per PHI type against ground-truth annotations
- Results are written as CSV for downstream analysis

## Constraints

- No pre-trained or fine-tuned model weights are distributed; a HuggingFace-compatible model must be placed in the model directory before inference
- GPU runtime required; the container runs with NVIDIA Docker runtime and elevated memory limits
- Training data must be formatted as UIMA CAS XMI files; arbitrary annotation formats are not supported
- Shift mode is only meaningful for Date and Age PHI types
- Currently targets German clinical text; no multilingual or English model is publicly available
- No REST API, streaming interface, or CPU-only inference path documented
