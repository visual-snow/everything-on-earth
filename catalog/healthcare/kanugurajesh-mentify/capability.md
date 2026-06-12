# Mentify Capabilities

Mentify is a Next.js web application providing AI-powered mental health support. It combines an LLM-backed chat counselor, mental health self-assessment tests with animated feedback, image-based symptom recognition, and personalized wellness recommendations. All AI inference is cloud-dependent via external APIs; no self-hosted model option is available. The project is a demo/prototype with no clinical validation.

## AI Chat Counselor

- A conversational therapy interface powered by a generative language model responds to user mental health concerns
- Conversations are conducted through a web-based chat interface

## Self-Assessment

- Mental health questionnaires produce a stage-classified score reflecting the user's current state
- An animated character provides visual feedback reflecting test result quality
- A reward and notification system encourages proactive health engagement

## Image Recognition

- Users can upload symptom photographs for AI-based recognition and guidance
- An image manipulation feature supports visualization exercises

## Document Analysis

- Medical history documents can be uploaded for AI-powered question-and-answer interaction
- A file upload service handles document storage

## Content

- A mental health blog provides educational articles and wellness resources
- A contact form allows users to reach out for additional support

## Constraints

- Requires external API keys for the language model, image processing, file upload, and email services; not self-contained
- No offline or air-gapped operation; all AI features depend on cloud API availability
- No clinical validation, regulatory approval, or HIPAA compliance documentation
- No database schema or persistent data storage layer documented
- No automated test suite or CI/CD configuration
- Docker instructions in the repository reference a different project and may not work correctly
