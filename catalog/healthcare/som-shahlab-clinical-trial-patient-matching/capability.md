# Clinical Trial Patient Matching Capabilities

Clinical Trial Patient Matching is a research framework for zero-shot matching of patients to clinical trial eligibility criteria using large language models. It is evaluated on the n2c2 2018 cohort selection challenge and benchmarks prompt strategies, retrieval pipelines, and multiple LLM backends. It operates on free-text clinical notes only; no structured data input is supported.

## Matching Pipeline

- Evaluates whether patients meet trial eligibility criteria based on their clinical notes
- Supports four prompt strategies combining all-criteria vs each-criterion with all-notes vs each-note approaches
- Retrieval-augmented mode uses vector embeddings to select the most relevant note chunks before prompting the LLM
- Full-note mode passes entire patient records to the model without chunking

## LLM Backends

- Supports Azure OpenAI endpoints for GPT-4 and GPT-3.5 models
- Supports open-source models via Hugging Face vLLM with tensor parallelism for large parameter counts
- Multiple models can be benchmarked across the same evaluation harness

## Evaluation

- Produces per-criterion precision, recall, and F1 scores against the n2c2 2018 benchmark
- Ablation studies cover prompt strategy, criterion definitions, rationale inclusion, retrieval depth, and few-shot example count

## Retrieval

- Builds a vector embedding database from patient notes using configurable embedding models
- Supports selectable retrieval depth controlling how many note chunks are fed to the LLM per query

## Constraints

- Requires credentialed access to the n2c2 2018 cohort selection dataset; data is not redistributed
- Azure OpenAI endpoints are institution-specific and require configuration adaptation for other deployments
- Large open-source models require multi-GPU setups with tensor parallelism
- Python 3.10 required; batch evaluation only with no streaming or real-time inference
- No FHIR, HL7, or structured data input; operates exclusively on free-text clinical notes
- No REST API, web UI, or containerized deployment
