# Niramaya Capabilities

Niramaya is a Flutter mobile application for mental health monitoring, built as a 2024 hackathon project. It provides an AI-driven virtual therapy chatbot, diary-based mood analysis, camera-based facial emotion detection, standardized self-diagnosis questionnaires, and medication and sleep reminders. The backend uses Django with Google Gemini for generative AI and DeepFace for emotion recognition. Android only; hackathon prototype with no clinical validation.

## AI Chatbot

- A conversational virtual therapist provides mental health guidance powered by a generative language model
- Responses are generated contextually based on user input

## Mood Analysis

- A diary feature accepts free-text entries and generates mental health reports via AI analysis
- Average mood scores are computed from interactive mood-guessing game sessions

## Emotion Detection

- Camera-based facial emotion detection identifies discrete emotion labels from the device camera
- The emotion recognition service runs on a local Django server tunneled via Ngrok; no persistent cloud endpoint exists

## Self-Assessment

- Standardized mental health diagnosis questionnaires for specific conditions
- India-specific helpline numbers and mental health resource links are provided

## Reminders

- Medication and sleep reminders via local device notifications

## Constraints

- Emotion recognition requires a locally running Django server exposed through Ngrok; no production deployment exists for this feature
- Android only; no iOS or web client documented
- Hackathon prototype; not production-hardened or clinically validated
- India-specific helpline resources; no internationalization
- No Docker, automated tests, CI pipeline, or HIPAA/privacy compliance documentation
