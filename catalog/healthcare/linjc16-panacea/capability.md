# Panacea Capabilities

Panacea is a 7-billion-parameter language model fine-tuned for clinical trial workflows. It covers trial design, patient-trial matching, trial search, and trial summarization across eight distinct tasks. The model weights are hosted on Hugging Face and training requires downloading three separate datasets.

## Trial Design

- Generates structured clinical trial protocol elements from natural language descriptions
- Covers eligibility criteria formulation and study design components

## Patient-Trial Matching

- Classifies whether a patient matches a given trial's eligibility criteria
- Evaluation scripts produce per-task classification metrics

## Trial Search

- Retrieves relevant clinical trials based on patient descriptions or disease conditions

## Trial Summarization

- Produces concise summaries of clinical trial records

## Training Pipeline

- A two-stage training process begins with domain vocabulary alignment using the TrialAlign dataset, followed by supervised fine-tuning using TrialInstruct
- The TrialPanorama dataset serves as the evaluation benchmark across all eight tasks
- A Gradio-based demo interface is included for interactive exploration

## Constraints

- Requires a GPU with sufficient VRAM to load and run a 7B-parameter model
- Three external datasets (TrialAlign, TrialInstruct, TrialPanorama) must be downloaded from Hugging Face and Figshare before training can begin
- No REST API server or web deployment; inference is script-driven only
- No containerized deployment or CI pipeline
