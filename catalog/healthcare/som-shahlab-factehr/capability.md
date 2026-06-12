# FactEHR Capabilities

FactEHR is a benchmark dataset and evaluation pipeline for assessing large language model factual reasoning over clinical notes. It covers two tasks: fact decomposition (breaking notes into atomic facts) and NLI-style entailment evaluation (verifying whether facts are supported by or support the source text). Published at MLHC 2025 by Stanford SHAHLAB. Evaluation only; no model training code is included.

## Dataset

- 2,168 de-identified clinical notes drawn from MIMIC-CXR, MIMIC-III, MedAlign, and CORAL
- 8,665 LLM-generated fact decompositions breaking each note into atomic statements
- Over 490,000 precision entailment pairs (note entails fact) and 495,000 recall entailment pairs (fact list entails sentence)
- 1,036 expert-annotated entailment labels for calibrating automated judgments against human ground truth

## Evaluation

- Precision scoring measures what fraction of generated facts are entailed by the source note
- Recall scoring measures what fraction of note sentences are entailed by the generated fact list
- LLM-as-a-judge mode uses any supported language model to score entailment pairs end-to-end
- NLI prompt tuning ablates across entailment-only, rationale, and chain-of-thought prompt formats
- Calibration against 1,036 expert annotations validates automated scoring quality

## Inference Backends

- Supports Google Vertex AI, Azure OpenAI (HIPAA-compliant path), Amazon Bedrock, OpenAI Batch API, and local HuggingFace Transformers
- Batch inference can be parallelized across multiple terminal sessions

## Constraints

- Data use agreements prohibit transmitting clinical notes to non-HIPAA-compliant commercial APIs
- PhysioNet credentialed account with signed data use agreements required for MIMIC data access
- Stanford VPN required for SHC dataset access; MedAlign requires manual download from Stanford Redivis
- Evaluation only; no model training, fine-tuning, or de-identification pipeline included
- No Docker, web UI, or interactive demo; entirely CLI and script-driven
