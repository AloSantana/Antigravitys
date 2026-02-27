# Cloud Deployment Guide

This guide provides comprehensive instructions for deploying Antigravity Workspace to cloud platforms.

## Table of Contents

- [Overview](#overview)
- [DigitalOcean App Platform](#digitalocean-app-platform)
- [Google Cloud Run](#google-cloud-run)
- [Environment Variables](#environment-variables)
- [Custom Domains](#custom-domains)
- [Cost Estimates](#cost-estimates)
- [Troubleshooting](#troubleshooting)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)

---

## Overview

Antigravity Workspace can be deployed to cloud platforms in two ways:

1. **One-Click Deployment** - Use the deploy buttons for instant setup
2. **Manual Deployment** - Follow step-by-step instructions for custom configurations
3. **CI/CD Pipeline** - Automated deployments via GitHub Actions

### Architecture

For cloud deployment, the backend serves both the API and the frontend static files from a single container. This simplifies deployment and ensures the web UI is immediately accessible.

**Key Features:**
- ✅ Backend serves frontend via FastAPI StaticFiles
- ✅ Content negotiation: browsers get HTML, APIs get JSON
- ✅ CORS configured for wildcard origins in cloud mode
- ✅ Health checks at `/health` endpoint
- ✅ WebSocket support for real-time communication

---

## DigitalOcean App Platform

### Prerequisites

1. **DigitalOcean Account**: Sign up at [digitalocean.com](https://www.digitalocean.com/)
2. **API Keys**: 
   - Gemini API key (required) - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - GitHub token (optional) - Get from [GitHub Settings](https://github.com/settings/tokens)

### One-Click Deployment

1. Click the deploy button:

   [![Deploy to DigitalOcean](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/primoscope/antigravity-workspace-template/tree/main)

2. **Configure the App:**
   - Authorize GitHub access if prompted
   - Review the app spec (pre-configured)
   - Click "Create Resources"

3. **Set Environment Variables:**
   - Navigate to **Settings → App-Level Environment Variables**
   - Add `GEMINI_API_KEY` (required)
   - Add `COPILOT_MCP_GITHUB_TOKEN` (optional)
   - Click "Save"

4. **Deploy:**
   - App Platform will automatically build and deploy
   - Wait 3-5 minutes for deployment
   - Access your app at the provided URL

### Manual Deployment via CLI

```bash
# Install doctl
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml --wait

# Get app URL
doctl apps list
```

### Configuration Details

The `.do/app.yaml` spec includes:

- **Service**: Single container running backend + frontend
- **Port**: 8000 (backend serves everything)
- **Health Check**: `/health` endpoint
- **Instance Size**: `professional-xs` (1GB RAM, 1 vCPU)
- **Redis**: Managed Redis 7 database
- **Auto-Deploy**: Enabled on push to main branch

### Scaling

To scale your DigitalOcean app:

```bash
# Scale horizontally (more instances)
doctl apps update <APP_ID> --spec .do/app.yaml

# Edit app.yaml and change:
# instance_count: 3  # Scale to 3 instances
```

Or via Dashboard:
- Go to **Settings → Scaling**
- Adjust instance count or size
- Click "Save"

---

## Google Cloud Run

### Prerequisites

1. **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com/)
2. **Project**: Create or select a GCP project
3. **Billing**: Enable billing on your project
4. **APIs**: Enable Cloud Run and Cloud Build APIs
5. **API Keys**: 
   - Gemini API key (required) - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - GitHub token (optional)

### One-Click Deployment

1. Click the deploy button:

   [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run/?git_repo=https://github.com/primoscope/antigravity-workspace-template)

2. **Configure Deployment:**
   - Sign in to Google Cloud
   - Select or create a project
   - Click "Deploy"

3. **Set Environment Variables:**
   - Enter `GEMINI_API_KEY` (required)
   - Enter `COPILOT_MCP_GITHUB_TOKEN` (optional)
   - Click "Deploy"

4. **Access:**
   - Wait 2-3 minutes for deployment
   - Access your app at the provided Cloud Run URL

### Manual Deployment via gcloud

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/antigravity-workspace

gcloud run deploy antigravity-workspace \
  --image gcr.io/YOUR_PROJECT_ID/antigravity-workspace \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "HOST=0.0.0.0,PORT=8000,ALLOWED_ORIGINS=*,REMOTE_ACCESS=true,GEMINI_API_KEY=your-key-here"
```

### Configuration Details

The `cloudbuild.yaml` includes:

- **Build Steps**: Docker build → Push to GCR → Deploy to Cloud Run
- **Image**: Multi-stage Dockerfile
- **Region**: `us-central1` (configurable)
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds
- **Concurrency**: 80 requests per instance
- **Scaling**: 0-10 instances (scales to zero)

### Setting Environment Variables

After deployment, update environment variables:

```bash
# Via CLI
gcloud run services update antigravity-workspace \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=your-key-here"

# List current variables
gcloud run services describe antigravity-workspace \
  --region us-central1 \
  --format "value(spec.template.spec.containers[0].env)"
```

Or via Console:
- Navigate to **Cloud Run → antigravity-workspace**
- Click "Edit & Deploy New Revision"
- Go to "Variables & Secrets" tab
- Add/edit environment variables
- Click "Deploy"

### Scaling Configuration

Cloud Run auto-scales by default. To customize:

```bash
gcloud run services update antigravity-workspace \
  --region us-central1 \
  --min-instances 1 \      # Keep 1 instance warm (costs more)
  --max-instances 20 \     # Allow up to 20 instances
  --concurrency 100        # 100 requests per instance
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini AI API key | `AIza...` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ALLOWED_ORIGINS` | CORS origins (use `*` for cloud) | `*` |
| `REMOTE_ACCESS` | Enable remote access mode | `true` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COPILOT_MCP_GITHUB_TOKEN` | GitHub PAT for MCP integration | - |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG_MODE` | Enable debug mode | `false` |
| `LOCAL_MODEL` | Ollama model name | `llama3` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `10485760` |
| `CACHE_TTL_SECONDS` | Response cache TTL | `300` |

### Setting Variables in Cloud Platforms

**DigitalOcean:**
```bash
# Via doctl
doctl apps update <APP_ID> --spec .do/app.yaml

# Edit app.yaml first to add variables
```

**Google Cloud Run:**
```bash
# Via gcloud
gcloud run services update antigravity-workspace \
  --region us-central1 \
  --set-env-vars "KEY=value,KEY2=value2"
```

---

## Custom Domains

### DigitalOcean

1. **Add Domain:**
   - Go to **Settings → Domains**
   - Click "Add Domain"
   - Enter your domain (e.g., `app.yourdomain.com`)
   - Follow DNS instructions

2. **Configure DNS:**
   - Add CNAME record in your DNS provider
   - Point to DigitalOcean's domain
   - Wait for DNS propagation (5-60 minutes)

3. **SSL:**
   - Automatically provisioned by Let's Encrypt
   - Renews automatically

### Google Cloud Run

1. **Domain Mapping:**
   ```bash
   gcloud run domain-mappings create \
     --service antigravity-workspace \
     --region us-central1 \
     --domain app.yourdomain.com
   ```

2. **Configure DNS:**
   - Follow instructions from the command output
   - Add DNS records (A, AAAA, or CNAME)
   - Verify domain ownership

3. **SSL:**
   - Automatically provisioned by Google-managed certificate
   - Renews automatically

---

## Cost Estimates

### DigitalOcean App Platform

**Basic Plan (~$5-12/month):**
- 512MB RAM, 1 vCPU
- $5/month base
- Redis: ~$7/month (optional)
- **Total**: $5-12/month

**Professional Plan (~$12-40/month):**
- 1GB RAM, 1 vCPU
- $12/month base
- Redis: ~$7/month (optional)
- Auto-scaling available
- **Total**: $12-40/month

**Bandwidth:**
- 1TB included
- $0.01/GB additional

### Google Cloud Run

**Pay-Per-Use Pricing:**

**Free Tier (per month):**
- 2 million requests
- 360,000 GB-seconds compute time
- 180,000 vCPU-seconds compute time
- 1GB egress

**Paid (after free tier):**
- Requests: $0.40 per million requests
- Compute time: $0.00002400 per GB-second
- vCPU time: $0.00001000 per vCPU-second
- Memory: $0.00000250 per GB-second
- Egress: $0.12 per GB

**Example (10K requests/day, avg 2s response time):**
- Monthly requests: 300K (within free tier)
- Compute: ~$5-15/month
- **Total**: ~$5-15/month

**Cost Optimization:**
- Use `--min-instances 0` to scale to zero (saves ~$10-20/month)
- Cache responses to reduce compute time
- Use Cloud CDN for static assets

---

## Troubleshooting

### Common Issues

#### 1. "Application Error" / 503 Service Unavailable

**Symptoms:**
- App fails to start
- Health check fails
- 503 errors

**Solutions:**
```bash
# Check logs (DigitalOcean)
doctl apps logs <APP_ID> --type run

# Check logs (Google Cloud Run)
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Common fixes:
# - Verify GEMINI_API_KEY is set
# - Check PORT is set to 8000
# - Ensure ALLOWED_ORIGINS includes *
# - Review build logs for errors
```

#### 2. WebSocket Connection Failed

**Symptoms:**
- Chat doesn't work
- Real-time updates fail

**Solutions:**
- Ensure `REMOTE_ACCESS=true` is set
- Check CORS configuration (`ALLOWED_ORIGINS=*`)
- Verify WebSocket protocol is allowed
- Test with browser DevTools Network tab

#### 3. File Upload Not Working

**Symptoms:**
- Can't upload files to drop zone
- Upload API returns 413 or 400

**Solutions:**
```bash
# Increase max file size
# DigitalOcean: Edit app.yaml
# Google Cloud Run: Update service

# Set environment variable
MAX_FILE_SIZE=52428800  # 50MB in bytes
```

#### 4. High Memory Usage / OOM Errors

**Symptoms:**
- App crashes randomly
- Out of memory errors in logs

**Solutions:**
```bash
# Increase memory allocation
# DigitalOcean: Change instance size in app.yaml
# Google Cloud Run: Update memory limit

gcloud run services update antigravity-workspace \
  --memory 4Gi  # Increase to 4GB
```

#### 5. Slow Cold Starts (Cloud Run)

**Symptoms:**
- First request takes 10-30 seconds
- Intermittent timeouts

**Solutions:**
```bash
# Keep 1 instance warm (costs ~$10-20/month)
gcloud run services update antigravity-workspace \
  --min-instances 1

# Optimize container startup time
# - Use lighter base images
# - Reduce dependencies
# - Enable HTTP/2
```

### Health Check Endpoints

Use these endpoints to diagnose issues:

```bash
# Basic health check
curl https://your-app-url.com/health

# Detailed readiness check
curl https://your-app-url.com/health/ready

# Liveness check
curl https://your-app-url.com/health/live

# Configuration
curl https://your-app-url.com/config
```

### Getting Help

1. **Check Logs:**
   - DigitalOcean: Dashboard → App → Runtime Logs
   - Google Cloud Run: Logging → Logs Explorer

2. **Test Locally:**
   ```bash
   docker build -t antigravity-test .
   docker run -p 8000:8000 \
     -e GEMINI_API_KEY=your-key \
     -e ALLOWED_ORIGINS=* \
     -e REMOTE_ACCESS=true \
     antigravity-test
   ```

3. **Community Support:**
   - GitHub Issues: [primoscope/antigravity-workspace-template](https://github.com/primoscope/antigravity-workspace-template/issues)
   - Discussions: [GitHub Discussions](https://github.com/primoscope/antigravity-workspace-template/discussions)

---

## CI/CD with GitHub Actions

Both platforms include GitHub Actions workflows for automated deployment.

### DigitalOcean CI/CD

**Setup:**

1. Generate DigitalOcean API token:
   - Go to [API Tokens](https://cloud.digitalocean.com/account/api/tokens)
   - Click "Generate New Token"
   - Copy token

2. Add to GitHub Secrets:
   - Go to repository **Settings → Secrets and variables → Actions**
   - Add secret: `DIGITALOCEAN_ACCESS_TOKEN`

3. Trigger deployment:
   - Go to **Actions → Deploy to DigitalOcean App Platform**
   - Click "Run workflow"

**Workflow file:** `.github/workflows/deploy-digitalocean.yml`

### Google Cloud Run CI/CD

**Setup:**

1. Create service account:
   ```bash
   gcloud iam service-accounts create github-deployer \
     --display-name "GitHub Actions Deployer"
   
   # Grant permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com \
     --role roles/run.admin
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com \
     --role roles/storage.admin
   
   # Create key
   gcloud iam service-accounts keys create key.json \
     --iam-account github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

2. Add to GitHub Secrets:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Contents of `key.json` file

3. Trigger deployment:
   - Go to **Actions → Deploy to Google Cloud Run**
   - Select region
   - Click "Run workflow"

**Workflow file:** `.github/workflows/deploy-gcp.yml`

### Automatic Deployments

To deploy automatically on every push to main:

**DigitalOcean:**
- Already configured in `app.yaml`: `deploy_on_push: true`

**Google Cloud Run:**
- Modify `.github/workflows/deploy-gcp.yml`:
  ```yaml
  on:
    push:
      branches:
        - main
    workflow_dispatch:  # Keep manual option
  ```

---

## Best Practices

### Security

1. **Use Secrets for API Keys:**
   - Never commit API keys to code
   - Use platform secret management
   - Rotate keys regularly

2. **Restrict CORS in Production:**
   - Change `ALLOWED_ORIGINS=*` to specific domains
   - Add your custom domain only

3. **Enable Authentication:**
   - Consider adding authentication layer
   - Use OAuth or JWT tokens
   - Restrict sensitive endpoints

### Performance

1. **Enable Caching:**
   - Use Redis for response caching
   - Configure CDN for static assets
   - Set appropriate cache TTLs

2. **Optimize Container:**
   - Use multi-stage builds
   - Minimize image size
   - Use .dockerignore

3. **Monitor Resources:**
   - Set up alerting for errors
   - Monitor memory/CPU usage
   - Track response times

### Cost Optimization

1. **Cloud Run:**
   - Use `--min-instances 0` for low traffic
   - Increase concurrency to reduce instances
   - Monitor and adjust memory allocation

2. **DigitalOcean:**
   - Start with Basic plan, scale as needed
   - Use managed databases for persistence
   - Monitor bandwidth usage

3. **General:**
   - Implement response caching
   - Optimize API calls to external services
   - Use compression for responses

---

## Next Steps

- ✅ Deploy to your preferred platform
- ✅ Configure environment variables
- ✅ Set up custom domain (optional)
- ✅ Configure CI/CD for automatic deployments
- ✅ Monitor logs and performance
- ✅ Set up alerts and monitoring

**Happy Deploying! 🚀**
