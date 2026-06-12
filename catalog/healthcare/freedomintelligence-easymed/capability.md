# EasyMED Capabilities

EasyMED is a modular multi-agent virtual standardized patient (VSP) framework for medical education. It decomposes clinical history-taking into coordinated agents for patient simulation, intent recognition, and post-consultation educational evaluation. It requires an OpenAI-compatible LLM backend and has no built-in web UI or local model weights.

## Patient Simulation

- A virtual patient agent conducts multi-turn dialogue grounded in a structured case profile
- Patient responses are controlled by an intent recognizer that classifies each learner question into one of 32 clinical intent categories to regulate information disclosure
- Case data is loaded from structured JSON files defining demographics, symptoms, history, physical exam findings, diagnoses, and treatment plans

## Evaluation

- A clinical evaluator provides structured post-session feedback by comparing the learner's collected information against a case reference template
- Scoring covers history-taking completeness (must-ask vs optional items), physical examination requests, auxiliary lab orders, main and differential diagnoses, and treatment plans

## Benchmarking

- SPBench provides a suite of patient case files and question lists for reproducible evaluation of VSP dialogue quality
- Multi-dimension quality scoring covers query comprehension, case consistency, controlled disclosure, response completeness, logical coherence, language naturalness, and patient demeanor

## Execution Modes

- An interactive REPL loop enables turn-by-turn patient consultation
- Batch dialogue generation scripts produce full conversations with or without intent annotations
- Offline trajectory evaluation scores completed conversations against case templates

## Constraints

- Requires Python 3.10 or later
- Requires an OpenAI-compatible LLM backend; no offline or local model support beyond API-compatible servers
- Case data must conform to the patient profile JSON schema; missing fields will break agent grounding
- Intent taxonomy is fixed at 32 categories; custom intents require prompt modification
- No Docker, web UI, REST server, streaming audio/video, or multi-user session management
