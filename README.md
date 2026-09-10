# Vertex AI Gemini Agent Chatbot

A deployable AI agent application built with **Google Vertex AI Gemini**, **Firestore**, and **Cloud Run**. It demonstrates persistent conversational memory, controlled tool execution, API design, and practical production-oriented safeguards in one end-to-end project.

## Google technology focus

- **Vertex AI Gemini** for model inference and tool-aware conversations
- **Firestore** for session-scoped persistent conversation history
- **Cloud Run** for containerized serverless deployment
- **Google Cloud authentication** through Application Default Credentials

## What this project demonstrates

This repository is designed as a practical reference for developers building agentic applications on Google Cloud. Rather than stopping at a single prompt/response example, it connects the model to memory, tools, an HTTP application layer, and deployable infrastructure.

### Core capabilities

- **Persistent memory** — conversation history is stored per session in Firestore
- **Tool calling** — the agent can invoke a calculator, a restricted web-fetch tool, and an email integration interface
- **REST API** — Flask endpoints support chat and session reset flows
- **Cloud deployment** — the application is structured for deployment to Cloud Run
- **Input safeguards** — validation, request-size controls, and domain allowlisting reduce unsafe tool execution
- **Responsive web UI** — a lightweight front end provides an interactive chat experience

## Architecture

```text
User
  ↓
Flask Web/API Layer
  ↓
Vertex AI Gemini
  ├── Conversation reasoning
  └── Tool selection
        ├── Calculator
        ├── Restricted Web Fetch
        └── Email integration interface
  ↓
Firestore session memory
  ↓
Cloud Run deployment
```

## Tech stack

| Layer | Technology |
|---|---|
| AI | Google Vertex AI Gemini |
| Memory | Google Cloud Firestore |
| Compute | Google Cloud Run |
| Backend | Python 3.11+, Flask |
| Front end | HTML, CSS, JavaScript |
| Auth | Google Cloud Application Default Credentials |

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/tejas5038/vertex-gemini-chatbot.git
cd vertex-gemini-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with:

```powershell
venv\Scripts\activate
```

### 3. Configure Google Cloud

Create your local environment file:

```bash
cp .env.example .env
```

Then configure your Google Cloud project and enable the services required by the application, including Vertex AI and Firestore.

Authenticate locally:

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 4. Run locally

```bash
python app.py
```

Open `http://localhost:8080`.

## Example API calls

Send a message:

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-session","user_message":"What is 25 * 47?"}'
```

Reset a conversation:

```bash
curl -X POST http://localhost:8080/api/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-session"}'
```

## Deploy to Cloud Run

After configuring your project-specific environment variables, deploy from the repository root:

```bash
gcloud run deploy vertex-gemini-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,GCP_LOCATION=us-central1,FIRESTORE_COLLECTION=chat_sessions
```

For a real production deployment, review authentication, authorization, rate limiting, logging, secrets management, and access policy before exposing the service publicly.

## Security design

The sample includes several safeguards that are useful when building tool-enabled AI systems:

- calculator expressions are constrained rather than passed to unrestricted execution
- web requests are limited to approved domains
- inputs and request sizes are validated
- credentials are expected to remain outside source control
- the email capability is an integration interface and is not enabled with embedded credentials

## Why this is useful

This project can be used as a starting point for workshops, demos, and experiments involving:

- Gemini-powered conversational applications
- agent memory patterns
- tool-use orchestration
- serverless AI deployment on Google Cloud
- secure integration of LLMs with external capabilities

## Selected upstream open-source contributions

Alongside building Google-technology projects, I contribute fixes and tests to open-source projects in the Google ecosystem.

- [Google Magika — PR #1443](https://github.com/google/magika/pull/1443) — merged upstream
- [Google Highway — PR #3361](https://github.com/google/highway/pull/3361) — merged upstream

## Author

**Tejas Pravinbhai Patel**  
Software Development Engineer | AI, distributed systems, and cloud engineering  
GitHub: [@tejas5038](https://github.com/tejas5038)

## License

MIT
