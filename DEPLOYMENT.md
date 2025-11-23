# Deployment Guide

## Prerequisites

### 1. GCP Account Setup
- Create a GCP project or use an existing one
- Enable billing on your project
- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### 2. Enable Required APIs

```bash
# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Create Firestore Database

```bash
# Create Firestore database in Native mode
gcloud firestore databases create --location=us-central1
```

Or via Console:
1. Go to https://console.cloud.google.com/firestore
2. Click "Create Database"
3. Select "Native mode"
4. Choose region: us-central1
5. Click "Create"

## Local Development

### 1. Setup Environment

```bash
# Clone/navigate to project
cd vertex-gemini-agent-chatbot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Required variables:
```
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-exp
FIRESTORE_COLLECTION=chat_sessions
```

### 3. Authenticate with GCP

```bash
# Login and set application default credentials
gcloud auth application-default login

# Verify your project is set
gcloud config get-value project
```

### 4. Run Locally

```bash
python app.py
```

Visit http://localhost:8080

## Cloud Run Deployment

### Option 1: Deploy from Source (Recommended)

```bash
# Deploy with gcloud
gcloud run deploy vertex-gemini-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCP_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash-exp,FIRESTORE_COLLECTION=chat_sessions \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0
```

### Option 2: Using Dockerfile

```bash
# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/vertex-gemini-chatbot

# Deploy
gcloud run deploy vertex-gemini-chatbot \
  --image gcr.io/$PROJECT_ID/vertex-gemini-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,GCP_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash-exp,FIRESTORE_COLLECTION=chat_sessions
```

### Option 3: Continuous Deployment with Cloud Build

Create `cloudbuild.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/vertex-gemini-chatbot', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/vertex-gemini-chatbot']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'vertex-gemini-chatbot'
      - '--image'
      - 'gcr.io/$PROJECT_ID/vertex-gemini-chatbot'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
images:
  - 'gcr.io/$PROJECT_ID/vertex-gemini-chatbot'
```

## Post-Deployment

### Get Service URL

```bash
gcloud run services describe vertex-gemini-chatbot \
  --region us-central1 \
  --format 'value(status.url)'
```

### Test Deployment

```bash
# Get the URL
SERVICE_URL=$(gcloud run services describe vertex-gemini-chatbot \
  --region us-central1 \
  --format 'value(status.url)')

# Health check
curl $SERVICE_URL/health

# Test chat
curl -X POST $SERVICE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "user_message": "What is 10 * 5?"}'
```

### View Logs

```bash
# Stream logs
gcloud run services logs tail vertex-gemini-chatbot --region us-central1

# View recent logs
gcloud run services logs read vertex-gemini-chatbot --region us-central1 --limit 50
```

## Security Enhancements (Production)

### 1. Add Authentication

Update deployment to require authentication:

```bash
gcloud run deploy vertex-gemini-chatbot \
  --no-allow-unauthenticated \
  --region us-central1
```

Then configure IAM for authorized users.

### 2. Use Secret Manager for Sensitive Data

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding api-key \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Deploy with secret
gcloud run deploy vertex-gemini-chatbot \
  --update-secrets=API_KEY=api-key:latest
```

### 3. Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service vertex-gemini-chatbot \
  --domain chat.yourdomain.com \
  --region us-central1
```

## Monitoring & Observability

### Enable Cloud Monitoring

1. Go to Cloud Console → Monitoring
2. Create alerts for:
   - Error rate > 5%
   - Response time > 5s
   - CPU utilization > 80%

### View Metrics

```bash
# Cloud Console
https://console.cloud.google.com/run/detail/us-central1/vertex-gemini-chatbot/metrics
```

## Cost Optimization

### Set Resource Limits

```bash
gcloud run deploy vertex-gemini-chatbot \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 5 \
  --concurrency 80
```

### Enable Request Timeout

```bash
gcloud run deploy vertex-gemini-chatbot \
  --timeout 300  # 5 minutes max
```

## Troubleshooting

### Common Issues

1. **Firestore Permission Denied**
   - Ensure Firestore API is enabled
   - Check service account has Firestore User role

2. **Vertex AI Authentication Failed**
   - Verify Vertex AI API is enabled
   - Check project ID is correct in environment variables

3. **Cold Start Timeout**
   - Increase timeout: `--timeout 300`
   - Consider min-instances: `--min-instances 1`

### Debug Logs

```bash
# Enable detailed logging
gcloud run deploy vertex-gemini-chatbot \
  --set-env-vars LOG_LEVEL=DEBUG
```

## Rollback

```bash
# List revisions
gcloud run revisions list --service vertex-gemini-chatbot --region us-central1

# Rollback to previous revision
gcloud run services update-traffic vertex-gemini-chatbot \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

## Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete vertex-gemini-chatbot --region us-central1

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/vertex-gemini-chatbot

# Delete Firestore data (be careful!)
# Use Firebase Console: https://console.firebase.google.com
```
