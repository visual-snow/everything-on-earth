# cnlp_transformers Capabilities

cnlp_transformers is a Python library that adds clinical NLP abstractions on top of Hugging Face Transformers. It supports fine-tuning and inference for classification, sequence tagging, and relation extraction on clinical text, and provides a REST API for serving trained models. It is research-oriented and not designed for production-scale deployment.

## Training

- Fine-tunes transformer models on labelled clinical text datasets via a CLI
- Supports multi-task learning with multiple classification or tagging targets trained jointly
- Includes hierarchical transformer, CNN, and LSTM model architectures as alternatives to standard encoders
- Multi-head attention is available for end-to-end temporal information extraction
- Encoder weights can be fully or partially frozen during fine-tuning

## Inference

- A REST endpoint accepts clinical text and returns per-class probability scores for all configured tasks
- Multiple models can be served simultaneously with router prefixes to separate endpoints
- Models are loaded from Hugging Face Hub by repository ID or from a local directory
- Pre-built container images are available for deployment

## Task Types

- Text classification assigns document-level or sentence-level labels
- Sequence tagging assigns per-token labels aligned to space-delimited input text
- Relation extraction identifies relationships between marked entity spans
- Token-level classification uses XML-style entity tags in the input to identify target spans

## Constraints

- Research-oriented; not intended for production-scale processing of large record volumes
- The hierarchical model requires a small encoder to fit within GPU memory constraints
- Token-based classification requires XML entity markers in the input text
- Tagging targets must be space-delimited labels aligned one-per-token to the input
- No built-in data anonymization, batch pipeline, or API authentication
