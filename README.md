# Vertex AI Gemini Agent Chatbot

A production-ready AI chatbot powered by Google Vertex AI Gemini with conversation memory and tool-calling capabilities.

## Features

- 🧠 **Persistent Memory**: Conversation history stored in Firestore per session
- 🛠️ **Tool Calling**: Calculator, web fetch, and email stub tools
- 🚀 **Production Ready**: Deploys to GCP Cloud Run
- 💬 **Real-time UI**: Clean, responsive chat interface
- 🔒 **Secure**: Input validation, whitelisting, safe execution

## Tools Available

1. **Calculator**: Safe mathematical expression evaluation
2. **Web Fetch**: HTTP requests to whitelisted public APIs
3. **Email (Stub)**: Interface ready for Gmail API integration

## Prerequisites

- Python 3.11+
- GCP Project with Vertex AI API enabled
- Firestore database created
- GCP credentials configured locally

## Quick Start

### 1. Clone and Setup

```bash
cd vertex-gemini-agent-chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your GCP project details
```

### 3. Authenticate with GCP

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 4. Run Locally

```bash
python app.py
```

Visit http://localhost:8080

## Deployment to Cloud Run

### 1. Build and Deploy

```bash
gcloud run deploy vertex-gemini-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project-id,GCP_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash-exp,FIRESTORE_COLLECTION=chat_sessions
```

### 2. Access Your App

The deployment will provide a URL like:
https://vertex-gemini-chatbot-xxxxx-uc.a.run.app

## Testing

### cURL Examples

```bash
# Send a chat message
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-1", "user_message": "What is 25 * 47?"}'

# Reset conversation
curl -X POST http://localhost:8080/api/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-1"}'

# Test web fetch tool
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-2", "user_message": "Fetch the current Bitcoin price from https://api.coindesk.com/v1/bpi/currentprice.json"}'
```

## Architecture

```
User → Flask App → Vertex AI Gemini → Tool Execution → Firestore
         ↓                                ↓
    HTML/CSS/JS                    Calculator/WebFetch/Email
```

## Security Notes

- Calculator: Only evaluates safe mathematical expressions
- Web Fetch: Whitelisted domains only
- Email: Stub implementation with OAuth placeholder
- Input validation on all endpoints
- Request size limits enforced

## Email Tool Setup (Optional)

To enable the email tool:

1. Enable Gmail API in GCP Console
2. Create OAuth 2.0 credentials
3. Download credentials.json
4. Run the OAuth flow locally
5. Update `shared/tools.py` with credentials path
6. Uncomment email execution code

## Environment Variables

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_LOCATION`: Vertex AI location (e.g., us-central1)
- `GEMINI_MODEL`: Model name (default: gemini-2.0-flash-exp)
- `FIRESTORE_COLLECTION`: Collection name for chat history

## License

MIT
