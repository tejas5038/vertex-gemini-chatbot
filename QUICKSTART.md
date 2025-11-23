# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Extract the Project

```bash
unzip vertex-gemini-agent-chatbot.zip
cd vertex-gemini-agent-chatbot
```

### Step 2: Set Up Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure GCP

```bash
# Login to GCP
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com firestore.googleapis.com

# Create Firestore database
gcloud firestore databases create --location=us-central1
```

### Step 4: Configure Environment

```bash
cp .env.example .env
# Edit .env and set:
# GCP_PROJECT_ID=your-project-id
```

### Step 5: Run Locally

```bash
python app.py
```

Visit **http://localhost:8080** 🎉

---

## 📦 What's Included

```
vertex-gemini-agent-chatbot/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # For Cloud Run deployment
├── README.md                # Full documentation
├── DEPLOYMENT.md            # Detailed deployment guide
├── test_api.sh             # API testing script
├── .env.example            # Environment template
├── shared/                 # Shared modules
│   ├── utils.py           # Gemini client initialization
│   ├── decorators.py      # Error handling
│   ├── validators.py      # Input validation
│   ├── tools.py           # Tool implementations
│   └── memory_store.py    # Firestore memory
├── templates/
│   └── index.html         # Chat UI
└── static/
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

---

## 🧪 Testing

### Run Test Suite

```bash
chmod +x test_api.sh
./test_api.sh http://localhost:8080
```

### Manual Testing with cURL

```bash
# Test calculator
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-1", "user_message": "What is 25 * 47?"}'

# Test web fetch
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-1", "user_message": "Fetch Bitcoin price from https://api.coindesk.com/v1/bpi/currentprice.json"}'
```

---

## ☁️ Deploy to Cloud Run

### One-Command Deployment

```bash
gcloud run deploy vertex-gemini-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project-id,GCP_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash-exp,FIRESTORE_COLLECTION=chat_sessions
```

### Get Your URL

```bash
gcloud run services describe vertex-gemini-chatbot \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## 🛠️ Available Tools

1. **Calculator** - Evaluates math expressions safely
   - Example: "What is 123 + 456 * 789?"

2. **Web Fetch** - Retrieves data from whitelisted APIs
   - Example: "Get Bitcoin price from https://api.coindesk.com/v1/bpi/currentprice.json"

3. **Email (Stub)** - Email interface (requires Gmail API setup)
   - Example: "Send email to john@example.com"

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Your GCP project ID | Required |
| `GCP_LOCATION` | Vertex AI location | us-central1 |
| `GEMINI_MODEL` | Model to use | gemini-2.0-flash-exp |
| `FIRESTORE_COLLECTION` | Collection name | chat_sessions |

### Whitelisted Domains (Web Fetch)

Edit `shared/tools.py` to add more domains:

```python
ALLOWED_DOMAINS = [
    'api.coindesk.com',
    'api.github.com',
    'jsonplaceholder.typicode.com',
    # Add your domains here
]
```

---

## 📚 Documentation

- **README.md** - Full project documentation
- **DEPLOYMENT.md** - Detailed deployment guide with troubleshooting
- **test_api.sh** - Automated API testing script

---

## 🆘 Common Issues

### "GCP_PROJECT_ID environment variable is required"
- Make sure you copied `.env.example` to `.env`
- Set `GCP_PROJECT_ID=your-actual-project-id`

### "Permission denied" on Firestore
- Enable Firestore API: `gcloud services enable firestore.googleapis.com`
- Create database: `gcloud firestore databases create --location=us-central1`

### "Module not found" errors
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

---

## 💡 Next Steps

1. **Customize the UI** - Edit `templates/index.html` and `static/style.css`
2. **Add More Tools** - Extend `shared/tools.py`
3. **Enable Email** - Set up Gmail API (see DEPLOYMENT.md)
4. **Add Authentication** - Implement user auth (see DEPLOYMENT.md)
5. **Monitor Usage** - Set up Cloud Monitoring

---

## 📞 Support

For detailed information:
- Full README: `README.md`
- Deployment guide: `DEPLOYMENT.md`
- Test the API: `./test_api.sh`

---

**Built with ❤️ using Google Vertex AI Gemini**
