# AI Therapist Capabilities

AI Therapist is a Next.js web application that provides AI-powered mental wellness conversations. It uses the OpenAI GPT API with streaming responses, persists private chat history per authenticated user in a relational database, and caches responses via a Redis layer for latency optimization. All inference is cloud-dependent; no self-hosted model option is available.

## Conversation

- A streaming chat interface delivers real-time AI responses as the model generates them
- Conversation history is persisted per user, allowing users to return to previous sessions
- The AI is configured for empathetic mental wellness dialogue

## Authentication and Privacy

- User authentication and session management are handled by an external identity service
- Each user's conversation history is private and isolated

## Infrastructure

- A relational database stores conversation records via an ORM with migration support
- A Redis cache reduces response latency for repeated or similar queries
- The application deploys to a serverless hosting platform

## Constraints

- Requires external managed services for the database, Redis cache, and authentication; not self-contained
- No offline or local-model mode; all inference routes through the OpenAI API
- The database must be migrated before the first application run
- No containerized deployment configuration; assumes a serverless hosting platform
- No crisis intervention safeguards, clinical disclaimers, or rate limiting documented
- No end-to-end encryption for conversation data at rest
- No automated test suite
