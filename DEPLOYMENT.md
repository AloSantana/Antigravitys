# Deployment Guide

Complete guide for deploying Antigravity Workspace to production.

## 🎯 Deployment Options

1. **Ubuntu VPS** - Recommended for most users
2. **Docker** - Best for containerized environments
3. **Kubernetes** - For large-scale deployments
4. **Cloud Platforms** - AWS, GCP, Azure

---

## 🚀 Ubuntu VPS Deployment

### Prerequisites

- Ubuntu 20.04+ or Debian 11+
- 2GB+ RAM (4GB recommended)
- 10GB+ disk space
- Root or sudo access
- Domain name (optional, for SSL)

### Automated Deployment

```bash
# 1. Clone repository
git clone https://github.com/primoscope/antigravity-workspace-template.git
cd antigravity-workspace-template

# 2. Run installer
sudo ./install.sh

# 3. Configure
./configure.sh

# 4. Enable and start service
sudo systemctl enable antigravity
sudo systemctl start antigravity

# 5. Check status
sudo systemctl status antigravity
```

### Manual Deployment

If you prefer manual setup:

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    nginx \
    supervisor \
    git curl wget

# 3. Install Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Install Docker (optional)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 5. Clone and setup
git clone https://github.com/primoscope/antigravity-workspace-template.git
cd antigravity-workspace-template

# 6. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 7. Install Python packages
pip install -r requirements.txt
pip install -r backend/requirements.txt

# 8. Install MCP servers
npm install -g \
    @modelcontextprotocol/server-filesystem \
    @modelcontextprotocol/server-git \
    @github/mcp-server \
    @modelcontextprotocol/server-memory \
    @modelcontextprotocol/server-sequential-thinking

# 9. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 10. Create systemd service
sudo cp /path/to/antigravity.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable antigravity
sudo systemctl start antigravity
```

### SSL Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

### Nginx Configuration

Edit `/etc/nginx/sites-available/antigravity`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend
    location / {
        root /path/to/antigravity-workspace-template/frontend;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/antigravity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t antigravity:latest .

# Run container
docker run -d \
  --name antigravity \
  --restart unless-stopped \
  -p 80:8000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/drop_zone:/app/drop_zone \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data.db:/app/data.db \
  antigravity:latest

# View logs
docker logs -f antigravity
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Scale backend
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/primoscope/antigravity-workspace-template:latest
    restart: always
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - COPILOT_MCP_GITHUB_TOKEN=${COPILOT_MCP_GITHUB_TOKEN}
    ports:
      - "8000:8000"
    volumes:
      - ./drop_zone:/app/drop_zone
      - ./logs:/app/logs
      - ./data.db:/app/data.db
    depends_on:
      - chromadb
      - redis
    networks:
      - antigravity
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  frontend:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - antigravity

  chromadb:
    image: chromadb/chroma:latest
    restart: always
    volumes:
      - chroma-data:/chroma/chroma
    networks:
      - antigravity

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - antigravity

volumes:
  chroma-data:
  redis-data:

networks:
  antigravity:
    driver: bridge
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm (optional)

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace antigravity

# Create secrets
kubectl create secret generic antigravity-secrets \
  --from-literal=gemini-api-key=${GEMINI_API_KEY} \
  --from-literal=github-token=${GITHUB_TOKEN} \
  -n antigravity

# Apply manifests
kubectl apply -f k8s/ -n antigravity

# Check status
kubectl get pods -n antigravity
kubectl get svc -n antigravity

# View logs
kubectl logs -f deployment/antigravity-backend -n antigravity
```

### Kubernetes Manifests

See `.github/agents/devops-infrastructure.agent.md` for complete K8s manifests including:
- Deployment
- Service
- Ingress
- HorizontalPodAutoscaler
- ConfigMap
- Secrets

---

## ☁️ Cloud Platform Deployment

### AWS

#### Using EC2

1. Launch EC2 instance (Ubuntu 20.04, t3.medium or larger)
2. Configure security group (ports 22, 80, 443, 8000)
3. SSH to instance
4. Run install script
5. Configure domain and SSL

#### Using ECS

```bash
# Build and push image
aws ecr create-repository --repository-name antigravity
docker build -t antigravity .
docker tag antigravity:latest <account>.dkr.ecr.<region>.amazonaws.com/antigravity:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/antigravity:latest

# Create ECS task definition and service
# See AWS ECS documentation
```

### Google Cloud Platform

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/antigravity

# Deploy to Cloud Run
gcloud run deploy antigravity \
  --image gcr.io/PROJECT_ID/antigravity \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=xxx
```

### Azure

```bash
# Create container registry
az acr create --resource-group myResourceGroup \
  --name antigravityRegistry --sku Basic

# Build and push
az acr build --registry antigravityRegistry \
  --image antigravity:latest .

# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name antigravity \
  --image antigravityRegistry.azurecr.io/antigravity:latest \
  --dns-name-label antigravity \
  --ports 8000
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

Never commit secrets to git:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Regular Updates

```bash
# Set up automatic security updates
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4. Monitoring

Set up monitoring with:
- Prometheus + Grafana
- DataDog
- New Relic
- CloudWatch (AWS)

### 5. Backup Strategy

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
cp data.db $BACKUP_DIR/data_$DATE.db

# Backup drop zone
tar -czf $BACKUP_DIR/dropzone_$DATE.tar.gz drop_zone/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/performance/health

# System health
./validate.sh
```

### Log Management

```bash
# View logs
sudo journalctl -u antigravity -f

# Rotate logs
sudo logrotate -f /etc/logrotate.d/antigravity

# Clear old logs
find logs/ -name "*.log" -mtime +30 -delete
```

### Performance Tuning

1. **Adjust worker count** in backend/main.py
2. **Enable caching** with Redis
3. **Use CDN** for static assets
4. **Database optimization** - add indexes
5. **Load balancing** - use multiple backend instances

---

## 🔄 Updates & Upgrades

### Update Application

```bash
# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart antigravity
```

### Zero-Downtime Updates

```bash
# Using Docker Compose
docker-compose pull
docker-compose up -d --no-deps --build backend

# Using systemd with graceful restart
sudo systemctl reload antigravity
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u antigravity -xe

# Check port availability
sudo lsof -i :8000

# Verify configuration
./validate.sh
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep python | sort -nrk 4 | head

# Adjust worker count
# Edit backend/main.py or use environment variable
export WORKERS=2
```

### Database Issues

```bash
# Backup database
cp data.db data.db.backup

# Vacuum database
sqlite3 data.db "VACUUM;"

# Check integrity
sqlite3 data.db "PRAGMA integrity_check;"
```

---

## 📚 Additional Resources

- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [.github/agents/](. github/agents/) - Agent documentation

---

## 🎉 Production Checklist

Before going live:

- [ ] SSL certificate installed
- [ ] Environment variables set
- [ ] Firewall configured
- [ ] Backups automated
- [ ] Monitoring enabled
- [ ] Logs configured
- [ ] Domain configured
- [ ] Health checks passing
- [ ] Performance tested
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Team trained

---

**Ready for production!** 🚀

For support:
- Issues: https://github.com/primoscope/antigravity-workspace-template/issues
- Discussions: https://github.com/primoscope/antigravity-workspace-template/discussions
