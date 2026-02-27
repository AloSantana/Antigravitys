# Vertex AI Setup Guide

This guide explains how to set up and use Google Cloud's Vertex AI with the Antigravity Workspace.

## Table of Contents
- [What is Vertex AI](#what-is-vertex-ai)
- [Prerequisites](#prerequisites)
- [Setup Methods](#setup-methods)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## What is Vertex AI

Vertex AI is Google Cloud's unified AI platform that provides:
- Access to Google's latest AI models (Gemini Pro, PaLM, etc.)
- Enterprise-grade security and compliance
- Better scalability and reliability than Gemini API alone
- Advanced features like custom model training and deployment

**When to use Vertex AI vs Gemini API:**
- **Vertex AI**: Production deployments, enterprise use, higher quotas, better SLAs
- **Gemini API**: Development, prototyping, personal projects, simpler setup

## Prerequisites

1. **Google Cloud Project**:
   - Create a GCP project at [console.cloud.google.com](https://console.cloud.google.com)
   - Enable billing for your project

2. **Enable Vertex AI API**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```
   Or enable via [Cloud Console](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)

3. **Python Dependencies**:
   ```bash
   pip install google-cloud-aiplatform
   ```

## Setup Methods

### Method 1: API Key (Simplest)

**Note**: API keys for Vertex AI are less common. Service accounts are recommended.

If you have a Vertex AI API key:

1. Add to `.env`:
   ```env
   VERTEX_API_KEY=your_vertex_api_key_here
   VERTEX_PROJECT_ID=your-gcp-project-id
   VERTEX_LOCATION=us-central1
   VERTEX_MODEL=gemini-pro
   ```

2. The provided key has been set:
   ```env
   VERTEX_API_KEY=AQ.Ab8RN6I5PKJWHHwXUERPtSAl_MO3plENhgsJa2vXkDrU6YXMhw
   ```

### Method 2: Service Account (Recommended for Production)

1. **Create Service Account**:
   - Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click "Create Service Account"
   - Name: `antigravity-vertex-ai`
   - Grant role: "Vertex AI User" or "Vertex AI Service Agent"

2. **Create JSON Key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the key file

3. **Configure**:
   ```bash
   # Set environment variable
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   
   # Or add to .env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   VERTEX_PROJECT_ID=your-gcp-project-id
   VERTEX_LOCATION=us-central1
   ```

### Method 3: gcloud CLI (Local Development)

1. **Install gcloud CLI**:
   ```bash
   # For Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # For macOS
   brew install --cask google-cloud-sdk
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud auth application-default login
   ```

3. **Configure .env**:
   ```env
   VERTEX_PROJECT_ID=your-gcp-project-id
   VERTEX_LOCATION=us-central1
   ```

## Configuration

### Environment Variables

Add to `.env` file:

```env
# ═══ Vertex AI Configuration ═══

# API Key (if using API key authentication)
VERTEX_API_KEY=AQ.Ab8RN6I5PKJWHHwXUERPtSAl_MO3plENhgsJa2vXkDrU6YXMhw

# Project Configuration
VERTEX_PROJECT_ID=your-gcp-project-id

# Region/Location (choose nearest to your users)
# Options: us-central1, us-east1, europe-west1, asia-southeast1, etc.
VERTEX_LOCATION=us-central1

# Model Selection
# Options: gemini-pro, gemini-pro-vision, text-bison, chat-bison
VERTEX_MODEL=gemini-pro
```

### Available Models

| Model | Best For | Context Window |
|-------|----------|----------------|
| `gemini-pro` | Text generation, reasoning | 32K tokens |
| `gemini-pro-vision` | Multimodal (text + images) | 16K tokens |
| `text-bison` | Text completion | 8K tokens |
| `chat-bison` | Conversational AI | 8K tokens |

### Region Selection

Choose the region closest to your users:

- **North America**: `us-central1`, `us-east1`, `us-west1`
- **Europe**: `europe-west1`, `europe-west4`
- **Asia**: `asia-southeast1`, `asia-northeast1`

## Usage

### Automatic Usage

The orchestrator automatically uses Vertex AI when:
1. Vertex AI is configured and available
2. A high-complexity request is received
3. Local LLM fails and Vertex AI is available

Priority: **Vertex AI** > Gemini API > Local LLM (for high-complexity tasks)

### Check Status

```bash
# Check if Vertex AI is configured
curl http://localhost:8000/agent/stats

# Response includes Vertex AI status:
{
  "vertex_ai_available": true,
  "vertex_ai_model": "gemini-pro",
  "vertex_ai_project": "your-project-id"
}
```

### Test Generation

```python
import asyncio
from backend.agent.vertex_client import VertexClient

async def test():
    client = VertexClient()
    if client.is_available():
        response = await client.generate("Hello, how are you?")
        print(response)
    else:
        print("Vertex AI not available")

asyncio.run(test())
```

## Testing

### Test 1: Check Configuration

```bash
cd backend
python3 -c "
from agent.vertex_client import VertexClient
import asyncio

async def test():
    client = VertexClient()
    stats = client.get_stats()
    print('Vertex AI Stats:', stats)
    print('Available:', client.is_available())

asyncio.run(test())
"
```

### Test 2: Generate Text

```bash
cd backend
python3 << 'EOF'
import asyncio
from agent.vertex_client import VertexClient

async def main():
    client = VertexClient()
    if not client.is_available():
        print("Vertex AI not available")
        return
    
    response = await client.generate("Write a haiku about coding")
    print("Response:", response)

asyncio.run(main())
EOF
```

### Test 3: Full Integration

```bash
# Start the server
./start.sh

# In another terminal, test the API
curl -X POST http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"request": "Please analyze the architecture of a microservices system"}'

# This should use Vertex AI (high complexity)
```

## Troubleshooting

### Error: "Vertex AI SDK not installed"

```bash
pip install google-cloud-aiplatform
# Or
pip install -r backend/requirements.txt
```

### Error: "Authentication failed"

**Check your authentication:**

```bash
# Method 1: Service account
echo $GOOGLE_APPLICATION_CREDENTIALS
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Method 2: gcloud
gcloud auth application-default print-access-token

# Method 3: API key
echo $VERTEX_API_KEY
```

### Error: "Project ID not set"

Add to `.env`:
```env
VERTEX_PROJECT_ID=your-actual-project-id
```

Or set via gcloud:
```bash
gcloud config set project YOUR_PROJECT_ID
```

### Error: "Permission denied"

Ensure your service account has the correct roles:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Error: "API not enabled"

```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### Error: "Quota exceeded"

Check your quota at [Cloud Console](https://console.cloud.google.com/iam-admin/quotas):
- Search for "Vertex AI API"
- Request quota increase if needed

## Cost Considerations

Vertex AI pricing varies by model and usage:

- **Gemini Pro**: ~$0.00025 per 1K characters input, ~$0.0005 per 1K characters output
- **Text Bison**: ~$0.001 per 1K characters
- **Free tier**: Some models have free quotas

**Monitor costs:**
- [Cloud Console Billing](https://console.cloud.google.com/billing)
- Set up budget alerts
- Use caching (already implemented) to reduce API calls

## Best Practices

1. **Use Service Accounts**: More secure than API keys
2. **Enable Caching**: Reduces API calls and costs (already enabled)
3. **Set Budget Alerts**: Monitor and control costs
4. **Use Appropriate Region**: Minimize latency
5. **Rotate Credentials**: Regular security practice
6. **Monitor Usage**: Track API calls and costs
7. **Fallback Strategy**: Keep Gemini API or Local LLM as fallback

## Security Notes

- **Never commit credentials**: Use `.env` (already in `.gitignore`)
- **Rotate API keys**: Regularly change credentials
- **Limit permissions**: Use least-privilege service accounts
- **Monitor access**: Check Cloud Audit Logs
- **Use VPC**: For enterprise deployments

## Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Best Practices](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/best-practices)

---

**Your Vertex AI is now configured and ready to use!** 🚀

The system will automatically use Vertex AI for high-complexity requests, providing enterprise-grade AI capabilities to your workspace.
